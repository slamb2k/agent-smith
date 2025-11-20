"""Merchant name normalization utilities."""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional


logger = logging.getLogger(__name__)


class MerchantNormalizer:
    """Normalizes merchant/payee names for consistent matching."""

    # Common patterns to remove
    LOCATION_CODE_PATTERN = r"\s+\d{4,}$"
    SUFFIX_PATTERNS = [
        r"\s+PTY\s+LTD$",
        r"\s+LIMITED$",
        r"\s+LTD$",
        r"\s+SUPERMARKETS?$",
        r"\s+AU$",
        r"\s+AUSTRALIA$",
    ]
    TRANSACTION_CODE_PATTERN = r"\s+[A-Z]{2,3}XXX\d+$"
    DIRECT_DEBIT_PATTERN = r"DIRECT DEBIT \d+"

    def __init__(self, mappings_file: Optional[Path] = None):
        """Initialize merchant normalizer.

        Args:
            mappings_file: Path to merchant mappings JSON
        """
        if mappings_file is None:
            project_root = Path(__file__).parent.parent.parent
            mappings_file = project_root / "data" / "merchants" / "merchant_mappings.json"

        self.mappings_file = Path(mappings_file)
        self.mappings: Dict[str, List[str]] = {}

        if self.mappings_file.exists():
            self.load_mappings()

    def normalize(self, payee: str) -> str:
        """Normalize a payee name.

        Args:
            payee: Raw payee name

        Returns:
            Normalized payee name
        """
        normalized = payee.upper().strip()

        # Remove location codes (e.g., "WOOLWORTHS 1234" -> "WOOLWORTHS")
        normalized = re.sub(self.LOCATION_CODE_PATTERN, "", normalized)

        # Remove transaction codes (e.g., "NSWxxx123")
        normalized = re.sub(self.TRANSACTION_CODE_PATTERN, "", normalized)

        # Handle direct debit pattern
        if re.match(self.DIRECT_DEBIT_PATTERN, normalized):
            normalized = "DIRECT DEBIT"

        # Remove common suffixes
        for pattern in self.SUFFIX_PATTERNS:
            normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE)

        return normalized.strip()

    def get_canonical_name(self, payee: str) -> str:
        """Get canonical merchant name from variation.

        Args:
            payee: Payee name (will be normalized first)

        Returns:
            Canonical merchant name if mapped, otherwise normalized payee
        """
        normalized = self.normalize(payee)

        # Check if this matches any known variations
        for canonical, variations in self.mappings.items():
            for variation in variations:
                if normalized.startswith(variation):
                    return canonical

        return normalized

    def add_mapping(self, canonical: str, variations: List[str]) -> None:
        """Add a merchant name mapping.

        Args:
            canonical: Canonical merchant name
            variations: List of variations that map to canonical
        """
        self.mappings[canonical] = variations
        logger.debug(f"Added mapping: {canonical} <- {variations}")

    def learn_from_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """Learn merchant variations from transaction history.

        Args:
            transactions: List of transactions with payee field
        """
        # Group by normalized payee prefix
        groups: Dict[str, Set[str]] = {}

        for txn in transactions:
            payee = txn.get("payee", "")
            normalized = self.normalize(payee)

            # Extract base name (first word typically)
            base = normalized.split()[0] if normalized else ""
            if not base or len(base) < 3:
                continue

            if base not in groups:
                groups[base] = set()
            groups[base].add(normalized)

        # Create mappings for groups with multiple variations
        for base, variations in groups.items():
            if len(variations) > 1:
                self.add_mapping(base, sorted(list(variations)))

        logger.info(
            f"Learned {len(self.mappings)} merchant mappings from {len(transactions)} transactions"
        )

    def save_mappings(self) -> None:
        """Save merchant mappings to JSON."""
        self.mappings_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.mappings_file, "w") as f:
            json.dump(self.mappings, f, indent=2)

        logger.info(f"Saved {len(self.mappings)} merchant mappings to {self.mappings_file}")

    def load_mappings(self) -> None:
        """Load merchant mappings from JSON."""
        if not self.mappings_file.exists():
            logger.debug(f"Mappings file not found: {self.mappings_file}")
            return

        with open(self.mappings_file) as f:
            self.mappings = json.load(f)

        logger.info(f"Loaded {len(self.mappings)} merchant mappings from {self.mappings_file}")
