"""Merchant intelligence and payee enrichment."""

import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class MerchantGroup:
    """Represents a group of related merchant names."""

    canonical_name: str
    variations: Set[str]
    transaction_count: int = 0


class MerchantMatcher:
    """Detects and groups merchant name variations."""

    def __init__(self) -> None:
        """Initialize merchant matcher."""
        self.canonical_names: Dict[str, MerchantGroup] = {}

    def normalize_payee(self, payee: str) -> str:
        """Normalize a payee name for comparison.

        Args:
            payee: Raw payee name

        Returns:
            Normalized payee name
        """
        # Convert to lowercase
        normalized = payee.lower()

        # Remove common suffixes
        suffixes = [
            r"\s+pty\s+ltd",
            r"\s+pty\s*$",
            r"\s+ltd\s*$",
            r"\s+inc\s*$",
            r"\s+llc\s*$",
        ]
        for suffix in suffixes:
            normalized = re.sub(suffix, "", normalized)

        # Remove transaction IDs (e.g., "UBER *TRIP AB123CD")
        # Remove mixed alphanumeric IDs (contains both letters and numbers)
        pattern = r"\s+\b(?=[a-z0-9]*[0-9])(?=[a-z0-9]*[a-z])[a-z0-9]{4,}\b"
        normalized = re.sub(pattern, "", normalized)
        # Remove purely numeric IDs
        normalized = re.sub(r"\s+\d{4,}", "", normalized)
        # Then handle patterns like "*TRIP" by just removing the asterisk
        normalized = re.sub(r"\*", "", normalized)

        # Remove extra whitespace
        normalized = " ".join(normalized.split())

        return normalized.strip()

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity ratio between two names.

        Args:
            name1: First name
            name2: Second name

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        return SequenceMatcher(None, name1, name2).ratio()

    def find_canonical(self, payee: str) -> Optional[str]:
        """Find canonical merchant name for a payee.

        Args:
            payee: Payee name to look up

        Returns:
            Canonical name if found, None otherwise
        """
        normalized = self.normalize_payee(payee)

        # Check for exact match in canonical names
        for group_key, group in self.canonical_names.items():
            if normalized in group.variations or normalized == group_key:
                return group.canonical_name

        return None

    def add_variation(self, canonical_name: str, variation: str) -> None:
        """Add a variation to a merchant group.

        Args:
            canonical_name: The canonical merchant name
            variation: A variation of the merchant name
        """
        normalized_canonical = self.normalize_payee(canonical_name)
        normalized_variation = self.normalize_payee(variation)

        if normalized_canonical not in self.canonical_names:
            # Create new group
            self.canonical_names[normalized_canonical] = MerchantGroup(
                canonical_name=canonical_name,
                variations={normalized_variation},
            )
        else:
            # Add to existing group
            self.canonical_names[normalized_canonical].variations.add(normalized_variation)

    def suggest_matches(self, payee: str, threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Suggest potential canonical matches for a payee.

        Args:
            payee: Payee name to match
            threshold: Minimum similarity threshold (0.0 to 1.0)

        Returns:
            List of (canonical_name, similarity_score) tuples above threshold
        """
        normalized = self.normalize_payee(payee)
        suggestions = []

        for group in self.canonical_names.values():
            # Check similarity against all variations
            for variation in group.variations:
                similarity = self.calculate_similarity(normalized, variation)
                if similarity >= threshold:
                    suggestions.append((group.canonical_name, similarity))
                    break  # Only add each group once

        # Sort by similarity (highest first)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions
