#!/usr/bin/env python3
"""Explore category structure in PocketSmith."""

import sys
from collections import defaultdict
from scripts.core.api_client import PocketSmithClient


def main() -> int:
    """Main function."""
    # Initialize API client
    print("Initializing PocketSmith API client...")
    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    # Fetch all categories (flattened)
    print("Fetching categories...")
    categories = client.get_categories(user_id, flatten=True)

    # Exclude transfer categories
    non_transfer = [c for c in categories if not c.get("is_transfer", False)]

    print(f"\nFound {len(categories)} total categories ({len(non_transfer)} non-transfer)\n")

    # Group by parent
    parent_categories = defaultdict(list)

    for cat in non_transfer:
        if cat.get("parent_id"):
            parent_id = cat["parent_id"]
            parent_categories[parent_id].append(cat)
        else:
            # Root category
            parent_categories[None].append(cat)

    # Print root categories and their children
    root_cats = sorted(parent_categories[None], key=lambda c: c.get("title", ""))

    for root in root_cats:
        print(f"📁 {root['title']} (ID: {root['id']})")

        children = parent_categories.get(root["id"], [])
        for child in sorted(children, key=lambda c: c.get("title", "")):
            print(f"   ├─ {child['title']} (ID: {child['id']})")

        if not children:
            print("   └─ (no subcategories)")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
