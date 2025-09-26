from __future__ import annotations

from pathlib import Path
from .planit_api_scraper import (
    fetch_renewables_from_planit_api,
    normalize_planit_api_result,
    PlanItAPIError,
    PlanItAPIRateLimit,
)
from .io import save_csv


if __name__ == "__main__":
    """
    PlanIt Renewables Test 2 - Using official PlanIt API
    Fetches renewables projects from last 3 months
    """
    output_path = Path(__file__).parent.parent.parent / "planit_renewables_test2.csv"

    try:
        print("[PlanIt API Test] 🚀 Starting targeted PlanIt API search...")

        # Use the exact same API call as your working CSV link
        raw_results = fetch_renewables_from_planit_api()

        print(f"[PlanIt API Test] 🔄 Normalizing {len(raw_results)} results...")

        # Normalize results to our expected format
        normalized_results = []
        for raw_record in raw_results:
            try:
                normalized = normalize_planit_api_result(raw_record)
                normalized_results.append(normalized)
            except Exception as e:
                print(f"[PlanIt API Test] ⚠️ Error normalizing record: {e}")
                continue

        # Save results
        save_csv(output_path, normalized_results)

        print(f"[PlanIt API Test] ✅ Success! Saved {len(normalized_results)} renewables projects to {output_path.name}")

        # Summary stats
        if normalized_results:
            statuses = {}
            authorities = {}
            for result in normalized_results:
                status = result.get('status', 'Unknown')
                authority = result.get('authority', 'Unknown')
                statuses[status] = statuses.get(status, 0) + 1
                authorities[authority] = authorities.get(authority, 0) + 1

            print(f"[PlanIt API Test] 📊 Status breakdown: {dict(list(statuses.items())[:5])}")
            print(f"[PlanIt API Test] 📊 Top authorities: {dict(list(authorities.items())[:5])}")

    except PlanItAPIRateLimit as e:
        print(f"[PlanIt API Test] 🛑 Rate limited by PlanIt API")
        print(f"[PlanIt API Test] ⏰ Please wait {e.retry_after_seconds} seconds before trying again")
        import sys
        sys.exit(1)

    except PlanItAPIError as e:
        print(f"[PlanIt API Test] ❌ PlanIt API error: {e}")
        import sys
        sys.exit(1)

    except Exception as e:
        print(f"[PlanIt API Test] ❌ Unexpected error: {e}")
        import sys
        sys.exit(1)