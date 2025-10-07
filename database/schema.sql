-- Supabase Database Schema for Web Scraper Project

-- Table for RTPI Events
CREATE TABLE rtpi_events (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    event_date DATE,
    location TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for West Lindsey Planning Applications
CREATE TABLE west_lindsey_planning (
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
CREATE TABLE west_lindsey_consultations (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    consultation_start DATE,
    consultation_end DATE,
    status TEXT,
    url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for PeeringDB Internet Exchanges (GB)
CREATE TABLE peeringdb_ix_gb (
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
CREATE TABLE peeringdb_fac_gb (
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
CREATE TABLE planit_datacentres (
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
CREATE TABLE planit_renewables (
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS) for all tables
ALTER TABLE rtpi_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE west_lindsey_planning ENABLE ROW LEVEL SECURITY;
ALTER TABLE west_lindsey_consultations ENABLE ROW LEVEL SECURITY;
ALTER TABLE peeringdb_ix_gb ENABLE ROW LEVEL SECURITY;
ALTER TABLE peeringdb_fac_gb ENABLE ROW LEVEL SECURITY;
ALTER TABLE planit_datacentres ENABLE ROW LEVEL SECURITY;
ALTER TABLE planit_renewables ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (adjust as needed for your security requirements)
CREATE POLICY "Enable read access for all users" ON rtpi_events FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON west_lindsey_planning FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON west_lindsey_consultations FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON peeringdb_ix_gb FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON peeringdb_fac_gb FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON planit_datacentres FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON planit_renewables FOR SELECT USING (true);

-- Create indexes for better performance
CREATE INDEX idx_west_lindsey_planning_reference ON west_lindsey_planning(reference);
CREATE INDEX idx_planit_datacentres_uid ON planit_datacentres(uid);
CREATE INDEX idx_planit_renewables_uid ON planit_renewables(uid);
CREATE INDEX idx_planit_renewables_area ON planit_renewables(area_name);
CREATE INDEX idx_peeringdb_ix_peeringdb_id ON peeringdb_ix_gb(peeringdb_id);
CREATE INDEX idx_peeringdb_fac_peeringdb_id ON peeringdb_fac_gb(peeringdb_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_rtpi_events_updated_at BEFORE UPDATE ON rtpi_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_west_lindsey_planning_updated_at BEFORE UPDATE ON west_lindsey_planning FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_west_lindsey_consultations_updated_at BEFORE UPDATE ON west_lindsey_consultations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_peeringdb_ix_gb_updated_at BEFORE UPDATE ON peeringdb_ix_gb FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_peeringdb_fac_gb_updated_at BEFORE UPDATE ON peeringdb_fac_gb FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_planit_datacentres_updated_at BEFORE UPDATE ON planit_datacentres FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_planit_renewables_updated_at BEFORE UPDATE ON planit_renewables FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();