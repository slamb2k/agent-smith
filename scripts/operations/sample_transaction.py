#!/usr/bin/env python3
"""Show sample transaction structure."""

import sys
import json
from datetime import datetime, timedelta
from scripts.core.api_client import PocketSmithClient


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

    # Fetch transactions
    transactions = client.get_transactions(
        user_id=user_id, start_date=start_str, end_date=end_str, page=1, per_page=10
    )

    print(f"\nFound {len(transactions)} transactions\n")

    # Show first few transactions
    for i, txn in enumerate(transactions[:5], 1):
        print(f"Transaction {i}:")
        print(json.dumps(txn, indent=2))
        print("\n" + "=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
