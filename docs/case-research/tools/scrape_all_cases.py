#!/usr/bin/env python3
"""Scrape all case folders using a threadpool."""

import subprocess
import time
import random
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


# Configuration
VENV_PYTHON = ".venv/bin/python"
SERVICE_ACCOUNT = "../../services/nes/.service-account-key.json"  # Update path as needed
ANNAPURNA_DIR = Path("tmp/annapurna")
THREAD_POOL_SIZE = 3
JITTER_SECONDS = 3


def scrape_case(case_number):
    """Scrape a single case with jitter backoff."""
    case_dir = ANNAPURNA_DIR / f"case{case_number}"
    details_file = case_dir / "details.md"
    
    # Check if case exists
    if not case_dir.exists() or not details_file.exists():
        return case_number, "skipped", "folder or details.md not found"
    
    # Skip if already processed - check subfolders for result files
    for subfolder in case_dir.iterdir():
        if subfolder.is_dir():
            if (subfolder / "case-result.json").exists() or (subfolder / "result.json").exists():
                return case_number, "skipped", "result file found in subfolder"
    
    # Add jitter before processing
    jitter = random.uniform(0, JITTER_SECONDS)
    time.sleep(jitter)
    
    print(f"Processing case{case_number}...")
    
    try:
        # Run the scrape command
        result = subprocess.run(
            [
                VENV_PYTHON,
                "manage.py",
                "scrape_case",
                "--work-dir", str(case_dir),
                "--service-account", SERVICE_ACCOUNT,
                str(details_file)
            ],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per case
        )
        
        if result.returncode == 0:
            print(f"✓ case{case_number} completed successfully")
            return case_number, "success", None
        else:
            error_preview = result.stderr[:4500] if result.stderr else result.stdout[:4500]
            print(f"✗ case{case_number} failed: {error_preview}")
            return case_number, "failed", result.stderr or result.stdout
            
    except subprocess.TimeoutExpired:
        print(f"✗ case{case_number} timed out")
        return case_number, "timeout", "Command exceeded 5 minute timeout"
    except Exception as e:
        print(f"✗ case{case_number} error: {str(e)}")
        return case_number, "error", str(e)


def cleanup_empty_folders():
    """Delete scrape-case-* folders that don't have case-result.json."""
    print("Cleaning up incomplete scrape folders...")
    deleted_count = 0
    
    for case_dir in ANNAPURNA_DIR.glob("case*"):
        if not case_dir.is_dir():
            continue
            
        for scrape_folder in case_dir.glob("scrape-case-*"):
            if not scrape_folder.is_dir():
                continue
                
            result_file = scrape_folder / "case-result.json"
            if not result_file.exists():
                print(f"  Deleting {scrape_folder.relative_to(ANNAPURNA_DIR)}")
                shutil.rmtree(scrape_folder)
                deleted_count += 1
    
    print(f"Deleted {deleted_count} incomplete folders\n")
    return deleted_count


def main():
    """Run scraping with threadpool."""
    # Clean up incomplete folders first
    cleanup_empty_folders()
    
    print(f"Starting scrape with {THREAD_POOL_SIZE} threads...")
    print(f"Jitter: 0-{JITTER_SECONDS}s per task\n")
    
    start_time = time.time()
    results = {"success": 0, "failed": 0, "skipped": 0, "timeout": 0, "error": 0}
    failures = []
    
    # Submit all tasks to threadpool
    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
        futures = {executor.submit(scrape_case, i): i for i in range(1, 101)}
        
        # Process completed tasks
        for future in as_completed(futures):
            case_num, status, error = future.result()
            results[status] += 1
            if status in ("failed", "timeout", "error") and error:
                failures.append((case_num, status, error))
    
    # Summary
    elapsed = time.time() - start_time
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total time: {elapsed:.1f}s")
    print(f"Success: {results['success']}")
    print(f"Failed: {results['failed']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Timeout: {results['timeout']}")
    print(f"Error: {results['error']}")
    
    # Write failures to log
    if failures:
        log_file = ANNAPURNA_DIR / "failures.log"
        with open(log_file, "w") as f:
            for case_num, status, error in failures:
                f.write(f"\n{'='*50}\n")
                f.write(f"Case {case_num} - {status.upper()}\n")
                f.write(f"{'='*50}\n")
                f.write(f"{error}\n")
        print(f"\nFailure details written to: {log_file}")


if __name__ == "__main__":
    main()
