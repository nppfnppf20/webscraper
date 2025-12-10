-- Debug: Check which tables have geometry columns in scraper schema

-- 1. Check all columns in planit_renewables
SELECT column_name, data_type, udt_name
FROM information_schema.columns
WHERE table_schema = 'scraper' 
  AND table_name = 'planit_renewables'
ORDER BY ordinal_position;

-- 2. Check all columns in planit_datacentres
SELECT column_name, data_type, udt_name
FROM information_schema.columns
WHERE table_schema = 'scraper' 
  AND table_name = 'planit_datacentres'
ORDER BY ordinal_position;

-- 3. Check specifically for geom columns across all scraper tables
SELECT 
    table_name,
    column_name,
    data_type,
    udt_name
FROM information_schema.columns
WHERE table_schema = 'scraper' 
  AND column_name = 'geom';

-- 4. Check if PostGIS extension is enabled
SELECT * FROM pg_extension WHERE extname = 'postgis';

-- 5. Check for geometry_columns (PostGIS system table)
SELECT f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type
FROM geometry_columns
WHERE f_table_schema = 'scraper';

