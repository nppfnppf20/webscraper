from __future__ import annotations

import csv
import sys
import os
from pathlib import Path
from .planit_api_scraper import (
    fetch_renewables_from_planit_api,
    normalize_planit_api_result,
    PlanItAPIError,
    PlanItAPIRateLimit,
)
from .io import save_csv

# Add parent directory to path for database import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import db


def _map_fields_for_database(rows):
    """Map CSV fields to database schema fields"""
    mapped_rows = []
    for row in rows:
        mapped_row = {}

        # Map fields to database schema (only include existing database columns)
        field_mapping = {
            'uid': 'uid',
            'name': 'name',  # CSV name -> DB name
            'description': 'description',
            'app_type': 'app_type',
            'app_size': 'app_size',
            'app_state': 'app_state',
            'start_date': 'start_date',
            'decided_date': 'decided_date',
            'address': 'address',
            'postcode': 'postcode',
            'area_name': 'area_name',
            'lat': 'latitude',
            'lng': 'longitude',
            'url': 'url',
            'link': 'url',  # fallback mapping
            'other_fields': 'other_fields',
            'last_scraped': 'last_scraped',
            'last_changed': 'last_changed',
        }

        for csv_field, db_field in field_mapping.items():
            if csv_field in row and row[csv_field]:
                mapped_row[db_field] = row[csv_field]

        # Set required defaults
        mapped_row['is_new'] = row.get('is_new', 'true') == 'true'
        mapped_row['scraper_name'] = 'test2'  # Tag records as test2
        if 'last_changed' in row:
            mapped_row['last_different'] = row['last_changed']

        mapped_rows.append(mapped_row)

    return mapped_rows


if __name__ == "__main__":
    """
    PlanIt Renewables Test 2 - Using official PlanIt API
    Fetches renewables projects from last 3 months
    """
    output_path = Path(__file__).parent.parent.parent / "planit_renewables_test2.csv"

    try:
        print("[PlanIt API Test] 🚀 Starting PlanIt API renewables test2 scraper...")

        # Get existing IDs from database (check all scrapers since UIDs are unique across all)
        existing_db_records = db.execute_query("SELECT id, uid FROM planit_renewables") or []
        existing_ids = set()
        for record in existing_db_records:
            # Add both id and uid to the set (use both, not elif)
            if record.get('id'):
                existing_ids.add(record['id'])
            if record.get('uid'):
                existing_ids.add(record['uid'])

        print(f"[PlanIt API Test] 📋 Found {len(existing_db_records)} existing records in database")

        # Fetch new data from API
        raw_results = fetch_renewables_from_planit_api()
        print(f"[PlanIt API Test] 🔄 Processing {len(raw_results)} API results...")

        # Process and filter new records
        new_records = []
        for raw_record in raw_results:
            try:
                normalized = normalize_planit_api_result(raw_record)

                # Check if this is a new record
                record_id = normalized.get('id', '') or normalized.get('uid', '')
                if record_id and record_id not in existing_ids:
                    normalized['is_new'] = 'true'
                    new_records.append(normalized)

            except Exception as e:
                print(f"[PlanIt API Test] ⚠️ Error normalizing record: {e}")
                continue

        print(f"[PlanIt API Test] ✨ Found {len(new_records)} new records to add")

        # Save to database
        if new_records:
            print(f"[PlanIt API Test] 💾 Saving {len(new_records)} new records to database...")
            mapped_rows = _map_fields_for_database(new_records)
            success = db.execute_upsert("planit_renewables", mapped_rows)
            if success:
                print(f"[PlanIt API Test] ✅ Successfully saved {len(new_records)} new records to database")
            else:
                print(f"[PlanIt API Test] ❌ Failed to save to database")
        else:
            print(f"[PlanIt API Test] ℹ️ No new records to save")

        # Optional: still save to CSV for backup
        all_records = new_records  # Only save new records to CSV
        if all_records:
            save_csv(output_path, all_records)

        total_in_db = len(existing_db_records) + len(new_records)
        print(f"[PlanIt API Test] ✅ Success! Database now contains {total_in_db} total renewables test2 records")

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