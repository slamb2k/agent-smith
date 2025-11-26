#!/usr/bin/env python
"""Interactive review process for transactions flagged with conflicts."""

import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient
from scripts.core.labels import has_review_flag, remove_review_labels

load_dotenv()


def get_category_suggestions(payee: str, categories: List[Dict[str, Any]]) -> List[str]:
    """Suggest categories based on transaction payee text.

    Args:
        payee: Transaction payee text
        categories: List of available categories

    Returns:
        List of suggested category names
    """
    suggestions = []
    payee_lower = payee.lower()

    # Common patterns to category mappings
    patterns = {
        "Phone": ["telstra", "optus", "vodafone", "mobile", "recharge"],
        "Software & Apps": ["google", "microsoft", "adobe", "app", "software"],
        "Household": ["ebay", "amazon", "furniture", "appliance"],
        "Online Services": ["subscription", "service", "hosting", "domain"],
        "Pets/Pet Care": ["pet", "vet", "animal"],
        "Healthcare / Medical": ["medical", "health", "doctor", "clinic"],
        "General Merchandise": ["store", "shop", "retail"],
        "Work-Related Expenses": ["work", "office", "professional"],
    }

    for category, keywords in patterns.items():
        if any(keyword in payee_lower for keyword in keywords):
            suggestions.append(category)

    return suggestions[:3]  # Return top 3 suggestions


def flatten_categories(categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flatten category hierarchy."""
    result = []
    for cat in categories:
        result.append(cat)
        if cat.get("children"):
            result.extend(flatten_categories(cat["children"]))
    return result


def clear_conflict_label(client: PocketSmithClient, txn_id: int, current_labels: List[str]) -> None:
    """Remove conflict label from transaction.

    Args:
        client: PocketSmith API client
        txn_id: Transaction ID
        current_labels: Current transaction labels
    """
    # Remove all review/conflict labels
    new_labels = remove_review_labels(current_labels)
    client.update_transaction(txn_id, labels=new_labels, note="")


def recategorize_transaction(
    client: PocketSmithClient, txn_id: int, category_id: int, current_labels: List[str]
) -> None:
    """Recategorize transaction and clear conflict label.

    Args:
        client: PocketSmith API client
        txn_id: Transaction ID
        category_id: New category ID
        current_labels: Current transaction labels
    """
    # Remove all review/conflict labels
    new_labels = remove_review_labels(current_labels)
    client.update_transaction(txn_id, category_id=category_id, labels=new_labels, note="")


def main() -> int:
    """Main entry point."""
    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    print("Agent Smith - Interactive Conflict Review")
    print("=" * 70)
    print()
    print("Fetching transactions flagged for review...")

    # Get all transactions with conflict labels
    all_conflicts = []
    page = 1
    while True:
        batch = client.get_transactions(
            user_id, start_date="2025-01-01", end_date="2025-12-31", page=page, per_page=100
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

    if not all_conflicts:
        print("✓ No conflicts found! All transactions are properly categorized.")
        return 0

    print(f"Found {len(all_conflicts)} transactions for review")
    print()

    # Get categories for suggestions and recategorization
    categories = client.get_categories(user_id)
    flat_cats = flatten_categories(categories)
    category_map = {cat["title"]: cat["id"] for cat in flat_cats}
    category_names = sorted(category_map.keys())

    # Process each conflict
    reviewed_count = 0
    accepted_count = 0
    recategorized_count = 0
    skipped_count = 0

    for idx, txn in enumerate(all_conflicts, 1):
        payee = txn.get("payee", "")
        amount = txn.get("amount", 0)
        date = txn.get("date", "")
        current_cat = txn.get("category", {}).get("title", "(none)")
        labels = txn.get("labels", [])
        note = txn.get("note", "")

        # Extract suggested category from note
        suggested = ""
        if "suggests:" in note:
            suggested = note.split("suggests:")[1].strip()

        print("=" * 70)
        print(f"Transaction {idx}/{len(all_conflicts)}")
        print()
        print(f"Date: {date}")
        print(f"Payee: {payee}")
        print(f"Amount: ${amount:,.2f}")
        print(f"Current Category: {current_cat}")
        if suggested:
            print(f"Rule Suggests: {suggested}")
        print()

        # Get AI suggestions
        suggestions = get_category_suggestions(payee, flat_cats)

        # Build options
        options = ["Accept (keep current category)", "Next (skip)", "Specify Category"]

        if suggestions:
            print("Suggested categories based on payee:")
            for i, sug in enumerate(suggestions, 4):
                if sug in category_map:
                    options.append(f"{sug}")
                    print(f"  {i}. {sug}")
            print()

        print("Options:")
        for i, opt in enumerate(options[:3], 1):
            print(f"  {i}. {opt}")

        if len(options) > 3:
            for i in range(3, len(options)):
                print(f"  {i+1}. {options[i]}")

        print("  0. Exit")
        print()

        # Get user choice
        try:
            choice = input("Choose option: ").strip()

            if choice == "0":
                print("\nExiting review process.")
                break

            elif choice == "1":
                # Accept current category
                clear_conflict_label(client, txn["id"], labels)
                print(f'✓ Accepted "{current_cat}"')
                accepted_count += 1
                reviewed_count += 1

            elif choice == "2":
                # Skip
                print("→ Skipped")
                skipped_count += 1

            elif choice == "3":
                # Specify category
                print()
                print("Available categories:")
                for i, cat_name in enumerate(category_names, 1):
                    print(f"  {i}. {cat_name}")
                print()

                cat_choice = input("Enter category number or name: ").strip()

                # Try to parse as number
                try:
                    cat_idx = int(cat_choice) - 1
                    if 0 <= cat_idx < len(category_names):
                        selected_cat = category_names[cat_idx]
                    else:
                        print("Invalid category number")
                        continue
                except ValueError:
                    # Treat as category name
                    selected_cat = cat_choice

                if selected_cat in category_map:
                    recategorize_transaction(client, txn["id"], category_map[selected_cat], labels)
                    print(f'✓ Recategorized to "{selected_cat}"')
                    recategorized_count += 1
                    reviewed_count += 1
                else:
                    print(f'Category "{selected_cat}" not found')
                    continue

            elif choice.isdigit() and int(choice) > 3:
                # Quick select from suggestions
                suggestion_idx = int(choice) - 4
                if 0 <= suggestion_idx < len(suggestions):
                    selected_cat = suggestions[suggestion_idx]
                    if selected_cat in category_map:
                        recategorize_transaction(
                            client, txn["id"], category_map[selected_cat], labels
                        )
                        print(f'✓ Recategorized to "{selected_cat}"')
                        recategorized_count += 1
                        reviewed_count += 1
                    else:
                        print(f'Category "{selected_cat}" not found')
                        continue
                else:
                    print("Invalid option")
                    continue

            else:
                print("Invalid option")
                continue

            print()

        except KeyboardInterrupt:
            print("\n\nExiting review process.")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    # Summary
    print("=" * 70)
    print("Review Summary:")
    print(f"  Total reviewed: {reviewed_count}/{len(all_conflicts)}")
    print(f"  Accepted: {accepted_count}")
    print(f"  Recategorized: {recategorized_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Remaining: {len(all_conflicts) - reviewed_count}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
