from __future__ import annotations

import time
from datetime import date, timedelta
from typing import Dict, List, Tuple
from urllib.parse import urlencode

from .session import make_session


PLANIT_BASE = "https://www.planit.org.uk"
SEARCH_TERMS = (
    '"solar" or photovoltaic or pv or "battery energy storage" or bess or wind or turbine or '
    'hydrogen or "anaerobic digestion" or biomass'
)
PAGE_SIZE = 300


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
    params = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "pg_sz": str(PAGE_SIZE),
        "page": str(page),
        "compress": "on",
        "search": SEARCH_TERMS,
    }
    url = f"{PLANIT_BASE}/api/applics/json?{urlencode(params)}"
    resp = session.get(url, timeout=30)
    if resp.status_code == 429:
        retry_after = int(resp.headers.get("Retry-After", "2"))
        time.sleep(retry_after)
        resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def normalize(record: Dict) -> Dict[str, str]:
    props = record
    other = props.get("other_fields") or {}
    desc = str(props.get("description", ""))
    fallback_title = " ".join((desc.splitlines() or [""])[0].split()).strip()
    if len(fallback_title) > 140:
        fallback_title = fallback_title[:137] + "..."
    return {
        "id": str(props.get("name", "")),
        "authority": str(props.get("area_name", props.get("authority", props.get("auth", "")))),
        "title": str(props.get("title") or fallback_title),
        "description": desc,
        "app_type": str(props.get("app_type", "")),
        "application_type": str(props.get("application_type", "")),
        "development_type": str(props.get("development_type", "")),
        "app_size": str(props.get("app_size", "")),
        "app_state": str(props.get("app_state", props.get("status", ""))),
        "decision": str(props.get("decision") or other.get("decision", "")),
        "start_date": str(props.get("start_date", "")),
        "decided_date": str(props.get("decided_date", "")),
        "last_changed": str(props.get("last_changed", "")),
        "address": str(props.get("address", "")),
        "postcode": str(props.get("postcode", "")),
        "lat": str(props.get("lat", props.get("latitude", ""))),
        "lng": str(props.get("lng", props.get("longitude", ""))),
        "link": str(props.get("link", "")),
    }


def fetch_all_major_renewables_last_n_years(years: int = 3) -> List[Dict[str, str]]:
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
                break
            for rec in records:
                props = rec["properties"] if isinstance(rec, dict) and "properties" in rec else rec
                row = normalize(props)
                # size filter: include Medium/Large/Very Large when present
                size_val = (row.get("app_size") or "").strip().lower()
                if size_val and size_val not in {"medium", "large", "very large"}:
                    continue
                # type filter: Full/Outline only
                app_type_val = (row.get("app_type") or "").strip().lower()
                if app_type_val not in {"full", "outline"}:
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
        time.sleep(0.5)
    return list(seen.values())

