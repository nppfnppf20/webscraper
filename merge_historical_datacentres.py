#!/usr/bin/env python3

import sys
import os
import csv
from datetime import datetime

# Add the backend/scraper to path
sys.path.append('backend/scraper')

# Import the historical collection function
from planit_api_datacentres_historical import fetch_datacentres_historical_from_planit_api, normalize_planit_datacentres_result

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
        sys.exit(1)