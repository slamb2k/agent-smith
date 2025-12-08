#!/usr/bin/env python3
"""Confirm all transactions awaiting review with concurrent processing.

Fetches all IDs first, then confirms in batches using parallel workers.
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("POCKETSMITH_API_KEY")
BASE_URL = "https://api.pocketsmith.com/v2"
BATCH_SIZE = 100
MAX_WORKERS = 3  # Conservative to avoid rate limiting
MAX_RETRIES = 5
BASE_DELAY = 1.0  # seconds


def get_headers() -> Dict[str, str]:
    if not API_KEY:
        raise ValueError("POCKETSMITH_API_KEY environment variable is required")
    return {
        "X-Developer-Key": API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def fetch_all_unconfirmed_ids() -> List[int]:
    """Fetch all transaction IDs with needs_review=true.

    NOTE: The PocketSmith API filter requires needs_review=1 (integer),
    NOT needs_review='true' (string) which doesn't work correctly.
    """
    headers = get_headers()

    # Get user ID with rate limit handling
    for attempt in range(5):
        resp = requests.get(f"{BASE_URL}/me", headers=headers)
        if resp.status_code == 200:
            break
        elif resp.status_code == 429:
            delay = 30 * (attempt + 1)
            print(f"Rate limited on /me, waiting {delay}s...")
            time.sleep(delay)
        else:
            print(f"Error fetching /me: {resp.status_code}")
            return []

    if resp.status_code != 200:
        print("Failed to get user after retries")
        return []

    user_id = resp.json()["id"]

    all_ids = []
    page = 1

    print("Fetching transactions needing review...")

    while True:
        url = f"{BASE_URL}/users/{user_id}/transactions"
        # Use needs_review=1 (integer) - NOT 'true' (string) which is broken!
        params = {"page": page, "per_page": 100, "needs_review": 1}

        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"Error fetching page {page}: {resp.status_code}")
            break

        transactions = resp.json()
        if not transactions:
            break

        for t in transactions:
            all_ids.append(t["id"])

        if page % 10 == 0:
            print(f"  Fetched {len(all_ids)} so far...")

        if len(transactions) < 100:
            break
        page += 1

    print(f"Found {len(all_ids)} transactions requiring confirmation.\n")
    return all_ids


def confirm_single(txn_id: int, attempt: int = 0) -> tuple:
    """Confirm a single transaction with retry on failure.

    Returns (txn_id, success: bool)
    """
    headers = get_headers()
    url = f"{BASE_URL}/transactions/{txn_id}"
    data = {"needs_review": False}

    # Small delay between requests to avoid rate limiting
    time.sleep(0.2)

    try:
        resp = requests.put(url, headers=headers, json=data)

        if resp.status_code == 200:
            return (txn_id, True)
        elif resp.status_code == 429:  # Rate limited
            if attempt < MAX_RETRIES:
                delay = BASE_DELAY * (2**attempt)
                print(f"    Rate limited on {txn_id}, waiting {delay}s...")
                time.sleep(delay)
                return confirm_single(txn_id, attempt + 1)
            return (txn_id, False)
        else:
            return (txn_id, False)
    except Exception:
        if attempt < MAX_RETRIES:
            delay = BASE_DELAY * (2**attempt)
            time.sleep(delay)
            return confirm_single(txn_id, attempt + 1)
        return (txn_id, False)


def confirm_batch_concurrent(ids: List[int], batch_num: int, total_batches: int) -> tuple:
    """Confirm a batch of transactions using concurrent workers."""
    success = 0
    fail = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(confirm_single, txn_id): txn_id for txn_id in ids}

        for future in as_completed(futures):
            txn_id, ok = future.result()
            if ok:
                success += 1
            else:
                fail += 1

    return success, fail


def main() -> int:
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv

    # Fetch all IDs
    all_ids = fetch_all_unconfirmed_ids()

    if not all_ids:
        print("No transactions awaiting review.")
        return 0

    if dry_run:
        print("DRY RUN - Would confirm these transactions:")
        print(f"  Total: {len(all_ids)}")
        print(f"  First 5: {all_ids[:5]}")
        print(f"  Last 5: {all_ids[-5:]}")
        print("\nRun without --dry-run to apply.")
        return 0

    # Process in batches
    total_success = 0
    total_fail = 0
    num_batches = (len(all_ids) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"Confirming {len(all_ids)} transactions in {num_batches} batches of {BATCH_SIZE}...")
    print(f"(Concurrent processing with {MAX_WORKERS} workers)\n")

    start_time = time.time()

    for i in range(0, len(all_ids), BATCH_SIZE):
        batch = all_ids[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        batch_start = time.time()
        success, fail = confirm_batch_concurrent(batch, batch_num, num_batches)
        batch_time = time.time() - batch_start

        total_success += success
        total_fail += fail

        completed = i + len(batch)
        pct = int(completed / len(all_ids) * 100)
        rate = len(batch) / batch_time if batch_time > 0 else 0

        print(
            f"  Batch {batch_num}/{num_batches}: {success} ok, {fail} fail | "
            f"{completed}/{len(all_ids)} ({pct}%) | {rate:.1f} txn/s"
        )

        # If we had many failures, add extra delay before next batch
        if fail > len(batch) * 0.1:  # More than 10% failures
            print("    Adding 5s delay due to high failure rate...")
            time.sleep(5)

    elapsed = time.time() - start_time
    avg_rate = len(all_ids) / elapsed if elapsed > 0 else 0
    print(f"\n✅ Confirmed {total_success} transactions in {elapsed:.1f}s ({avg_rate:.1f} txn/s)")
    if total_fail > 0:
        print(f"❌ Failed: {total_fail}")

    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
