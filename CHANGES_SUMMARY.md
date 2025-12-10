# Changes Summary - Scraper Schema Fix

## What Was Broken

Your scrapers were failing with these errors:
1. ❌ `invalid input syntax for type integer: "DorsetCouncil/P/HOU/2025/07212"` (PlanIt Renewables)
2. ❌ `Could not find the table 'public.planit_renewables' in the schema cache` (All scrapers)
3. ❌ PeeringDB Facilities timing out after 300 seconds

## Root Causes

1. **Wrong Schema**: Supabase REST API client only works with `public` schema, but you wanted to use `scraper` schema
2. **Wrong Field Mapping**: PlanIt Renewables was mapping CSV `id` (string UIDs) → database `id` (integer primary key)
3. **Missing Tables**: Tables didn't exist in `scraper` schema

## What Was Fixed

### 1. Database Connection (`backend/database.py`)
**Changed:** `execute_upsert()` method

**Before:**
- Only used Supabase REST API client
- Couldn't access custom schemas

**After:**
- ✅ Uses direct PostgreSQL for custom schemas (`scraper`)
- ✅ Uses Supabase client for `public` schema
- ✅ Filters out auto-increment `id` column from inserts
- ✅ Handles empty values properly
- ✅ Better error messages with traceback

### 2. PlanIt Renewables Field Mapping (`backend/scraper/run_planit_renewables_daily.py`)
**Changed:** `_map_fields_for_database()` function

**Before:**
```python
field_mapping = {
    'id': 'id',        # ❌ Wrong - maps to integer primary key
    'title': 'title',  # ❌ Wrong - field doesn't exist
    # missing 'link' → 'url' mapping
}
```

**After:**
```python
field_mapping = {
    'id': 'uid',       # ✅ Maps to text UID column
    'title': 'name',   # ✅ Maps to correct field
    'link': 'url',     # ✅ Added missing mapping
}
```

### 3. Database Schema Setup
**Created:** `database/scraper_schema.sql`

This SQL script creates all required tables in the `scraper` schema:
- ✅ `scraper.planit_renewables`
- ✅ `scraper.planit_datacentres`
- ✅ `scraper.peeringdb_fac_gb`
- ✅ `scraper.peeringdb_ix_gb`
- ✅ `scraper.west_lindsey_planning`
- ✅ `scraper.west_lindsey_consultations`

With proper:
- Primary keys and unique constraints
- Indexes for performance
- Triggers for `updated_at` timestamps

## Files Changed

```
backend/database.py                               [MODIFIED]
backend/scraper/run_planit_renewables_daily.py   [MODIFIED]
database/scraper_schema.sql                       [CREATED]
database/SCRAPER_SCHEMA_SETUP.md                  [CREATED]
CHANGES_SUMMARY.md                                [CREATED]
```

## What You Need To Do Next

### Step 1: Create Database Tables ⚠️ REQUIRED
Run `database/scraper_schema.sql` in your Supabase SQL Editor to create the tables.

See detailed instructions in: `database/SCRAPER_SCHEMA_SETUP.md`

### Step 2: Deploy Code Changes
The code changes are ready to commit and deploy:
```bash
git add .
git commit -m "Fix scraper schema support and field mappings"
git push
```

### Step 3: Verify Environment Variables
Make sure your Render cron job has:
```
POSTGRES_SCHEMA=scraper
DATABASE_URL=postgresql://...  (your Supabase connection string)
```

### Step 4: Test Scrapers
After deploying, your scrapers should show:
```
✅ Successfully saved X records to database
```

Instead of the previous errors.

## Expected Results

All scrapers should now:
1. ✅ Successfully connect to the `scraper` schema
2. ✅ Insert data with correct field mappings
3. ✅ Handle upserts properly (update existing, insert new)
4. ✅ Complete without timeouts

## Verification Queries

Check data was inserted:
```sql
-- Check PlanIt Renewables
SELECT COUNT(*), MAX(last_scraped) FROM scraper.planit_renewables;

-- Check PlanIt Datacentres
SELECT COUNT(*), MAX(last_scraped) FROM scraper.planit_datacentres;

-- Check PeeringDB Facilities
SELECT COUNT(*), MAX(created_at) FROM scraper.peeringdb_fac_gb;

-- Check PeeringDB IX
SELECT COUNT(*), MAX(created_at) FROM scraper.peeringdb_ix_gb;
```

## Rollback Plan

If you need to revert:
1. Change `POSTGRES_SCHEMA=public` in environment
2. Ensure tables exist in `public` schema (they should already)
3. Revert code changes

## Questions?

- Schema setup: See `database/SCRAPER_SCHEMA_SETUP.md`
- Field mappings: Check `backend/scraper/run_planit_renewables_daily.py`
- Database logic: See `backend/database.py` line 85+

