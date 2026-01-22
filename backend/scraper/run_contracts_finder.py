from __future__ import annotations

import sys
import os
from datetime import datetime

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from .contracts_finder import (
    fetch_notices_from_contracts_finder,
    normalize_contracts_finder_notice,
    ContractsFinderAPIError,
    ContractsFinderRateLimit,
)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import db


def _map_fields_for_database(rows):
    """Map fields to database schema"""
    mapped_rows = []
    for row in rows:
        mapped_row = {}

        # Map fields to database schema
        field_mapping = {
            'notice_id': 'notice_id',
            'title': 'title',
            'description': 'description',
            'organisation': 'organisation',
            'published_date': 'published_date',
            'closing_date': 'closing_date',
            'value_low': 'value_low',
            'value_high': 'value_high',
            'status': 'status',
            'notice_type': 'notice_type',
            'region': 'region',
            'postcode': 'postcode',
            'cpv_codes': 'cpv_codes',
            'suitable_for_sme': 'suitable_for_sme',
            'suitable_for_vco': 'suitable_for_vco',
            'url': 'url',
            'last_scraped': 'last_scraped',
        }

        for source_field, db_field in field_mapping.items():
            if source_field in row and row[source_field] is not None:
                mapped_row[db_field] = row[source_field]

        mapped_rows.append(mapped_row)

    return mapped_rows


if __name__ == "__main__":
    """
    Contracts Finder Scraper - Fetches UK Government contract opportunities
    Searches for notices published in the last 7 days
    """

    try:
        print("[Contracts Finder] Starting Contracts Finder scraper...")

        # Read existing data from database to check for duplicates
        existing_records = db.execute_query("SELECT notice_id FROM contracts_finder")
        existing_ids = set(row['notice_id'] for row in existing_records if row.get('notice_id'))

        print(f"[Contracts Finder] Found {len(existing_ids)} existing records in database")

        # Fetch notices from last 7 days
        raw_results = fetch_notices_from_contracts_finder()

        print(f"[Contracts Finder] Processing {len(raw_results)} API results...")

        # Process results
        new_records = []
        updated_records = []

        for notice_hit in raw_results:
            try:
                normalized = normalize_contracts_finder_notice(notice_hit)

                notice_id = normalized.get('notice_id', '')
                if not notice_id:
                    continue

                if notice_id in existing_ids:
                    # Existing record - will be updated
                    updated_records.append(normalized)
                else:
                    # New record
                    new_records.append(normalized)

            except Exception as e:
                print(f"[Contracts Finder] Error normalizing record: {e}")
                continue

        print(f"[Contracts Finder] Found {len(new_records)} new records, {len(updated_records)} existing records to update")

        # Combine all records for upsert
        all_records = new_records + updated_records

        if all_records:
            print(f"[Contracts Finder] Saving {len(all_records)} records to database...")
            mapped_records = _map_fields_for_database(all_records)
            success = db.execute_upsert("contracts_finder", mapped_records, conflict_columns=['notice_id'])

            if success:
                print(f"[Contracts Finder] Successfully saved records to database")
            else:
                print(f"[Contracts Finder] Failed to save to database")
                sys.exit(1)
        else:
            print(f"[Contracts Finder] No records to save")

        # Print summary
        total_count = len(existing_ids) + len(new_records)
        print(f"[Contracts Finder] Success! Database now contains approximately {total_count} contract notices")

        # Summary stats
        if new_records:
            statuses = {}
            types = {}
            for record in new_records:
                status = record.get('status', 'Unknown')
                notice_type = record.get('notice_type', 'Unknown')
                statuses[status] = statuses.get(status, 0) + 1
                types[notice_type] = types.get(notice_type, 0) + 1

            print(f"[Contracts Finder] New records - Status breakdown: {dict(list(statuses.items())[:5])}")
            print(f"[Contracts Finder] New records - Type breakdown: {dict(list(types.items())[:5])}")

    except ContractsFinderRateLimit as e:
        print(f"[Contracts Finder] Rate limited by API")
        print(f"[Contracts Finder] Please wait {e.retry_after_seconds} seconds before trying again")
        sys.exit(1)

    except ContractsFinderAPIError as e:
        print(f"[Contracts Finder] API error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"[Contracts Finder] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
