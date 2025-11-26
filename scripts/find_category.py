#!/usr/bin/env python
"""Find or create Online Payments category."""

from typing import List, Dict, Any
from scripts.core.api_client import PocketSmithClient
from scripts.core.category_utils import find_category_by_name
from dotenv import load_dotenv

load_dotenv()
client = PocketSmithClient()
user = client.get_user()
user_id = user["id"]

# Get categories - hierarchical for display, flattened for searching
categories_hierarchical = client.get_categories(user_id, flatten=False)
categories_flat = client.get_categories(user_id, flatten=True)


def print_category_tree(cats: List[Dict[str, Any]], indent: int = 0) -> None:
    """Print category tree recursively."""
    for cat in cats:
        title = cat.get("title")
        cat_id: int = cat["id"]
        print("  " * indent + f"- {title} (ID: {cat_id})")

        if cat.get("children"):
            print_category_tree(cat["children"], indent + 1)


print("Existing categories:")
print_category_tree(categories_hierarchical)

# Search in flattened list (much simpler!)
online_payments = find_category_by_name(categories_flat, "Online Payments")

if online_payments:
    print(f'\n✓ Found "Online Payments" with ID: {online_payments["id"]}')
else:
    print('\n✗ "Online Payments" category not found')

    # Look for Shopping or Online Services as potential parents
    shopping = find_category_by_name(categories_flat, "Shopping")
    online_services = find_category_by_name(categories_flat, "Online Services")

    if online_services:
        suggestion = "- could rename or create sibling"
        print(f'Found "Online Services" (ID: {online_services["id"]}) {suggestion}')
    if shopping:
        print(f'Found "Shopping" (ID: {shopping["id"]})')
