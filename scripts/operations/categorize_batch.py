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

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


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
        if len(batch) < 100:  # Last page
            break
        page += 1

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

        # Get available categories
        user = client.get_user()
        categories = client.get_categories(user["id"])

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
        print(f"LLM categorized: {stats['llm_categorized']}")
        print(f"LLM validated: {stats['llm_validated']}")
        print(f"Conflicts (needs review): {stats.get('conflicts', 0)}")
        print(f"Skipped (low confidence): {stats['skipped']}")
        print("=" * 60)

        # Apply results (if not dry run)
        if not args.dry_run:
            print("\nApplying categorizations...")
            applied = 0
            conflicts_marked = 0

            # Create transaction lookup for conflict handling
            txn_lookup = {t["id"]: t for t in transactions}

            for txn_id, result in results["results"].items():
                # Handle conflicts specially
                if result.get("needs_review"):
                    # Get existing labels from original transaction to preserve them
                    existing_labels = txn_lookup.get(txn_id, {}).get("labels", [])
                    conflict_labels = existing_labels + ["⚠️ Review: Category Conflict"]
                    client.update_transaction(
                        txn_id,
                        labels=conflict_labels,
                        note=f"Local rule suggests: {result.get('suggested_category')}",
                    )
                    conflicts_marked += 1
                elif result.get("category") or result.get("labels"):
                    # Apply if we have category and/or labels
                    update_kwargs = {}

                    if result.get("category"):
                        # Find category ID
                        cat = next(
                            (c for c in categories if c["title"] == result["category"]), None
                        )
                        if cat:
                            update_kwargs["category_id"] = cat["id"]

                    if result.get("labels"):
                        update_kwargs["labels"] = result["labels"]

                    if update_kwargs:
                        client.update_transaction(txn_id, **update_kwargs)
                        applied += 1

            print(f"✓ Applied {applied} categorizations")
            if conflicts_marked > 0:
                print(
                    f"⚠️  Marked {conflicts_marked} conflicts for review "
                    f"(label: '⚠️ Review: Category Conflict')"
                )
        else:
            print("\n(Dry run - no changes applied)")

        return 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
