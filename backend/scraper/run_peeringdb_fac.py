from __future__ import annotations

from pathlib import Path
from .peeringdb import fetch_facilities_gb, normalize_facility
from .io import save_csv


if __name__ == "__main__":
    rows = [normalize_facility(f) for f in fetch_facilities_gb()]
    out = Path(__file__).parent.parent.parent / "peeringdb_fac_gb.csv"
    save_csv(out, rows)
    print(f"Saved {len(rows)} facility rows to {out}")

