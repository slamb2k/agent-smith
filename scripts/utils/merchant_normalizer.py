"""Merchant name normalization utilities."""

import re
from difflib import SequenceMatcher
from typing import List


def normalize_merchant(payee: str) -> str:
    """Clean and normalize merchant names.

    Handles:
    - Uppercase conversion
    - Whitespace normalization
    - Special character removal/normalization
    - Common suffix removal
    - Location code removal

    Args:
        payee: Raw merchant/payee name

    Returns:
        Normalized merchant name
    """
    # Convert to uppercase and strip leading/trailing whitespace
    normalized = payee.upper().strip()

    # Normalize special characters (replace with spaces)
    normalized = re.sub(r"[*\-/]", " ", normalized)

    # Remove location codes (4+ digits at end)
    normalized = re.sub(r"\s+\d{4,}$", "", normalized)

    # Remove common suffixes
    suffix_patterns = [
        r"\s+PTY\s+LTD$",
        r"\s+LIMITED$",
        r"\s+LTD$",
        r"\s+SUPERMARKETS?$",
        r"\s+AU$",
        r"\s+AUSTRALIA$",
    ]
    for pattern in suffix_patterns:
        normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE)

    # Normalize multiple spaces to single space
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def find_similar_merchants(payee: str, merchants: List[str], threshold: float = 0.85) -> List[str]:
    """Find similar merchant names using fuzzy matching.

    Uses difflib.SequenceMatcher for fuzzy string matching.
    Returns results sorted by similarity (highest first).

    Args:
        payee: Merchant name to match against
        merchants: List of merchant names to search
        threshold: Similarity threshold (0.0-1.0), default 0.85

    Returns:
        List of matching merchant names sorted by similarity (highest first)
    """
    matches = []

    for merchant in merchants:
        # Calculate similarity ratio
        similarity = SequenceMatcher(None, payee, merchant).ratio()

        if similarity >= threshold:
            matches.append((merchant, similarity))

    # Sort by similarity (highest first), then alphabetically
    matches.sort(key=lambda x: (-x[1], x[0]))

    # Return just the merchant names
    return [merchant for merchant, _ in matches]
