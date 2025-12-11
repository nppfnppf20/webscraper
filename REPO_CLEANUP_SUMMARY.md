# Repository Cleanup Summary - Cron Job Only

## Date: December 11, 2025

This repository has been trimmed down to be **cron-job only** for running daily data scrapers. The frontend has been moved to a separate application.

---

## ✅ What Was Removed

### **Frontend (Deleted)**
- `svelte-dashboard/` - Entire Svelte frontend directory
  - All Vue/Svelte components
  - `node_modules/`
  - Frontend build configuration
  - All UI code

### **API Servers (Deleted)**
- `backend/api_server.py` - Flask API server
- `backend/api_server_db.py` - Database API endpoints

### **Utility Scripts (Deleted)**
One-off scripts no longer needed:
- `check_repd_stats.py`
- `collect_historical_datacentres.py`
- `fix_config.py`
- `fix_urls.py`
- `merge_historical_datacentres.py`
- `migrate_data.py`
- `simple_fix.py`
- `update_consultation_dates.py`

### **Assets (Deleted)**
- `rtpi_screenshot.png` - Frontend screenshot

### **Documentation (Deleted)**
Historical documentation no longer needed:
- `CHANGES_SUMMARY.md`
- `FIX_SUMMARY_GEOMETRY.md`
- `FIX_SUMMARY_ITERATION_2.md`

### **CSV Files (Moved to Backup)**
All CSV output files moved to `csv_backup/`:
- `peeringdb_fac_gb.csv`
- `peeringdb_ix_gb.csv`
- `planit_datacentres.csv`
- `planit_renewables.csv`
- `planit_renewables_incremental.csv`
- `planit_renewables_test.csv`
- `planit_renewables_test2.csv`
- `rtpi_events.csv`
- `test_default.csv`
- `west_lindsey_consultations.csv`
- `west_lindsey_planning.csv`

---

## ✅ What Was Kept

### **Core Scraper Files**
```
backend/
  ├── database.py              ✅ Database connection & queries
  └── scraper/                 ✅ All scraper modules
      ├── io.py                   - CSV utilities
      ├── peeringdb.py            - PeeringDB scraper
      ├── planit_api_datacentres.py
      ├── planit_renewables.py
      ├── run_peeringdb.py
      ├── run_planit_api_datacentres.py
      ├── run_planit_renewables_daily.py
      ├── run_west_lindsey.py
      ├── session.py              - HTTP session manager
      └── west_lindsey.py

run_all_scrapers.py            ✅ Main orchestrator
```

### **Configuration Files**
```
requirements.txt               ✅ Python dependencies
render.yaml                    ✅ Render deployment config (updated)
runtime.txt                    ✅ Python version
.env                           ✅ Environment variables
.gitignore                     ✅ Git configuration
```

### **Database Schema Files**
```
database/
  ├── scraper_schema.sql                   ✅ Main schema
  ├── add_postgis_geometry.sql             ✅ PostGIS setup
  ├── add_filtering_fields.sql             ✅ Renewables filters
  ├── add_datacentres_filtering_fields.sql ✅ Datacentres filters
  ├── debug_geometry_columns.sql           ✅ Debug helper
  ├── fix_renewables_geometry.sql          ✅ Geometry fix
  └── SCRAPER_SCHEMA_SETUP.md              ✅ Setup docs
```

### **Documentation (Essential)**
```
RENDER_CRON_SETUP.md           ✅ Deployment guide
REPO_CLEANUP_SUMMARY.md        ✅ This file
```

---

## 📁 New Simplified Structure

```
webscraper/                    (cron job only)
├── backend/
│   ├── database.py
│   └── scraper/
│       └── (all scraper files)
├── database/
│   └── (SQL schema files)
├── csv_backup/                ← CSV files backed up here
│   └── (all .csv files)
├── run_all_scrapers.py
├── requirements.txt
├── render.yaml                ← Updated (cron only)
├── runtime.txt
├── .env
├── .gitignore
├── RENDER_CRON_SETUP.md
└── REPO_CLEANUP_SUMMARY.md
```

---

## 🔧 Updated Configuration

### **render.yaml (Simplified)**

**Before:** 2 web services + 1 cron job  
**After:** 1 cron job only

```yaml
services:
  - type: cron
    name: daily-scraper
    env: python
    buildCommand: pip install -r requirements.txt
    schedule: "0 2 * * *"  # 2 AM UTC daily
    command: python run_all_scrapers.py
    envVars:
      - key: DATABASE_URL
      - key: SUPABASE_URL
      - key: SUPABASE_ANON_KEY
      - key: POSTGRES_SCHEMA
        value: scraper
```

---

## 🎯 Purpose of This Repo

This repository now has a **single responsibility**: Run daily cron jobs to scrape data and save it to the Supabase `scraper` schema.

**What it does:**
- ✅ Runs daily at 2 AM UTC
- ✅ Scrapes PlanIt renewables & datacentres
- ✅ Scrapes PeeringDB internet exchanges
- ✅ Scrapes West Lindsey planning data
- ✅ Saves everything to `scraper.planit_renewables`, `scraper.planit_datacentres`, etc.
- ✅ Includes PostGIS geometry for spatial queries

**What it doesn't do:**
- ❌ Serve a frontend (moved to separate app)
- ❌ Provide an API (frontend reads directly from Supabase)
- ❌ Generate CSV files (data is in database)

---

## 📊 Frontend (Separate Application)

Your frontend application will:
1. Connect directly to Supabase
2. Read from the `scraper` schema
3. No dependency on this scraper cron job repo

**Example frontend query:**
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://rvchlfjjdphcwldjfagr.supabase.co',
  'YOUR_ANON_KEY'
)

// Query scraped data directly
const { data } = await supabase
  .schema('scraper')
  .from('planit_renewables')
  .select('*')
  .eq('app_state', 'Permitted')
  .gte('site_area_ha', 10)
```

---

## 🚀 Deployment

### **Current Render Setup:**
- **Service Name:** `daily-scraper`
- **Type:** Cron job
- **Schedule:** Daily at 2 AM UTC
- **Command:** `python run_all_scrapers.py`

### **Environment Variables (Set in Render):**
```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
POSTGRES_SCHEMA=scraper
```

### **Deploy Updates:**
```bash
git add .
git commit -m "Trim repo to cron-job only"
git push
```

Render will automatically deploy the changes.

---

## 📝 Benefits of This Cleanup

✅ **Simpler codebase** - Only scraper logic  
✅ **Faster deployments** - No frontend build step  
✅ **Clearer responsibility** - Single purpose  
✅ **Easier maintenance** - Less code to manage  
✅ **Better separation** - Frontend in its own repo  
✅ **Smaller repo size** - No node_modules or build artifacts  

---

## 🔄 Backup Information

### **CSV Files Preserved:**
All CSV files have been moved to `csv_backup/` folder for reference.

### **Git History Intact:**
All deleted files remain in git history if needed:
```bash
# View file from previous commit
git show HEAD~1:backend/api_server.py

# Restore a deleted file if needed
git checkout HEAD~1 -- backend/api_server.py
```

---

## ✅ Next Steps

1. ✅ **Commit and push** these changes
2. ✅ **Verify cron job** runs successfully in Render
3. ✅ **Build separate frontend** that reads from Supabase
4. ✅ **Configure PostGIS** in Supabase (expose `scraper` schema to frontend if needed)

---

**Cleanup completed successfully!** 🎉

This repository is now lean, focused, and purpose-built for daily data scraping.

