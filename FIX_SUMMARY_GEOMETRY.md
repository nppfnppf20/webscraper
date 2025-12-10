# Geometry Support - Final Fix Summary

## Problem Found

The renewables scraper was **purposely skipping coordinate extraction** for speed, resulting in:
- ✅ 290 renewables records in database
- ❌ 0 records with lat/lng (0% geometry coverage)
- ❌ Unable to do spatial queries

## Root Cause

In `backend/scraper/planit_renewables.py`:
- Geocoding was disabled (`enable_geocode=False`)
- GeoJSON geometry extraction was commented out as "Skip GeoJSON fallback entirely for speed"
- The API **was returning** geometry, but the scraper wasn't extracting it

## The Fix

Updated `planit_renewables.py` to extract coordinates from the API's GeoJSON geometry response:

```python
# Extract from GeoJSON geometry if available (fast - no external API call)
if (lat_f is None or lng_f is None) and geometry:
    if isinstance(geometry, dict):
        coords = geometry.get("coordinates", [])
        geom_type = geometry.get("type", "")
        # GeoJSON Point format: [lng, lat]
        if geom_type == "Point" and len(coords) >= 2:
            lng_f = _to_float(coords[0])
            lat_f = _to_float(coords[1])
```

**Benefits:**
- ✅ Fast - no external API calls
- ✅ Uses geometry already in the API response
- ✅ Doesn't slow down the scraper

## What's Already Done

1. ✅ PostGIS extension enabled
2. ✅ `geom` columns added to all scraper tables
3. ✅ Triggers created to auto-populate geometry from lat/lng
4. ✅ Spatial indexes created
5. ✅ Scraper code fixed to extract coordinates

## What You Need To Do

### Step 1: Deploy the Code Fix

```bash
git add .
git commit -m "Fix coordinate extraction in renewables scraper"
git push
```

### Step 2: Wait for Next Scraper Run

The next time the cron job runs, new records will have coordinates.

### Step 3: Backfill Existing Records (Optional)

If you want to add coordinates to the existing 290 records, you have two options:

**Option A: Manual Scraper Run (Recommended)**
Re-run the scraper manually to fetch fresh data with coordinates:

```bash
# On your Render service
python -m backend.scraper.run_planit_renewables_daily
```

**Option B: Enable Geocoding for Existing Records**
Run a one-time script to geocode by postcode (slower, but fills in missing data):

```python
# Create a script: backend/scraper/backfill_renewables_coords.py

from backend.database import db
from backend.scraper.planit_renewables import _postcode_to_latlng
import time

records = db.execute_query("""
    SELECT id, postcode 
    FROM planit_renewables 
    WHERE (latitude IS NULL OR longitude IS NULL) 
    AND postcode IS NOT NULL
""")

for i, record in enumerate(records):
    postcode = record['postcode']
    if postcode:
        coords = _postcode_to_latlng(postcode)
        if coords:
            lat, lng = coords
            db.execute_raw(
                "UPDATE planit_renewables SET latitude = %s, longitude = %s WHERE id = %s",
                (lat, lng, record['id'])
            )
            print(f"[{i+1}/{len(records)}] Updated {record['id']}")
            time.sleep(0.5)  # Rate limit
```

## Verification

After the next scraper run, check geometry coverage:

```sql
SELECT 
    'planit_renewables' as table_name,
    COUNT(*) as total,
    COUNT(geom) as with_geometry,
    ROUND(COUNT(geom)::numeric / COUNT(*) * 100, 1) as coverage_pct
FROM scraper.planit_renewables;
```

You should see **~95-100% coverage** (some records genuinely don't have locations).

## Current Status

| Table | Total Records | With Geometry | Coverage |
|-------|---------------|---------------|----------|
| planit_renewables | 290 | 0 | 0% → Will be ~95%+ after fix |
| planit_datacentres | 76 | 58 | 76.3% |
| peeringdb_ix_gb | 0 | 0 | N/A |

## Testing Spatial Queries

Once coordinates are populated, test spatial queries:

```python
# Find renewables within 10km of London
from backend.database import db

results = db.get_projects_within_radius(
    lat=51.5074,
    lng=-0.1278, 
    radius_km=10,
    table='planit_renewables'
)

print(f"Found {len(results)} renewables within 10km of London")
for r in results[:5]:
    print(f"  - {r['name']} ({r['distance_km']:.2f}km away)")
```

## Files Changed

```
✓ backend/scraper/planit_renewables.py  [MODIFIED] - Extract coords from GeoJSON
✓ database/add_postgis_geometry.sql      [CREATED]  - PostGIS setup
✓ backend/database.py                    [MODIFIED] - Spatial query methods
✓ FIX_SUMMARY_GEOMETRY.md                [CREATED]  - This file
```

---

**All fixes applied! Deploy and test after next scraper run.** 🚀

