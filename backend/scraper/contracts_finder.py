from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

from .session import make_session


class ContractsFinderAPIError(Exception):
    """Exception raised when Contracts Finder API returns an error"""
    pass


class ContractsFinderRateLimit(Exception):
    """Exception raised when Contracts Finder API rate limit is exceeded"""
    def __init__(self, retry_after_seconds: int = 60):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"Rate limit exceeded. Retry after {retry_after_seconds} seconds.")


def fetch_notices_from_contracts_finder(
    published_from: Optional[datetime] = None,
    published_to: Optional[datetime] = None,
    statuses: Optional[List[str]] = None,
    keyword: Optional[str] = None,
    max_results: int = 1000
) -> List[Dict]:
    """
    Fetch contract notices from the UK Contracts Finder API.

    Args:
        published_from: Start date for published notices (default: 7 days ago)
        published_to: End date for published notices (default: now)
        statuses: List of statuses to filter by (e.g., ["Open", "Closed", "Awarded"])
        keyword: Optional keyword to search for
        max_results: Maximum number of results to return

    Returns:
        List of contract notices
    """

    base_url = "https://www.contractsfinder.service.gov.uk/api/rest/2/search_notices/json"

    # Default to last 7 days if no dates provided
    if published_from is None:
        published_from = datetime.now() - timedelta(days=7)
    if published_to is None:
        published_to = datetime.now()

    # Build search criteria
    search_criteria = {
        "publishedFrom": published_from.strftime("%Y-%m-%dT%H:%M:%S"),
        "publishedTo": published_to.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    if statuses:
        search_criteria["statuses"] = statuses

    if keyword:
        search_criteria["keyword"] = keyword

    # Build request body
    request_body = {
        "searchCriteria": search_criteria,
        "size": max_results
    }

    session = make_session()

    print(f"[Contracts Finder] Searching for notices from {published_from.strftime('%Y-%m-%d')} to {published_to.strftime('%Y-%m-%d')}")

    try:
        response = session.post(
            base_url,
            json=request_body,
            timeout=60,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "60"))
            print(f"[Contracts Finder] Rate limited! Need to wait {retry_after}s")
            raise ContractsFinderRateLimit(retry_after)

        # Handle 403 (also used for rate limiting by this API)
        if response.status_code == 403:
            print(f"[Contracts Finder] Access forbidden (possibly rate limited)")
            raise ContractsFinderRateLimit(60)

        # Handle other errors
        if response.status_code != 200:
            error_msg = f"API returned status {response.status_code}: {response.text[:500]}"
            print(f"[Contracts Finder] {error_msg}")
            raise ContractsFinderAPIError(error_msg)

        data = response.json()

        # Extract results
        hit_count = data.get('hitCount', 0)
        notice_list = data.get('noticeList', [])

        print(f"[Contracts Finder] Found {hit_count} total notices, retrieved {len(notice_list)}")

        return notice_list

    except requests.exceptions.RequestException as e:
        print(f"[Contracts Finder] Network error: {e}")
        raise ContractsFinderAPIError(f"Network error: {e}")


def normalize_contracts_finder_notice(notice_hit: Dict) -> Dict:
    """
    Normalize a Contracts Finder notice into our database schema.

    Args:
        notice_hit: A single notice hit from the API response

    Returns:
        Normalized dict matching our contracts_finder table schema
    """
    # The API returns notices wrapped in a "item" key with a score
    notice = notice_hit.get('item', notice_hit)

    # Extract basic fields
    result = {
        'notice_id': notice.get('id', ''),
        'title': notice.get('title', ''),
        'description': notice.get('description', ''),
        'status': notice.get('noticeStatus', ''),
        'notice_type': notice.get('noticeType', ''),
        'organisation': notice.get('organisationName', ''),
    }

    # Extract dates
    published_date = notice.get('publishedDate', '')
    if published_date:
        result['published_date'] = published_date

    closing_date = notice.get('deadlineDate', '') or notice.get('closingDate', '')
    if closing_date:
        result['closing_date'] = closing_date

    # Extract value range
    value_low = notice.get('valueLow', notice.get('minValue', None))
    value_high = notice.get('valueHigh', notice.get('maxValue', None))

    if value_low is not None:
        try:
            result['value_low'] = float(value_low)
        except (ValueError, TypeError):
            pass

    if value_high is not None:
        try:
            result['value_high'] = float(value_high)
        except (ValueError, TypeError):
            pass

    # Extract location info
    result['region'] = notice.get('region', '')
    result['postcode'] = notice.get('postcode', '')

    # Extract CPV codes (API returns as string, sometimes with extended codes)
    cpv_codes = notice.get('cpvCodes', '')
    cpv_extended = notice.get('cpvCodesExtended', '')
    if cpv_codes and cpv_extended:
        result['cpv_codes'] = f"{cpv_codes} {cpv_extended}".strip()
    else:
        result['cpv_codes'] = str(cpv_codes) if cpv_codes else ''

    # Extract SME/VCO suitability flags
    result['suitable_for_sme'] = notice.get('isSuitableForSme', False)
    result['suitable_for_vco'] = notice.get('isSuitableForVco', False)

    # Build URL to notice
    notice_id = notice.get('id', '')
    if notice_id:
        result['url'] = f"https://www.contractsfinder.service.gov.uk/Notice/{notice_id}"
    else:
        result['url'] = ''

    # Add scrape timestamp
    result['last_scraped'] = datetime.now().isoformat()

    return result
