from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Dict


def save_csv(path: Path | str, rows: Iterable[Dict[str, str]]) -> None:
    path = Path(path)
    rows = list(rows)
    if not rows:
        # Write empty file with no headers if needed
        path.write_text("")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    # Use union of all keys to handle optional fields
    seen_keys = []
    seen_set = set()
    # Preserve order of first appearance across rows
    for r in rows:
        for k in r.keys():
            if k not in seen_set:
                seen_set.add(k)
                seen_keys.append(k)
    headers = seen_keys
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

