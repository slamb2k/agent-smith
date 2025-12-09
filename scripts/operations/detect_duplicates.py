#!/usr/bin/env python3
"""Detect and optionally label suspected duplicate transactions.

Duplicates are identified as transactions with the same:
- Payee name
- Amount
- Date
- Same account (excludes transfers which span accounts)

Transactions already reviewed (cleared of the label) are excluded from detection.
"""

import argparse
import json
import sys
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from scripts.core.api_client import PocketSmithClient
from scripts.core.labels import LABEL_SUSPECTED_DUPLICATE


def detect_duplicates(
    transactions: List[Dict[str, Any]],
    exclude_reviewed: bool = True,
) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """Detect suspected duplicate transactions.

    Args:
        transactions: List of transaction objects from API
        exclude_reviewed: If True, skip transactions that already have the
                         duplicate label (they've been reviewed and confirmed)

    Returns:
        Tuple of:
        - List of transactions that are suspected duplicates (unreviewed only)
        - Dict mapping signature to list of all transactions with that signature
    """
    # Group transactions by signature (payee|amount|date) within same account
    by_account_sig: Dict[str, Dict[str, List[Dict]]] = defaultdict(lambda: defaultdict(list))

    for txn in transactions:
        account_id = str(txn.get("transaction_account", {}).get("id", ""))
        payee = txn.get("payee", "").strip()
        amount = txn.get("amount", 0)
        date = txn.get("date", "")

        # Skip if it looks like a transfer (will be in multiple accounts)
        if "transfer" in payee.lower():
            continue

        # Create signature for this account
        sig = f"{payee}|{amount}|{date}"
        by_account_sig[account_id][sig].append(txn)

    # Find duplicate groups (more than 1 transaction per signature)
    all_groups: Dict[str, List[Dict]] = {}
    unreviewed_duplicates: List[Dict] = []

    for account_id, sigs in by_account_sig.items():
        for sig, txns in sigs.items():
            if len(txns) > 1:
                # This is a duplicate group
                full_sig = f"{account_id}|{sig}"
                all_groups[full_sig] = txns

                # Find unreviewed transactions in this group
                for txn in txns:
                    labels = txn.get("labels", [])
                    has_label = LABEL_SUSPECTED_DUPLICATE in labels

                    if exclude_reviewed and has_label:
                        # Already reviewed - skip
                        continue

                    unreviewed_duplicates.append(txn)

    return unreviewed_duplicates, all_groups


def format_duplicate_summary(
    groups: Dict[str, List[Dict[str, Any]]],
    limit: int = 20,
) -> str:
    """Format duplicate groups for display.

    Args:
        groups: Dict mapping signature to list of transactions
        limit: Maximum number of groups to show

    Returns:
        Formatted string summary
    """
    if not groups:
        return "No suspected duplicates found."

    lines = []
    lines.append(f"Found {len(groups)} duplicate groups:\n")

    # Sort by count descending
    sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)

    for i, (sig, txns) in enumerate(sorted_groups[:limit]):
        parts = sig.split("|")
        if len(parts) >= 4:
            # account_id|payee|amount|date
            payee = parts[1][:40]
            amount = float(parts[2]) if parts[2] else 0
            date = parts[3]
        else:
            payee = "Unknown"
            amount = 0
            date = "Unknown"

        account_name = txns[0].get("transaction_account", {}).get("name", "Unknown")
        lines.append(f"{i+1}. {payee:<40} | ${amount:>10.2f} | {date} | x{len(txns)}")
        lines.append(f"   Account: {account_name}")
        lines.append("")

    if len(groups) > limit:
        lines.append(f"... and {len(groups) - limit} more groups")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        choices=["json", "summary", "ids"],
        default="summary",
        help="Output format",
    )
    parser.add_argument(
        "--include-reviewed",
        action="store_true",
        help="Include transactions already labeled as duplicates",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of groups to show in summary (default: 20)",
    )
    args = parser.parse_args()

    # Connect to PocketSmith
    client = PocketSmithClient()
    user = client.get_user()
    print(f"Connected as: {user['email']}", file=sys.stderr)

    # Fetch all transactions
    print("Fetching transactions...", file=sys.stderr)
    transactions = client.get_all_transactions(user["id"])
    print(f"Fetched {len(transactions)} transactions", file=sys.stderr)

    # Detect duplicates
    exclude_reviewed = not args.include_reviewed
    unreviewed, groups = detect_duplicates(transactions, exclude_reviewed=exclude_reviewed)

    # Output results
    if args.output == "json":
        result = {
            "unreviewed_count": len(unreviewed),
            "group_count": len(groups),
            "transactions": unreviewed,
            "groups": {
                sig: [
                    {"id": t["id"], "payee": t.get("payee"), "amount": t.get("amount")}
                    for t in txns
                ]
                for sig, txns in groups.items()
            },
        }
        print(json.dumps(result, indent=2))
    elif args.output == "ids":
        # Just output transaction IDs (for piping to other scripts)
        ids = [str(t["id"]) for t in unreviewed]
        print(",".join(ids))
    else:  # summary
        print()
        print(format_duplicate_summary(groups, limit=args.limit))
        print()
        print(f"Total unreviewed suspected duplicates: {len(unreviewed)}")
        if exclude_reviewed:
            print("(Use --include-reviewed to also show already-labeled transactions)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
