"""
Master script to run all scrapers sequentially.
This is designed to be run by Render cron jobs.
"""
import sys
import time
import subprocess
from pathlib import Path

def run_scraper(module_name: str, description: str):
    """Run a scraper module as a subprocess and report results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Module: {module_name}")
    print(f"{'='*60}")

    start = time.time()
    try:
        # Run the scraper as a subprocess so __main__ block executes
        result = subprocess.run(
            [sys.executable, "-m", module_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per scraper
        )

        elapsed = time.time() - start

        # Print the scraper's output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode == 0:
            print(f"✓ {description} completed in {elapsed:.2f}s")
            return True
        else:
            print(f"✗ {description} failed after {elapsed:.2f}s (exit code: {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"✗ {description} timed out after {elapsed:.2f}s")
        return False
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
        # ("backend.scraper.run_peeringdb_fac", "PeeringDB Facilities (GB)"),  # Disabled - not needed
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
