#!/usr/bin/env python
"""Batch update multiple transactions with the same category and labels.

This script provides deterministic batch updates for review workflows.
"""

import sys
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient


def update_transactions_batch(
    transaction_ids: List[int],
    category_id: Optional[int] = None,
    clear_review_flags: bool = True,
    preserve_labels: bool = True,
) -> Dict[str, Any]:
    """Update multiple transactions with the same category and label settings.

    Args:
        transaction_ids: List of transaction IDs to update
        category_id: New category ID (None = don't change category)
        clear_review_flags: Remove review flags from labels
        preserve_labels: Keep non-review labels (Note: currently clears all labels)

    Returns:
        Dictionary with results:
        {
            'total': int,
            'updated': int,
            'failed': int,
            'failed_ids': [int]
        }
    """
    load_dotenv()
    client = PocketSmithClient()

    results: Dict[str, Any] = {
        "total": len(transaction_ids),
        "updated": 0,
        "failed": 0,
        "failed_ids": [],
    }

    # Update each transaction
    # Note: We don't fetch existing data since get_transaction() doesn't exist yet
    # This means we'll clear all labels when clear_review_flags=True
    print(f"Updating {len(transaction_ids)} transactions...", flush=True)

    for txn_id in transaction_ids:
        try:
            updates: Dict[str, Any] = {}

            # Handle labels - clear all labels for now
            # TODO: Add get_transaction() to API client to preserve non-review labels
            if clear_review_flags:
                updates["labels"] = []  # Clear all labels
                updates["note"] = ""  # Clear review notes

            # Update category if specified
            if category_id is not None:
                updates["category_id"] = category_id

            # Apply update
            client.update_transaction(txn_id, **updates)
            results["updated"] += 1

            # Progress indicator
            if results["updated"] % 10 == 0:
                print(
                    f"  Progress: {results['updated']}/{len(transaction_ids)}", end="\r", flush=True
                )

        except Exception as e:
            print(f"\nWarning: Failed to update transaction {txn_id}: {e}", file=sys.stderr)
            results["failed"] += 1
            results["failed_ids"].append(txn_id)

    print()  # New line after progress
    return results


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Batch update multiple transactions")
    parser.add_argument(
        "--transaction-ids", required=True, help="Comma-separated list of transaction IDs"
    )
    parser.add_argument("--category-id", type=int, help="Category ID to set (optional)")
    parser.add_argument(
        "--clear-review-flags",
        action="store_true",
        default=True,
        help="Clear review flags (default: true)",
    )
    parser.add_argument(
        "--no-preserve-labels",
        action="store_true",
        help="Clear all labels (default: preserve non-review labels)",
    )
    parser.add_argument(
        "--output", choices=["json", "summary"], default="summary", help="Output format"
    )

    args = parser.parse_args()

    # Parse transaction IDs
    try:
        txn_ids = [int(x.strip()) for x in args.transaction_ids.split(",")]
    except ValueError:
        print("Error: Invalid transaction IDs format", file=sys.stderr)
        return 1

    if not txn_ids:
        print("Error: No transaction IDs provided", file=sys.stderr)
        return 1

    # Perform batch update
    results = update_transactions_batch(
        txn_ids,
        category_id=args.category_id,
        clear_review_flags=args.clear_review_flags,
        preserve_labels=not args.no_preserve_labels,
    )

    # Output results
    if args.output == "json":
        print(json.dumps(results, indent=2))
    elif args.output == "summary":
        print("\nBatch Update Complete:")
        print(f"  Total: {results['total']}")
        print(f"  Updated: {results['updated']}")
        print(f"  Failed: {results['failed']}")
        if results["failed_ids"]:
            print(f"  Failed IDs: {results['failed_ids']}")

    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
