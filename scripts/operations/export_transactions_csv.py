#!/usr/bin/env python3
"""Export transactions to CSV for specified categories over a date range."""

import argparse
import csv
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from scripts.core.api_client import PocketSmithClient
from scripts.core.category_utils import find_category_by_id, get_category_path


def calculate_date_range(months: int = 3) -> Tuple[str, str]:
    """Calculate start and end dates for the last N months.

    Args:
        months: Number of months to look back (default: 3)

    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    return (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))


def is_kids_transfer(txn: Dict[str, Any], accounts: List[Dict[str, Any]]) -> bool:
    """Check if a transaction is a transfer to kids account.

    Args:
        txn: Transaction object
        accounts: List of all transaction accounts

    Returns:
        True if this is a transfer to a kids account
    """
    # Check if it's a transfer transaction
    if not txn.get("is_transfer", False):
        return False

    # Check payee and note for kids-related keywords
    payee = (txn.get("payee") or "").lower()
    note = (txn.get("note") or "").lower()
    keywords = ["kids", "kid", "child", "children", "son", "daughter"]

    if any(keyword in payee or keyword in note for keyword in keywords):
        return True

    # Check if the transaction account name contains kids-related keywords
    account_id = txn.get("transaction_account_id")
    if account_id:
        for account in accounts:
            if account.get("id") == account_id:
                account_name = (account.get("name") or "").lower()
                if any(keyword in account_name for keyword in keywords):
                    return True

    return False


def matches_target_categories(
    txn: Dict[str, Any], categories: List[Dict[str, Any]], target_categories: List[str]
) -> bool:
    """Check if transaction belongs to one of the target categories.

    Args:
        txn: Transaction object
        categories: Flat list of all categories
        target_categories: List of parent category names to match

    Returns:
        True if transaction matches any target category
    """
    category_obj = txn.get("category")
    if not category_obj:
        return False

    category_id = category_obj.get("id")
    if not category_id:
        return False

    category = find_category_by_id(categories, category_id)
    if not category:
        return False

    # Get full category path
    path = get_category_path(categories, category)

    # Check if any part of the path matches our target categories
    for target in target_categories:
        if any(target.lower() in part.lower() for part in path):
            return True

    return False


def get_account_name(txn: Dict[str, Any], accounts: List[Dict[str, Any]]) -> str:
    """Get the account name for a transaction.

    Args:
        txn: Transaction object
        accounts: List of all transaction accounts

    Returns:
        Account name or "Unknown"
    """
    # First try the nested transaction_account object (most reliable)
    transaction_account = txn.get("transaction_account")
    if transaction_account and isinstance(transaction_account, dict):
        account_name = transaction_account.get("name")
        if account_name:
            return str(account_name)

    # Fallback: try transaction_account_id and look it up in accounts list
    account_id = txn.get("transaction_account_id")
    if account_id:
        for account in accounts:
            if account.get("id") == account_id:
                name = account.get("name")
                return str(name) if name is not None else "Unknown"

    return "Unknown"


def format_transaction_for_csv(
    txn: Dict[str, Any], categories: List[Dict[str, Any]], accounts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Format a transaction for CSV export.

    Args:
        txn: Transaction object
        categories: Flat list of all categories
        accounts: List of all transaction accounts

    Returns:
        Dict with formatted fields for CSV
    """
    # Get category path
    category_obj = txn.get("category")
    parent_category = ""
    subcategory = ""

    if category_obj:
        category_id = category_obj.get("id")
        if category_id:
            category = find_category_by_id(categories, category_id)
            if category:
                path = get_category_path(categories, category)
                if len(path) >= 1:
                    parent_category = path[0]
                if len(path) >= 2:
                    subcategory = path[-1]  # Last item in path is the most specific

    # Format date
    date_str = txn.get("date", "")
    try:
        date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        formatted_date = date_obj.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        formatted_date = date_str

    # Get amount (preserve sign - negative for debits, positive for credits)
    amount = float(txn.get("amount", 0))

    # Get labels as comma-separated string
    labels = txn.get("labels", [])
    labels_str = ", ".join(labels) if labels else ""

    # Get memo/notes
    note = txn.get("note", "") or ""

    return {
        "Date": formatted_date,
        "Payee": txn.get("payee", ""),
        "Amount": f"{amount:.2f}",
        "Category": parent_category,
        "Subcategory": subcategory if subcategory != parent_category else "",
        "Account": get_account_name(txn, accounts),
        "Notes": note,
        "Labels": labels_str,
    }


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--months", type=int, default=3, help="Number of months to look back (default: 3)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output CSV file path (default: reports/transactions_<months>_months.csv)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="export_all",
        help="Export all transactions without category filtering",
    )
    args = parser.parse_args()

    # Set default output based on months if not specified
    if args.output is None:
        args.output = f"reports/transactions_{args.months}_months.csv"

    # Initialize API client
    print("Initializing PocketSmith API client...", flush=True)
    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    # Calculate date range
    start_date, end_date = calculate_date_range(args.months)
    print(f"Fetching transactions from {start_date} to {end_date}...", flush=True)

    # Fetch all categories (flattened)
    print("Fetching categories...", flush=True)
    categories = client.get_categories(user_id, flatten=True)

    # Fetch all transaction accounts
    print("Fetching accounts...", flush=True)
    accounts = client.get_transaction_accounts(user_id)

    # Fetch all transactions for the period
    print("Fetching transactions...", flush=True)
    transactions = client.get_all_transactions(
        user_id=user_id, start_date=start_date, end_date=end_date
    )
    print(f"Fetched {len(transactions)} total transactions", flush=True)

    # Define target categories (used when not exporting all)
    target_categories = [
        "Food & Dining",
        "Housing & Utilities",
        "Transportation",
        "Healthcare & Insurance",
        "Personal & Lifestyle",
        "Shopping",
        "Work Expenses",
    ]

    # Filter and format transactions
    if args.export_all:
        print("Exporting all transactions (no filtering)...", flush=True)
    else:
        print("Filtering transactions by category...", flush=True)

    csv_rows = []
    category_counts: Dict[str, int] = {}

    for txn in transactions:
        if args.export_all:
            # Export all transactions without filtering
            row = format_transaction_for_csv(txn, categories, accounts)
            csv_rows.append(row)

            # Count by category
            cat_key = row["Category"] or "Uncategorized"
            if row["Subcategory"]:
                cat_key = f"{row['Category']} > {row['Subcategory']}"
            category_counts[cat_key] = category_counts.get(cat_key, 0) + 1
        else:
            # Check if it's a kids transfer
            if is_kids_transfer(txn, accounts):
                row = format_transaction_for_csv(txn, categories, accounts)
                row["Category"] = "Transfers"
                row["Subcategory"] = "Kids Account"
                csv_rows.append(row)
                key = "Transfers (Kids Account)"
                category_counts[key] = category_counts.get(key, 0) + 1
                continue

            # Check if it matches target categories
            if matches_target_categories(txn, categories, target_categories):
                row = format_transaction_for_csv(txn, categories, accounts)
                csv_rows.append(row)

                # Count by category
                cat_key = row["Category"]
                if row["Subcategory"]:
                    cat_key = f"{row['Category']} > {row['Subcategory']}"
                category_counts[cat_key] = category_counts.get(cat_key, 0) + 1

    print(f"Total transactions to export: {len(csv_rows)}", flush=True)

    # Sort by date descending (most recent first)
    csv_rows.sort(key=lambda x: x["Date"], reverse=True)

    # Create output directory if needed
    output_path = args.output
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        print(f"Creating directory: {output_dir}", flush=True)
        os.makedirs(output_dir, exist_ok=True)

    # Write CSV
    print(f"Writing CSV to: {output_path}", flush=True)
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Date",
            "Payee",
            "Amount",
            "Category",
            "Subcategory",
            "Account",
            "Notes",
            "Labels",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)

    print("\nCSV export complete!", flush=True)
    print(f"File: {os.path.abspath(output_path)}", flush=True)
    print(f"Total transactions: {len(csv_rows)}", flush=True)

    # Print category breakdown
    print("\nTransactions by category:", flush=True)
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}", flush=True)

    # Print sample of first 5 rows
    print("\nSample (first 5 rows):", flush=True)
    print("-" * 80, flush=True)
    for i, row in enumerate(csv_rows[:5]):
        line = f"{row['Date']} | {row['Payee']:<30} | " f"${row['Amount']:>10} | {row['Category']}"
        print(line, flush=True)
    print("-" * 80, flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
