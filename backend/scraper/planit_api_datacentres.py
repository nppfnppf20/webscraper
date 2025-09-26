from __future__ import annotations

import time
from datetime import date, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlencode
import requests

from .session import make_session


class PlanItAPIError(Exception):
    """Exception raised when PlanIt API returns an error"""
    pass


class PlanItAPIRateLimit(Exception):
    """Exception raised when PlanIt API rate limit is exceeded"""
    def __init__(self, retry_after_seconds: int):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"Rate limit exceeded. Retry after {retry_after_seconds} seconds.")


def fetch_datacentres_from_planit_api() -> List[Dict]:
    """
    Fetch datacentre projects using the PlanIt API
    Uses datacentre-specific search terms for last 3 months

    Returns:
        List of planning applications for datacentre projects
    """

    # Use the same API endpoint but with datacentre search terms
    base_url = "https://www.planit.org.uk/api/applics/json"

    # Datacentre-specific search terms for last 3 months (90 days)
    params = {
        'recent': '90',  # Last 90 days (3 months)
        'search': '"data centre" or "data center" or datacenter or datacentre or "server farm" or "computer facility" or "cloud facility" or "hosting facility" or "data facility" or "data storage" or "server hall" or "telecommunications facility"',
        'select': '*',  # Select all fields
        'sort': '-start_date',  # Sort by start date descending
        'pg_sz': '300',  # 300 results per page
        'page': '1',  # Start with page 1
        'compress': 'on'  # Compress response
    }

    session = make_session()
    all_results = []
    page = 1
    total_found = 0

    print(f"[PlanIt API Datacentres] 🚀 Searching for datacentre projects from last 3 months")

    while True:
        params['page'] = str(page)
        url = f"{base_url}?{urlencode(params)}"

        print(f"[PlanIt API Datacentres] Requesting page {page}... ", end="", flush=True)

        try:
            # Make API request with proper headers
            response = session.get(url, timeout=30, headers={
                'User-Agent': 'Web Scraper Dashboard - Datacentres Research',
                'Accept': 'application/json'
            })

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60"))
                print(f"\n[PlanIt API Datacentres] 🛑 Rate limited! Need to wait {retry_after}s")
                raise PlanItAPIRateLimit(retry_after)

            # Handle other errors
            if response.status_code != 200:
                error_msg = f"API returned status {response.status_code}: {response.text[:200]}"
                print(f"\n[PlanIt API Datacentres] ❌ {error_msg}")
                raise PlanItAPIError(error_msg)

            data = response.json()

            # Check for API errors in response
            if 'error' in data:
                error_msg = f"API error: {data['error']}"
                print(f"\n[PlanIt API Datacentres] ❌ {error_msg}")
                raise PlanItAPIError(error_msg)

            # Extract results
            records = data.get('records', [])
            total_found = data.get('total', 0)
            from_idx = data.get('from', 0)
            to_idx = data.get('to', 0)

            print(f"Got {len(records)} records (showing {from_idx+1}-{to_idx+1} of {total_found} total)")

            if not records:
                print("[PlanIt API Datacentres] No more records found")
                break

            # Add results to our collection
            all_results.extend(records)

            # Check if we got all results (if we got less than page size, we're done)
            if len(records) < 300 or to_idx >= total_found - 1:
                print(f"[PlanIt API Datacentres] ✅ Retrieved all available results")
                break

            page += 1

            # Be respectful with rate limiting
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"\n[PlanIt API Datacentres] ❌ Network error: {e}")
            raise PlanItAPIError(f"Network error: {e}")

    print(f"[PlanIt API Datacentres] 🎯 Total results collected: {len(all_results)}")
    return all_results


def normalize_planit_datacentres_result(record: Dict) -> Dict[str, str]:
    """
    Pass through ALL fields from PlanIt API - no filtering
    Convert everything to strings for CSV compatibility
    """
    result = {}

    # Convert all fields to strings and include them
    for key, value in record.items():
        if key == 'location' and isinstance(value, dict):
            # Special handling for location - extract coordinates if available
            if value.get('type') == 'Point' and value.get('coordinates'):
                coords = value['coordinates']
                if len(coords) >= 2:
                    result['lng'] = str(coords[0])  # Longitude first in GeoJSON
                    result['lat'] = str(coords[1])  # Latitude second
                else:
                    result['lat'] = ''
                    result['lng'] = ''
            else:
                result['lat'] = ''
                result['lng'] = ''
            # Also keep the raw location data
            result['location'] = str(value)
        elif isinstance(value, (dict, list)):
            # Convert complex objects to strings
            result[key] = str(value)
        else:
            # Convert simple values to strings
            result[key] = str(value) if value is not None else ''

    return result