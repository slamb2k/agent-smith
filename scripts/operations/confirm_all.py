#!/usr/bin/env python3
"""Confirm all transactions awaiting review.

Sets needs_review=false for all transactions that have needs_review=true.
"""

import argparse
import sys
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient

load_dotenv()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without applying changes",
    )
    args = parser.parse_args()

    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    print("Fetching transactions awaiting review...", end="", flush=True)

    # Fetch all transactions with needs_review=1
    # NOTE: The API requires needs_review=1 (integer), NOT 'true' (string)
    all_unconfirmed = []
    page = 1
    while True:
        batch = client.get(
            f"/users/{user_id}/transactions",
            params={
                "needs_review": 1,
                "page": page,
                "per_page": 100,
            },
        )
        if not batch:
            break
        all_unconfirmed.extend(batch)
        print(f" {len(all_unconfirmed)}", end="", flush=True)
        if len(batch) < 100:
            break
        page += 1

    print(" found.")

    if not all_unconfirmed:
        print("\nNo transactions awaiting review.")
        return 0

    print(f"\nFound {len(all_unconfirmed)} transactions to confirm.")

    if args.dry_run:
        print("\nDRY RUN - Would confirm these transactions:")
        for t in all_unconfirmed[:10]:
            print(f"  - {t['date']} | {t.get('payee', 'N/A')[:30]} | ${abs(t['amount']):.2f}")
        if len(all_unconfirmed) > 10:
            print(f"  ... and {len(all_unconfirmed) - 10} more")
        print("\nRun without --dry-run to apply.")
        return 0

    # Build updates
    updates = [{"transaction_id": t["id"], "needs_review": False} for t in all_unconfirmed]

    print(f"\nConfirming {len(updates)} transactions...")

    def progress_callback(completed: int, total: int, txn_id: int, success: bool) -> None:
        if completed % 50 == 0 or completed == total:
            pct = int(completed / total * 100)
            print(f"  Progress: {completed}/{total} ({pct}%)", end="\r", flush=True)

    result = client.update_transactions_batch(
        updates=updates,
        max_workers=5,
        progress_callback=progress_callback,
    )
    print()

    print(f"\n✅ Confirmed {result['successful']} transactions")
    if result["failed"] > 0:
        print(f"❌ Failed: {result['failed']}")
        for err in result["errors"][:5]:
            print(f"  - Transaction {err['transaction_id']}: {err['error']}")

    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
