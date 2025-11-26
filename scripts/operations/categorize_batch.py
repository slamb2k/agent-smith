"""Batch transaction categorization script using new workflow.

This script processes multiple transactions using the hybrid workflow:
1. Apply rules to all transactions
2. Batch uncategorized transactions → LLM (Case 1)
3. Batch medium-confidence validations → LLM (Case 2)
4. Apply results to PocketSmith
"""

import sys
import logging
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient
from scripts.workflows.categorization import CategorizationWorkflow
from scripts.core.labels import LABEL_CATEGORY_CONFLICT, add_review_label

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def find_category_by_name(
    categories: List[Dict[str, Any]], category_name: str
) -> Optional[Dict[str, Any]]:
    """Find a category by name with fallback matching.

    Tries multiple matching strategies:
    1. Exact match on title
    2. Case-insensitive match
    3. Extract child name from "Parent > Child" format
    4. Partial match on title

    Args:
        categories: List of category dicts with 'id' and 'title'
        category_name: Category name to find (may be in various formats)

    Returns:
        Category dict if found, None otherwise
    """
    if not category_name:
        return None

    # Strategy 1: Exact match
    for cat in categories:
        if cat["title"] == category_name:
            return cat

    # Strategy 2: Case-insensitive match
    category_lower = category_name.lower()
    for cat in categories:
        if cat["title"].lower() == category_lower:
            logger.debug(
                f"Category matched case-insensitively: '{category_name}' -> '{cat['title']}'"
            )
            return cat

    # Strategy 3: Handle "Parent > Child" format - extract child name
    if " > " in category_name:
        child_name = category_name.split(" > ")[-1].strip()
        for cat in categories:
            if cat["title"] == child_name:
                logger.debug(
                    f"Category matched via child extraction: '{category_name}' -> '{cat['title']}'"
                )
                return cat
            if cat["title"].lower() == child_name.lower():
                logger.debug(
                    f"Category matched via child (case-insensitive): "
                    f"'{category_name}' -> '{cat['title']}'"
                )
                return cat

    # Strategy 4: Partial match (category_name contains the title or vice versa)
    for cat in categories:
        if cat["title"].lower() in category_lower or category_lower in cat["title"].lower():
            logger.debug(
                f"Category matched via partial match: '{category_name}' -> '{cat['title']}'"
            )
            return cat

    # No match found - log warning
    available = [c["title"] for c in categories[:10]]
    logger.warning(f"Category not found: '{category_name}'. Available: {available}...")
    return None


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Batch categorize transactions using hybrid rules + LLM workflow"
    )

    parser.add_argument(
        "--period",
        type=str,
        help="Period to process (YYYY-MM or 'last-30-days')",
        default="last-30-days",
    )

    parser.add_argument(
        "--account",
        type=str,
        help="Specific account name to process (optional)",
        default=None,
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["conservative", "smart", "aggressive"],
        default="smart",
        help="Intelligence mode (conservative|smart|aggressive)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying",
    )

    return parser.parse_args()


def get_transactions(
    client: PocketSmithClient,
    period: str,
    account_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch transactions for the specified period.

    Args:
        client: PocketSmith API client
        period: Period string (YYYY-MM or 'last-30-days')
        account_filter: Optional account name filter

    Returns:
        List of transaction dicts
    """
    user = client.get_user()

    # Parse period into date range
    if period == "last-30-days":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    elif "-" in period:
        # Format: YYYY-MM
        year, month = period.split("-")
        start_date = datetime(int(year), int(month), 1)
        # End date is last day of month
        if int(month) == 12:
            end_date = datetime(int(year) + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(int(year), int(month) + 1, 1) - timedelta(days=1)
    else:
        raise ValueError(f"Invalid period format: {period}")

    # Fetch ALL transactions with pagination
    print(f"Fetching transactions for {period}...", end="", flush=True)
    all_transactions = []
    page = 1
    while True:
        batch = client.get_transactions(
            user_id=user["id"],
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            page=page,
            per_page=100,
        )
        if not batch:
            break
        all_transactions.extend(batch)
        print(f" {len(all_transactions)}", end="", flush=True)
        if len(batch) < 100:  # Last page
            break
        page += 1
    print(" transactions fetched.")

    # Filter by account if specified
    if account_filter:
        all_transactions = [t for t in all_transactions if t.get("_account_name") == account_filter]

    # Option 4: Process ALL transactions (smart platform coexistence)
    # The workflow will intelligently handle:
    # - Uncategorized: apply category + labels
    # - Already categorized + matching: apply labels only
    # - Already categorized + conflict: flag for review
    # - Label-only rules: apply labels regardless
    return all_transactions


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        # Initialize client
        client = PocketSmithClient()

        # Fetch transactions
        print(f"Fetching transactions for {args.period}...")
        transactions = get_transactions(client, args.period, args.account)

        if not transactions:
            print("No transactions found for the specified period.")
            return 0

        print(f"Processing {len(transactions)} transactions...\n")

        # Get available categories (flatten to include all child categories)
        user = client.get_user()
        categories = client.get_categories(user["id"], flatten=True)

        # Initialize workflow
        workflow = CategorizationWorkflow(
            client=client,
            mode=args.mode,
        )

        # Process batch
        if args.dry_run:
            print("DRY RUN MODE - No changes will be applied\n")

        print(f"Processing with mode={args.mode}...")
        results = workflow.categorize_transactions_batch(
            transactions=transactions,
            available_categories=categories,
        )

        # Display results
        stats = results["stats"]
        print("\n" + "=" * 60)
        print("CATEGORIZATION RESULTS")
        print("=" * 60)
        print(f"Total transactions: {stats['total']}")
        print(f"Rule matches: {stats['rule_matches']}")
        print(f"Existing preserved: {stats.get('existing_preserved', 0)}")
        print(f"LLM categorized: {stats['llm_categorized']}")
        print(f"LLM validated: {stats['llm_validated']}")
        print(f"Conflicts (needs review): {stats.get('conflicts', 0)}")
        print(f"Skipped (low confidence): {stats['skipped']}")
        print("=" * 60)

        # Apply results (if not dry run)
        if not args.dry_run:
            # Build batch updates
            txn_lookup = {t["id"]: t for t in transactions}
            updates = []
            conflicts_marked = 0
            skipped_no_category = 0

            for txn_id, result in results["results"].items():
                # Handle conflicts specially
                if result.get("needs_review"):
                    existing_labels = txn_lookup.get(txn_id, {}).get("labels", [])
                    conflict_labels = add_review_label(existing_labels, LABEL_CATEGORY_CONFLICT)
                    updates.append(
                        {
                            "transaction_id": txn_id,
                            "labels": conflict_labels,
                            "note": f"Local rule suggests: {result.get('suggested_category')}",
                        }
                    )
                    conflicts_marked += 1
                elif result.get("category") or result.get("labels"):
                    update = {"transaction_id": txn_id}

                    if result.get("category"):
                        cat = find_category_by_name(categories, result["category"])
                        if cat:
                            update["category_id"] = cat["id"]
                        else:
                            cat_name = result["category"]
                            logger.warning(
                                f"Skipping txn {txn_id}: category '{cat_name}' not found"
                            )
                            skipped_no_category += 1
                            continue

                    if result.get("labels"):
                        update["labels"] = result["labels"]

                    updates.append(update)

            if updates:
                print(f"\nApplying {len(updates)} updates (batch mode, 5 concurrent)...")

                def progress_callback(
                    completed: int, total: int, txn_id: int, success: bool
                ) -> None:
                    if completed % 10 == 0 or completed == total:
                        pct = int(completed / total * 100)
                        status = "✓" if success else "✗"
                        print(
                            f"  Progress: {completed}/{total} ({pct}%) {status}",
                            end="\r",
                            flush=True,
                        )

                batch_result = client.update_transactions_batch(
                    updates=updates,
                    max_workers=5,
                    progress_callback=progress_callback,
                )
                print()  # New line after progress

                print(f"✓ Applied {batch_result['successful']} categorizations")
                if batch_result["failed"] > 0:
                    print(f"✗ Failed: {batch_result['failed']}")
                    for err in batch_result["errors"][:5]:  # Show first 5 errors
                        print(f"  - Transaction {err['transaction_id']}: {err['error']}")
            else:
                print("\nNo updates to apply.")

            if conflicts_marked > 0:
                print(
                    f"⚠️  Marked {conflicts_marked} conflicts for review "
                    f"(label: '{LABEL_CATEGORY_CONFLICT}')"
                )
            if skipped_no_category > 0:
                print(f"⚠️  Skipped {skipped_no_category} (category not found)")
        else:
            print("\n(Dry run - no changes applied)")

        return 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
