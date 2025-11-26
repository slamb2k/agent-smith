#!/usr/bin/env python
"""Create a new categorization rule.

This script provides deterministic rule creation with validation.
Adds rules to data/rules.yaml with proper formatting.
"""

import sys
import re
from pathlib import Path
from typing import List, Optional
import yaml


def extract_keyword_pattern(payee: str) -> str:
    """Extract the most distinctive keyword from a payee string.

    Args:
        payee: Payee text

    Returns:
        Extracted keyword pattern
    """
    # Remove common prefixes/suffixes
    cleaned = payee.upper()
    cleaned = re.sub(r"^PAYMENT BY AUTHORITY TO\s+", "", cleaned)
    cleaned = re.sub(r"\s+\d+$", "", cleaned)  # Remove trailing numbers

    # Split into words and find longest meaningful word
    words = cleaned.split()
    meaningful_words = [w for w in words if len(w) > 3 and not w.isdigit()]

    if meaningful_words:
        # Return longest word as likely merchant name
        return max(meaningful_words, key=len)

    # Fallback: return first substantial word
    return words[0] if words else payee


def escape_pattern(text: str) -> str:
    """Escape special regex characters in text.

    Args:
        text: Text to escape

    Returns:
        Escaped pattern suitable for regex
    """
    # Escape special regex chars but keep common patterns like wildcards
    return re.escape(text)


def validate_rule(
    pattern: str, category: str, existing_rules: List[dict]
) -> tuple[bool, Optional[str]]:
    """Validate a new rule doesn't conflict with existing rules.

    Args:
        pattern: Rule pattern
        category: Target category
        existing_rules: List of existing rules

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for duplicate patterns
    for rule in existing_rules:
        if rule.get("type") != "category":
            continue

        rule_patterns = rule.get("patterns", [])
        if pattern.lower() in [p.lower() for p in rule_patterns]:
            existing_cat = rule.get("category")
            if existing_cat != category:
                return False, f"Pattern already exists with category '{existing_cat}'"
            return False, "Rule already exists"

    return True, None


def create_rule(
    pattern: str,
    category: str,
    confidence: int = 80,
    labels: Optional[List[str]] = None,
    pattern_type: str = "keyword",
) -> dict:
    """Create a new categorization rule.

    Args:
        pattern: Pattern to match (keyword or regex)
        category: Target category name
        confidence: Confidence score (0-100)
        labels: Optional labels to apply
        pattern_type: 'keyword' or 'full' pattern

    Returns:
        Created rule dictionary
    """
    rules_path = Path("data/rules.yaml")

    # Load existing rules
    with open(rules_path) as f:
        rules_data = yaml.safe_load(f)

    existing_rules = rules_data.get("rules", [])

    # Validate rule
    is_valid, error = validate_rule(pattern, category, existing_rules)
    if not is_valid:
        raise ValueError(f"Invalid rule: {error}")

    # Create rule
    rule_name = f"{pattern} → {category}"
    new_rule = {
        "type": "category",
        "name": rule_name,
        "patterns": [pattern],
        "category": category,
        "confidence": confidence,
    }

    if labels:
        new_rule["labels"] = labels

    # Add to rules
    rules_data["rules"].append(new_rule)

    # Save back to file
    with open(rules_path, "w") as f:
        yaml.dump(rules_data, f, default_flow_style=False, sort_keys=False)

    return new_rule


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Create a new categorization rule")
    parser.add_argument("category", help="Target category name")
    parser.add_argument("--payee", help="Payee text to extract pattern from")
    parser.add_argument("--pattern", help="Explicit pattern (overrides payee extraction)")
    parser.add_argument(
        "--pattern-type",
        choices=["keyword", "full"],
        default="keyword",
        help="Pattern extraction type",
    )
    parser.add_argument(
        "--confidence", type=int, default=80, help="Confidence score (0-100), default: 80"
    )
    parser.add_argument("--labels", nargs="*", help="Optional labels to apply")
    parser.add_argument("--dry-run", action="store_true", help="Show proposed rule without saving")

    args = parser.parse_args()

    # Determine pattern
    if args.pattern:
        pattern = args.pattern
    elif args.payee:
        if args.pattern_type == "keyword":
            pattern = extract_keyword_pattern(args.payee)
        else:
            pattern = escape_pattern(args.payee)
    else:
        print("Error: Must provide --payee or --pattern", file=sys.stderr)
        return 1

    # Show proposed rule
    print("Proposed rule:")
    print(f"  Pattern: {pattern}")
    print(f"  Category: {args.category}")
    print(f"  Confidence: {args.confidence}")
    if args.labels:
        print(f"  Labels: {', '.join(args.labels)}")
    print()

    if args.dry_run:
        print("(Dry run - not saved)")
        return 0

    try:
        # Create rule
        rule = create_rule(
            pattern,
            args.category,
            confidence=args.confidence,
            labels=args.labels,
            pattern_type=args.pattern_type,
        )

        print(f"✓ Rule created: {rule['name']}")
        print("  Saved to: data/rules.yaml")

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
