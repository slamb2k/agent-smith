#!/usr/bin/env python
"""Fetch all transactions flagged with conflict labels.

This script provides deterministic conflict retrieval for the review workflow.
Output is JSON to stdout for easy consumption by orchestration layers.
"""

import sys
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient
from scripts.core.labels import has_review_flag


def fetch_conflicts(
    start_date: str = "2025-01-01", end_date: str = "2025-12-31"
) -> List[Dict[str, Any]]:
    """Fetch all transactions with conflict labels.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List of transaction dictionaries with conflict labels
    """
    load_dotenv()
    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    all_conflicts = []
    page = 1

    while True:
        batch = client.get_transactions(
            user_id, start_date=start_date, end_date=end_date, page=page, per_page=100
        )

        if not batch:
            break

        for txn in batch:
            labels = txn.get("labels", [])
            if has_review_flag(labels):
                all_conflicts.append(txn)

        if len(batch) < 100:
            break

        page += 1

    return all_conflicts


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Fetch transactions with conflict labels")
    parser.add_argument("--start-date", default="2025-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default="2025-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "--output", choices=["json", "count", "summary"], default="json", help="Output format"
    )

    args = parser.parse_args()

    conflicts = fetch_conflicts(args.start_date, args.end_date)

    if args.output == "json":
        print(json.dumps(conflicts, indent=2))
    elif args.output == "count":
        print(len(conflicts))
    elif args.output == "summary":
        print(f"Found {len(conflicts)} transactions with conflict labels")
        if conflicts:
            print("\nFirst conflict:")
            first = conflicts[0]
            print(f"  Date: {first.get('date')}")
            print(f"  Payee: {first.get('payee')}")
            print(f"  Amount: ${abs(first.get('amount', 0))}")
            cat = first.get("category", {})
            print(f"  Category: {cat.get('title', 'Uncategorized')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
