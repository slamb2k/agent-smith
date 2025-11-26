#!/usr/bin/env python
"""Reprocess conflict transactions with updated rules.

This script applies the current rule set to a list of conflicted transactions
and updates those that now match with higher confidence.
"""

import sys
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient
from scripts.workflows.categorization import CategorizationWorkflow, IntelligenceMode
from scripts.core.labels import remove_review_labels


def reprocess_conflicts(
    transactions: List[Dict[str, Any]], mode: IntelligenceMode = IntelligenceMode.CONSERVATIVE
) -> Dict[str, Any]:
    """Reprocess transactions with current rules.

    Args:
        transactions: List of transaction dictionaries to reprocess
        mode: Intelligence mode for categorization

    Returns:
        Dictionary with results:
        {
            'total': int,
            'resolved': int,
            'still_conflicted': int,
            'resolved_txns': [txn_ids],
            'remaining_txns': [txn_ids]
        }
    """
    load_dotenv()
    client = PocketSmithClient()
    workflow = CategorizationWorkflow(client)

    results: Dict[str, Any] = {
        "total": len(transactions),
        "resolved": 0,
        "still_conflicted": 0,
        "resolved_txns": [],
        "remaining_txns": [],
    }

    print(f"Reprocessing {len(transactions)} transactions...", flush=True)

    for idx, txn in enumerate(transactions, 1):
        txn_id = txn["id"]
        current_category = txn.get("category", {}).get("title")

        # Apply categorization logic
        result = workflow.categorize_single_transaction(txn)

        suggested_category = result.get("category")

        # Check if conflict is resolved (suggestion matches current)
        if suggested_category == current_category:
            # Resolved: rule now suggests same category
            results["resolved"] += 1
            results["resolved_txns"].append(txn_id)

            # Update transaction to clear review labels
            existing_labels = txn.get("labels", [])
            new_labels = remove_review_labels(existing_labels)
            client.update_transaction(txn_id, labels=new_labels, note="")

        else:
            # Still conflicted
            results["still_conflicted"] += 1
            results["remaining_txns"].append(txn_id)

        # Show progress
        if idx % 10 == 0 or idx == len(transactions):
            pct = int(idx / len(transactions) * 100)
            print(f"  Progress: {idx}/{len(transactions)} ({pct}%)", end="\r", flush=True)

    print()  # New line after progress
    return results


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Reprocess conflict transactions with updated rules"
    )
    parser.add_argument(
        "--transactions-file", help="JSON file containing transactions to reprocess"
    )
    parser.add_argument(
        "--transaction-ids", nargs="+", type=int, help="Specific transaction IDs to reprocess"
    )
    parser.add_argument(
        "--mode",
        choices=["conservative", "smart", "aggressive"],
        default="conservative",
        help="Categorization intelligence mode",
    )
    parser.add_argument(
        "--output", choices=["json", "summary"], default="summary", help="Output format"
    )

    args = parser.parse_args()

    # Load transactions
    transactions = []

    if args.transactions_file:
        with open(args.transactions_file) as f:
            transactions = json.load(f)
    elif args.transaction_ids:
        # Fetch specific transactions
        load_dotenv()
        client = PocketSmithClient()
        _ = client.get_user()  # noqa: F841

        for txn_id in args.transaction_ids:
            # Note: This requires fetching from API
            # In practice, pass full transaction data via file
            print("Warning: Fetching individual transactions by ID not implemented")
            print("Use --transactions-file with JSON array of transactions")
            return 1
    else:
        print("Error: Must provide --transactions-file or --transaction-ids", file=sys.stderr)
        return 1

    # Map mode string to enum
    mode_map = {
        "conservative": IntelligenceMode.CONSERVATIVE,
        "smart": IntelligenceMode.SMART,
        "aggressive": IntelligenceMode.AGGRESSIVE,
    }
    mode = mode_map[args.mode]

    # Reprocess
    results = reprocess_conflicts(transactions, mode=mode)

    if args.output == "json":
        print(json.dumps(results, indent=2))
    elif args.output == "summary":
        print("\nReprocessing complete:")
        print(f"  Total: {results['total']}")
        print(f"  ✓ Resolved: {results['resolved']}")
        print(f"  ⚠ Still conflicted: {results['still_conflicted']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
