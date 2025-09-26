from __future__ import annotations

from pathlib import Path
from .planit_api_datacentres import (
    fetch_datacentres_from_planit_api,
    normalize_planit_datacentres_result,
    PlanItAPIError,
    PlanItAPIRateLimit,
)
from .io import save_csv


if __name__ == "__main__":
    """
    PlanIt Datacentres API - Using official PlanIt API
    Fetches datacentre projects from last 3 months
    """
    output_path = Path(__file__).parent.parent.parent / "planit_datacentres.csv"

    try:
        print("[PlanIt API Datacentres] 🚀 Starting targeted PlanIt API search...")

        # Use the PlanIt API with datacentre search terms
        raw_results = fetch_datacentres_from_planit_api()

        print(f"[PlanIt API Datacentres] 🔄 Normalizing {len(raw_results)} results...")

        # Normalize results to our expected format
        normalized_results = []
        for raw_record in raw_results:
            try:
                normalized = normalize_planit_datacentres_result(raw_record)
                normalized_results.append(normalized)
            except Exception as e:
                print(f"[PlanIt API Datacentres] ⚠️ Error normalizing record: {e}")
                continue

        # Save results
        save_csv(output_path, normalized_results)

        print(f"[PlanIt API Datacentres] ✅ Success! Saved {len(normalized_results)} datacentre projects to {output_path.name}")

        # Summary stats
        if normalized_results:
            statuses = {}
            authorities = {}
            for result in normalized_results:
                status = result.get('app_state', result.get('status', 'Unknown'))
                authority = result.get('area_name', result.get('authority', 'Unknown'))
                statuses[status] = statuses.get(status, 0) + 1
                authorities[authority] = authorities.get(authority, 0) + 1

            print(f"[PlanIt API Datacentres] 📊 Status breakdown: {dict(list(statuses.items())[:5])}")
            print(f"[PlanIt API Datacentres] 📊 Top authorities: {dict(list(authorities.items())[:5])}")

    except PlanItAPIRateLimit as e:
        print(f"[PlanIt API Datacentres] 🛑 Rate limited by PlanIt API")
        print(f"[PlanIt API Datacentres] ⏰ Please wait {e.retry_after_seconds} seconds before trying again")
        import sys
        sys.exit(1)

    except PlanItAPIError as e:
        print(f"[PlanIt API Datacentres] ❌ PlanIt API error: {e}")
        import sys
        sys.exit(1)

    except Exception as e:
        print(f"[PlanIt API Datacentres] ❌ Unexpected error: {e}")
        import sys
        sys.exit(1)