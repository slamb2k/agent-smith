#!/usr/bin/env python3
"""Confirm all transactions using PocketSmith web UI bulk endpoint.

Uses the web UI endpoint POST /transactions/query.json which can confirm
200+ transactions in a single HTTP request.

Requires:
- POCKETSMITH_API_KEY: For fetching transaction IDs via developer API
- POCKETSMITH_SESSION_COOKIE: Web UI session cookie (_pocketsmith_session_id)
- POCKETSMITH_CSRF_TOKEN: Web UI CSRF token (x-csrf-token header)

Get session cookie and CSRF token from browser dev tools (Network tab).
"""

import os
import sys
import time
from typing import List, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

# Developer API for fetching
API_KEY = os.getenv("POCKETSMITH_API_KEY")
API_BASE_URL = "https://api.pocketsmith.com/v2"

# Web UI for bulk confirmation
WEB_BASE_URL = "https://my.pocketsmith.com"
SESSION_COOKIE = os.getenv("POCKETSMITH_SESSION_COOKIE")
CSRF_TOKEN = os.getenv("POCKETSMITH_CSRF_TOKEN")

BATCH_SIZE = 200  # Web UI handles 200 at a time


def get_api_headers() -> Dict[str, str]:
    """Headers for developer API."""
    if not API_KEY:
        raise ValueError("POCKETSMITH_API_KEY environment variable is required")
    return {
        "X-Developer-Key": API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def get_web_headers() -> Dict[str, str]:
    """Headers for web UI endpoint."""
    if not CSRF_TOKEN or not SESSION_COOKIE:
        raise ValueError("POCKETSMITH_CSRF_TOKEN and POCKETSMITH_SESSION_COOKIE required")
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-CSRF-Token": CSRF_TOKEN,
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": f"_pocketsmith_session_id={SESSION_COOKIE}",
    }


def fetch_all_unconfirmed_ids() -> List[int]:
    """Fetch all transaction IDs with needs_review=true via developer API.

    NOTE: The PocketSmith API filter requires needs_review=1 (integer),
    NOT needs_review='true' (string) which doesn't work correctly.
    """
    headers = get_api_headers()

    # Get user ID
    resp = requests.get(f"{API_BASE_URL}/me", headers=headers)
    user_id = resp.json()["id"]

    all_ids = []
    page = 1

    print("Fetching transactions needing review...")

    while True:
        url = f"{API_BASE_URL}/users/{user_id}/transactions"
        # Use needs_review=1 (integer) - NOT 'true' (string) which is broken!
        params = {"page": page, "per_page": 100, "needs_review": 1}

        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 429:
            print(f"  Rate limited at page {page}, waiting 60s...")
            time.sleep(60)
            continue
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


def confirm_batch_bulk(ids: List[int], batch_num: int, total_batches: int) -> tuple:
    """Confirm a batch of transactions using web UI bulk endpoint.

    Sends a single POST request with confirm[]=ID1&confirm[]=ID2&...
    Returns (success_count, failed_count)
    """
    headers = get_web_headers()
    url = f"{WEB_BASE_URL}/transactions/query.json"

    # Build form data: confirm[]=ID1&confirm[]=ID2&...
    form_data = "&".join([f"confirm[]={txn_id}" for txn_id in ids])

    try:
        resp = requests.post(url, headers=headers, data=form_data, timeout=60)

        if resp.status_code == 200:
            return (len(ids), 0)
        elif resp.status_code == 422:
            # Unprocessable entity - some may have been processed
            print("    Warning: 422 response, some may have failed")
            return (0, len(ids))
        elif resp.status_code == 401:
            print("    Error: Unauthorized - session cookie may be expired")
            return (0, len(ids))
        else:
            print(f"    Error: HTTP {resp.status_code}")
            return (0, len(ids))

    except requests.Timeout:
        print("    Timeout after 60s")
        return (0, len(ids))
    except Exception as e:
        print(f"    Exception: {e}")
        return (0, len(ids))


def main() -> int:
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv

    # Validate credentials
    if not API_KEY:
        print("Error: POCKETSMITH_API_KEY not set")
        return 1
    if not SESSION_COOKIE:
        print("Error: POCKETSMITH_SESSION_COOKIE not set")
        print("\nGet it from browser dev tools:")
        print("  1. Open my.pocketsmith.com")
        print("  2. Open Dev Tools → Network tab")
        print("  3. Reload page, click any request to my.pocketsmith.com")
        print("  4. Copy the _pocketsmith_session_id cookie value")
        print("  5. Add to .env: POCKETSMITH_SESSION_COOKIE=<value>")
        return 1
    if not CSRF_TOKEN:
        print("Error: POCKETSMITH_CSRF_TOKEN not set")
        print("\nGet it from browser dev tools:")
        print("  1. Look for x-csrf-token in request headers")
        print("  2. Or find meta[name='csrf-token'] in page source")
        print("  3. Add to .env: POCKETSMITH_CSRF_TOKEN=<value>")
        return 1

    # Fetch all IDs using developer API
    all_ids = fetch_all_unconfirmed_ids()

    if not all_ids:
        print("No transactions awaiting review.")
        return 0

    if dry_run:
        print("DRY RUN - Would confirm these transactions:")
        print(f"  Total: {len(all_ids)}")
        print(f"  First 5: {all_ids[:5]}")
        print(f"  Last 5: {all_ids[-5:]}")
        num_batches = (len(all_ids) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\n  Would process in {num_batches} batches of {BATCH_SIZE}")
        print("Run without --dry-run to apply.")
        return 0

    # Process in batches using web UI bulk endpoint
    total_success = 0
    total_fail = 0
    num_batches = (len(all_ids) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"Confirming {len(all_ids)} transactions in {num_batches} batches of {BATCH_SIZE}...")
    print("(Using web UI bulk endpoint - 1 request per batch)\n")

    start_time = time.time()

    for i in range(0, len(all_ids), BATCH_SIZE):
        batch = all_ids[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        batch_start = time.time()
        success, fail = confirm_batch_bulk(batch, batch_num, num_batches)
        batch_time = time.time() - batch_start

        total_success += success
        total_fail += fail

        completed = i + len(batch)
        pct = int(completed / len(all_ids) * 100)
        rate = len(batch) / batch_time if batch_time > 0 else 0

        print(
            f"  Batch {batch_num}/{num_batches}: {success} ok, {fail} fail | "
            f"{completed}/{len(all_ids)} ({pct}%) | {batch_time:.1f}s | {rate:.0f} txn/s"
        )

        # Small delay between batches to be nice to the server
        if batch_num < num_batches:
            time.sleep(0.5)

    elapsed = time.time() - start_time
    avg_rate = len(all_ids) / elapsed if elapsed > 0 else 0
    print(f"\n✅ Confirmed {total_success} transactions in {elapsed:.1f}s ({avg_rate:.0f} txn/s)")
    if total_fail > 0:
        print(f"❌ Failed: {total_fail}")

    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
