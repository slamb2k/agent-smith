#!/usr/bin/env python
"""Set up PayPal transactions for testing review-conflicts workflow.

This script updates all PayPal transactions to:
1. Category: Online Services (correct categorization)
2. Adds Generic PayPal review flag label

This allows testing the review-conflicts workflow where you can:
- Review the group of PayPal transactions
- Accept them (they're already correctly categorized)
- Create a rule to prevent future flags
"""

import sys
from typing import Any
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient
from scripts.core.labels import LABEL_GENERIC_PAYPAL, add_review_label


def find_online_services_category(client: PocketSmithClient, user_id: int) -> int:
    """Find the 'Online Services' category.

    Args:
        client: API client
        user_id: User ID

    Returns:
        Category ID for Online Services

    Raises:
        ValueError: If Online Services category not found
    """
    # Get all categories
    categories = client.get_categories(user_id)

    # Search for Online Services category
    def find_category(cats: list, name: str) -> Any:
        for cat in cats:
            title = cat.get("title", "")
            if title == name:
                return cat["id"]
            if cat.get("children"):
                child_id = find_category(cat["children"], name)
                if child_id:
                    return child_id
        return None

    category_id = find_category(categories, "Online Services")

    if not category_id:
        raise ValueError(
            "Online Services category not found. Please ensure it exists in PocketSmith."
        )

    print(f"Found 'Online Services' category (ID: {category_id})")
    return int(category_id)


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Set up PayPal transactions for review-conflicts testing"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without making changes"
    )
    parser.add_argument("--start-date", default="2025-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default="2025-12-31", help="End date (YYYY-MM-DD)")

    args = parser.parse_args()

    load_dotenv()
    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    # Get Online Services category
    if not args.dry_run:
        online_services_id = find_online_services_category(client, user_id)
    else:
        online_services_id = 999999  # Placeholder for dry run
        print("Dry run: Would find 'Online Services' category")

    # Fetch all PayPal transactions
    print(f"\nFetching PayPal transactions from {args.start_date} to {args.end_date}...")
    paypal_transactions = []
    page = 1

    while True:
        batch = client.get_transactions(
            user_id, start_date=args.start_date, end_date=args.end_date, page=page, per_page=100
        )

        if not batch:
            break

        for txn in batch:
            payee = txn.get("payee", "")
            if "PAYPAL" in payee.upper():
                paypal_transactions.append(txn)

        if len(batch) < 100:
            break

        page += 1

    if not paypal_transactions:
        print("No PayPal transactions found")
        return 0

    print(f"Found {len(paypal_transactions)} PayPal transactions")

    # Update each transaction
    print(f"\n{'Dry run: Would update' if args.dry_run else 'Updating'} transactions...")
    updated = 0

    for txn in paypal_transactions:
        txn_id = txn["id"]
        payee = txn.get("payee", "")[:60]
        current_cat = txn.get("category", {}).get("title", "Uncategorized")
        existing_labels = txn.get("labels", [])

        # Add review flag to labels
        new_labels = add_review_label(existing_labels, LABEL_GENERIC_PAYPAL)

        if not args.dry_run:
            try:
                client.update_transaction(
                    txn_id,
                    category_id=online_services_id,
                    labels=new_labels,
                    note="Generic PayPal - flagged for review",
                )
                updated += 1

                if updated % 10 == 0:
                    print(f"  Progress: {updated}/{len(paypal_transactions)}", end="\r", flush=True)
            except Exception as e:
                print(f"\n  Warning: Failed to update {txn_id}: {e}")
        else:
            print(f"  Would update: {payee}")
            print(f"    Current: {current_cat} → Online Services")
            print(f"    Add label: {LABEL_GENERIC_PAYPAL}")
            updated += 1

            if updated >= 5:
                print(f"  ... and {len(paypal_transactions) - 5} more")
                break

    if not args.dry_run:
        print()  # New line after progress

    # Summary
    print(f"\n{'Dry run complete' if args.dry_run else 'Update complete'}:")
    print(f"  PayPal transactions: {len(paypal_transactions)}")
    print(f"  {'Would update' if args.dry_run else 'Updated'}: {updated}")
    print("  Category: Online Services")
    print(f"  Label: {LABEL_GENERIC_PAYPAL}")

    if not args.dry_run:
        print("\nReady to test! Run:")
        print("  uv run python -u scripts/operations/review_conflicts_v2.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
