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


def fetch_renewables_historical_from_planit_api(start_date: str, end_date: str) -> List[Dict]:
    """
    Fetch historical renewables projects using the PlanIt API for a specific date range

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List of planning applications for renewables projects
    """

    # Use the same API endpoint but with specific date range
    base_url = "https://www.planit.org.uk/api/applics/json"

    # Historical search with specific date range
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'search': '"solar farm" or photovoltaic or "battery storage" or BESS or "energy storage" or "wind turbine" or windfarm or hydro or "anaerobic digestion"',
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

    print(f"[PlanIt API Renewables Historical] 🚀 Searching for renewables projects from {start_date} to {end_date}")

    while True:
        params['page'] = str(page)
        url = f"{base_url}?{urlencode(params)}"

        print(f"[PlanIt API Renewables Historical] Requesting page {page}... ", end="", flush=True)

        try:
            # Make API request with proper headers
            response = session.get(url, timeout=30, headers={
                'User-Agent': 'Web Scraper Dashboard - Renewables Historical Research',
                'Accept': 'application/json'
            })

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60"))
                print(f"\n[PlanIt API Renewables Historical] 🛑 Rate limited! Need to wait {retry_after}s")
                raise PlanItAPIRateLimit(retry_after)

            # Handle other errors
            if response.status_code != 200:
                error_msg = f"API returned status {response.status_code}: {response.text[:200]}"
                print(f"\n[PlanIt API Renewables Historical] ❌ {error_msg}")
                raise PlanItAPIError(error_msg)

            data = response.json()

            # Check for API errors in response
            if 'error' in data:
                error_msg = f"API error: {data['error']}"
                print(f"\n[PlanIt API Renewables Historical] ❌ {error_msg}")
                raise PlanItAPIError(error_msg)

            # Extract results
            records = data.get('records', [])
            total_found = data.get('total', 0)
            from_idx = data.get('from', 0)
            to_idx = data.get('to', 0)

            print(f"Got {len(records)} records (showing {from_idx+1}-{to_idx+1} of {total_found} total)")

            if not records:
                print("[PlanIt API Renewables Historical] No more records found")
                break

            # Add results to our collection
            all_results.extend(records)

            # Check if we got all results (if we got less than page size, we're done)
            if len(records) < 300 or to_idx >= total_found - 1:
                print(f"[PlanIt API Renewables Historical] ✅ Retrieved all available results")
                break

            page += 1

            # Be respectful with rate limiting
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"\n[PlanIt API Renewables Historical] ❌ Network error: {e}")
            raise PlanItAPIError(f"Network error: {e}")

    print(f"[PlanIt API Renewables Historical] 🎯 Total results collected: {len(all_results)}")
    return all_results


def normalize_planit_renewables_result(record: Dict) -> Dict[str, str]:
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