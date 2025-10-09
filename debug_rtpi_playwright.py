#!/usr/bin/env python3
"""Debug script using Playwright to investigate RTPI events page"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def debug_rtpi_with_playwright():
    async with async_playwright() as p:
        try:
            # Launch browser with realistic settings
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

            url = "https://www.rtpi.org.uk/events"
            print(f"Loading {url}...")

            # Navigate to the page
            response = await page.goto(url, wait_until='networkidle', timeout=30000)
            print(f"Response status: {response.status}")

            if response.status != 200:
                print(f"Failed to load page: {response.status}")
                return

            # Wait for content to load
            print("Waiting for content to load...")
            await page.wait_for_timeout(5000)

            # Get page content
            content = await page.content()
            print(f"Page content length: {len(content)}")

            # Save the HTML
            with open('rtpi_playwright.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Saved HTML to rtpi_playwright.html")

            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')

            print("\n=== ANALYSIS ===")

            # Look for event links
            all_links = soup.find_all('a', href=True)
            print(f"Total links found: {len(all_links)}")

            event_links = []
            for link in all_links:
                href = link.get('href', '')
                if '/events/' in href and href != '/events/':
                    event_links.append((href, link.get_text(strip=True)))

            print(f"Event links found: {len(event_links)}")
            for i, (href, text) in enumerate(event_links[:10]):
                print(f"  {i+1}: {href} -> {text[:50]}")

            # Look for event containers
            event_containers = soup.find_all(['div', 'article', 'section'],
                                           class_=lambda x: x and any(keyword in x.lower()
                                           for keyword in ['event', 'card', 'item']))
            print(f"Event-like containers: {len(event_containers)}")

            # Look for pagination or load more buttons
            pagination = soup.find_all(['button', 'a'],
                                     class_=lambda x: x and any(keyword in x.lower()
                                     for keyword in ['load', 'more', 'page', 'next']))
            print(f"Pagination/load more elements: {len(pagination)}")

            # Check for JavaScript that might load events
            scripts = soup.find_all('script')
            print(f"Script tags: {len(scripts)}")

            # Look for data attributes or API endpoints
            api_mentions = []
            for script in scripts:
                if script.string:
                    content_lower = script.string.lower()
                    if any(keyword in content_lower for keyword in ['api', 'fetch', 'ajax', 'events']):
                        api_mentions.append(script.string[:200])

            if api_mentions:
                print(f"Scripts mentioning API/fetch: {len(api_mentions)}")
                for i, mention in enumerate(api_mentions[:3]):
                    print(f"  {i+1}: {mention[:100]}...")

            # Take a screenshot for visual inspection
            await page.screenshot(path='rtpi_screenshot.png', full_page=True)
            print("Screenshot saved to rtpi_screenshot.png")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_rtpi_with_playwright())