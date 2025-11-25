#!/usr/bin/env python
"""Find or create Online Payments category."""

from typing import List, Dict, Any, Optional
from scripts.core.api_client import PocketSmithClient
from dotenv import load_dotenv

load_dotenv()
client = PocketSmithClient()
user = client.get_user()
user_id = user["id"]

# Get all categories
categories = client.get_categories(user_id)


def find_category(cats: List[Dict[str, Any]], name: str, indent: int = 0) -> Optional[int]:
    """Recursively search for category and print tree."""
    for cat in cats:
        title = cat.get("title")
        cat_id: int = cat["id"]
        print("  " * indent + f"- {title} (ID: {cat_id})")

        if title == name:
            return cat_id

        if cat.get("children"):
            child_id = find_category(cat["children"], name, indent + 1)
            if child_id:
                return child_id
    return None


print("Existing categories:")
online_payments_id = find_category(categories, "Online Payments")

if online_payments_id:
    print(f'\nFound "Online Payments" with ID: {online_payments_id}')
else:
    print('\n"Online Payments" category not found')

    # Look for Shopping or Online Services as potential parents
    shopping_id = find_category(categories, "Shopping")
    online_services_id = find_category(categories, "Online Services")

    if online_services_id:
        suggestion = "- could rename or create sibling"
        print(f'Found "Online Services" (ID: {online_services_id}) {suggestion}')
    if shopping_id:
        print(f'Found "Shopping" (ID: {shopping_id})')
