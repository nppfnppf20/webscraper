#!/usr/bin/env python3
"""Simple test to just get event links from RTPI"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

async def test_rtpi_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        try:
            print("Loading RTPI events page...")
            response = await page.goto("https://www.rtpi.org.uk/events", wait_until='networkidle', timeout=30000)
            print(f"Response status: {response.status}")

            print("Waiting for Vue content...")
            await page.wait_for_timeout(5000)

            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Find event links
            event_links = []
            links = soup.find_all('a', href=True)
            print(f"Total links found: {len(links)}")

            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)

                if (href.startswith('/events/') and
                    href != '/events/' and
                    len(href.split('/')) > 3 and
                    len(text) > 10):

                    full_url = urljoin("https://www.rtpi.org.uk", href)
                    event_links.append({
                        'url': full_url,
                        'title': text[:100],
                        'date': 'TBD',
                        'region': 'TBD',
                        'category': 'Event',
                        'price': 'TBD',
                        'id': full_url
                    })

            print(f"Found {len(event_links)} event links:")
            for i, event in enumerate(event_links):
                print(f"  {i+1}: {event['title']} -> {event['url']}")

            return event_links

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            await browser.close()

if __name__ == "__main__":
    events = asyncio.run(test_rtpi_links())
    print(f"\nTotal events found: {len(events)}")

    # Save to CSV for testing
    if events:
        import csv
        with open('rtpi_events_test.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'date', 'region', 'category', 'price', 'url'])
            writer.writeheader()
            writer.writerows(events)
        print(f"Saved {len(events)} events to rtpi_events_test.csv")