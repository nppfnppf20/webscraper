from __future__ import annotations

from typing import Optional, Dict, List
from .session import make_session


BASE_URL = "https://westlindsey-publicportal.statmap.co.uk/horizoNext/api/publicportal"


def fetch_application(application_id: int) -> Optional[Dict]:
    session = make_session()
    url = f"{BASE_URL}/planningApplications/{application_id}"
    resp = session.get(url, timeout=20)
    if resp.status_code == 200:
        return resp.json()
    return None


def normalize_application(data: Dict) -> Dict[str, str]:
    return {
        "id": str(data.get("id", "")),
        "reference": data.get("name", ""),
        "location": (data.get("location", "") or "").replace("\n", ", "),
        "ward": data.get("ward", ""),
        "parish": data.get("parish", ""),
        "decision": data.get("decision", ""),
        "receivedDate": data.get("receivedDate", ""),
        "validDate": data.get("validDate", ""),
        "decisionDate": data.get("decisionDate", ""),
        "committeeDate": data.get("committeeDate", ""),
        "uprn": str(data.get("uprn", "")),
    }


def fetch_consultations(application_id: int) -> Optional[Dict]:
    session = make_session()
    url = f"{BASE_URL}/consultations/{application_id}"
    resp = session.get(url, timeout=20)
    if resp.status_code == 200:
        return resp.json()
    return None


def normalize_consultation(comment: Dict) -> Dict[str, str]:
    consultee_info = comment.get("consulteeId_relatedRecord", {}) or {}
    return {
        "id": str(comment.get("id", "")),
        "applicationId": str(comment.get("paId", "")),
        "createdTime": comment.get("createdTime", ""),
        "lastModifiedTime": comment.get("lastModifiedTime", ""),
        "opinion": comment.get("opinion", ""),
        "responsePublished": str(comment.get("responsePublished", "")),
        "responseDetailsToPublish": comment.get("responseDetailsToPublish", ""),
        "consulteeName": consultee_info.get("name", ""),
        "consulteeEmail": consultee_info.get("email_1", ""),
        "consulteeAddress": (consultee_info.get("address", "") or "").replace("\n", ", "),
    }

