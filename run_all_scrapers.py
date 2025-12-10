"""
Master script to run all scrapers sequentially.
This is designed to be run by Render cron jobs.
"""
import sys
import time
from pathlib import Path

# Add backend to path so we can import scrapers
sys.path.insert(0, str(Path(__file__).parent))

def run_scraper(module_name: str, description: str):
    """Run a scraper module and report results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Module: {module_name}")
    print(f"{'='*60}")

    start = time.time()
    try:
        # Import and run the scraper module
        module = __import__(module_name, fromlist=[''])

        # If the module has a main() function, call it
        if hasattr(module, 'main'):
            module.main()

        elapsed = time.time() - start
        print(f"✓ {description} completed in {elapsed:.2f}s")
        return True
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ {description} failed after {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all scrapers in sequence"""
    print("="*60)
    print("STARTING ALL SCRAPERS")
    print("="*60)

    start_time = time.time()
    results = []

    # Define scrapers to run
    scrapers = [
        ("backend.scraper.run_peeringdb", "PeeringDB IX (GB)"),
        ("backend.scraper.run_peeringdb_fac", "PeeringDB Facilities (GB)"),
        ("backend.scraper.run_planit_api_datacentres", "PlanIt Datacentres"),
        ("backend.scraper.run_planit_renewables_daily", "PlanIt Renewables"),
        ("backend.scraper.run_west_lindsey", "West Lindsey Planning"),
    ]

    # Run each scraper
    for module_name, description in scrapers:
        success = run_scraper(module_name, description)
        results.append((description, success))

    # Print summary
    total_time = time.time() - start_time
    print("\n" + "="*60)
    print("SCRAPING SUMMARY")
    print("="*60)

    for description, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {description}")

    print(f"\nTotal time: {total_time:.2f}s")
    print("="*60)

    # Exit with error code if any failed
    if not all(success for _, success in results):
        sys.exit(1)

if __name__ == "__main__":
    main()
