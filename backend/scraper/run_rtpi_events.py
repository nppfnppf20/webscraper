from __future__ import annotations

from pathlib import Path
from .rtpi_events import run
from .io import save_csv


if __name__ == "__main__":
    rows = run()
    out = Path(__file__).parent.parent.parent / "rtpi_events.csv"
    save_csv(out, rows)
    print(f"Saved {len(rows)} events to {out}")

