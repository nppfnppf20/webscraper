"""
Data migration script to import CSV data into Supabase
Run this after setting up your Supabase database and configuring .env
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(str(Path(__file__).parent / 'backend'))

from database import db

def safe_float(value: str) -> Optional[float]:
    """Safely convert string to float"""
    if not value or value.strip() == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_int(value: str) -> Optional[int]:
    """Safely convert string to int"""
    if not value or value.strip() == '':
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def safe_date(value: str) -> Optional[str]:
    """Safely convert date string to ISO format"""
    if not value or value.strip() == '':
        return None
    try:
        # Try different date formats
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        return None
    except:
        return None

def safe_datetime(value: str) -> Optional[str]:
    """Safely convert datetime string to ISO format"""
    if not value or value.strip() == '':
        return None
    try:
        # Try different datetime formats
        for fmt in ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                continue
        return None
    except:
        return None

def migrate_planit_renewables():
    """Migrate PlanIt renewables data"""
    print("Migrating PlanIt renewables data...")

    csv_files = [
        'planit_renewables.csv',
        'planit_renewables_test2.csv',
        'planit_renewables_incremental.csv'
    ]

    all_data = []

    for csv_file in csv_files:
        file_path = Path(csv_file)
        if not file_path.exists():
            print(f"File {csv_file} not found, skipping...")
            continue

        print(f"Processing {csv_file}...")

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map CSV columns to database schema
                data = {
                    'uid': row.get('uid') or row.get('id'),
                    'name': row.get('name') or row.get('title', ''),
                    'scraper_name': row.get('scraper_name', ''),
                    'description': row.get('description', ''),
                    'address': row.get('address', ''),
                    'postcode': row.get('postcode', ''),
                    'url': row.get('url') or row.get('link', ''),
                    'app_size': row.get('app_size', ''),
                    'app_state': row.get('app_state', ''),
                    'app_type': row.get('app_type', ''),
                    'start_date': safe_date(row.get('start_date')),
                    'decided_date': safe_date(row.get('decided_date')),
                    'consulted_date': safe_date(row.get('consulted_date')),
                    'area_name': row.get('area_name', ''),
                    'latitude': safe_float(row.get('lat') or row.get('latitude')),
                    'longitude': safe_float(row.get('lng') or row.get('longitude')),
                    'location_x': safe_float(row.get('location_x')),
                    'location_y': safe_float(row.get('location_y')),
                    'last_scraped': safe_datetime(row.get('last_scraped')),
                    'last_different': safe_datetime(row.get('last_different')),
                    'last_changed': safe_datetime(row.get('last_changed')),
                    'is_new': row.get('is_new', '').lower() in ('true', '1', 'yes')
                }

                # Handle other_fields as JSON
                other_fields = row.get('other_fields', '')
                if other_fields:
                    try:
                        data['other_fields'] = json.loads(other_fields)
                    except:
                        data['other_fields'] = {}

                if data['uid']:  # Only add if we have a unique identifier
                    all_data.append(data)

    if all_data:
        print(f"Inserting {len(all_data)} renewables records...")
        success = db.execute_upsert('planit_renewables', all_data, ['uid'])
        if success:
            print("✅ PlanIt renewables migration completed successfully")
        else:
            print("❌ PlanIt renewables migration failed")
    else:
        print("No renewables data to migrate")

def migrate_planit_datacentres():
    """Migrate PlanIt datacentres data"""
    print("Migrating PlanIt datacentres data...")

    file_path = Path('planit_datacentres.csv')
    if not file_path.exists():
        print("planit_datacentres.csv not found, skipping...")
        return

    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = {
                'uid': row.get('uid') or row.get('id'),
                'name': row.get('name') or row.get('title', ''),
                'scraper_name': row.get('scraper_name', ''),
                'description': row.get('description', ''),
                'address': row.get('address', ''),
                'postcode': row.get('postcode', ''),
                'url': row.get('url') or row.get('link', ''),
                'app_size': row.get('app_size', ''),
                'app_state': row.get('app_state', ''),
                'app_type': row.get('app_type', ''),
                'start_date': safe_date(row.get('start_date')),
                'decided_date': safe_date(row.get('decided_date')),
                'area_name': row.get('area_name', ''),
                'latitude': safe_float(row.get('lat') or row.get('latitude')),
                'longitude': safe_float(row.get('lng') or row.get('longitude')),
                'last_scraped': safe_datetime(row.get('last_scraped'))
            }

            if record['uid']:
                data.append(record)

    if data:
        print(f"Inserting {len(data)} datacentre records...")
        success = db.execute_upsert('planit_datacentres', data, ['uid'])
        if success:
            print("✅ PlanIt datacentres migration completed successfully")
        else:
            print("❌ PlanIt datacentres migration failed")

def migrate_west_lindsey():
    """Migrate West Lindsey data"""
    print("Migrating West Lindsey data...")

    # Planning applications
    planning_file = Path('west_lindsey_planning.csv')
    if planning_file.exists():
        data = []
        with open(planning_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = {
                    'reference': row.get('reference', ''),
                    'title': row.get('title', ''),
                    'description': row.get('description', ''),
                    'address': row.get('address', ''),
                    'postcode': row.get('postcode', ''),
                    'status': row.get('status', ''),
                    'decision': row.get('decision', ''),
                    'received_date': safe_date(row.get('received_date')),
                    'decided_date': safe_date(row.get('decided_date'))
                }
                if record['reference']:
                    data.append(record)

        if data:
            success = db.execute_upsert('west_lindsey_planning', data, ['reference'])
            if success:
                print("✅ West Lindsey planning migration completed")
            else:
                print("❌ West Lindsey planning migration failed")

    # Consultations
    consultations_file = Path('west_lindsey_consultations.csv')
    if consultations_file.exists():
        data = []
        with open(consultations_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = {
                    'title': row.get('title', ''),
                    'description': row.get('description', ''),
                    'consultation_start': safe_date(row.get('consultation_start')),
                    'consultation_end': safe_date(row.get('consultation_end')),
                    'status': row.get('status', ''),
                    'url': row.get('url', '')
                }
                data.append(record)

        if data:
            success = db.execute_upsert('west_lindsey_consultations', data)
            if success:
                print("✅ West Lindsey consultations migration completed")
            else:
                print("❌ West Lindsey consultations migration failed")

def migrate_peeringdb():
    """Migrate PeeringDB data"""
    print("Migrating PeeringDB data...")

    # Internet Exchanges
    ix_file = Path('peeringdb_ix_gb.csv')
    if ix_file.exists():
        data = []
        with open(ix_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = {
                    'peeringdb_id': safe_int(row.get('id') or row.get('peeringdb_id')),
                    'name': row.get('name', ''),
                    'city': row.get('city', ''),
                    'country': row.get('country', ''),
                    'region_continent': row.get('region_continent', ''),
                    'latitude': safe_float(row.get('latitude')),
                    'longitude': safe_float(row.get('longitude'))
                }
                if record['peeringdb_id']:
                    data.append(record)

        if data:
            success = db.execute_upsert('peeringdb_ix_gb', data, ['peeringdb_id'])
            if success:
                print("✅ PeeringDB IX migration completed")
            else:
                print("❌ PeeringDB IX migration failed")

    # Facilities
    fac_file = Path('peeringdb_fac_gb.csv')
    if fac_file.exists():
        data = []
        with open(fac_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = {
                    'peeringdb_id': safe_int(row.get('id') or row.get('peeringdb_id')),
                    'name': row.get('name', ''),
                    'city': row.get('city', ''),
                    'country': row.get('country', ''),
                    'address1': row.get('address1', ''),
                    'address2': row.get('address2', ''),
                    'zipcode': row.get('zipcode', ''),
                    'latitude': safe_float(row.get('latitude')),
                    'longitude': safe_float(row.get('longitude'))
                }
                if record['peeringdb_id']:
                    data.append(record)

        if data:
            success = db.execute_upsert('peeringdb_fac_gb', data, ['peeringdb_id'])
            if success:
                print("✅ PeeringDB Facilities migration completed")
            else:
                print("❌ PeeringDB Facilities migration failed")

def main():
    """Run all migrations"""
    print("🚀 Starting data migration to Supabase...")
    print("=" * 50)

    if not db.supabase:
        print("❌ Supabase client not initialized. Check your .env configuration.")
        return

    try:
        migrate_planit_renewables()
        print()
        migrate_planit_datacentres()
        print()
        migrate_west_lindsey()
        print()
        migrate_peeringdb()
        print()

        print("=" * 50)
        print("✅ Migration completed!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and fill in your Supabase credentials")
        print("2. Run the schema.sql file in your Supabase SQL editor")
        print("3. Test the new database API by running: python backend/api_server_db.py")

    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()