-- Add filtering fields to planit_renewables table
-- Run this in Supabase SQL Editor

ALTER TABLE scraper.planit_renewables 
ADD COLUMN IF NOT EXISTS application_type TEXT,
ADD COLUMN IF NOT EXISTS development_type TEXT,
ADD COLUMN IF NOT EXISTS decision TEXT,
ADD COLUMN IF NOT EXISTS status_class TEXT,
ADD COLUMN IF NOT EXISTS site_area_ha DECIMAL(10, 2);

-- Add comments for documentation
COMMENT ON COLUMN scraper.planit_renewables.application_type IS 'Detailed application type from PlanIt API';
COMMENT ON COLUMN scraper.planit_renewables.development_type IS 'Development category from PlanIt API';
COMMENT ON COLUMN scraper.planit_renewables.decision IS 'Planning decision details';
COMMENT ON COLUMN scraper.planit_renewables.status_class IS 'Classified status for filtering (e.g., approved, rejected, pending)';
COMMENT ON COLUMN scraper.planit_renewables.site_area_ha IS 'Site area in hectares';

-- Create indexes for common filter queries
CREATE INDEX IF NOT EXISTS idx_planit_renewables_status_class 
ON scraper.planit_renewables(status_class);

CREATE INDEX IF NOT EXISTS idx_planit_renewables_app_type 
ON scraper.planit_renewables(app_type);

CREATE INDEX IF NOT EXISTS idx_planit_renewables_app_size 
ON scraper.planit_renewables(app_size);

-- Verify columns added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'scraper' 
  AND table_name = 'planit_renewables'
  AND column_name IN ('application_type', 'development_type', 'decision', 'status_class', 'site_area_ha');

