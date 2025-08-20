from __future__ import annotations

from pathlib import Path
from .planit_datacentres import fetch_all_major_datacentres_last_n_years
from .io import save_csv


if __name__ == "__main__":
    rows = fetch_all_major_datacentres_last_n_years(5)
    out = Path(__file__).parent.parent.parent / "planit_datacentres.csv"
    save_csv(out, rows)
    print(f"Saved {len(rows)} PlanIt data centre rows to {out}")

