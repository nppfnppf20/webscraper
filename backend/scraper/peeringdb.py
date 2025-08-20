from __future__ import annotations

from typing import List, Dict
from .session import make_session


BASE_API_URL = "https://www.peeringdb.com/api"


def fetch_ix_gb() -> List[Dict]:
    session = make_session()
    url = f"{BASE_API_URL}/ix"
    params = {"country__in": "GB"}
    resp = session.get(url, params=params, timeout=20)
    if resp.status_code == 200:
        return resp.json().get("data", [])
    return []


def normalize_ix(data: Dict) -> Dict[str, str]:
    return {
        "id": str(data.get("id", "")),
        "name": data.get("name", ""),
        "country": data.get("country", ""),
        "city": data.get("city", ""),
        "networks": str(data.get("net_count", "")),
    }


def fetch_facilities_gb() -> List[Dict]:
    session = make_session()
    url = f"{BASE_API_URL}/fac"
    params = {"country__in": "GB"}
    resp = session.get(url, params=params, timeout=20)
    if resp.status_code == 200:
        return resp.json().get("data", [])
    return []


def normalize_facility(data: Dict) -> Dict[str, str]:
    return {
        "id": str(data.get("id", "")),
        "name": data.get("name", ""),
        "address": data.get("address1", ""),
        "city": data.get("city", ""),
        "country": data.get("country", ""),
        "postal_code": data.get("zipcode", ""),
    }

