from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict

from flask import Flask, jsonify
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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

