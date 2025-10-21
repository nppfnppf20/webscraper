from __future__ import annotations

from pathlib import Path
from .peeringdb import fetch_facilities_gb, normalize_facility
from .io import save_csv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import db


def _map_fields_for_database(rows):
    """Map PeeringDB facility fields to database schema"""
    mapped_rows = []
    for row in rows:
        mapped_row = {}

        # Map fields to database schema
        field_mapping = {
            'id': 'peeringdb_id',  # Map PeeringDB ID to peeringdb_id column
            'name': 'name',
            'address': 'address1',  # Map address to address1
            'city': 'city',
            'country': 'country',
            'postal_code': 'zipcode',
        }

        for csv_field, db_field in field_mapping.items():
            if csv_field in row and row[csv_field]:
                mapped_row[db_field] = row[csv_field]

        mapped_rows.append(mapped_row)

    return mapped_rows


if __name__ == "__main__":
    """
    PeeringDB Facilities - Fetch facilities in GB and save to database
    """
    print("[PeeringDB Facilities] 🚀 Starting PeeringDB facilities fetch...")

    try:
        # Read existing data from database
        existing_records = db.execute_query("SELECT * FROM peeringdb_fac_gb")
        existing_ids = set()

        # Collect existing PeeringDB IDs
        for row in existing_records:
            if 'peeringdb_id' in row and row['peeringdb_id']:
                existing_ids.add(str(row['peeringdb_id']))

        print(f"[PeeringDB Facilities] 📋 Found {len(existing_records)} existing records in database")

        # Fetch facilities from PeeringDB API
        raw_facilities = fetch_facilities_gb()
        print(f"[PeeringDB Facilities] 🔄 Processing {len(raw_facilities)} API results...")

        # Process new results
        all_facilities = [normalize_facility(f) for f in raw_facilities]
        new_records = []
        new_count = 0

        for facility in all_facilities:
            # Check if this is a new record using PeeringDB ID
            peeringdb_id = facility.get('id', '')
            if peeringdb_id and str(peeringdb_id) not in existing_ids:
                new_records.append(facility)
                new_count += 1

        print(f"[PeeringDB Facilities] ✨ Found {new_count} new records to add")

        # Save new records to database
        if new_records:
            print(f"[PeeringDB Facilities] 💾 Saving {len(new_records)} new records to database...")
            mapped_new = _map_fields_for_database(new_records)
            success = db.execute_upsert("peeringdb_fac_gb", mapped_new)
            if success:
                print(f"[PeeringDB Facilities] ✅ Successfully saved {len(new_records)} new records to database")
            else:
                print(f"[PeeringDB Facilities] ❌ Failed to save to database")
        else:
            print(f"[PeeringDB Facilities] ℹ️ No new records to save")

        total_count = len(existing_records) + new_count
        print(f"[PeeringDB Facilities] ✅ Success! Database now contains {total_count} total facilities")

        # Summary stats for new records only
        if new_records:
            cities = {}
            for facility in new_records:
                city = facility.get('city', 'Unknown')
                cities[city] = cities.get(city, 0) + 1

            print(f"[PeeringDB Facilities] 📊 New records - Top cities: {dict(list(cities.items())[:5])}")
        else:
            print(f"[PeeringDB Facilities] 📊 No new records to analyze")

    except Exception as e:
        print(f"[PeeringDB Facilities] ❌ Unexpected error: {e}")
        import sys
        sys.exit(1)

