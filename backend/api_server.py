from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict

import sys
import time
import subprocess
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


# Project root (data files are saved at repo root)
DATA_DIR = Path(__file__).parent.parent


def read_csv_to_list_of_dicts(filepath: Path) -> List[Dict[str, str]]:
    if not filepath.exists():
        return []
    rows: List[Dict[str, str]] = []
    with filepath.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: (v or "") for k, v in row.items()})
    return rows


@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok"})


@app.route("/api/rtpi/events")
def get_rtpi_events():
    filepath = DATA_DIR / "rtpi_events.csv"
    return jsonify(read_csv_to_list_of_dicts(filepath))


@app.route("/api/west-lindsey/application")
def get_west_lindsey_application():
    filepath = DATA_DIR / "west_lindsey_planning.csv"
    data = read_csv_to_list_of_dicts(filepath)
    return jsonify(data[0] if data else {})


@app.route("/api/west-lindsey/consultations")
def get_west_lindsey_consultations():
    filepath = DATA_DIR / "west_lindsey_consultations.csv"
    return jsonify(read_csv_to_list_of_dicts(filepath))


@app.route("/api/peeringdb/ix/gb")
def get_peeringdb_ix_gb():
    filepath = DATA_DIR / "peeringdb_ix_gb.csv"
    return jsonify(read_csv_to_list_of_dicts(filepath))


@app.route("/api/peeringdb/fac/gb")
def get_peeringdb_fac_gb():
    filepath = DATA_DIR / "peeringdb_fac_gb.csv"
    return jsonify(read_csv_to_list_of_dicts(filepath))


@app.route("/api/planit/datacentres")
def get_planit_datacentres():
    filepath = DATA_DIR / "planit_datacentres.csv"
    return jsonify(read_csv_to_list_of_dicts(filepath))

@app.route("/api/planit/renewables")
def get_planit_renewables():
    filepath = DATA_DIR / "planit_renewables.csv"
    return jsonify(read_csv_to_list_of_dicts(filepath))


# --- Refresh (re-scrape) endpoints ---
_locks: dict[str, threading.Lock] = {
    k: threading.Lock() for k in [
        "rtpi", "west-lindsey", "peeringdb-ix", "peeringdb-fac", "planit-dc", "planit-renew"
    ]
}

def _run_module(module_name: str) -> tuple[int, str, str]:
    """Run a python module in the current venv, capture return code, stdout+stderr combined, and elapsed seconds (as string)."""
    start = time.time()
    proc = subprocess.run([sys.executable, "-m", module_name], capture_output=True, text=True)
    elapsed = f"{time.time() - start:.2f}"
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output, elapsed

def _count_rows(csv_filename: str) -> int:
    filepath = DATA_DIR / csv_filename
    try:
        return len(read_csv_to_list_of_dicts(filepath))
    except Exception:
        return 0

def _refresh(lock_key: str, module: str, csv_filename: str):
    lock = _locks[lock_key]
    if not lock.acquire(blocking=False):
        return jsonify({"ok": False, "error": "already_running"}), 409
    try:
        code, out, elapsed = _run_module(module)
        if code != 0:
            return jsonify({"ok": False, "error": "runner_failed", "elapsed_s": elapsed, "log": out[-2000:]}), 500
        rows = _count_rows(csv_filename)
        return jsonify({"ok": True, "csv": csv_filename, "updated": rows, "elapsed_s": elapsed})
    finally:
        lock.release()


@app.post("/api/refresh/rtpi")
def refresh_rtpi():
    return _refresh("rtpi", "backend.scraper.run_rtpi_events", "rtpi_events.csv")


@app.post("/api/refresh/west-lindsey")
def refresh_west_lindsey():
    # Runs both application summary and consultations
    return _refresh("west-lindsey", "backend.scraper.run_west_lindsey", "west_lindsey_consultations.csv")


@app.post("/api/refresh/peeringdb-ix")
def refresh_peeringdb_ix():
    return _refresh("peeringdb-ix", "backend.scraper.run_peeringdb", "peeringdb_ix_gb.csv")


@app.post("/api/refresh/peeringdb-fac")
def refresh_peeringdb_fac():
    return _refresh("peeringdb-fac", "backend.scraper.run_peeringdb_fac", "peeringdb_fac_gb.csv")


@app.post("/api/refresh/planit-dc")
def refresh_planit_dc():
    return _refresh("planit-dc", "backend.scraper.run_planit_datacentres", "planit_datacentres.csv")


@app.post("/api/refresh/planit-renew")
def refresh_planit_renew():
    return _refresh("planit-renew", "backend.scraper.run_planit_renewables", "planit_renewables.csv")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

