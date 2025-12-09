#!/usr/bin/env python3
"""Clean up erroneous labels from transactions.

This script removes ALL labels from transactions that have the specific
set of labels that were incorrectly mass-applied due to a bug in the
unified_rules.py label parsing.

The bug caused label rules with patterns to match ALL transactions
because the patterns field wasn't being parsed, resulting in rules
with no conditions that matched everything.
"""

import argparse
import sys
from typing import Dict, List, Any
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient

load_dotenv()

# The exact set of labels that were incorrectly mass-applied
BAD_LABELS = {
    "Education",
    "Medical",
    "Child Support",
    "Kids Expense",
    "Child Support Received",
    "Child Support Paid",
}


def find_affected_transactions(
    client: PocketSmithClient,
    user_id: int,
) -> List[Dict[str, Any]]:
    """Find all transactions with the erroneous label set.

    Args:
        client: PocketSmith API client
        user_id: User ID

    Returns:
        List of affected transactions
    """
    print("Fetching all transactions to find affected ones...", end="", flush=True)

    # Fetch all transactions (we need to check labels)
    all_transactions = client.get_all_transactions(
        user_id=user_id,
        start_date="2024-01-01",  # Bug affected transactions from this date
        end_date="2025-12-31",
    )
    print(f" fetched {len(all_transactions)} transactions", flush=True)

    # Find transactions with ANY of the bad labels
    affected = []
    for txn in all_transactions:
        txn_labels = set(txn.get("labels", []))
        if txn_labels & BAD_LABELS:  # Intersection - has any bad label
            affected.append(txn)

    return affected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without applying changes",
    )
    parser.add_argument(
        "--keep-valid",
        action="store_true",
        help="Only remove the bad labels, keep any other valid labels",
    )
    args = parser.parse_args()

    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    # Find affected transactions
    affected = find_affected_transactions(client, user_id)

    if not affected:
        print("\nNo transactions found with erroneous labels.")
        return 0

    print(f"\nFound {len(affected)} transactions with erroneous labels.")

    # Count label distributions
    label_counts: Dict[str, int] = {}
    for txn in affected:
        for label in txn.get("labels", []):
            label_counts[label] = label_counts.get(label, 0) + 1

    print("\nLabel distribution in affected transactions:")
    for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
        marker = " [BAD]" if label in BAD_LABELS else ""
        print(f"  {label}: {count}{marker}")

    if args.dry_run:
        print("\nDRY RUN - Would remove labels from these transactions:")
        for txn in affected[:10]:
            labels = txn.get("labels", [])
            print(f"  - {txn['date']} | {txn.get('payee', 'N/A')[:30]} | Labels: {labels}")
        if len(affected) > 10:
            print(f"  ... and {len(affected) - 10} more")
        print("\nRun without --dry-run to apply changes.")
        return 0

    # Build updates
    updates = []
    for txn in affected:
        if args.keep_valid:
            # Only remove bad labels, keep others
            current_labels = set(txn.get("labels", []))
            new_labels = list(current_labels - BAD_LABELS)
        else:
            # Remove ALL labels
            new_labels = []

        updates.append(
            {
                "transaction_id": txn["id"],
                "labels": new_labels,
            }
        )

    print(f"\nRemoving labels from {len(updates)} transactions...")

    def progress_callback(completed: int, total: int, txn_id: int, success: bool) -> None:
        if completed % 50 == 0 or completed == total:
            pct = int(completed / total * 100)
            status = "ok" if success else "FAIL"
            print(f"  Progress: {completed}/{total} ({pct}%) [{status}]", end="\r", flush=True)

    result = client.update_transactions_batch(
        updates=updates,
        max_workers=5,
        progress_callback=progress_callback,
    )
    print()  # New line after progress

    print("\nCleanup complete!")
    print(f"  Successful: {result['successful']}")
    if result["failed"] > 0:
        print(f"  Failed: {result['failed']}")
        for err in result["errors"][:5]:
            print(f"    - Transaction {err['transaction_id']}: {err['error']}")

    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
