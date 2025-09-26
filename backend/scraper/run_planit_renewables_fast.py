from __future__ import annotations

from pathlib import Path
from .planit_renewables import (
    fetch_major_renewables_last_complete_month,
    RateLimitExceeded,
)
from .io import save_csv


if __name__ == "__main__":
    """Fast version: fetch only last complete month without geocoding for dashboard refreshes"""
    output_path = Path(__file__).parent.parent.parent / "planit_renewables.csv"

    try:
        print("[PlanIt Fast] Fetching only last complete month without geocoding for faster refresh...")
        rows = fetch_major_renewables_last_complete_month(enable_geocode=False)

        save_csv(output_path, rows)
        print(f"[PlanIt Fast] ✅ Saved {len(rows)} renewables records to {output_path}")

    except RateLimitExceeded as e:
        print(f"\n🛑 RATE LIMITED: API wants {e.retry_after_seconds} seconds wait time")
        print(f"⏰ Please try again after {e.retry_after_seconds//60}m {e.retry_after_seconds%60}s")

        # Save any incremental progress we have
        incremental_path = Path(__file__).parent.parent.parent / "planit_renewables_incremental.csv"
        if incremental_path.exists():
            import shutil
            shutil.copy2(incremental_path, output_path)
            print(f"💾 Saved incremental progress to {output_path}")

        import sys
        sys.exit(1)