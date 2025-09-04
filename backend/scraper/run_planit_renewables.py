from __future__ import annotations

import argparse
from pathlib import Path
from .planit_renewables import (
    fetch_all_major_renewables_last_n_years,
    fetch_all_major_renewables_last_n_months,
    fetch_major_renewables_last_complete_month,
    RateLimitExceeded,
)
from .io import save_csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch PlanIt renewables applications")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--years", type=int, help="Number of years to look back", default=None)
    group.add_argument("--months", type=int, help="Number of months to look back", default=None)
    group.add_argument("--last-complete-month", action="store_true", help="Fetch only the last complete calendar month")
    parser.add_argument("--no-geocode", action="store_true", help="Disable postcode geocoding fallback to speed up runs")
    parser.add_argument("--out", type=Path, help="Output CSV path", default=Path(__file__).parent.parent.parent / "planit_renewables.csv")
    args = parser.parse_args()

    try:
        if args.last_complete_month:
            rows = fetch_major_renewables_last_complete_month(enable_geocode=not args.no_geocode)
        elif args.months is not None:
            rows = fetch_all_major_renewables_last_n_months(args.months, enable_geocode=not args.no_geocode)
        else:
            years = args.years if args.years is not None else 2
            rows = fetch_all_major_renewables_last_n_years(years, enable_geocode=not args.no_geocode)

        save_csv(args.out, rows)
        print(f"Saved {len(rows)} PlanIt renewables rows to {args.out}")
        
        # Also copy incremental file to final output for convenience
        incremental_path = Path(__file__).parent.parent.parent / "planit_renewables_incremental.csv"
        if incremental_path.exists():
            import shutil
            shutil.copy2(incremental_path, args.out)
            print(f"Copied incremental progress to {args.out}")
            
    except RateLimitExceeded as e:
        print(f"\n🛑 RATE LIMITED: API wants {e.retry_after_seconds} seconds wait time")
        print(f"⏰ Please restart the scraper after {e.retry_after_seconds} seconds ({e.retry_after_seconds//60} minutes {e.retry_after_seconds%60} seconds)")
        
        # Save any incremental progress we have
        incremental_path = Path(__file__).parent.parent.parent / "planit_renewables_incremental.csv"
        if incremental_path.exists():
            import shutil
            shutil.copy2(incremental_path, args.out)
            print(f"💾 Saved incremental progress to {args.out}")
            
        import sys
        sys.exit(1)

