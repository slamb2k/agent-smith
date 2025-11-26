#!/usr/bin/env python
"""Group conflict transactions by common payee patterns for batch processing.

This script analyzes conflict transactions and groups them by extractable
patterns that could become categorization rules.
"""

import sys
import json
import re
from typing import List, Dict, Any
from collections import defaultdict


def extract_keyword(payee: str) -> str:
    """Extract the primary keyword from a payee string.

    This identifies the main merchant/entity that could be used in a rule.

    Args:
        payee: Transaction payee text

    Returns:
        Extracted keyword (uppercase) or empty string if no clear pattern

    Examples:
        >>> extract_keyword("WOOLWORTHS SMITH ST")
        "WOOLWORTHS"
        >>> extract_keyword("PAYPAL *EBAY")
        "PAYPAL"
        >>> extract_keyword("Transfer to John Smith")
        ""  # Too generic
    """
    if not payee:
        return ""

    # Convert to uppercase for consistent matching
    payee_upper = payee.upper()

    # Remove common noise patterns
    # - Transaction IDs, reference numbers
    # - Dates (DD/MM, YYYY-MM-DD, etc.)
    # - Card numbers (last 4 digits, etc.)
    payee_clean = re.sub(r"\b\d{2,}[-/]\d{2,}[-/]\d{2,4}\b", "", payee_upper)  # Dates
    payee_clean = re.sub(r"\bREF\s*\d+\b", "", payee_clean)  # Reference numbers
    payee_clean = re.sub(r"\bTXN\s*\d+\b", "", payee_clean)  # Transaction IDs
    payee_clean = re.sub(r"\b\d{4,}\b", "", payee_clean)  # Long numbers

    # Split into words
    words = payee_clean.split()

    # Filter out common generic words that shouldn't be keywords
    generic_terms = {
        "PAYMENT",
        "TRANSFER",
        "BY",
        "AUTHORITY",
        "TO",
        "FROM",
        "DIRECT",
        "DEBIT",
        "PURCHASE",
        "VALUE",
        "DATE",
        "CARD",
        "AUSTRALIA",
        "PTY",
        "LTD",
        "CO",
        "THE",
        "AND",
        "OR",
        "FOR",
        "AT",
        "IN",
        "ON",
        "WITH",
    }

    meaningful_words = [w for w in words if w not in generic_terms and len(w) >= 3]

    if not meaningful_words:
        return ""

    # Special handling for known patterns
    # PAYPAL - ALWAYS extract merchant after * (don't group by "PAYPAL" alone)
    if "PAYPAL" in meaningful_words:
        # Check if there's a specific merchant identifier
        if "*" in payee_upper:
            # Extract everything after * until end or " - " separator
            match = re.search(r"\*\s*([A-Z][A-Z0-9\s]+?)(?:\s*-|\s*\d{2}|\s*AUD|$)", payee_upper)
            if match:
                merchant = match.group(1).strip()
                # Clean up merchant name - take first significant word(s)
                merchant_words = [
                    w for w in merchant.split() if w not in {"PAYMENT", "PURCHASE", "TRANSFER"}
                ]
                if merchant_words:
                    # Use first word as the grouping keyword (most specific)
                    return merchant_words[0]
        # No merchant found after * - don't group generic PAYPAL transactions
        return ""

    # Return the first meaningful word (usually the merchant name)
    return meaningful_words[0]


def group_transactions_by_pattern(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Group transactions by extractable payee patterns.

    Args:
        transactions: List of transaction dicts with conflict labels

    Returns:
        Dictionary with:
        - groups: List of groups, each with pattern, transactions, count
        - ungrouped: List of transactions that couldn't be grouped
        - stats: Summary statistics
    """
    # Group by extracted keyword
    pattern_groups = defaultdict(list)
    ungrouped = []

    for txn in transactions:
        payee = txn.get("payee", "")
        keyword = extract_keyword(payee)

        if keyword:
            pattern_groups[keyword].append(txn)
        else:
            # No clear pattern, handle individually
            ungrouped.append(txn)

    # Convert to list of groups, filtering out singles (they'll go to ungrouped)
    groups: List[Dict[str, Any]] = []
    for pattern, txns in pattern_groups.items():
        if len(txns) >= 2:
            # Multiple transactions with same pattern = groupable
            groups.append(
                {
                    "pattern": pattern,
                    "count": len(txns),
                    "transactions": txns,
                    "sample_payees": [t.get("payee", "")[:60] for t in txns[:3]],
                }
            )
        else:
            # Single transaction with this pattern
            ungrouped.extend(txns)

    # Sort groups by count (largest first)
    groups.sort(key=lambda g: g.get("count", 0), reverse=True)

    # Stats
    total_transactions = len(transactions)
    grouped_count = sum(g.get("count", 0) for g in groups)
    ungrouped_count = len(ungrouped)

    return {
        "groups": groups,
        "ungrouped": ungrouped,
        "stats": {
            "total": total_transactions,
            "grouped": grouped_count,
            "ungrouped": ungrouped_count,
            "num_groups": len(groups),
        },
    }


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Group conflict transactions by common payee patterns"
    )
    parser.add_argument(
        "--transactions-file",
        required=True,
        help="JSON file containing transactions from fetch_conflicts.py",
    )
    parser.add_argument(
        "--output", choices=["json", "summary"], default="summary", help="Output format"
    )
    parser.add_argument(
        "--min-group-size",
        type=int,
        default=2,
        help="Minimum transactions required to form a group (default: 2)",
    )

    args = parser.parse_args()

    # Load transactions
    try:
        with open(args.transactions_file) as f:
            transactions = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.transactions_file}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.transactions_file}: {e}", file=sys.stderr)
        return 1

    if not transactions:
        print("No transactions to group")
        return 0

    # Group transactions
    result = group_transactions_by_pattern(transactions)

    # Output
    if args.output == "json":
        print(json.dumps(result, indent=2))
    elif args.output == "summary":
        stats = result["stats"]
        print("\nGrouping Analysis:")
        print(f"  Total transactions: {stats['total']}")
        print(f"  Grouped: {stats['grouped']} ({stats['num_groups']} groups)")
        print(f"  Ungrouped (unique): {stats['ungrouped']}")
        print()

        if result["groups"]:
            print("Groups (by pattern):")
            for i, group in enumerate(result["groups"], 1):
                print(f"\n  {i}. Pattern: '{group['pattern']}' ({group['count']} transactions)")
                print("     Sample payees:")
                for payee in group["sample_payees"]:
                    print(f"       - {payee}")

        if result["ungrouped"]:
            print(f"\n  {stats['ungrouped']} transactions will be reviewed individually")

    return 0


if __name__ == "__main__":
    sys.exit(main())
