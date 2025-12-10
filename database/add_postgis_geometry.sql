-- Add PostGIS Geometry Support to Scraper Tables
-- Run this in Supabase SQL Editor after creating your scraper schema tables

-- ============================================================
-- 1. Enable PostGIS Extension
-- ============================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================
-- 2. Add Geometry Columns to Existing Tables
-- ============================================================

-- PlanIt Renewables
ALTER TABLE scraper.planit_renewables 
ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

-- PlanIt Datacentres
ALTER TABLE scraper.planit_datacentres 
ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

-- PeeringDB Facilities
ALTER TABLE scraper.peeringdb_fac_gb 
ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

-- PeeringDB Internet Exchanges
ALTER TABLE scraper.peeringdb_ix_gb 
ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

COMMENT ON COLUMN scraper.planit_renewables.geom IS 'PostGIS geometry point (SRID 4326 - WGS84)';
COMMENT ON COLUMN scraper.planit_datacentres.geom IS 'PostGIS geometry point (SRID 4326 - WGS84)';
COMMENT ON COLUMN scraper.peeringdb_fac_gb.geom IS 'PostGIS geometry point (SRID 4326 - WGS84)';
COMMENT ON COLUMN scraper.peeringdb_ix_gb.geom IS 'PostGIS geometry point (SRID 4326 - WGS84)';

-- ============================================================
-- 3. Create Function to Auto-Update Geometry from Lat/Lng
-- ============================================================

CREATE OR REPLACE FUNCTION scraper.update_geom_from_lat_lng()
RETURNS TRIGGER AS $$
BEGIN
    -- Auto-populate geom from latitude/longitude columns
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.geom = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    ELSE
        NEW.geom = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION scraper.update_geom_from_lat_lng() IS 'Automatically populate geometry column from latitude/longitude';

-- ============================================================
-- 4. Create Triggers to Auto-Populate Geometry
-- ============================================================

-- PlanIt Renewables
DROP TRIGGER IF EXISTS trg_update_planit_renewables_geom ON scraper.planit_renewables;
CREATE TRIGGER trg_update_planit_renewables_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude ON scraper.planit_renewables
    FOR EACH ROW 
    EXECUTE FUNCTION scraper.update_geom_from_lat_lng();

-- PlanIt Datacentres
DROP TRIGGER IF EXISTS trg_update_planit_datacentres_geom ON scraper.planit_datacentres;
CREATE TRIGGER trg_update_planit_datacentres_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude ON scraper.planit_datacentres
    FOR EACH ROW 
    EXECUTE FUNCTION scraper.update_geom_from_lat_lng();

-- PeeringDB Facilities
DROP TRIGGER IF EXISTS trg_update_peeringdb_fac_geom ON scraper.peeringdb_fac_gb;
CREATE TRIGGER trg_update_peeringdb_fac_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude ON scraper.peeringdb_fac_gb
    FOR EACH ROW 
    EXECUTE FUNCTION scraper.update_geom_from_lat_lng();

-- PeeringDB Internet Exchanges
DROP TRIGGER IF EXISTS trg_update_peeringdb_ix_geom ON scraper.peeringdb_ix_gb;
CREATE TRIGGER trg_update_peeringdb_ix_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude ON scraper.peeringdb_ix_gb
    FOR EACH ROW 
    EXECUTE FUNCTION scraper.update_geom_from_lat_lng();

-- ============================================================
-- 5. Populate Geometry for Existing Records
-- ============================================================

-- Update PlanIt Renewables (existing records)
UPDATE scraper.planit_renewables
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE latitude IS NOT NULL 
  AND longitude IS NOT NULL
  AND geom IS NULL;

-- Update PlanIt Datacentres (existing records)
UPDATE scraper.planit_datacentres
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE latitude IS NOT NULL 
  AND longitude IS NOT NULL
  AND geom IS NULL;

-- Update PeeringDB Facilities (existing records)
UPDATE scraper.peeringdb_fac_gb
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE latitude IS NOT NULL 
  AND longitude IS NOT NULL
  AND geom IS NULL;

-- Update PeeringDB Internet Exchanges (existing records)
UPDATE scraper.peeringdb_ix_gb
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE latitude IS NOT NULL 
  AND longitude IS NOT NULL
  AND geom IS NULL;

-- ============================================================
-- 6. Create Spatial Indexes for Fast Queries
-- ============================================================

-- PlanIt Renewables
CREATE INDEX IF NOT EXISTS idx_planit_renewables_geom 
ON scraper.planit_renewables USING GIST(geom);

-- PlanIt Datacentres
CREATE INDEX IF NOT EXISTS idx_planit_datacentres_geom 
ON scraper.planit_datacentres USING GIST(geom);

-- PeeringDB Facilities
CREATE INDEX IF NOT EXISTS idx_peeringdb_fac_geom 
ON scraper.peeringdb_fac_gb USING GIST(geom);

-- PeeringDB Internet Exchanges
CREATE INDEX IF NOT EXISTS idx_peeringdb_ix_geom 
ON scraper.peeringdb_ix_gb USING GIST(geom);

-- ============================================================
-- 7. Verification Queries
-- ============================================================

-- Check geometry coverage
SELECT 
    'planit_renewables' as table_name,
    COUNT(*) as total_records,
    COUNT(geom) as records_with_geometry,
    ROUND(COUNT(geom)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as geometry_coverage_pct
FROM scraper.planit_renewables
UNION ALL
SELECT 
    'planit_datacentres' as table_name,
    COUNT(*) as total_records,
    COUNT(geom) as records_with_geometry,
    ROUND(COUNT(geom)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as geometry_coverage_pct
FROM scraper.planit_datacentres
UNION ALL
SELECT 
    'peeringdb_fac_gb' as table_name,
    COUNT(*) as total_records,
    COUNT(geom) as records_with_geometry,
    ROUND(COUNT(geom)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as geometry_coverage_pct
FROM scraper.peeringdb_fac_gb
UNION ALL
SELECT 
    'peeringdb_ix_gb' as table_name,
    COUNT(*) as total_records,
    COUNT(geom) as records_with_geometry,
    ROUND(COUNT(geom)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as geometry_coverage_pct
FROM scraper.peeringdb_ix_gb;

-- ============================================================
-- 8. Example Spatial Queries
-- ============================================================

-- Example 1: Find all renewables within 10km of a specific point (London)
-- SELECT 
--     uid, name, app_state,
--     ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(-0.1278, 51.5074), 4326)::geography) / 1000 as distance_km
-- FROM scraper.planit_renewables
-- WHERE ST_DWithin(
--     geom::geography,
--     ST_SetSRID(ST_MakePoint(-0.1278, 51.5074), 4326)::geography,
--     10000  -- 10km in meters
-- )
-- ORDER BY distance_km;

-- Example 2: Find all datacentres within 5km of any renewable
-- SELECT DISTINCT
--     dc.uid as dc_uid,
--     dc.name as dc_name,
--     ren.uid as renewable_uid,
--     ren.name as renewable_name,
--     ST_Distance(dc.geom::geography, ren.geom::geography) / 1000 as distance_km
-- FROM scraper.planit_datacentres dc
-- CROSS JOIN scraper.planit_renewables ren
-- WHERE ST_DWithin(
--     dc.geom::geography,
--     ren.geom::geography,
--     5000  -- 5km
-- )
-- ORDER BY distance_km;

-- Example 3: Count projects within radius of a point
-- SELECT 
--     COUNT(*) as projects_within_10km
-- FROM scraper.planit_renewables
-- WHERE ST_DWithin(
--     geom::geography,
--     ST_SetSRID(ST_MakePoint(-0.1278, 51.5074), 4326)::geography,  -- London
--     10000
-- );

-- ============================================================
-- DONE! 
-- ============================================================
-- All tables now have:
-- ✅ geometry column (geom)
-- ✅ Auto-population trigger from lat/lng
-- ✅ Spatial indexes for fast queries
-- ✅ Existing records updated with geometry
-- ============================================================

