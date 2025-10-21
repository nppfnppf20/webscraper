from __future__ import annotations

import csv
from pathlib import Path
from .planit_api_datacentres import (
    fetch_datacentres_from_planit_api,
    normalize_planit_datacentres_result,
    PlanItAPIError,
    PlanItAPIRateLimit,
)
from .io import save_csv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import db


def _map_fields_for_database(rows):
    """Map fields to database schema (only include existing database columns)"""
    mapped_rows = []
    for row in rows:
        mapped_row = {}

        # Map fields to database schema (only existing datacentres columns)
        field_mapping = {
            'uid': 'uid',
            'name': 'name',
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
            'last_scraped': 'last_scraped',
        }

        for csv_field, db_field in field_mapping.items():
            if csv_field in row and row[csv_field]:
                mapped_row[db_field] = row[csv_field]

        # Set required defaults (only use existing columns)
        mapped_row['scraper_name'] = 'datacentres'  # Tag records as datacentres

        mapped_rows.append(mapped_row)

    return mapped_rows


if __name__ == "__main__":
    """
    PlanIt Datacentres API - Using official PlanIt API
    Fetches datacentre projects from last 3 months
    """
    output_path = Path(__file__).parent.parent.parent / "planit_datacentres.csv"

    try:
        print("[PlanIt API Datacentres] 🚀 Starting accumulative PlanIt API search...")

        # Read existing data from database
        existing_records = db.execute_query("SELECT * FROM planit_datacentres")
        existing_ids = set()

        # Collect existing IDs (fix the elif bug)
        for row in existing_records:
            if 'id' in row and row['id']:
                existing_ids.add(row['id'])
            if 'uid' in row and row['uid']:  # Use both id and uid
                existing_ids.add(row['uid'])

        print(f"[PlanIt API Datacentres] 📋 Found {len(existing_records)} existing records in database")

        # Use the PlanIt API with datacentre search terms
        raw_results = fetch_datacentres_from_planit_api()

        print(f"[PlanIt API Datacentres] 🔄 Processing {len(raw_results)} API results...")

        # Process new results
        new_records = []
        new_count = 0
        for raw_record in raw_results:
            try:
                normalized = normalize_planit_datacentres_result(raw_record)

                # Check if this is a new record (try id first, then uid)
                record_id = normalized.get('id', '') or normalized.get('uid', '')
                if record_id and record_id not in existing_ids:
                    normalized['is_new'] = 'true'
                    new_records.append(normalized)
                    new_count += 1
                # If it's an existing record, we don't need to add it again

            except Exception as e:
                print(f"[PlanIt API Datacentres] ⚠️ Error normalizing record: {e}")
                continue

        print(f"[PlanIt API Datacentres] ✨ Found {new_count} new records to add")

        # Save new records to database
        if new_records:
            print(f"[PlanIt API Datacentres] 💾 Saving {len(new_records)} new records to database...")
            mapped_new = _map_fields_for_database(new_records)
            success = db.execute_upsert("planit_datacentres", mapped_new)
            if success:
                print(f"[PlanIt API Datacentres] ✅ Successfully saved {len(new_records)} new records to database")
            else:
                print(f"[PlanIt API Datacentres] ❌ Failed to save to database")
        else:
            print(f"[PlanIt API Datacentres] ℹ️ No new records to save")

        total_count = len(existing_records) + new_count
        print(f"[PlanIt API Datacentres] ✅ Success! Database now contains {total_count} total datacentre projects")

        # Summary stats for new records only
        if new_records:
            statuses = {}
            authorities = {}
            for result in new_records:
                status = result.get('app_state', result.get('status', 'Unknown'))
                authority = result.get('area_name', result.get('authority', 'Unknown'))
                statuses[status] = statuses.get(status, 0) + 1
                authorities[authority] = authorities.get(authority, 0) + 1

            print(f"[PlanIt API Datacentres] 📊 New records - Status breakdown: {dict(list(statuses.items())[:5])}")
            print(f"[PlanIt API Datacentres] 📊 New records - Top authorities: {dict(list(authorities.items())[:5])}")
        else:
            print(f"[PlanIt API Datacentres] 📊 No new records to analyze")

    except PlanItAPIRateLimit as e:
        print(f"[PlanIt API Datacentres] 🛑 Rate limited by PlanIt API")
        print(f"[PlanIt API Datacentres] ⏰ Please wait {e.retry_after_seconds} seconds before trying again")
        import sys
        sys.exit(1)

    except PlanItAPIError as e:
        print(f"[PlanIt API Datacentres] ❌ PlanIt API error: {e}")
        import sys
        sys.exit(1)

    except Exception as e:
        print(f"[PlanIt API Datacentres] ❌ Unexpected error: {e}")
        import sys
        sys.exit(1)

