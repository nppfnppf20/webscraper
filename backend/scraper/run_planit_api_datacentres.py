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

        # Mark all existing records as not new and collect IDs
        for row in existing_records:
            row['is_new'] = 'false'
            if 'id' in row and row['id']:
                existing_ids.add(row['id'])
            elif 'uid' in row and row['uid']:  # fallback to uid if no id
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

        # Update existing records in database (mark as not new)
        if existing_records:
            print(f"[PlanIt API Datacentres] 🔄 Updating {len(existing_records)} existing records...")
            mapped_existing = _map_fields_for_database(existing_records)
            db.execute_upsert("planit_datacentres", mapped_existing)

        # Insert new records to database
        if new_records:
            print(f"[PlanIt API Datacentres] ➕ Inserting {len(new_records)} new records...")
            mapped_new = _map_fields_for_database(new_records)
            db.execute_upsert("planit_datacentres", mapped_new)

        total_count = len(existing_records) + new_count
        print(f"[PlanIt API Datacentres] 📊 Total records in database: {total_count} ({len(existing_records)} existing + {new_count} new)")

        # Also save to CSV for backwards compatibility (optional)
        all_records = existing_records + new_records
        save_csv(output_path, all_records)

        print(f"[PlanIt API Datacentres] ✅ Success! Updated database with {total_count} datacentre projects")

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


def _map_fields_for_database(rows):
    """Map CSV fields to database schema fields"""
    mapped_rows = []
    for row in rows:
        mapped_row = {}

        # Keep existing fields that match database schema
        db_fields = [
            'name', 'uid', 'description', 'address', 'postcode', 'url',
            'app_size', 'app_state', 'app_type', 'start_date', 'decided_date',
            'area_name', 'last_scraped', 'last_different', 'lng', 'lat',
            'last_changed', 'location_x', 'location_y', 'is_new'
        ]

        for field in db_fields:
            if field in row:
                mapped_row[field] = row[field]

        # Map additional fields to match database
        if 'lat' in row:
            mapped_row['latitude'] = row['lat']
        if 'lng' in row:
            mapped_row['longitude'] = row['lng']
        if 'link' in row and not mapped_row.get('url'):
            mapped_row['url'] = row['link']
        if 'name' in row:
            mapped_row['title'] = row['name']

        # Handle ID field mapping
        if 'uid' in row:
            mapped_row['id'] = row['uid']

        # Set default values for required fields
        if 'is_new' not in mapped_row:
            mapped_row['is_new'] = True

        mapped_rows.append(mapped_row)

    return mapped_rows