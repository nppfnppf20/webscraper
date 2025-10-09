from __future__ import annotations

import asyncio
import re
import time
from typing import List, Dict
from urllib.parse import urljoin

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


SCRAPER_ID = "rtpi_events"
BASE_URL = "https://www.rtpi.org.uk"
EVENTS_URL = f"{BASE_URL}/events"


async def extract_event_details(page, event_url: str) -> Dict[str, str]:
    """Extract detailed information from an individual event page using Playwright."""
    try:
        print(f"  Loading event page: {event_url}")

        # Navigate to event page
        response = await page.goto(event_url, wait_until='networkidle', timeout=30000)
        if response.status != 200:
            print(f"  Failed to load event page: {response.status}")
            return {}

        # Wait for content to load
        await page.wait_for_timeout(2000)

        # Get page content
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        main = soup.find('main')
        if not main:
            return {}

        # Extract title
        title_elem = main.find(['h1', 'h2'])
        title = title_elem.get_text(strip=True) if title_elem else ""

        page_text = main.get_text()

        # Extract price information
        price_patterns = [
            r'from\s*£(\d+[,\d]*(?:\.\d{2})?)',
            r'£(\d+[,\d]*(?:\.\d{2})?)',
        ]

        price = ""
        for pattern in price_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                price = f"£{match.group(1)}"
                break

        if not price and 'free' in page_text.lower():
            price = "Free"

        # Extract region/location
        region = ""
        if 'national' in page_text.lower():
            region = "National"
        elif 'online' in page_text.lower():
            region = "Online"
        elif 'virtual' in page_text.lower():
            region = "Virtual"

        # Extract category - look for event type keywords
        category = ""
        text_lower = page_text.lower()
        if 'masterclass' in text_lower:
            category = "CPD Masterclass"
        elif 'workshop' in text_lower:
            category = "Workshop"
        elif 'conference' in text_lower:
            category = "Conference"
        elif 'seminar' in text_lower:
            category = "Seminar"
        elif 'training' in text_lower:
            category = "Training"
        elif 'event' in text_lower:
            category = "Event"

        # Extract date information
        date_patterns = [
            r'\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b',
            r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',
            r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b'
        ]

        date = ""
        for pattern in date_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                date = match.group(1)
                break

        if not date:
            date = "See event page for dates"

        return {
            "id": event_url,
            "title": title,
            "date": date,
            "region": region,
            "category": category,
            "price": price,
            "url": event_url,
        }

    except Exception as e:
        print(f"  Error extracting details from {event_url}: {e}")
        return {}


async def fetch_rtpi_events() -> List[Dict[str, str]]:
    """Scrape RTPI events using Playwright to handle JavaScript-rendered content."""

    async with async_playwright() as p:
        browser = None
        try:
            print(f"Loading RTPI events page: {EVENTS_URL}")

            # Launch browser with realistic settings to avoid detection
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = await context.new_page()

            # Set extra headers
            await page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })

            # Load the main events page
            response = await page.goto(EVENTS_URL, wait_until='networkidle', timeout=30000)
            if response.status != 200:
                print(f"Failed to load page: {response.status}")
                return []

            print("Page loaded successfully, waiting for Vue content to render...")

            # Wait for the Vue component to load and render content
            try:
                await page.wait_for_selector('[data-vue-module="ContentListing"]', timeout=10000)
            except Exception as e:
                print(f"Warning: Could not find Vue content listing: {e}")

            # Wait a bit more for content to populate
            await page.wait_for_timeout(5000)

            # Try to find if there's a "load more" or pagination mechanism
            try:
                load_more_buttons = await page.query_selector_all('button:has-text("Load"), button:has-text("More"), button:has-text("Show")')
                if load_more_buttons:
                    print(f"Found {len(load_more_buttons)} potential load more buttons, clicking them...")
                    for button in load_more_buttons:
                        try:
                            await button.click()
                            await page.wait_for_timeout(2000)
                        except Exception as e:
                            print(f"Could not click button: {e}")
            except Exception as e:
                print(f"No load more buttons found: {e}")

            # Get the page source after Vue has rendered
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Find all event links
            event_links = []
            links = soup.find_all('a', href=True)

            print(f"Found {len(links)} total links on page")

            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)

                # Look for links that point to individual events
                if (href.startswith('/events/') and
                    href != '/events/' and  # Not the main events page
                    len(href.split('/')) > 3 and  # Has a specific event slug
                    len(text) > 10):  # Has substantial link text

                    full_url = urljoin(BASE_URL, href)
                    event_links.append((full_url, text))

            # Remove duplicates
            unique_events = {}
            for url, text in event_links:
                if url not in unique_events:
                    unique_events[url] = text

            print(f"Found {len(unique_events)} unique event links")
            for i, (url, text) in enumerate(list(unique_events.items())[:10]):
                print(f"  {i+1}: {text[:80]} -> {url}")

            # Extract details from each event
            events = []
            for i, (event_url, event_title) in enumerate(unique_events.items()):
                print(f"\nProcessing event {i+1}/{len(unique_events)}: {event_title[:50]}...")

                event_details = await extract_event_details(page, event_url)
                if event_details and event_details.get('title'):
                    events.append(event_details)

                # Be polite to the server
                if i < len(unique_events) - 1:
                    await asyncio.sleep(2)

            print(f"\nSuccessfully extracted {len(events)} events")
            return events

        except Exception as e:
            print(f"Error fetching RTPI events: {e}")
            import traceback
            traceback.print_exc()
            return []

        finally:
            if browser:
                await browser.close()


def run() -> List[Dict[str, str]]:
    return asyncio.run(fetch_rtpi_events())

