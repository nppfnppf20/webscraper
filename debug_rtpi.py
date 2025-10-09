#!/usr/bin/env python3
"""Debug script to investigate RTPI events page structure"""

import time
from requests_html import HTMLSession
from bs4 import BeautifulSoup

def debug_rtpi_page():
    session = HTMLSession()

    try:
        print("Loading RTPI events page...")
        url = "https://www.rtpi.org.uk/events"

        # Try with different user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        r = session.get(url, headers=headers)
        print(f"Initial response status: {r.status_code}")

        if r.status_code != 200:
            print(f"Failed to load page: {r.status_code}")
            return

        print("Page loaded, content length before render:", len(r.text))

        # Save initial HTML
        with open('rtpi_before_render.html', 'w', encoding='utf-8') as f:
            f.write(r.text)
        print("Saved initial HTML to rtpi_before_render.html")

        # Render JavaScript
        print("Rendering JavaScript...")
        r.html.render(timeout=30, wait=3)

        print("Content length after render:", len(r.html.html))

        # Save rendered HTML
        with open('rtpi_after_render.html', 'w', encoding='utf-8') as f:
            f.write(r.html.html)
        print("Saved rendered HTML to rtpi_after_render.html")

        # Parse with BeautifulSoup
        soup = BeautifulSoup(r.html.html, 'html.parser')

        # Look for different types of content
        print("\n=== ANALYSIS ===")

        # Check for event containers
        event_containers = soup.find_all(['div', 'article', 'section'], class_=lambda x: x and 'event' in x.lower())
        print(f"Found {len(event_containers)} elements with 'event' in class name")

        # Check for links
        all_links = soup.find_all('a', href=True)
        print(f"Found {len(all_links)} total links")

        # Check for event-related links
        event_links = [link for link in all_links if link.get('href', '').startswith('/events/')]
        print(f"Found {len(event_links)} event-related links")

        # Check for JavaScript variables or data
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tags")

        # Look for data attributes or JSON
        elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
        print(f"Found {len(elements_with_data)} elements with data attributes")

        # Check for common dynamic content patterns
        potential_containers = soup.find_all(['div', 'section'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['container', 'grid', 'list', 'items', 'cards', 'events']
        ))
        print(f"Found {len(potential_containers)} potential content containers")

        # Print some sample links for debugging
        print("\nSample links found:")
        for i, link in enumerate(all_links[:10]):
            href = link.get('href', '')
            text = link.get_text(strip=True)[:50]
            print(f"  {i+1}: {href} -> {text}")

        # Check for any API calls or XHR endpoints
        print("\nLooking for potential API endpoints in scripts...")
        api_patterns = []
        for script in scripts:
            if script.string:
                content = script.string
                # Look for common API patterns
                import re
                api_matches = re.findall(r'["\']([^"\']*(?:api|ajax|endpoint)[^"\']*)["\']', content, re.IGNORECASE)
                api_patterns.extend(api_matches)

        if api_patterns:
            print("Potential API endpoints found:")
            for pattern in set(api_patterns[:10]):
                print(f"  {pattern}")
        else:
            print("No obvious API endpoints found in scripts")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    debug_rtpi_page()