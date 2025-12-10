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
        self.schema = os.getenv('POSTGRES_SCHEMA', 'public')  # Default to 'public' schema

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
                # Set search_path to use the specified schema
                if self.conn and self.schema != 'public':
                    with self.conn.cursor() as cur:
                        cur.execute(f"SET search_path TO {self.schema}, public")
                        self.conn.commit()
            except Exception as e:
                print(f"Failed to connect to database: {e}")

    def get_connection(self):
        """Get a fresh database connection with schema search_path set"""
        if self.database_url:
            conn = psycopg2.connect(self.database_url)
            # Set search_path for this connection
            if conn and self.schema != 'public':
                with conn.cursor() as cur:
                    cur.execute(f"SET search_path TO {self.schema}, public")
                    conn.commit()
            return conn
        return None

    def execute_query(self, query: str, params: tuple = None, timeout_seconds: int = 30) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    # Set statement timeout to prevent hanging queries
                    cursor.execute(f"SET statement_timeout = {timeout_seconds * 1000}")  # PostgreSQL uses milliseconds
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    def execute_raw(self, query: str, params: tuple = None) -> bool:
        """Execute a raw SQL query (DDL/DML)"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Raw query failed: {e}")
            return False

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
        
        # Use direct PostgreSQL for custom schemas (Supabase client only works with 'public')
        if self.schema != 'public' and self.database_url:
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cursor:
                        for record in data:
                            # Filter out 'id' column (auto-increment primary key)
                            # and empty/None/invalid values
                            filtered_record = {}
                            for k, v in record.items():
                                # Skip auto-increment id column
                                if k == 'id':
                                    continue
                                # Skip various empty/invalid values
                                if v is None or v == '' or v == 'None' or v == 'null' or v == 'NULL':
                                    continue
                                # Skip string representations of None for dates
                                if isinstance(v, str) and v.strip().lower() in ('none', 'null', 'n/a', 'nan'):
                                    continue
                                filtered_record[k] = v
                            
                            if not filtered_record:
                                continue  # Skip empty records
                            
                            # Get column names and values
                            columns = list(filtered_record.keys())
                            values = [filtered_record[col] for col in columns]
                            placeholders = ', '.join(['%s'] * len(columns))
                            columns_str = ', '.join([f'"{col}"' for col in columns])
                            
                            # Determine conflict columns (default to 'uid' if exists, otherwise first unique column)
                            if not conflict_columns:
                                if 'uid' in columns:
                                    conflict_columns = ['uid']
                                elif 'peeringdb_id' in columns:
                                    conflict_columns = ['peeringdb_id']
                                elif 'reference' in columns:
                                    conflict_columns = ['reference']
                                else:
                                    # If no obvious unique column, skip to avoid errors
                                    print(f"Warning: No unique column found for table {table}, inserting only")
                                    query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                                    cursor.execute(query, values)
                                    continue
                            
                            conflict_str = ', '.join([f'"{col}"' for col in conflict_columns])
                            
                            # Build update clause for ON CONFLICT
                            update_cols = [col for col in columns if col not in conflict_columns and col != 'id']
                            update_str = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in update_cols])
                            
                            # Build upsert query
                            if update_str:
                                query = f"""
                                    INSERT INTO {table} ({columns_str})
                                    VALUES ({placeholders})
                                    ON CONFLICT ({conflict_str}) 
                                    DO UPDATE SET {update_str}
                                """
                            else:
                                # If no columns to update, just do nothing on conflict
                                query = f"""
                                    INSERT INTO {table} ({columns_str})
                                    VALUES ({placeholders})
                                    ON CONFLICT ({conflict_str}) DO NOTHING
                                """
                            
                            cursor.execute(query, values)
                        
                        conn.commit()
                        return True
            except Exception as e:
                print(f"PostgreSQL upsert failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        # Use Supabase client for 'public' schema
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


    def get_west_lindsey_application(self) -> Dict[str, Any]:
        """Get West Lindsey planning application (latest one)"""
        results = self.execute_query("SELECT * FROM west_lindsey_planning ORDER BY created_at DESC LIMIT 1")
        return results[0] if results else {}

    def get_west_lindsey_consultations(self) -> List[Dict[str, Any]]:
        """Get West Lindsey consultations with frontend-compatible field names"""
        results = self.execute_query("SELECT * FROM west_lindsey_consultations ORDER BY original_created_time DESC NULLS LAST")

        # Map database fields back to original CSV field names that frontend expects
        for item in results:
            item['consulteeName'] = item.get('consultee_name') or item.get('title', '')
            item['opinion'] = item.get('status', '')
            item['responseDetailsToPublish'] = item.get('description', '')
            item['responsePublished'] = item.get('response_published', '0')
            item['createdTime'] = item.get('original_created_time', '')
            item['lastModifiedTime'] = item.get('original_last_modified_time', '')
            item['consulteeEmail'] = item.get('consultee_email', '')
            item['consulteeAddress'] = item.get('consultee_address', '')
            item['id'] = item.get('consultation_id') or item.get('id')
            item['applicationId'] = item.get('application_id', '')

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
        """Get PlanIt renewables test2 data with field mapping for frontend compatibility"""
        # Show all renewables data ordered by most recent application date, then last scraped
        results = self.execute_query("SELECT * FROM planit_renewables ORDER BY start_date DESC NULLS LAST, last_scraped DESC NULLS LAST")

        # Map database fields to frontend expected fields
        for item in results:
            # Add frontend-compatible field names
            item['lat'] = item.get('latitude')
            item['lng'] = item.get('longitude')
            item['link'] = item.get('url')

            # Fix missing names - use uid as fallback if name is empty
            if not item.get('name'):
                item['name'] = item.get('uid', '')

            # Fix missing area_name - extract from uid if missing
            if not item.get('area_name') and item.get('uid'):
                # Extract authority from uid (e.g., "EastRiding/25/02255/STPLFE" -> "EastRiding")
                uid_parts = item.get('uid', '').split('/')
                if len(uid_parts) > 0:
                    item['area_name'] = uid_parts[0]

        return results

    def get_repd_data(self) -> List[Dict[str, Any]]:
        """Get REPD Publication Q3 2025 data with lat/lng conversion, filtered for Solar (>=3MW), Wind Onshore, and Battery"""
        # Use PostGIS to convert geometry to lat/lng
        query = """
            SELECT
                *,
                ST_Y(ST_Transform(geom, 4326)) as lat,
                ST_X(ST_Transform(geom, 4326)) as lng
            FROM "REPD_Publication_Q3_2025"
            WHERE (
                (
                    "Technology Type" = 'Solar Photovoltaics'
                    AND "Installed Capacity (MWelec)" IS NOT NULL
                    AND TRIM("Installed Capacity (MWelec)") != ''
                    AND CAST("Installed Capacity (MWelec)" AS FLOAT) >= 3
                )
                OR "Technology Type" = 'Wind Onshore'
                OR "Technology Type" = 'Battery'
            )
            AND UPPER(TRIM("Development Status")) IN (
                'OPERATIONAL',
                'PLANNING PERMISSION REFUSED',
                'APPEAL REFUSED',
                'REVISED',
                'APPEAL GRANTED',
                'PLANNING APPLICATION SUBMITTED',
                'PLANNING PERMISSION GRANTED',
                'UNDER CONSTRUCTION'
            )
            ORDER BY "Site Name"
        """
        results = self.execute_query(query)

        return results

    def get_trp_commercial(self) -> List[Dict[str, Any]]:
        """Get TRP Projects - Commercial, Economic and Industrial"""
        query = """
            SELECT
                *,
                ST_Y(ST_Transform(geom, 4326)) as lat,
                ST_X(ST_Transform(geom, 4326)) as lng
            FROM "TRP Projects- Commercial, Economic and Industrial"
            ORDER BY name
        """
        return self.execute_query(query)

    def get_trp_energy(self) -> List[Dict[str, Any]]:
        """Get TRP Projects - Energy, digital and infrastructure"""
        query = """
            SELECT
                *,
                ST_Y(ST_Transform(geom, 4326)) as lat,
                ST_X(ST_Transform(geom, 4326)) as lng
            FROM "TRP Projects- Energy, digital and infrastructure"
            ORDER BY name
        """
        return self.execute_query(query)

    def get_trp_residential(self) -> List[Dict[str, Any]]:
        """Get TRP Projects - Residential and Strategic Land"""
        query = """
            SELECT
                *,
                ST_Y(ST_Transform(geom, 4326)) as lat,
                ST_X(ST_Transform(geom, 4326)) as lng
            FROM "TRP Projects- Residential and Strategic Land"
            ORDER BY name
        """
        return self.execute_query(query)

    def update_renewables_dismissed_status(self, record_id: int, dismissed: bool) -> bool:
        """Update the dismissed status of a renewables record"""
        query = "UPDATE planit_renewables SET dismissed = %s WHERE id = %s"
        return self.execute_raw(query, (dismissed, record_id))

    # ============================================================
    # Spatial/PostGIS Query Methods
    # ============================================================

    def get_projects_within_radius(self, lat: float, lng: float, radius_km: float = 10.0, 
                                   table: str = 'planit_renewables') -> List[Dict[str, Any]]:
        """
        Find all projects within X km of a specific lat/lng point
        
        Args:
            lat: Latitude of center point
            lng: Longitude of center point
            radius_km: Search radius in kilometers
            table: Table name (e.g., 'planit_renewables', 'planit_datacentres')
        
        Returns:
            List of projects with distance_km field added
        """
        query = f"""
            SELECT 
                *,
                ST_Distance(
                    geom::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) / 1000 as distance_km
            FROM {table}
            WHERE geom IS NOT NULL
            AND ST_DWithin(
                geom::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
            )
            ORDER BY distance_km ASC
        """
        radius_meters = radius_km * 1000
        return self.execute_query(query, (lng, lat, lng, lat, radius_meters))

    def get_projects_near_my_sites(self, distance_km: float = 5.0, 
                                   scraped_table: str = 'planit_renewables',
                                   my_projects_table: str = 'my_projects',
                                   my_projects_schema: str = 'public',
                                   only_new: bool = True) -> List[Dict[str, Any]]:
        """
        Find scraped projects within X km of any of your project sites
        
        Args:
            distance_km: Search radius in kilometers
            scraped_table: Scraped data table (e.g., 'planit_renewables')
            my_projects_table: Your projects table name
            my_projects_schema: Schema containing your projects
            only_new: Only return projects marked as new
        
        Returns:
            List of nearby projects with distance and your project info
        """
        new_filter = "AND scraped.is_new = TRUE" if only_new else ""
        
        query = f"""
            SELECT 
                scraped.*,
                my_proj.id as my_project_id,
                my_proj.name as my_project_name,
                ST_Distance(
                    scraped.geom::geography,
                    my_proj.geom::geography
                ) / 1000 as distance_km
            FROM {self.schema}.{scraped_table} scraped
            CROSS JOIN {my_projects_schema}.{my_projects_table} my_proj
            WHERE scraped.geom IS NOT NULL
            AND my_proj.geom IS NOT NULL
            AND ST_DWithin(
                scraped.geom::geography,
                my_proj.geom::geography,
                %s
            )
            {new_filter}
            ORDER BY distance_km ASC
        """
        return self.execute_query(query, (distance_km * 1000,))

    def get_projects_between_tables(self, table1: str = 'planit_renewables', 
                                    table2: str = 'planit_datacentres',
                                    distance_km: float = 5.0) -> List[Dict[str, Any]]:
        """
        Find pairs of projects from two different tables that are close together
        Example: Find datacentres near renewable projects
        
        Args:
            table1: First table name
            table2: Second table name  
            distance_km: Maximum distance between projects
            
        Returns:
            List of project pairs with distance
        """
        query = f"""
            SELECT DISTINCT
                t1.uid as table1_uid,
                t1.name as table1_name,
                t1.area_name as table1_area,
                t2.uid as table2_uid,
                t2.name as table2_name,
                t2.area_name as table2_area,
                ST_Distance(t1.geom::geography, t2.geom::geography) / 1000 as distance_km
            FROM {self.schema}.{table1} t1
            CROSS JOIN {self.schema}.{table2} t2
            WHERE t1.geom IS NOT NULL 
            AND t2.geom IS NOT NULL
            AND ST_DWithin(
                t1.geom::geography,
                t2.geom::geography,
                %s
            )
            ORDER BY distance_km ASC
        """
        return self.execute_query(query, (distance_km * 1000,))

    def get_project_density_by_area(self, table: str = 'planit_renewables', 
                                   grid_size_km: float = 10.0) -> List[Dict[str, Any]]:
        """
        Get density of projects in grid cells across the country
        Useful for heatmaps
        
        Args:
            table: Table to analyze
            grid_size_km: Size of grid cells in kilometers (approximate)
            
        Returns:
            List of grid cells with project counts and center coordinates
        """
        # Convert km to degrees (very approximate: 1 degree ≈ 111km at equator)
        grid_degrees = grid_size_km / 111.0
        
        query = f"""
            SELECT 
                FLOOR(ST_X(geom) / %s) * %s as grid_lng,
                FLOOR(ST_Y(geom) / %s) * %s as grid_lat,
                COUNT(*) as project_count,
                AVG(ST_X(geom)) as center_lng,
                AVG(ST_Y(geom)) as center_lat
            FROM {self.schema}.{table}
            WHERE geom IS NOT NULL
            GROUP BY grid_lng, grid_lat
            HAVING COUNT(*) > 0
            ORDER BY project_count DESC
        """
        return self.execute_query(query, (grid_degrees, grid_degrees, grid_degrees, grid_degrees))

    def get_geometry_coverage_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics on geometry coverage across all scraper tables
        Useful for monitoring data quality
        
        Returns:
            List with coverage stats for each table
        """
        query = """
            SELECT 
                'planit_renewables' as table_name,
                COUNT(*) as total_records,
                COUNT(geom) as records_with_geometry,
                ROUND(COUNT(geom)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as geometry_coverage_pct
            FROM planit_renewables
            UNION ALL
            SELECT 
                'planit_datacentres' as table_name,
                COUNT(*) as total_records,
                COUNT(geom) as records_with_geometry,
                ROUND(COUNT(geom)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as geometry_coverage_pct
            FROM planit_datacentres
            UNION ALL
            SELECT 
                'peeringdb_fac_gb' as table_name,
                COUNT(*) as total_records,
                COUNT(geom) as records_with_geometry,
                ROUND(COUNT(geom)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as geometry_coverage_pct
            FROM peeringdb_fac_gb
            UNION ALL
            SELECT 
                'peeringdb_ix_gb' as table_name,
                COUNT(*) as total_records,
                COUNT(geom) as records_with_geometry,
                ROUND(COUNT(geom)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as geometry_coverage_pct
            FROM peeringdb_ix_gb
        """
        return self.execute_query(query)

# Global database instance
db = SupabaseDB()