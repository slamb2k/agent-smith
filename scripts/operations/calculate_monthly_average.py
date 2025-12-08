#!/usr/bin/env python3
"""Calculate average monthly expenditure by category over the last 12 months."""

import argparse
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Optional
from scripts.core.api_client import PocketSmithClient
from scripts.core.category_utils import find_category_by_id, get_category_path


def calculate_date_range() -> Tuple[str, str]:
    """Calculate start and end dates for the last 12 months.

    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    return (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))


def is_expense_transaction(txn: Dict[str, Any]) -> bool:
    """Check if a transaction is an expense.

    Args:
        txn: Transaction object

    Returns:
        True if transaction is an expense (negative amount)
    """
    amount = float(txn.get("amount", 0))
    return amount < 0


def is_kids_transfer(txn: Dict[str, Any]) -> bool:
    """Check if a transaction is a transfer to kids account.

    Args:
        txn: Transaction object

    Returns:
        True if payee/note mentions kids or similar
    """
    payee = (txn.get("payee") or "").lower()
    note = (txn.get("note") or "").lower()

    keywords = ["kids", "kid", "child", "children", "son", "daughter"]

    return any(keyword in payee or keyword in note for keyword in keywords)


def get_category_display_name(categories: List[Dict[str, Any]], category_id: int) -> str:
    """Get display name for a category with hierarchy.

    Args:
        categories: Flat list of all categories
        category_id: Category ID

    Returns:
        Category display name (e.g., "Food & Dining > Groceries")
    """
    category = find_category_by_id(categories, category_id)
    if not category:
        return "Unknown"

    path = get_category_path(categories, category)
    return " > ".join(path)


def categorize_transaction(
    txn: Dict[str, Any], categories: List[Dict[str, Any]], target_categories: Dict[str, List[str]]
) -> Tuple[Optional[str], Optional[str]]:
    """Categorize a transaction into one of the target categories.

    Args:
        txn: Transaction object
        categories: Flat list of all categories
        target_categories: Map of main category to list of subcategory keywords

    Returns:
        Tuple of (main_category, full_category_path) or (None, None) if not matched
    """
    # The category field is an object, not just an ID
    category_obj = txn.get("category")
    if not category_obj:
        return (None, None)

    category_id = category_obj.get("id")
    if not category_id:
        return (None, None)

    category = find_category_by_id(categories, category_id)
    if not category:
        return (None, None)

    path = get_category_path(categories, category)
    full_path = " > ".join(path)

    # Check if this category matches any of our target categories
    for main_cat, keywords in target_categories.items():
        for keyword in keywords:
            if any(keyword.lower() in part.lower() for part in path):
                return (main_cat, full_path)

    return (None, None)


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", choices=["summary", "detailed"], default="summary", help="Output format"
    )
    args = parser.parse_args()

    # Initialize API client
    print("Initializing PocketSmith API client...")
    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    # Calculate date range
    start_date, end_date = calculate_date_range()
    print(f"Fetching transactions from {start_date} to {end_date}...")

    # Fetch all categories (flattened)
    print("Fetching categories...")
    categories = client.get_categories(user_id, flatten=True)

    # Fetch all transactions for the period
    print("Fetching transactions...")
    transactions = client.get_all_transactions(
        user_id=user_id, start_date=start_date, end_date=end_date
    )
    print(f"Fetched {len(transactions)} transactions")

    # Define target categories (exact matches from PocketSmith)
    target_categories = {
        "Food & Dining": ["Food & Dining"],
        "Housing & Utilities": ["Housing & Utilities"],
        "Transportation": ["Transportation"],
        "Healthcare & Insurance": ["Healthcare & Insurance"],
        "Personal & Lifestyle": ["Personal & Lifestyle"],
        "Shopping": ["Shopping"],
        "Work Expenses": ["Work Expenses"],
    }

    # Data structure: {main_category: {subcategory: total_amount}}
    category_totals: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    kids_transfer_total = 0.0

    # Process transactions
    print("Processing transactions...")
    processed_count = 0

    for txn in transactions:
        # Check if it's a kids transfer
        if is_kids_transfer(txn):
            amount = abs(float(txn.get("amount", 0)))
            kids_transfer_total += amount
            processed_count += 1
            continue

        # Only process expense transactions
        if not is_expense_transaction(txn):
            continue

        # Categorize transaction
        main_cat, full_path = categorize_transaction(txn, categories, target_categories)
        if main_cat and full_path:
            amount = abs(float(txn.get("amount", 0)))
            category_totals[main_cat][full_path] += amount
            processed_count += 1

    print(f"Processed {processed_count} relevant transactions")

    # Calculate monthly averages
    months = 12

    # Print results
    print("\n")
    print("=" * 70)
    print("📊 AVERAGE MONTHLY EXPENDITURE (Last 12 Months)")
    print("=" * 70)
    print(f"Period: {start_date} to {end_date}")
    print()

    # Category emojis
    category_emojis = {
        "Food & Dining": "🍽️",
        "Housing & Utilities": "🏠",
        "Transportation": "🚗",
        "Healthcare & Insurance": "🏥",
        "Personal & Lifestyle": "👤",
        "Shopping": "🛍️",
        "Work Expenses": "💼",
    }

    grand_total = 0.0

    # Print each category
    for main_cat in [
        "Food & Dining",
        "Housing & Utilities",
        "Transportation",
        "Healthcare & Insurance",
        "Personal & Lifestyle",
        "Shopping",
        "Work Expenses",
    ]:
        if main_cat not in category_totals:
            continue

        subcategories = category_totals[main_cat]
        category_total = sum(subcategories.values())
        category_avg = category_total / months
        grand_total += category_total

        emoji = category_emojis.get(main_cat, "")
        print(f"{emoji} {main_cat:<30} ${category_avg:>10,.2f}")

        # Print subcategories (sorted by amount, descending)
        if args.output == "detailed" or len(subcategories) > 0:
            sorted_subcats = sorted(subcategories.items(), key=lambda x: x[1], reverse=True)
            for i, (subcat, total) in enumerate(sorted_subcats):
                avg = total / months
                # Extract just the last part of the path for cleaner display
                display_name = subcat.split(" > ")[-1] if " > " in subcat else subcat
                # Use different prefix for last item
                prefix = "   └─" if i == len(sorted_subcats) - 1 else "   ├─"
                print(f"{prefix} {display_name:<27} ${avg:>10,.2f}")
        print()

    # Print kids transfers
    if kids_transfer_total > 0:
        kids_avg = kids_transfer_total / months
        grand_total += kids_transfer_total
        print(f"💸 Transfers (Kids Account)        ${kids_avg:>10,.2f}")
        print()

    # Print total
    print("-" * 70)
    total_avg = grand_total / months
    print(f"TOTAL AVERAGE MONTHLY              ${total_avg:>10,.2f}")
    print("=" * 70)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
