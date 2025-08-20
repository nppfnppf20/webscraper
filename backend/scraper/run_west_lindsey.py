from __future__ import annotations

from pathlib import Path
from .west_lindsey import fetch_application, normalize_application, fetch_consultations, normalize_consultation
from .io import save_csv


APPLICATION_ID = 149857


if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent

    app_data = fetch_application(APPLICATION_ID)
    app_rows = [normalize_application(app_data)] if app_data else []
    save_csv(root / "west_lindsey_planning.csv", app_rows)
    print(f"Saved application summary to {root / 'west_lindsey_planning.csv'}")

    cons = fetch_consultations(APPLICATION_ID) or {}
    comments = cons.get("comments", []) if isinstance(cons, dict) else []
    cons_rows = [normalize_consultation(c) for c in comments]
    save_csv(root / "west_lindsey_consultations.csv", cons_rows)
    print(f"Saved {len(cons_rows)} consultation rows to {root / 'west_lindsey_consultations.csv'}")

