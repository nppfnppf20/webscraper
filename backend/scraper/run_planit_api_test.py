from __future__ import annotations

import csv
from pathlib import Path
from .planit_api_scraper import (
    fetch_renewables_from_planit_api,
    normalize_planit_api_result,
    PlanItAPIError,
    PlanItAPIRateLimit,
)
from .io import save_csv


if __name__ == "__main__":
    """
    PlanIt Renewables Test 2 - Using official PlanIt API
    Fetches renewables projects from last 3 months
    """
    output_path = Path(__file__).parent.parent.parent / "planit_renewables_test2.csv"

    try:
        print("[PlanIt API Test] 🚀 Starting accumulative PlanIt API search...")

        # Read existing data
        existing_records = []
        existing_ids = set()
        if output_path.exists():
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Mark all existing records as not new
                        row['is_new'] = 'false'
                        existing_records.append(row)
                        if 'id' in row and row['id']:
                            existing_ids.add(row['id'])
                        elif 'uid' in row and row['uid']:  # fallback to uid if no id
                            existing_ids.add(row['uid'])
                print(f"[PlanIt API Test] 📋 Found {len(existing_records)} existing records")
            except Exception as e:
                print(f"[PlanIt API Test] ⚠️ Could not read existing file: {e}")

        # Use the exact same API call as your working CSV link
        raw_results = fetch_renewables_from_planit_api()

        print(f"[PlanIt API Test] 🔄 Processing {len(raw_results)} API results...")

        # Process new results
        new_records = []
        new_count = 0
        for raw_record in raw_results:
            try:
                normalized = normalize_planit_api_result(raw_record)

                # Check if this is a new record (try id first, then uid)
                record_id = normalized.get('id', '') or normalized.get('uid', '')
                if record_id and record_id not in existing_ids:
                    normalized['is_new'] = 'true'
                    new_records.append(normalized)
                    new_count += 1
                # If it's an existing record, we don't need to add it again

            except Exception as e:
                print(f"[PlanIt API Test] ⚠️ Error normalizing record: {e}")
                continue

        print(f"[PlanIt API Test] ✨ Found {new_count} new records to add")

        # Combine existing and new records
        all_records = existing_records + new_records
        total_count = len(all_records)

        print(f"[PlanIt API Test] 📊 Total records: {total_count} ({len(existing_records)} existing + {new_count} new)")

        # Save combined results
        save_csv(output_path, all_records)

        print(f"[PlanIt API Test] ✅ Success! Saved {total_count} renewables projects to {output_path.name}")

        # Summary stats for new records only
        if new_records:
            statuses = {}
            authorities = {}
            for result in new_records:
                status = result.get('app_state', result.get('status', 'Unknown'))
                authority = result.get('area_name', result.get('authority', 'Unknown'))
                statuses[status] = statuses.get(status, 0) + 1
                authorities[authority] = authorities.get(authority, 0) + 1

            print(f"[PlanIt API Test] 📊 New records - Status breakdown: {dict(list(statuses.items())[:5])}")
            print(f"[PlanIt API Test] 📊 New records - Top authorities: {dict(list(authorities.items())[:5])}")
        else:
            print(f"[PlanIt API Test] 📊 No new records to analyze")

    except PlanItAPIRateLimit as e:
        print(f"[PlanIt API Test] 🛑 Rate limited by PlanIt API")
        print(f"[PlanIt API Test] ⏰ Please wait {e.retry_after_seconds} seconds before trying again")
        import sys
        sys.exit(1)

    except PlanItAPIError as e:
        print(f"[PlanIt API Test] ❌ PlanIt API error: {e}")
        import sys
        sys.exit(1)

    except Exception as e:
        print(f"[PlanIt API Test] ❌ Unexpected error: {e}")
        import sys
        sys.exit(1)