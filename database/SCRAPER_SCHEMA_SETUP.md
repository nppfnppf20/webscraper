# Scraper Schema Setup Instructions

## What Changed

The scrapers now use **direct PostgreSQL connections** to write to the `scraper` schema instead of using the Supabase REST API (which only works with the `public` schema).

### Code Changes Made:
1. ✅ **Fixed field mapping** in `run_planit_renewables_daily.py` - now maps CSV `id` → database `uid` (not integer `id`)
2. ✅ **Improved `execute_upsert()`** in `database.py` - now uses PostgreSQL directly for custom schemas
3. ✅ **Created scraper schema SQL** - `database/scraper_schema.sql` to create all tables

## Next Steps: Create Database Tables

You need to create the tables in your Supabase `scraper` schema. Here's how:

### Step 1: Run the SQL Script in Supabase

1. Go to your **Supabase Dashboard**
2. Navigate to **SQL Editor**
3. Copy the contents of `database/scraper_schema.sql`
4. Paste and **Run** the SQL

This will:
- Create the `scraper` schema
- Create all required tables (`planit_renewables`, `planit_datacentres`, `peeringdb_fac_gb`, etc.)
- Set up indexes and triggers

### Step 2: Verify Tables Were Created

Run this query in Supabase SQL Editor:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'scraper'
ORDER BY table_name;
```

You should see:
- `peeringdb_fac_gb`
- `peeringdb_ix_gb`
- `planit_datacentres`
- `planit_renewables`
- `west_lindsey_consultations`
- `west_lindsey_planning`

### Step 3: Deploy and Test

Once the tables are created:
1. **Deploy your code** to Render (the changes to `database.py` and scrapers)
2. Make sure your environment variables include: `POSTGRES_SCHEMA=scraper`
3. **Test the scrapers** - they should now successfully write to the `scraper` schema

## What Was Fixed

### Problem 1: Data Type Mismatch
**Error:** `invalid input syntax for type integer: "DorsetCouncil/P/HOU/2025/07212"`

**Cause:** Scraper was trying to insert application UIDs (strings) into the auto-increment `id` column (integer)

**Fix:** Updated field mapping to use `uid` column instead

### Problem 2: Schema Not Found
**Error:** `Could not find the table 'public.planit_renewables' in the schema cache`

**Cause:** Supabase REST API client only works with `public` schema

**Fix:** Updated `execute_upsert()` to use direct PostgreSQL for custom schemas

### Problem 3: PeeringDB Timeout
**Error:** PeeringDB scraper timing out after 300s

**Cause:** Tables didn't exist in `scraper` schema, causing queries to hang

**Fix:** Created SQL script to set up all tables in `scraper` schema

## Verification

After setup, your scraper logs should show:
```
✅ Successfully saved X records to database
```

Instead of:
```
❌ Failed to save to database
Could not find the table 'public.planit_renewables'
```

## Need Help?

If you encounter issues:
1. Check that `POSTGRES_SCHEMA=scraper` is set in your environment
2. Verify tables exist: `SELECT * FROM scraper.planit_renewables LIMIT 1;`
3. Check connection: Ensure `DATABASE_URL` is correctly set

