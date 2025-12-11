-- Add filtering fields to planit_datacentres table
-- Run this in Supabase SQL Editor

ALTER TABLE scraper.planit_datacentres 
ADD COLUMN IF NOT EXISTS application_type TEXT,
ADD COLUMN IF NOT EXISTS development_type TEXT,
ADD COLUMN IF NOT EXISTS decision TEXT,
ADD COLUMN IF NOT EXISTS last_changed TIMESTAMP WITH TIME ZONE;

-- Add comments for documentation
COMMENT ON COLUMN scraper.planit_datacentres.application_type IS 'Detailed application type from PlanIt API';
COMMENT ON COLUMN scraper.planit_datacentres.development_type IS 'Development category from PlanIt API';
COMMENT ON COLUMN scraper.planit_datacentres.decision IS 'Planning decision details';
COMMENT ON COLUMN scraper.planit_datacentres.last_changed IS 'Last time the application was changed';

-- Create indexes for common filter queries
CREATE INDEX IF NOT EXISTS idx_planit_datacentres_app_type 
ON scraper.planit_datacentres(app_type);

CREATE INDEX IF NOT EXISTS idx_planit_datacentres_app_size 
ON scraper.planit_datacentres(app_size);

CREATE INDEX IF NOT EXISTS idx_planit_datacentres_app_state 
ON scraper.planit_datacentres(app_state);

CREATE INDEX IF NOT EXISTS idx_planit_datacentres_last_changed 
ON scraper.planit_datacentres(last_changed);

-- Verify columns added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'scraper' 
  AND table_name = 'planit_datacentres'
  AND column_name IN ('application_type', 'development_type', 'decision', 'last_changed');

