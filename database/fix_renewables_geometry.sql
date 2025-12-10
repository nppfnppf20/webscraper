-- Fix: Add geometry column to planit_renewables if missing
-- Run this in Supabase SQL Editor

-- Enable PostGIS if not already enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- Add geometry column to planit_renewables
ALTER TABLE scraper.planit_renewables 
ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

COMMENT ON COLUMN scraper.planit_renewables.geom IS 'PostGIS geometry point (SRID 4326 - WGS84)';

-- Create or replace the trigger function (in case it doesn't exist)
CREATE OR REPLACE FUNCTION scraper.update_geom_from_lat_lng()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.geom = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    ELSE
        NEW.geom = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists and recreate
DROP TRIGGER IF EXISTS trg_update_planit_renewables_geom ON scraper.planit_renewables;

CREATE TRIGGER trg_update_planit_renewables_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude ON scraper.planit_renewables
    FOR EACH ROW 
    EXECUTE FUNCTION scraper.update_geom_from_lat_lng();

-- Populate geometry for existing records
UPDATE scraper.planit_renewables
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE latitude IS NOT NULL 
  AND longitude IS NOT NULL
  AND (geom IS NULL OR ST_IsEmpty(geom));

-- Create spatial index
CREATE INDEX IF NOT EXISTS idx_planit_renewables_geom 
ON scraper.planit_renewables USING GIST(geom);

-- Verify the fix
SELECT 
    COUNT(*) as total_records,
    COUNT(geom) as records_with_geometry,
    COUNT(latitude) as records_with_latitude,
    COUNT(longitude) as records_with_longitude,
    ROUND(COUNT(geom)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as geometry_coverage_pct
FROM scraper.planit_renewables;

-- Show sample records with geometry
SELECT 
    uid, 
    name, 
    latitude, 
    longitude, 
    geom IS NOT NULL as has_geometry,
    ST_AsText(geom) as geometry_wkt
FROM scraper.planit_renewables
WHERE latitude IS NOT NULL AND longitude IS NOT NULL
LIMIT 5;

