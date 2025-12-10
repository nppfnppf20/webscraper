# Render Cron Job Setup Guide

## Overview

This project now has automatic daily scraping configured via Render cron jobs.

## Architecture

```
Render Cron Job (daily at 2 AM UTC)
  └─> run_all_scrapers.py
       ├─> PeeringDB IX scraper → Supabase DB
       ├─> PeeringDB Facilities scraper → Supabase DB
       ├─> PlanIt Datacentres scraper → Supabase DB
       ├─> PlanIt Renewables scraper → Supabase DB
       └─> West Lindsey scraper → Supabase DB

Your API (api_server_db.py)
  └─> Reads from Supabase DB
       └─> Serves data to Frontend

Your Frontend
  └─> Calls API endpoints
       └─> Displays data to users
```

## Files Modified/Created

1. **run_all_scrapers.py** (NEW)
   - Master script that runs all scrapers sequentially
   - Logs progress and errors
   - Exits with error code if any scraper fails

2. **render.yaml** (MODIFIED)
   - Added cron job service named "daily-scraper"
   - Runs at 2 AM UTC every day
   - Uses same environment variables as your API

## Deployment Steps

1. **Commit and push changes:**
   ```bash
   git add run_all_scrapers.py render.yaml RENDER_CRON_SETUP.md
   git commit -m "Add daily scraper cron job"
   git push
   ```

2. **Render will automatically:**
   - Detect the new cron job service in render.yaml
   - Create a new "daily-scraper" service
   - Schedule it to run daily at 2 AM UTC

3. **Configure environment variables in Render dashboard:**
   - Go to your Render dashboard
   - Find the new "daily-scraper" cron job
   - Ensure these env vars are set (should auto-sync from your existing services):
     - `SUPABASE_URL`
     - `SUPABASE_ANON_KEY`
     - `SUPABASE_SERVICE_ROLE_KEY`
     - `DATABASE_URL`

## Customizing the Schedule

The cron schedule uses standard cron syntax: `"minute hour day month dayOfWeek"`

Current: `"0 2 * * *"` = 2 AM UTC daily

Examples:
- `"0 */6 * * *"` = Every 6 hours
- `"0 0 * * *"` = Midnight UTC daily
- `"0 8 * * 1-5"` = 8 AM UTC on weekdays only
- `"30 14 * * *"` = 2:30 PM UTC daily

Edit line 35 in render.yaml to change the schedule.

## Manual Trigger

You can also manually trigger scrapers via your API:

```bash
# Trigger individual scrapers
curl -X POST https://web-scraper-api-vnue.onrender.com/api/refresh/planit-renew
curl -X POST https://web-scraper-api-vnue.onrender.com/api/refresh/peeringdb-ix
curl -X POST https://web-scraper-api-vnue.onrender.com/api/refresh/west-lindsey
```

Or from your frontend, add refresh buttons that call these endpoints.

## Monitoring

1. **View cron job logs in Render dashboard:**
   - Go to dashboard → "daily-scraper" service
   - Click "Logs" tab
   - See output from run_all_scrapers.py

2. **Check if scrapers ran successfully:**
   - Look for "SCRAPING SUMMARY" in logs
   - Each scraper shows ✓ SUCCESS or ✗ FAILED
   - Total execution time is displayed

## Troubleshooting

**Cron job not appearing?**
- Push changes to Git
- Check Render dashboard for errors
- Verify render.yaml syntax

**Scrapers failing?**
- Check cron job logs in Render dashboard
- Verify environment variables are set correctly
- Ensure database connection works

**Data not updating?**
- Check cron job ran (see logs)
- Verify Supabase tables are being updated
- Check API is reading from correct tables

## Cost

Render cron jobs on paid plan:
- Free if combined with existing paid web service
- Check your Render plan for specifics

## Next Steps (Optional)

1. **Add refresh buttons to frontend:**
   - Call `/api/refresh/*` endpoints
   - Show loading state
   - Display success/error messages

2. **Add separate cron jobs for different schedules:**
   - Some scrapers run more frequently than others
   - Copy the cron job block in render.yaml
   - Change the name, schedule, and command

3. **Add monitoring/alerting:**
   - Set up Render email notifications for cron failures
   - Add a health check endpoint that shows last scrape time
