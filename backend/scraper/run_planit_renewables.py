from __future__ import annotations

import argparse
from pathlib import Path
from .planit_renewables import (
    fetch_all_major_renewables_last_n_years,
    fetch_all_major_renewables_last_n_months,
    fetch_major_renewables_last_complete_month,
)
from .io import save_csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch PlanIt renewables applications")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--years", type=int, help="Number of years to look back", default=None)
    group.add_argument("--months", type=int, help="Number of months to look back", default=None)
    group.add_argument("--last-complete-month", action="store_true", help="Fetch only the last complete calendar month")
    parser.add_argument("--out", type=Path, help="Output CSV path", default=Path(__file__).parent.parent.parent / "planit_renewables.csv")
    args = parser.parse_args()

    if args.last_complete_month:
        rows = fetch_major_renewables_last_complete_month()
    elif args.months is not None:
        rows = fetch_all_major_renewables_last_n_months(args.months)
    else:
        years = args.years if args.years is not None else 2
        rows = fetch_all_major_renewables_last_n_years(years)

    save_csv(args.out, rows)
    print(f"Saved {len(rows)} PlanIt renewables rows to {args.out}")

