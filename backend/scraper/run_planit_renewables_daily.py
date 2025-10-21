from __future__ import annotations

from pathlib import Path
from datetime import date, timedelta
from .planit_renewables import fetch_page, normalize, RateLimitExceeded
from .session import make_session
from .io import save_csv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import db


def fetch_recent_renewables_limited(days_back: int = 30, max_pages: int = 3) -> list:
    """
    Fetch only recent renewables with strict limits for dashboard refresh
    - Only look back specified days
    - Limit to max_pages to prevent runaway scraping
    - No geocoding for speed
    """
    session = make_session()

    # Calculate date range - just last N days
    today = date.today()
    start_date = today - timedelta(days=days_back)
    end_date = today

    print(f"[PlanIt Daily] 🚀 Fetching {days_back} days ({start_date} to {end_date}), max {max_pages} pages...")

    seen = {}
    page = 1

    while page <= max_pages:
        print(f"[PlanIt Daily] Page {page}/{max_pages}...", flush=True)

        try:
            data = fetch_page(session, start_date, end_date, page)
            records = data.get("records") or data.get("features") or []

            if isinstance(records, dict) and "features" in records:
                records = records["features"]

            if not records:
                print(f"[PlanIt Daily] No more records on page {page}")
                break

            print(f"[PlanIt Daily] Processing {len(records)} records from page {page}")

            for record in records:
                props = record.get("properties", record)
                geom = record.get("geometry")

                # Quick filter - only renewables
                desc = str(props.get("description", "")).lower()
                if not any(term in desc for term in ["solar", "photovoltaic", "battery", "wind", "renewable"]):
                    continue

                row = normalize(props, geometry=geom, enable_geocode=False)
                id_val = row.get("id", "")
                if id_val and id_val not in seen:
                    seen[id_val] = row

            print(f"[PlanIt Daily] Cumulative records: {len(seen)}")

            # If we got less than the page size, we're done
            if len(records) < 100:  # PAGE_SIZE
                print(f"[PlanIt Daily] Reached end of results")
                break

            page += 1

        except RateLimitExceeded:
            print(f"[PlanIt Daily] Rate limited, stopping at page {page}")
            break
        except Exception as e:
            print(f"[PlanIt Daily] Error on page {page}: {e}")
            break

    return list(seen.values())


def _map_fields_for_database(rows):
    """Map CSV fields to database schema fields (conservative mapping)"""
    mapped_rows = []
    for row in rows:
        mapped_row = {}

        # Only use fields that definitely exist in database (minimal set)
        field_mapping = {
            'id': 'id',
            'title': 'title',
            'description': 'description',
            'app_type': 'app_type',
            'app_size': 'app_size',
            'app_state': 'app_state',
            'start_date': 'start_date',
            'decided_date': 'decided_date',
            'last_changed': 'last_changed',
            'address': 'address',
            'authority': 'area_name',  # Map authority to area_name
            'lat': 'latitude',  # Map lat to latitude
            'lng': 'longitude',  # Map lng to longitude
        }

        for csv_field, db_field in field_mapping.items():
            if csv_field in row and row[csv_field]:
                mapped_row[db_field] = row[csv_field]

        # Set required defaults
        mapped_row['is_new'] = True
        if 'last_changed' in row:
            mapped_row['last_scraped'] = row['last_changed']
            mapped_row['last_different'] = row['last_changed']

        mapped_rows.append(mapped_row)

    return mapped_rows


if __name__ == "__main__":
    """Super fast version: just last 30 days, max 3 pages, no geocoding"""
    output_path = Path(__file__).parent.parent.parent / "planit_renewables.csv"

    try:
        # Very limited scope for dashboard refresh
        rows = fetch_recent_renewables_limited(days_back=30, max_pages=3)

        # Save to database with field mapping
        if rows:
            print(f"[PlanIt Daily] 💾 Saving {len(rows)} records to database...")
            mapped_rows = _map_fields_for_database(rows)
            success = db.execute_upsert("planit_renewables", mapped_rows)
            if success:
                print(f"[PlanIt Daily] ✅ Successfully saved {len(rows)} records to database")
            else:
                print(f"[PlanIt Daily] ❌ Failed to save to database")

        # Also save to CSV for backwards compatibility (optional)
        save_csv(output_path, rows)
        print(f"[PlanIt Daily] ✅ Success! Updated database with {len(rows)} recent renewables")

    except Exception as e:
        print(f"[PlanIt Daily] ❌ Error: {e}")
        import sys
        sys.exit(1)