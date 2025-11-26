#!/usr/bin/env python
"""Interactive review of conflict transactions with intelligent grouping.

This script provides an optimized workflow:
1. Group transactions by common payee patterns
2. Process groups first (batch categorization + rule creation)
3. Process remaining ungrouped transactions individually
"""

import sys
from typing import Dict, Any
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient
from scripts.core.labels import has_review_flag, remove_review_labels
from scripts.operations.group_conflicts import group_transactions_by_pattern


def get_all_categories(client: PocketSmithClient, user_id: int) -> Dict[str, int]:
    """Fetch and flatten all categories into a name -> ID map.

    Args:
        client: API client
        user_id: User ID

    Returns:
        Dictionary mapping category names to IDs
    """
    categories = client.get_categories(user_id)
    category_map = {}

    def flatten(cats: list, parent_name: str | None = None) -> None:
        for cat in cats:
            name = cat["title"]
            # Store both simple name and hierarchical name
            category_map[name] = cat["id"]
            if parent_name:
                hierarchical = f"{parent_name}:{name}"
                category_map[hierarchical] = cat["id"]

            if cat.get("children"):
                flatten(cat["children"], name)

    flatten(categories)
    return category_map


def process_group_batch(
    client: PocketSmithClient, group: Dict[str, Any], category_map: Dict[str, int]
) -> Dict[str, Any]:
    """Process a group of transactions with the same pattern.

    Presents the group to user, lets them choose category and whether
    to create a rule, then applies to all transactions in the group.

    Args:
        client: API client
        group: Group dict with pattern, transactions, count
        category_map: Category name -> ID mapping

    Returns:
        Result dict with action taken and counts
    """
    pattern = group["pattern"]
    transactions = group["transactions"]
    count = group["count"]

    print("=" * 70)
    print(f"\nGROUP: {count} transactions matching '{pattern}'")
    print("\nSample transactions:")
    for i, txn in enumerate(transactions[:5], 1):
        date = txn.get("date")
        payee = txn.get("payee", "")[:60]
        amount = abs(txn.get("amount", 0))
        current_cat = txn.get("category", {}).get("title", "Uncategorized")
        print(f"  {i}. {date} | ${amount:.2f} | {current_cat}")
        print(f"     {payee}")

    if len(transactions) > 5:
        print(f"  ... and {len(transactions) - 5} more")

    print("\nOptions:")
    print(f"1. Categorize all {count} transactions and create rule")
    print("2. Skip this group (review individually later)")
    print("0. Exit review")

    choice = input("\nYour choice: ").strip()

    if choice == "0":
        return {"action": "exit"}

    elif choice == "2":
        return {"action": "skip", "count": count}

    elif choice == "1":
        # Select category
        print("\nSelect category for these transactions:")
        category_names = sorted(category_map.keys())

        # Show common categories first
        common = [
            "Groceries",
            "Restaurants",
            "Cafes & Takeaway",
            "Fuel",
            "Phone",
            "Internet & Phone",
            "Online Services",
            "Shopping",
            "Utilities",
        ]
        print("\nCommon categories:")
        for i, name in enumerate(common, 1):
            if name in category_map:
                print(f"  {i}. {name}")

        print(f"\n  {len(common) + 1}. Browse all categories")
        print("  0. Cancel")

        cat_choice = input("\nCategory choice: ").strip()

        if cat_choice == "0":
            return {"action": "cancel"}

        # Parse choice
        selected_category = None
        try:
            idx = int(cat_choice) - 1
            if 0 <= idx < len(common) and common[idx] in category_map:
                selected_category = common[idx]
            elif idx == len(common):
                # Browse all
                print("\nAll categories:")
                for i, name in enumerate(category_names, 1):
                    print(f"  {i}. {name}")
                full_choice = input("\nCategory number: ").strip()
                try:
                    full_idx = int(full_choice) - 1
                    if 0 <= full_idx < len(category_names):
                        selected_category = category_names[full_idx]
                except ValueError:
                    # Try as name
                    if full_choice in category_map:
                        selected_category = full_choice
        except ValueError:
            # Try as name directly
            if cat_choice in category_map:
                selected_category = cat_choice

        if not selected_category:
            print("Invalid category selection")
            return {"action": "cancel"}

        category_id = category_map[selected_category]

        # Ask about rule creation
        print(f"\nWill categorize {count} transactions as '{selected_category}'")
        print(f"Create a rule for pattern '{pattern}'?")
        print("1. Yes, create rule (will auto-categorize future matches)")
        print("2. No, just update these transactions")

        rule_choice = input("\nChoice: ").strip()
        create_rule = rule_choice == "1"

        # Apply to all transactions in group
        print(f"\nUpdating {count} transactions...")
        updated = 0
        for txn in transactions:
            txn_id = txn["id"]
            existing_labels = txn.get("labels", [])
            new_labels = remove_review_labels(existing_labels)

            try:
                client.update_transaction(
                    txn_id, category_id=category_id, labels=new_labels, note=""
                )
                updated += 1
            except Exception as e:
                print(f"  Warning: Failed to update transaction {txn_id}: {e}")

        print(f"✓ Updated {updated}/{count} transactions to '{selected_category}'")

        # Create rule if requested
        rule_created = False
        if create_rule:
            try:
                from scripts.operations.create_rule import create_rule as create_rule_fn

                rule = create_rule_fn(
                    pattern, selected_category, confidence=85, pattern_type="keyword"
                )
                print(f"✓ Created rule: {rule['name']}")
                rule_created = True
            except Exception as e:
                print(f"  Warning: Failed to create rule: {e}")

        return {
            "action": "processed",
            "count": updated,
            "category": selected_category,
            "rule_created": rule_created,
        }

    else:
        print("Invalid choice")
        return {"action": "cancel"}


def process_individual(
    client: PocketSmithClient,
    txn: Dict[str, Any],
    category_map: Dict[str, int],
    idx: int,
    total: int,
) -> Dict[str, Any]:
    """Process a single ungrouped transaction.

    Args:
        client: API client
        txn: Transaction dict
        category_map: Category name -> ID mapping
        idx: Current index (1-based)
        total: Total ungrouped count

    Returns:
        Result dict with action taken
    """
    print("=" * 70)
    print(f"\nTransaction {idx}/{total}")

    date = txn.get("date")
    payee = txn.get("payee", "")
    amount = abs(txn.get("amount", 0))
    current_cat = txn.get("category", {}).get("title", "Uncategorized")
    labels = txn.get("labels", [])
    note = txn.get("note", "")

    print(f"Date: {date}")
    print(f"Payee: {payee}")
    print(f"Amount: ${amount:.2f}")
    print(f"Current Category: {current_cat}")
    if note:
        print(f"Note: {note}")

    print("\nOptions:")
    print("1. Accept (keep current category, clear review flag)")
    print("2. Specify Category")
    print("3. Skip (review later)")
    print("0. Exit review")

    choice = input("\nYour choice: ").strip()

    if choice == "0":
        return {"action": "exit"}

    elif choice == "3":
        return {"action": "skip"}

    elif choice == "1":
        # Accept current category
        new_labels = remove_review_labels(labels)
        try:
            client.update_transaction(txn["id"], labels=new_labels, note="")
            print(f"✓ Accepted '{current_cat}'")
            return {"action": "accepted", "category": current_cat}
        except Exception as e:
            print(f"Error: {e}")
            return {"action": "error"}

    elif choice == "2":
        # Specify category
        category_names = sorted(category_map.keys())
        print("\nCategories:")
        for i, name in enumerate(category_names[:20], 1):
            print(f"  {i}. {name}")
        if len(category_names) > 20:
            print(f"  ... and {len(category_names) - 20} more")

        cat_input = input("\nCategory number or name: ").strip()

        selected_category = None
        try:
            idx = int(cat_input) - 1
            if 0 <= idx < len(category_names):
                selected_category = category_names[idx]
        except ValueError:
            if cat_input in category_map:
                selected_category = cat_input

        if not selected_category:
            print("Invalid category")
            return {"action": "error"}

        category_id = category_map[selected_category]
        new_labels = remove_review_labels(labels)

        try:
            client.update_transaction(
                txn["id"], category_id=category_id, labels=new_labels, note=""
            )
            print(f"✓ Recategorized to '{selected_category}'")
            return {"action": "recategorized", "category": selected_category}
        except Exception as e:
            print(f"Error: {e}")
            return {"action": "error"}

    else:
        print("Invalid choice")
        return {"action": "error"}


def main() -> int:
    """Main entry point."""
    load_dotenv()
    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    # Fetch all conflicts
    print("Fetching transactions with review flags...", flush=True)
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
        print("\n✓ No transactions flagged for review!")
        return 0

    print(f"\nFound {len(all_conflicts)} transactions flagged for review")

    # Group transactions
    print("\nAnalyzing patterns...")
    grouping_result = group_transactions_by_pattern(all_conflicts)
    groups = grouping_result["groups"]
    ungrouped = grouping_result["ungrouped"]
    stats = grouping_result["stats"]

    print("\nGrouping Summary:")
    print(f"  Groups: {stats['num_groups']} ({stats['grouped']} transactions)")
    print(f"  Ungrouped: {stats['ungrouped']} (unique patterns)")

    # Get categories
    category_map = get_all_categories(client, user_id)

    # Statistics
    groups_processed = 0
    groups_skipped = 0
    transactions_updated = 0
    rules_created = 0
    individuals_accepted = 0
    individuals_recategorized = 0
    individuals_skipped = 0

    # Phase 1: Process groups
    if groups:
        print("\n" + "=" * 70)
        print("PHASE 1: Review Groups")
        print("=" * 70)

        for group in groups:
            result = process_group_batch(client, group, category_map)

            if result["action"] == "exit":
                break
            elif result["action"] == "processed":
                groups_processed += 1
                transactions_updated += result["count"]
                if result.get("rule_created"):
                    rules_created += 1
            elif result["action"] == "skip":
                groups_skipped += 1
                # Add to ungrouped for individual processing
                ungrouped.extend(group["transactions"])

    # Phase 2: Process ungrouped individuals
    if ungrouped and result.get("action") != "exit":
        print("\n" + "=" * 70)
        print("PHASE 2: Review Individual Transactions")
        print("=" * 70)
        print(f"\n{len(ungrouped)} transactions to review individually\n")

        for idx, txn in enumerate(ungrouped, 1):
            result = process_individual(client, txn, category_map, idx, len(ungrouped))

            if result["action"] == "exit":
                break
            elif result["action"] == "accepted":
                individuals_accepted += 1
                transactions_updated += 1
            elif result["action"] == "recategorized":
                individuals_recategorized += 1
                transactions_updated += 1
            elif result["action"] == "skip":
                individuals_skipped += 1

    # Final Summary
    print("\n" + "=" * 70)
    print("Review Complete")
    print("=" * 70)
    print("\nGroups:")
    print(f"  Processed: {groups_processed}")
    print(f"  Skipped: {groups_skipped}")
    print("\nIndividual Transactions:")
    print(f"  Accepted: {individuals_accepted}")
    print(f"  Recategorized: {individuals_recategorized}")
    print(f"  Skipped: {individuals_skipped}")
    print("\nTotal:")
    print(f"  Transactions updated: {transactions_updated}")
    print(f"  Rules created: {rules_created}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
