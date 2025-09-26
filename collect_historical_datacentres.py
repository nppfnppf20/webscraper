#!/usr/bin/env python3

import time
from datetime import date, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlencode
import requests
import csv
import os

# Session creation (copied from session.py)
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def make_session():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Referer": "https://www.planit.org.uk/",
            "Connection": "keep-alive",
        }
    )
    return session

# Exception classes
class PlanItAPIError(Exception):
    """Exception raised when PlanIt API returns an error"""
    pass

class PlanItAPIRateLimit(Exception):
    """Exception raised when PlanIt API rate limit is exceeded"""
    def __init__(self, retry_after_seconds: int):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"Rate limit exceeded. Retry after {retry_after_seconds} seconds.")

def fetch_datacentres_historical_from_planit_api(start_date: str, end_date: str) -> List[Dict]:
    """
    Fetch historical datacentre projects using the PlanIt API for a specific date range
    """

    base_url = "https://www.planit.org.uk/api/applics/json"

    params = {
        'start_date': start_date,
        'end_date': end_date,
        'search': '"data centre" or "data center" or datacenter or datacentre or "server farm" or "computer facility" or "cloud facility" or "hosting facility" or "data facility" or "data storage" or "server hall" or "telecommunications facility"',
        'select': '*',
        'sort': '-start_date',
        'pg_sz': '300',
        'page': '1',
        'compress': 'on'
    }

    session = make_session()
    all_results = []
    page = 1
    total_found = 0

    print(f"[PlanIt API Datacentres Historical] 🚀 Searching for datacentre projects from {start_date} to {end_date}")

    while True:
        params['page'] = str(page)
        url = f"{base_url}?{urlencode(params)}"

        print(f"[PlanIt API Datacentres Historical] Requesting page {page}... ", end="", flush=True)

        try:
            response = session.get(url, timeout=30, headers={
                'User-Agent': 'Web Scraper Dashboard - Datacentres Historical Research',
                'Accept': 'application/json'
            })

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60"))
                print(f"\\n[PlanIt API Datacentres Historical] 🛑 Rate limited! Need to wait {retry_after}s")
                raise PlanItAPIRateLimit(retry_after)

            if response.status_code != 200:
                error_msg = f"API returned status {response.status_code}: {response.text[:200]}"
                print(f"\\n[PlanIt API Datacentres Historical] ❌ {error_msg}")
                raise PlanItAPIError(error_msg)

            data = response.json()

            if 'error' in data:
                error_msg = f"API error: {data['error']}"
                print(f"\\n[PlanIt API Datacentres Historical] ❌ {error_msg}")
                raise PlanItAPIError(error_msg)

            records = data.get('records', [])
            total_found = data.get('total', 0)
            from_idx = data.get('from', 0)
            to_idx = data.get('to', 0)

            print(f"Got {len(records)} records (showing {from_idx+1}-{to_idx+1} of {total_found} total)")

            if not records:
                print("[PlanIt API Datacentres Historical] No more records found")
                break

            all_results.extend(records)

            if len(records) < 300 or to_idx >= total_found - 1:
                print(f"[PlanIt API Datacentres Historical] ✅ Retrieved all available results")
                break

            page += 1
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"\\n[PlanIt API Datacentres Historical] ❌ Network error: {e}")
            raise PlanItAPIError(f"Network error: {e}")

    print(f"[PlanIt API Datacentres Historical] 🎯 Total results collected: {len(all_results)}")
    return all_results

def normalize_planit_datacentres_result(record: Dict) -> Dict[str, str]:
    """
    Pass through ALL fields from PlanIt API - no filtering
    Convert everything to strings for CSV compatibility
    """
    result = {}

    for key, value in record.items():
        if key == 'location' and isinstance(value, dict):
            if value.get('type') == 'Point' and value.get('coordinates'):
                coords = value['coordinates']
                if len(coords) >= 2:
                    result['lng'] = str(coords[0])
                    result['lat'] = str(coords[1])
                else:
                    result['lat'] = ''
                    result['lng'] = ''
            else:
                result['lat'] = ''
                result['lng'] = ''
            result['location'] = str(value)
        elif isinstance(value, (dict, list)):
            result[key] = str(value)
        else:
            result[key] = str(value) if value is not None else ''

    return result

def main():
    print("🚀 Starting historical datacentres collection and merge...")

    # Fetch historical data
    print("📊 Fetching historical datacentres data (2025-04-01 to 2025-06-29)...")
    try:
        historical_results = fetch_datacentres_historical_from_planit_api('2025-04-01', '2025-06-29')
        print(f"✅ Found {len(historical_results)} historical datacentres records")
    except Exception as e:
        print(f"❌ Error fetching historical data: {e}")
        import traceback
        traceback.print_exc()
        return False

    if not historical_results:
        print("No historical data to merge")
        return True

    # Normalize historical results
    print("🔄 Normalizing historical results...")
    normalized_historical = [normalize_planit_datacentres_result(record) for record in historical_results]

    # Load existing data
    existing_file = 'planit_datacentres.csv'
    print(f"📁 Loading existing data from {existing_file}...")

    existing_records = []
    fieldnames = None
    if os.path.exists(existing_file):
        try:
            with open(existing_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                existing_records = list(reader)
            print(f"📋 Loaded {len(existing_records)} existing records")
        except Exception as e:
            print(f"⚠️ Error loading existing file: {e}")
            print("Creating new file...")

    # Get fieldnames from data if not from existing file
    if not fieldnames and normalized_historical:
        fieldnames = list(normalized_historical[0].keys())

    # Create combined dataset with deduplication
    print("🔗 Merging datasets and removing duplicates...")

    # Track unique IDs to avoid duplicates
    seen_ids = set()
    combined_records = []

    # Add existing records first
    for record in existing_records:
        record_id = record.get('uid', '')
        if record_id and record_id not in seen_ids:
            seen_ids.add(record_id)
            combined_records.append(record)

    # Add historical records if not already present
    new_records_added = 0
    for record in normalized_historical:
        record_id = record.get('uid', '')
        if record_id and record_id not in seen_ids:
            seen_ids.add(record_id)
            combined_records.append(record)
            new_records_added += 1

    print(f"📈 Added {new_records_added} new historical records")
    print(f"📊 Total records after merge: {len(combined_records)}")

    # Save merged data
    print(f"💾 Saving merged data to {existing_file}...")
    try:
        with open(existing_file, 'w', encoding='utf-8', newline='') as f:
            if combined_records and fieldnames:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(combined_records)

        print(f"✅ Successfully saved {len(combined_records)} records to {existing_file}")

        # Verify the save
        with open(existing_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            verification_records = list(reader)
        print(f"🔍 Verification: File now contains {len(verification_records)} records")

        return True

    except Exception as e:
        print(f"❌ Error saving merged data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Historical datacentres merge completed successfully!")
    else:
        print("💥 Historical datacentres merge failed!")
        exit(1)