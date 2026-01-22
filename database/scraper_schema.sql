-- Supabase Database Schema for Web Scraper Project - SCRAPER SCHEMA
-- This creates all tables in the 'scraper' schema instead of 'public'

-- Create scraper schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS scraper;

-- Table for West Lindsey Planning Applications
CREATE TABLE IF NOT EXISTS scraper.west_lindsey_planning (
    id SERIAL PRIMARY KEY,
    reference TEXT UNIQUE,
    title TEXT,
    description TEXT,
    address TEXT,
    postcode TEXT,
    status TEXT,
    decision TEXT,
    received_date DATE,
    decided_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for West Lindsey Consultations
CREATE TABLE IF NOT EXISTS scraper.west_lindsey_consultations (
    id SERIAL PRIMARY KEY,
    consultation_id TEXT,
    application_id TEXT,
    title TEXT,
    consultee_name TEXT,
    consultee_email TEXT,
    consultee_address TEXT,
    status TEXT,
    description TEXT,
    response_published TEXT,
    original_created_time TEXT,
    original_last_modified_time TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for PeeringDB Internet Exchanges (GB)
CREATE TABLE IF NOT EXISTS scraper.peeringdb_ix_gb (
    id SERIAL PRIMARY KEY,
    peeringdb_id INTEGER UNIQUE,
    name TEXT,
    city TEXT,
    country TEXT,
    region_continent TEXT,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for PeeringDB Facilities (GB)
CREATE TABLE IF NOT EXISTS scraper.peeringdb_fac_gb (
    id SERIAL PRIMARY KEY,
    peeringdb_id INTEGER UNIQUE,
    name TEXT,
    city TEXT,
    country TEXT,
    address1 TEXT,
    address2 TEXT,
    zipcode TEXT,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for PlanIt Data Centres
CREATE TABLE IF NOT EXISTS scraper.planit_datacentres (
    id SERIAL PRIMARY KEY,
    uid TEXT UNIQUE,
    name TEXT,
    scraper_name TEXT,
    description TEXT,
    address TEXT,
    postcode TEXT,
    url TEXT,
    app_size TEXT,
    app_state TEXT,
    app_type TEXT,
    start_date DATE,
    decided_date DATE,
    area_name TEXT,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    last_scraped TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for PlanIt Renewables
CREATE TABLE IF NOT EXISTS scraper.planit_renewables (
    id SERIAL PRIMARY KEY,
    uid TEXT UNIQUE,
    name TEXT,
    scraper_name TEXT,
    description TEXT,
    address TEXT,
    postcode TEXT,
    url TEXT,
    app_size TEXT,
    app_state TEXT,
    app_type TEXT,
    start_date DATE,
    decided_date DATE,
    consulted_date DATE,
    area_name TEXT,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    location_x DECIMAL(15, 2),
    location_y DECIMAL(15, 2),
    other_fields JSONB,
    last_scraped TIMESTAMP WITH TIME ZONE,
    last_different TIMESTAMP WITH TIME ZONE,
    last_changed TIMESTAMP WITH TIME ZONE,
    is_new BOOLEAN DEFAULT FALSE,
    dismissed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_scraper_west_lindsey_planning_reference ON scraper.west_lindsey_planning(reference);
CREATE INDEX IF NOT EXISTS idx_scraper_planit_datacentres_uid ON scraper.planit_datacentres(uid);
CREATE INDEX IF NOT EXISTS idx_scraper_planit_renewables_uid ON scraper.planit_renewables(uid);
CREATE INDEX IF NOT EXISTS idx_scraper_planit_renewables_area ON scraper.planit_renewables(area_name);
CREATE INDEX IF NOT EXISTS idx_scraper_peeringdb_ix_peeringdb_id ON scraper.peeringdb_ix_gb(peeringdb_id);
CREATE INDEX IF NOT EXISTS idx_scraper_peeringdb_fac_peeringdb_id ON scraper.peeringdb_fac_gb(peeringdb_id);

-- Create updated_at trigger function (if not already exists in database)
CREATE OR REPLACE FUNCTION scraper.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_west_lindsey_planning_updated_at ON scraper.west_lindsey_planning;
CREATE TRIGGER update_west_lindsey_planning_updated_at 
    BEFORE UPDATE ON scraper.west_lindsey_planning 
    FOR EACH ROW EXECUTE FUNCTION scraper.update_updated_at_column();

DROP TRIGGER IF EXISTS update_west_lindsey_consultations_updated_at ON scraper.west_lindsey_consultations;
CREATE TRIGGER update_west_lindsey_consultations_updated_at 
    BEFORE UPDATE ON scraper.west_lindsey_consultations 
    FOR EACH ROW EXECUTE FUNCTION scraper.update_updated_at_column();

DROP TRIGGER IF EXISTS update_peeringdb_ix_gb_updated_at ON scraper.peeringdb_ix_gb;
CREATE TRIGGER update_peeringdb_ix_gb_updated_at 
    BEFORE UPDATE ON scraper.peeringdb_ix_gb 
    FOR EACH ROW EXECUTE FUNCTION scraper.update_updated_at_column();

DROP TRIGGER IF EXISTS update_peeringdb_fac_gb_updated_at ON scraper.peeringdb_fac_gb;
CREATE TRIGGER update_peeringdb_fac_gb_updated_at 
    BEFORE UPDATE ON scraper.peeringdb_fac_gb 
    FOR EACH ROW EXECUTE FUNCTION scraper.update_updated_at_column();

DROP TRIGGER IF EXISTS update_planit_datacentres_updated_at ON scraper.planit_datacentres;
CREATE TRIGGER update_planit_datacentres_updated_at 
    BEFORE UPDATE ON scraper.planit_datacentres 
    FOR EACH ROW EXECUTE FUNCTION scraper.update_updated_at_column();

DROP TRIGGER IF EXISTS update_planit_renewables_updated_at ON scraper.planit_renewables;
CREATE TRIGGER update_planit_renewables_updated_at
    BEFORE UPDATE ON scraper.planit_renewables
    FOR EACH ROW EXECUTE FUNCTION scraper.update_updated_at_column();

-- Table for Contracts Finder (UK Government Contract Opportunities)
CREATE TABLE IF NOT EXISTS scraper.contracts_finder (
    id SERIAL PRIMARY KEY,
    notice_id TEXT UNIQUE,
    title TEXT,
    description TEXT,
    organisation TEXT,
    published_date TIMESTAMP WITH TIME ZONE,
    closing_date TIMESTAMP WITH TIME ZONE,
    value_low DECIMAL(15, 2),
    value_high DECIMAL(15, 2),
    status TEXT,
    notice_type TEXT,
    region TEXT,
    postcode TEXT,
    cpv_codes TEXT,
    suitable_for_sme BOOLEAN,
    suitable_for_vco BOOLEAN,
    url TEXT,
    last_scraped TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scraper_contracts_finder_notice_id ON scraper.contracts_finder(notice_id);
CREATE INDEX IF NOT EXISTS idx_scraper_contracts_finder_status ON scraper.contracts_finder(status);
CREATE INDEX IF NOT EXISTS idx_scraper_contracts_finder_published ON scraper.contracts_finder(published_date);

DROP TRIGGER IF EXISTS update_contracts_finder_updated_at ON scraper.contracts_finder;
CREATE TRIGGER update_contracts_finder_updated_at
    BEFORE UPDATE ON scraper.contracts_finder
    FOR EACH ROW EXECUTE FUNCTION scraper.update_updated_at_column();

-- Grant permissions (adjust as needed)
-- GRANT USAGE ON SCHEMA scraper TO anon, authenticated;
-- GRANT SELECT ON ALL TABLES IN SCHEMA scraper TO anon, authenticated;

