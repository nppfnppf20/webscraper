from __future__ import annotations

import sys
import time
import subprocess
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import db

app = Flask(__name__)
CORS(app)

@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok"})

@app.route("/api/rtpi/events")
def get_rtpi_events():
    return jsonify(db.get_rtpi_events())

@app.route("/api/west-lindsey/application")
def get_west_lindsey_application():
    return jsonify(db.get_west_lindsey_application())

@app.route("/api/west-lindsey/consultations")
def get_west_lindsey_consultations():
    return jsonify(db.get_west_lindsey_consultations())

@app.route("/api/peeringdb/ix/gb")
def get_peeringdb_ix_gb():
    return jsonify(db.get_peeringdb_ix_gb())

@app.route("/api/peeringdb/fac/gb")
def get_peeringdb_fac_gb():
    return jsonify(db.get_peeringdb_fac_gb())

@app.route("/api/planit/datacentres")
def get_planit_datacentres():
    return jsonify(db.get_planit_datacentres())

@app.route("/api/planit/renewables")
def get_planit_renewables():
    return jsonify(db.get_planit_renewables())

@app.route("/api/planit/renewables-test2")
def get_planit_renewables_test2():
    return jsonify(db.get_planit_renewables_test2())

# --- Refresh (re-scrape) endpoints ---
_locks: dict[str, threading.Lock] = {
    k: threading.Lock() for k in [
        "rtpi", "west-lindsey", "peeringdb-ix", "peeringdb-fac", "planit-dc", "planit-renew", "planit-test2"
    ]
}

def _run_module(module_name: str) -> tuple[int, str, str]:
    """Run a python module in the current venv, capture return code, stdout+stderr combined, and elapsed seconds (as string)."""
    print(f"[Flask] Starting scraper: {module_name}", flush=True)
    start = time.time()
    # Change to parent directory to run modules with 60 second timeout
    try:
        import os
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        proc = subprocess.run([sys.executable, "-m", module_name], capture_output=True, text=True, cwd=parent_dir, timeout=45)
        elapsed = f"{time.time() - start:.2f}"
        output = (proc.stdout or "") + (proc.stderr or "")
        print(f"[Flask] Scraper {module_name} completed in {elapsed}s with return code {proc.returncode}", flush=True)
        if proc.returncode != 0:
            print(f"[Flask] Error output: {output[-500:]}", flush=True)  # Show last 500 chars of error
        return proc.returncode, output, elapsed
    except subprocess.TimeoutExpired:
        elapsed = f"{time.time() - start:.2f}"
        print(f"[Flask] Scraper {module_name} TIMED OUT after {elapsed}s", flush=True)
        return 124, f"Process timed out after 45 seconds", elapsed

def _refresh(lock_key: str, module: str, table_name: str):
    """Refresh data by running scraper module"""
    lock = _locks[lock_key]
    if not lock.acquire(blocking=False):
        return jsonify({"ok": False, "error": "already_running"}), 409
    try:
        code, out, elapsed = _run_module(module)
        if code != 0:
            return jsonify({"ok": False, "error": "runner_failed", "elapsed_s": elapsed, "log": out[-2000:]}), 500

        # Count rows after refresh - this would need to be updated based on actual table
        row_count = 0  # You can implement this based on your needs
        return jsonify({"ok": True, "table": table_name, "updated": row_count, "elapsed_s": elapsed})
    finally:
        lock.release()

@app.post("/api/refresh/rtpi")
def refresh_rtpi():
    return _refresh("rtpi", "backend.scraper.run_rtpi_events", "rtpi_events")

@app.post("/api/refresh/west-lindsey")
def refresh_west_lindsey():
    return _refresh("west-lindsey", "backend.scraper.run_west_lindsey", "west_lindsey_consultations")

@app.post("/api/refresh/peeringdb-ix")
def refresh_peeringdb_ix():
    return _refresh("peeringdb-ix", "backend.scraper.run_peeringdb", "peeringdb_ix_gb")

@app.post("/api/refresh/peeringdb-fac")
def refresh_peeringdb_fac():
    return _refresh("peeringdb-fac", "backend.scraper.run_peeringdb_fac", "peeringdb_fac_gb")

@app.post("/api/refresh/planit-dc")
def refresh_planit_dc():
    return _refresh("planit-dc", "backend.scraper.run_planit_api_datacentres", "planit_datacentres")

@app.post("/api/refresh/planit-renew")
def refresh_planit_renew():
    return _refresh("planit-renew", "backend.scraper.run_planit_renewables_daily", "planit_renewables")

@app.post("/api/refresh/planit-test2")
def refresh_planit_test2():
    return _refresh("planit-test2", "backend.scraper.run_planit_api_test", "planit_renewables")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)