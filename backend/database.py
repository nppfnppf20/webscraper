"""
Database module for Supabase integration
"""
import os
from typing import List, Dict, Any, Optional
import psycopg2
import psycopg2.extras
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseDB:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.database_url = os.getenv('DATABASE_URL')

        # Initialize Supabase client
        if self.supabase_url and self.supabase_key:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        else:
            self.supabase = None

        # Initialize direct PostgreSQL connection for complex queries
        self.conn = None
        if self.database_url:
            try:
                self.conn = psycopg2.connect(self.database_url)
            except Exception as e:
                print(f"Failed to connect to database: {e}")

    def get_connection(self):
        """Get a fresh database connection"""
        if self.database_url:
            return psycopg2.connect(self.database_url)
        return None

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    def execute_insert(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert data into table"""
        try:
            if self.supabase:
                result = self.supabase.table(table).insert(data).execute()
                return bool(result.data)
        except Exception as e:
            print(f"Insert failed: {e}")
        return False

    def execute_upsert(self, table: str, data: List[Dict[str, Any]], conflict_columns: List[str] = None) -> bool:
        """Upsert data into table (insert or update on conflict)"""
        try:
            if self.supabase:
                # Use simple upsert without on_conflict specification
                result = self.supabase.table(table).upsert(data).execute()
                return bool(result.data)
        except Exception as e:
            print(f"Upsert failed: {e}")
            # Try regular insert if upsert fails
            try:
                result = self.supabase.table(table).insert(data).execute()
                return bool(result.data)
            except Exception as e2:
                print(f"Insert also failed: {e2}")
        return False

    # API Methods for each data source

    def get_rtpi_events(self) -> List[Dict[str, Any]]:
        """Get RTPI events"""
        return self.execute_query("SELECT * FROM rtpi_events ORDER BY created_at DESC")

    def get_west_lindsey_application(self) -> Dict[str, Any]:
        """Get West Lindsey planning application (latest one)"""
        results = self.execute_query("SELECT * FROM west_lindsey_planning ORDER BY created_at DESC LIMIT 1")
        return results[0] if results else {}

    def get_west_lindsey_consultations(self) -> List[Dict[str, Any]]:
        """Get West Lindsey consultations with frontend-compatible field names"""
        results = self.execute_query("SELECT * FROM west_lindsey_consultations ORDER BY created_at DESC")

        # Map database fields back to original CSV field names that frontend expects
        for item in results:
            item['consulteeName'] = item.get('title', '')
            item['opinion'] = item.get('status', '')
            item['responseDetailsToPublish'] = item.get('description', '')
            item['responsePublished'] = '1' if item.get('description') else '0'  # Fake this field
            item['createdTime'] = item.get('created_at', '')
            item['lastModifiedTime'] = item.get('updated_at', '')

        return results

    def get_peeringdb_ix_gb(self) -> List[Dict[str, Any]]:
        """Get PeeringDB Internet Exchanges (GB)"""
        return self.execute_query("SELECT * FROM peeringdb_ix_gb ORDER BY name")

    def get_peeringdb_fac_gb(self) -> List[Dict[str, Any]]:
        """Get PeeringDB Facilities (GB)"""
        return self.execute_query("SELECT * FROM peeringdb_fac_gb ORDER BY name")

    def get_planit_datacentres(self) -> List[Dict[str, Any]]:
        """Get PlanIt data centres with field mapping for frontend compatibility"""
        results = self.execute_query("SELECT * FROM planit_datacentres ORDER BY last_scraped DESC NULLS LAST")

        # Map database fields to frontend expected fields
        for item in results:
            # Add frontend-compatible field names
            item['lat'] = item.get('latitude')
            item['lng'] = item.get('longitude')
            item['link'] = item.get('url')

        return results

    def get_planit_renewables(self) -> List[Dict[str, Any]]:
        """Get PlanIt renewables with field mapping for frontend compatibility"""
        results = self.execute_query("SELECT * FROM planit_renewables ORDER BY last_scraped DESC NULLS LAST")

        # Map database fields to frontend expected fields
        for item in results:
            # Add frontend-compatible field names
            item['lat'] = item.get('latitude')
            item['lng'] = item.get('longitude')
            item['link'] = item.get('url')

        return results

    def get_planit_renewables_test2(self) -> List[Dict[str, Any]]:
        """Get PlanIt renewables test data with field mapping for frontend compatibility"""
        results = self.execute_query("SELECT * FROM planit_renewables ORDER BY last_scraped DESC NULLS LAST")

        # Map database fields to frontend expected fields
        for item in results:
            # Add frontend-compatible field names
            item['lat'] = item.get('latitude')
            item['lng'] = item.get('longitude')
            item['link'] = item.get('url')

        return results

# Global database instance
db = SupabaseDB()