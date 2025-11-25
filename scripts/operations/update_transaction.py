#!/usr/bin/env python
"""Update transaction category and labels.

This script provides deterministic transaction updates for the review workflow.
Handles clearing conflict labels and updating categories.
"""

import sys
import json
from typing import List, Optional
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient
from scripts.core.labels import remove_review_labels


def update_transaction(
    txn_id: int,
    category_id: Optional[int] = None,
    clear_conflict: bool = True,
    preserve_labels: bool = True,
    existing_labels: Optional[List[str]] = None,
) -> dict:
    """Update a transaction's category and/or labels.

    Args:
        txn_id: Transaction ID
        category_id: New category ID (None = don't change)
        clear_conflict: Remove conflict-related labels
        preserve_labels: Keep non-conflict labels
        existing_labels: Current labels (for preservation)

    Returns:
        Updated transaction data
    """
    load_dotenv()
    client = PocketSmithClient()

    # Prepare update payload
    updates: dict = {}

    # Handle labels
    if clear_conflict:
        if preserve_labels and existing_labels:
            # Remove only review/conflict labels, preserve user labels
            new_labels: List[str] = remove_review_labels(existing_labels)
        else:
            # Clear all labels
            new_labels = []
        updates["labels"] = new_labels
        # Clear conflict note
        updates["note"] = ""

    # Update category if specified
    if category_id is not None:
        updates["category_id"] = category_id

    # Apply update
    result = client.update_transaction(txn_id, **updates)

    return result


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Update transaction category and labels")
    parser.add_argument("transaction_id", type=int, help="Transaction ID to update")
    parser.add_argument("--category-id", type=int, help="New category ID")
    parser.add_argument("--category-name", help="New category name (will lookup ID)")
    parser.add_argument(
        "--clear-conflict",
        action="store_true",
        default=True,
        help="Remove conflict labels (default: true)",
    )
    parser.add_argument(
        "--preserve-labels",
        action="store_true",
        default=True,
        help="Keep non-conflict labels (default: true)",
    )
    parser.add_argument("--existing-labels", nargs="*", help="Current labels (for preservation)")
    parser.add_argument(
        "--output", choices=["json", "summary"], default="summary", help="Output format"
    )

    args = parser.parse_args()

    # Lookup category ID by name if needed
    category_id = args.category_id
    if args.category_name and not category_id:
        load_dotenv()
        client = PocketSmithClient()
        user = client.get_user()
        categories = client.get_categories(user["id"])

        def find_category(cats: List[dict], name: str) -> Optional[int]:
            for cat in cats:
                if cat.get("title") == name:
                    cat_id: int = cat["id"]
                    return cat_id
                if cat.get("children"):
                    child_id = find_category(cat["children"], name)
                    if child_id:
                        return child_id
            return None

        category_id = find_category(categories, args.category_name)
        if not category_id:
            print(f"Error: Category '{args.category_name}' not found", file=sys.stderr)
            return 1

    # Update transaction
    result = update_transaction(
        args.transaction_id,
        category_id=category_id,
        clear_conflict=args.clear_conflict,
        preserve_labels=args.preserve_labels,
        existing_labels=args.existing_labels,
    )

    if args.output == "json":
        print(json.dumps(result, indent=2))
    elif args.output == "summary":
        cat_title = result.get("category", {}).get("title", "Uncategorized")
        print(f"✓ Updated transaction {args.transaction_id}")
        if category_id:
            print(f"  Category: {cat_title}")
        if args.clear_conflict:
            print("  Cleared conflict flag")

    return 0


if __name__ == "__main__":
    sys.exit(main())
