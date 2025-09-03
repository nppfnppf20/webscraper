from __future__ import annotations

import json
import re
import time
from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlencode

from .session import make_session
import requests


PLANIT_BASE = "https://www.planit.org.uk"
# Narrow to Solar/BESS only and exclude domestic/roof-scale installs
SEARCH_TERMS = (
    '"solar" or "solar farm" or photovoltaic or "battery energy storage" or bess -roof -domestic -householder'
)
PAGE_SIZE = 300
_POSTCODE_CACHE: Dict[str, Tuple[float, float]] = {}


def month_range_backwards(months: int) -> List[Tuple[date, date]]:
    today = date.today()
    year = today.year
    month = today.month
    ranges: List[Tuple[date, date]] = []
    for i in range(months):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        start = date(y, m, 1)
        nm = m + 1
        ny = y
        if nm == 13:
            nm = 1
            ny += 1
        end = date(ny, nm, 1) - timedelta(days=1)
        ranges.append((start, end))
    return ranges


def fetch_page(session, start: date, end: date, page: int) -> Dict:
    # Cap end date to today to avoid future-date rejections
    today = date.today()
    if end > today:
        end = today
    params = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "pg_sz": str(PAGE_SIZE),
        "page": str(page),
        "compress": "on",
        "search": SEARCH_TERMS,
    }
    url = f"{PLANIT_BASE}/api/applics/json?{urlencode(params)}"
    print(f"[PlanIt] GET {start}..{end} page={page}", flush=True)
    resp = session.get(url, timeout=30)
    if resp.status_code == 429:
        retry_after = int(resp.headers.get("Retry-After", "2"))
        print(f"[PlanIt] 429 rate limited. Sleeping {retry_after}s", flush=True)
        time.sleep(retry_after)
        resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _postcode_to_latlng(postcode: str) -> Optional[Tuple[float, float]]:
    pc = postcode.replace(" ", "").upper()
    if not pc:
        return None
    if pc in _POSTCODE_CACHE:
        return _POSTCODE_CACHE[pc]
    try:
        url = f"https://api.postcodes.io/postcodes/{pc}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result")
            if isinstance(result, dict):
                lat = _to_float(result.get("latitude"))
                lng = _to_float(result.get("longitude"))
                if lat is not None and lng is not None:
                    _POSTCODE_CACHE[pc] = (lat, lng)
                    return _POSTCODE_CACHE[pc]
    except Exception:
        return None
    return None


def _parse_float_from_text(value: str) -> Optional[float]:
    try:
        # Replace common thousand separators and attempt direct parse
        cleaned = value.replace(",", "").strip()
        return float(cleaned)
    except Exception:
        # Fallback: find first number like 12 or 12.34 in the text
        match = re.search(r"(\d+(?:\.\d+)?)", value)
        if match:
            try:
                return float(match.group(1))
            except Exception:
                return None
    return None


def _extract_site_area_ha(other_fields: Dict) -> Optional[float]:
    if not isinstance(other_fields, dict):
        return None
    for key, raw in other_fields.items():
        lk = str(key).lower()
        if ("area" in lk or "site" in lk) and ("ha" in lk or "hectare" in lk):
            text = str(raw)
            val = _parse_float_from_text(text)
            if val is not None and val >= 0:
                return val
    # Secondary heuristic: values that explicitly mention "ha" in value text
    for key, raw in other_fields.items():
        text = str(raw).lower()
        if "ha" in text or "hectare" in text:
            val = _parse_float_from_text(text)
            if val is not None and val >= 0:
                return val
    return None


def _classify_status(decision: str, app_state: str) -> str:
    d = (decision or "").strip().lower()
    s = (app_state or "").strip().lower()
    if any(w in d for w in ["granted", "approved", "permit", "consented", "allowed"]):
        return "Approved"
    if any(w in d for w in ["refused", "dismissed", "rejected", "declined"]):
        return "Refused"
    # Pending/in-progress indicators
    if any(w in s for w in ["pending", "registered", "consideration", "awaiting", "valid", "in progress"]):
        return "Pending"
    # If no clear signal, default to Pending until decision present
    return "Pending"


def _to_float(value: object) -> Optional[float]:
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value).strip()
        if not s:
            return None
        s = s.replace(",", "")
        return float(s)
    except Exception:
        return None


def normalize(record: Dict, geometry: Optional[Dict] = None) -> Dict[str, str]:
    props = record
    other = props.get("other_fields") or {}
    desc = str(props.get("description", ""))
    fallback_title = " ".join((desc.splitlines() or [""])[0].split()).strip()
    if len(fallback_title) > 140:
        fallback_title = fallback_title[:137] + "..."
    decision_val = str(props.get("decision") or other.get("decision", ""))
    app_state_val = str(props.get("app_state", props.get("status", "")))
    site_area_ha = _extract_site_area_ha(other)
    # Lat/lng from props or geometry fallback
    lat_val = props.get("lat", props.get("latitude", ""))
    lng_val = props.get("lng", props.get("longitude", ""))
    lat_f = _to_float(lat_val)
    lng_f = _to_float(lng_val)
    if (lat_f is None or lng_f is None) and isinstance(geometry, dict):
        gtype = geometry.get("type")
        coords = geometry.get("coordinates")
        if gtype == "Point" and isinstance(coords, (list, tuple)) and len(coords) >= 2:
            # GeoJSON: [lng, lat]
            try:
                lng_f = _to_float(coords[0])
                lat_f = _to_float(coords[1])
            except Exception:
                pass
    # Postcode geocode fallback via postcodes.io (only if still missing)
    if (lat_f is None or lng_f is None):
        pc = str(props.get("postcode") or "").strip()
        if pc:
            latlng = _postcode_to_latlng(pc)
            if latlng is not None:
                lat_f, lng_f = latlng[0], latlng[1]
    row = {
        "id": str(props.get("name", "")),
        "authority": str(props.get("area_name", props.get("authority", props.get("auth", "")))),
        "title": str(props.get("title") or fallback_title),
        "description": desc,
        "app_type": str(props.get("app_type", "")),
        "application_type": str(props.get("application_type", "")),
        "development_type": str(props.get("development_type", "")),
        "app_size": str(props.get("app_size", "")),
        "app_state": app_state_val,
        "decision": decision_val,
        "start_date": str(props.get("start_date", "")),
        "decided_date": str(props.get("decided_date", "")),
        "last_changed": str(props.get("last_changed", "")),
        "address": str(props.get("address", "")),
        "postcode": str(props.get("postcode", "")),
        "lat": "" if lat_f is None else f"{lat_f}",
        "lng": "" if lng_f is None else f"{lng_f}",
        "link": str(props.get("link", "")),
    }
    if site_area_ha is not None:
        row["site_area_ha"] = f"{site_area_ha}"
    row["status_class"] = _classify_status(decision_val, app_state_val)
    if isinstance(geometry, dict):
        gtype = geometry.get("type")
        if gtype:
            row["geometry_type"] = str(gtype)
        try:
            row["geometry_geojson"] = json.dumps(geometry, separators=(",", ":"))
        except Exception:
            pass
    return row


def fetch_all_major_renewables_last_n_years(years: int = 2) -> List[Dict[str, str]]:
    session = make_session()
    ranges = month_range_backwards(years * 12)
    seen: Dict[str, Dict[str, str]] = {}
    for start, end in ranges:
        page = 1
        while True:
            data = fetch_page(session, start, end, page)
            records = data.get("records") or data.get("features") or []
            if isinstance(records, dict) and "features" in records:
                records = records["features"]
            if not records:
                print(f"[PlanIt] No records for {start}..{end} page {page}", flush=True)
                break
            for rec in records:
                props = rec["properties"] if isinstance(rec, dict) and "properties" in rec else rec
                geom = rec.get("geometry") if isinstance(rec, dict) else None
                row = normalize(props, geometry=geom)
                # size filter: include only Large / Very Large when present
                size_val = (row.get("app_size") or "").strip().lower()
                if size_val and size_val not in {"large", "very large"}:
                    continue
                # type filter: Full/Outline only
                app_type_val = (row.get("app_type") or "").strip().lower()
                if app_type_val not in {"full", "outline"}:
                    continue
                # site area threshold if available
                try:
                    sa = float(row.get("site_area_ha")) if row.get("site_area_ha") is not None else None
                except Exception:
                    sa = None
                if sa is not None and sa < 20.0:
                    continue
                rid = row.get("id")
                if rid:
                    seen[rid] = row
            to = data.get("to")
            total = data.get("total")
            if to is not None and total is not None and to >= total:
                break
            if len(records) < PAGE_SIZE:
                break
            page += 1
            time.sleep(0.5)
        print(f"[PlanIt] Completed {start}..{end}. Cumulative distinct records: {len(seen)}", flush=True)
        time.sleep(0.5)
    return list(seen.values())


def fetch_all_major_renewables_last_n_months(months: int = 1) -> List[Dict[str, str]]:
    session = make_session()
    ranges = month_range_backwards(months)
    seen: Dict[str, Dict[str, str]] = {}
    for start, end in ranges:
        page = 1
        while True:
            data = fetch_page(session, start, end, page)
            records = data.get("records") or data.get("features") or []
            if isinstance(records, dict) and "features" in records:
                records = records["features"]
            if not records:
                print(f"[PlanIt] No records for {start}..{end} page {page}", flush=True)
                break
            for rec in records:
                props = rec["properties"] if isinstance(rec, dict) and "properties" in rec else rec
                geom = rec.get("geometry") if isinstance(rec, dict) else None
                row = normalize(props, geometry=geom)
                size_val = (row.get("app_size") or "").strip().lower()
                if size_val and size_val not in {"large", "very large"}:
                    continue
                app_type_val = (row.get("app_type") or "").strip().lower()
                if app_type_val not in {"full", "outline"}:
                    continue
                try:
                    sa = float(row.get("site_area_ha")) if row.get("site_area_ha") is not None else None
                except Exception:
                    sa = None
                if sa is not None and sa < 20.0:
                    continue
                rid = row.get("id")
                if rid:
                    seen[rid] = row
            to = data.get("to")
            total = data.get("total")
            if to is not None and total is not None and to >= total:
                break
            if len(records) < PAGE_SIZE:
                break
            page += 1
            time.sleep(0.5)
        print(f"[PlanIt] Completed {start}..{end}. Cumulative distinct records: {len(seen)}", flush=True)
        time.sleep(0.5)
    return list(seen.values())


def _last_complete_month_range() -> Tuple[date, date]:
    today = date.today()
    year = today.year
    month = today.month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    start = date(prev_year, prev_month, 1)
    end = date(year, month, 1) - timedelta(days=1)
    return start, end


def fetch_major_renewables_last_complete_month() -> List[Dict[str, str]]:
    session = make_session()
    start, end = _last_complete_month_range()
    seen: Dict[str, Dict[str, str]] = {}
    page = 1
    while True:
        data = fetch_page(session, start, end, page)
        records = data.get("records") or data.get("features") or []
        if isinstance(records, dict) and "features" in records:
            records = records["features"]
        if not records:
            print(f"[PlanIt] No records for {start}..{end} page {page}", flush=True)
            break
        for rec in records:
            props = rec["properties"] if isinstance(rec, dict) and "properties" in rec else rec
            geom = rec.get("geometry") if isinstance(rec, dict) else None
            row = normalize(props, geometry=geom)
            size_val = (row.get("app_size") or "").strip().lower()
            if size_val and size_val not in {"large", "very large"}:
                continue
            app_type_val = (row.get("app_type") or "").strip().lower()
            if app_type_val not in {"full", "outline"}:
                continue
            try:
                sa = float(row.get("site_area_ha")) if row.get("site_area_ha") is not None else None
            except Exception:
                sa = None
            if sa is not None and sa < 20.0:
                continue
            rid = row.get("id")
            if rid:
                seen[rid] = row
        to = data.get("to")
        total = data.get("total")
        if to is not None and total is not None and to >= total:
            break
        if len(records) < PAGE_SIZE:
            break
        page += 1
        time.sleep(0.5)
    print(f"[PlanIt] Completed last complete month {start}..{end}. Total distinct records: {len(seen)}", flush=True)
    return list(seen.values())

