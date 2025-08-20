from __future__ import annotations

import time
from typing import List, Dict
from urllib.parse import urljoin

from .session import make_session


SCRAPER_ID = "rtpi_events"
BASE_URL = "https://www.rtpi.org.uk"
API_SEARCH_URL = f"{BASE_URL}/umbraco/api/events/search"
PAGE_SIZE = 100


def normalize_event(event_data: Dict) -> Dict[str, str]:
    def join_names(items: list[dict] | None) -> str:
        if not items:
            return ""
        return ", ".join([i.get("Name", "") for i in items if i.get("Name")])

    url = urljoin(BASE_URL, event_data.get("Url", ""))
    price = "Free" if event_data.get("FreeEvent") else (event_data.get("FromPrice") or "")
    return {
        "id": url,
        "title": event_data.get("Name", ""),
        "date": event_data.get("Date", ""),
        "region": join_names(event_data.get("Region")),
        "category": join_names(event_data.get("ContentType")),
        "price": price,
        "url": url,
    }


def fetch_rtpi_events_api() -> List[Dict[str, str]]:
    session = make_session()
    all_events: list[dict] = []
    page = 1
    while True:
        params = {"pageSize": PAGE_SIZE, "page": page}
        resp = session.get(API_SEARCH_URL, params=params, timeout=20)
        if resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        all_events.extend(data)
        page += 1
        time.sleep(0.75)
    return [normalize_event(e) for e in all_events]


def run() -> List[Dict[str, str]]:
    return fetch_rtpi_events_api()

