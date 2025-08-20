from __future__ import annotations

from pathlib import Path
from .peeringdb import fetch_ix_gb, normalize_ix
from .io import save_csv


if __name__ == "__main__":
    rows = [normalize_ix(ix) for ix in fetch_ix_gb()]
    out = Path(__file__).parent.parent.parent / "peeringdb_ix_gb.csv"
    save_csv(out, rows)
    print(f"Saved {len(rows)} IX rows to {out}")

