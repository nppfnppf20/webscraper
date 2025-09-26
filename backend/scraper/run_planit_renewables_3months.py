from __future__ import annotations

from pathlib import Path
from .planit_renewables import (
    fetch_all_major_renewables_last_n_months,
    RateLimitExceeded,
)
from .io import save_csv


if __name__ == "__main__":
    """Very fast version: last 3 months, no geocoding, for dashboard refreshes"""
    output_path = Path(__file__).parent.parent.parent / "planit_renewables.csv"

    try:
        print("[PlanIt 3M] 🚀 Fetching last 3 months without geocoding for dashboard refresh...")

        # Fetch only 3 months of data, no geocoding for speed
        rows = fetch_all_major_renewables_last_n_months(3, enable_geocode=False)

        save_csv(output_path, rows)
        print(f"[PlanIt 3M] ✅ Success! Saved {len(rows)} renewables records to {output_path.name}")

    except RateLimitExceeded as e:
        print(f"[PlanIt 3M] 🛑 RATE LIMITED: {e.retry_after_seconds}s wait required")

        # Save any incremental progress
        incremental_path = Path(__file__).parent.parent.parent / "planit_renewables_incremental.csv"
        if incremental_path.exists():
            import shutil
            shutil.copy2(incremental_path, output_path)
            print(f"[PlanIt 3M] 💾 Saved incremental progress")

        import sys
        sys.exit(1)

    except Exception as e:
        print(f"[PlanIt 3M] ❌ Error: {e}")
        import sys
        sys.exit(1)