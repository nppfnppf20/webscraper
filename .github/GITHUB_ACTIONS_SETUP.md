# GitHub Actions Setup Guide

## 🚀 Automated Scrapers via GitHub Actions

Your web scraper now uses GitHub Actions to run scrapers on a daily schedule, independent of your local machine. This works perfectly with Render hosting.

## 📋 Required GitHub Repository Secrets

After pushing this code to GitHub, you need to add these environment variables as **Repository Secrets**:

### 1. Go to GitHub Repository Settings
- Navigate to your repository on GitHub
- Click **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret** for each of the following:

### 2. Add These Secrets

| Secret Name | Description | Where to find it |
|-------------|-------------|------------------|
| `SUPABASE_URL` | Your Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_ANON_KEY` | Your Supabase anonymous key | Supabase Dashboard → Settings → API |
| `DATABASE_URL` | PostgreSQL connection string | Supabase Dashboard → Settings → Database |

### 3. Database URL Format
Your `DATABASE_URL` should look like:
```
postgresql://postgres:[password]@[host]:[port]/postgres
```

## ⏰ Scraping Schedule

| Time (UTC) | Scraper | Purpose |
|------------|---------|---------|
| 6:00 AM | West Lindsey | Consultation data |
| 8:00 AM | PeeringDB IX | Internet Exchanges |
| 10:00 AM | PeeringDB Facilities | Data centre facilities |
| 12:00 PM | PlanIt Data Centres | Planning applications |
| 2:00 PM | PlanIt Renewables | Energy projects |
| 4:00 PM | PlanIt Test2 | Alternative renewables |

## 🔧 Manual Triggering

Each workflow can be triggered manually:
1. Go to **Actions** tab in your GitHub repository
2. Select the scraper workflow you want to run
3. Click **Run workflow**

## 📊 Monitoring

- View workflow runs in the **Actions** tab
- Each scraper runs independently - one failure won't stop others
- Logs are available for each run
- Failed runs will show error details

## 🏠 Hosting Compatibility

This setup works with:
- ✅ **Render** (recommended)
- ✅ **Vercel**
- ✅ **Netlify**
- ✅ **Railway**
- ✅ Any hosting platform

The scrapers run on GitHub's servers and update your Supabase database directly, so your hosting platform only needs to serve the web application.

## 🔄 How it Works

1. **GitHub Actions** runs scrapers on schedule
2. **Scrapers** fetch new data from APIs
3. **Data** is saved directly to Supabase database
4. **Your website** (hosted on Render) displays the fresh data
5. **Users** see updated information automatically

No server maintenance or cron job management required! 🎉