from __future__ import annotations

from pathlib import Path
from .planit_renewables import fetch_all_major_renewables_last_n_years
from .io import save_csv


if __name__ == "__main__":
    rows = fetch_all_major_renewables_last_n_years(3)
    out = Path(__file__).parent.parent.parent / "planit_renewables.csv"
    save_csv(out, rows)
    print(f"Saved {len(rows)} PlanIt renewables rows to {out}")

