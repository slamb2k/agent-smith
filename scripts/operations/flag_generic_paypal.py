#!/usr/bin/env python
"""Flag generic PayPal transactions for recategorization.

This script identifies PayPal transactions that have NO merchant information
and flags them with conflict labels so they can be reviewed/recategorized.
"""

import sys
from typing import Dict, Any
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient
from scripts.core.labels import LABEL_GENERIC_PAYPAL, has_review_flag, add_review_label


def is_generic_paypal(payee: str) -> bool:
    """Check if PayPal transaction is generic (no merchant info).

    Args:
        payee: Transaction payee text

    Returns:
        True if generic PayPal (no merchant identifier)
    """
    payee_upper = payee.upper()

    # Generic patterns (no merchant info)
    generic_patterns = ["PAYMENT BY AUTHORITY TO PAYPAL AUSTRALIA", "PAYPAL AUSTRALIA"]

    # If it matches generic pattern AND doesn't have merchant identifier
    for pattern in generic_patterns:
        if pattern in payee_upper:
            # Check for merchant indicators
            if "*" not in payee_upper and "Purchase from PAYPAL" not in payee:
                return True

    return False


def flag_generic_paypal_transactions(
    start_date: str = "2025-01-01", end_date: str = "2025-12-31", dry_run: bool = False
) -> Dict[str, Any]:
    """Flag generic PayPal transactions for review.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        dry_run: If True, don't actually update transactions

    Returns:
        Dictionary with results
    """
    load_dotenv()
    client = PocketSmithClient()
    user = client.get_user()
    user_id = user["id"]

    results: Dict[str, Any] = {
        "total_paypal": 0,
        "generic_paypal": 0,
        "merchant_paypal": 0,
        "flagged": 0,
        "flagged_txns": [],
    }

    print("Fetching PayPal transactions...")
    page = 1

    while True:
        batch = client.get_transactions(
            user_id, start_date=start_date, end_date=end_date, page=page, per_page=100
        )

        if not batch:
            break

        for txn in batch:
            payee = txn.get("payee", "")

            if "PAYPAL" not in payee.upper():
                continue

            results["total_paypal"] += 1

            if is_generic_paypal(payee):
                results["generic_paypal"] += 1

                # Flag for review if not already flagged
                labels = txn.get("labels", [])

                if not has_review_flag(labels):
                    if not dry_run:
                        # Add review label using constant
                        new_labels = add_review_label(labels, LABEL_GENERIC_PAYPAL)
                        note = "Generic PayPal - suggest Online Services"
                        client.update_transaction(txn["id"], labels=new_labels, note=note)

                    results["flagged"] += 1
                    results["flagged_txns"].append(
                        {
                            "id": txn["id"],
                            "date": txn.get("date"),
                            "payee": payee,
                            "category": txn.get("category", {}).get("title"),
                        }
                    )
            else:
                results["merchant_paypal"] += 1

        if len(batch) < 100:
            break

        page += 1

        # Show progress
        if results["total_paypal"] % 50 == 0:
            print(f"  Processed {results['total_paypal']} PayPal transactions...", flush=True)

    return results


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Flag generic PayPal transactions for recategorization"
    )
    parser.add_argument("--start-date", default="2025-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default="2025-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be flagged without updating"
    )

    args = parser.parse_args()

    results = flag_generic_paypal_transactions(args.start_date, args.end_date, args.dry_run)

    print("\nResults:")
    print(f"  Total PayPal transactions: {results['total_paypal']}")
    print(f"  Generic (no merchant): {results['generic_paypal']}")
    print(f"  With merchant info: {results['merchant_paypal']}")
    flag_text = "Would flag" if args.dry_run else "Flagged"
    print(f"  {flag_text}: {results['flagged']}")

    if results["flagged"] > 0 and args.dry_run:
        print("\nSample transactions that would be flagged:")
        for txn in results["flagged_txns"][:5]:
            print(f"  {txn['date']} | {txn['category']} | {txn['payee'][:50]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
