from __future__ import annotations

import re
import time
from typing import List, Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests_html import HTMLSession


SCRAPER_ID = "rtpi_events"
BASE_URL = "https://www.rtpi.org.uk"
EVENTS_URL = f"{BASE_URL}/events"


def extract_event_details(session, event_url: str) -> Dict[str, str]:
    """Extract detailed information from an individual event page using requests-html."""
    try:
        r = session.get(event_url)
        r.html.render(timeout=20)  # Render JavaScript
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(r.html.html, 'html.parser')
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
        print(f"Error extracting details from {event_url}: {e}")
        return {}


def fetch_rtpi_events() -> List[Dict[str, str]]:
    """Scrape RTPI events using requests-html to handle JavaScript-rendered content."""
    session = HTMLSession()
    
    try:
        print(f"Loading RTPI events page: {EVENTS_URL}")
        
        # Load the main events page
        r = session.get(EVENTS_URL)
        print("Rendering JavaScript content...")
        r.html.render(timeout=30)  # Render JavaScript with longer timeout
        
        # Get the page source after JavaScript execution
        soup = BeautifulSoup(r.html.html, 'html.parser')
        
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
        
        print(f"Found {len(unique_events)} unique event links:")
        for i, (url, text) in enumerate(list(unique_events.items())[:10]):
            print(f"  {i+1}: {text[:80]} -> {url}")
        
        # Extract details from each event
        events = []
        for i, (event_url, event_title) in enumerate(unique_events.items()):
            print(f"\nProcessing event {i+1}/{len(unique_events)}: {event_title[:50]}...")
            
            event_details = extract_event_details(session, event_url)
            if event_details and event_details.get('title'):
                events.append(event_details)
            
            # Be polite to the server
            if i < len(unique_events) - 1:
                time.sleep(2)
        
        print(f"\nSuccessfully extracted {len(events)} events")
        return events
        
    except Exception as e:
        print(f"Error fetching RTPI events: {e}")
        import traceback
        traceback.print_exc()
        return []
        
    finally:
        session.close()


def run() -> List[Dict[str, str]]:
    return fetch_rtpi_events()

