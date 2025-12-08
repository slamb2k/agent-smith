#!/usr/bin/env python3
"""Analyze transaction distribution by category."""

import sys
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict
from scripts.core.api_client import PocketSmithClient
from scripts.core.category_utils import find_category_by_id, get_category_path


def main() -> int:
    """Main function."""
    # Initialize API client
    print("Initializing PocketSmith API client...")
    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    # Calculate date range for last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    print(f"Fetching transactions from {start_str} to {end_str}...")

    # Fetch all categories (flattened)
    print("Fetching categories...")
    categories = client.get_categories(user_id, flatten=True)

    # Fetch all transactions for the period
    print("Fetching transactions...")
    transactions = client.get_all_transactions(
        user_id=user_id, start_date=start_str, end_date=end_str
    )
    print(f"Fetched {len(transactions)} transactions\n")

    # Analyze by category
    category_counts: Dict[str, int] = defaultdict(int)
    category_totals: Dict[str, float] = defaultdict(float)
    expense_count = 0
    income_count = 0
    uncategorized_count = 0

    for txn in transactions:
        amount = float(txn.get("amount", 0))
        category_id = txn.get("category_id")

        if amount < 0:
            expense_count += 1
        else:
            income_count += 1

        if not category_id:
            uncategorized_count += 1
            continue

        category = find_category_by_id(categories, category_id)
        if category:
            path = get_category_path(categories, category)
            root = path[0] if path else "Unknown"
            category_counts[root] += 1
            category_totals[root] += abs(amount)

    print("TRANSACTION SUMMARY")
    print("=" * 70)
    print(f"Total Transactions:    {len(transactions)}")
    print(f"Expenses:              {expense_count}")
    print(f"Income:                {income_count}")
    print(f"Uncategorized:         {uncategorized_count}")
    print()

    print("BREAKDOWN BY CATEGORY")
    print("=" * 70)
    for cat in sorted(category_counts.keys()):
        count = category_counts[cat]
        total = category_totals[cat]
        avg = total / 12  # 12 months
        print(f"{cat:<30} {count:>5} txns   ${total:>10,.2f} total   ${avg:>8,.2f}/mo")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
