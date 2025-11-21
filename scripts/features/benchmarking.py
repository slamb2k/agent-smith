"""Comparative benchmarking with privacy-first design."""

import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass
from statistics import mean, median


@dataclass
class PeerCriteria:
    """Criteria for selecting comparable peers."""

    household_size: Optional[int] = None
    income_bracket: Optional[str] = None
    location: Optional[str] = None
    age_bracket: Optional[str] = None


@dataclass
class BenchmarkResult:
    """Comparison result against peer group."""

    category: str
    user_amount: float
    peer_average: float
    peer_median: float
    percentile: int  # Where user falls (0-100)
    peer_count: int


class BenchmarkEngine:
    """Privacy-first comparative benchmarking."""

    def __init__(self) -> None:
        """Initialize benchmark engine."""
        # In production, this would connect to aggregated data store
        self.aggregated_data: Dict[str, List[float]] = {}

    def anonymize_user_id(self, user_id: str) -> str:
        """Anonymize a user ID using SHA-256 hash.

        Args:
            user_id: Original user ID

        Returns:
            Anonymized hash
        """
        return hashlib.sha256(user_id.encode()).hexdigest()

    def _build_key(self, category: str, criteria: PeerCriteria) -> str:
        """Build aggregation key from category and criteria.

        Args:
            category: Spending category
            criteria: Peer criteria

        Returns:
            Aggregation key
        """
        parts = [category]
        if criteria.household_size:
            parts.append(f"hs_{criteria.household_size}")
        if criteria.income_bracket:
            parts.append(f"ib_{criteria.income_bracket}")
        if criteria.location:
            parts.append(f"loc_{criteria.location}")
        if criteria.age_bracket:
            parts.append(f"age_{criteria.age_bracket}")
        return ":".join(parts)

    def add_data_point(
        self,
        category: str,
        amount: float,
        user_id: str,
        criteria: PeerCriteria,
    ) -> None:
        """Add an anonymized data point to aggregated data.

        Args:
            category: Spending category
            amount: Amount spent
            user_id: User ID (will be anonymized)
            criteria: Peer criteria for grouping
        """
        # Anonymize user ID (not stored, just for ethics)
        _ = self.anonymize_user_id(user_id)

        # Store only aggregated amount (no user linkage)
        key = self._build_key(category, criteria)
        if key not in self.aggregated_data:
            self.aggregated_data[key] = []
        self.aggregated_data[key].append(amount)

    def compare(
        self,
        category: str,
        user_amount: float,
        criteria: PeerCriteria,
    ) -> Optional[BenchmarkResult]:
        """Compare user spending to peer group.

        Args:
            category: Spending category
            user_amount: User's spending amount
            criteria: Peer criteria

        Returns:
            BenchmarkResult or None if insufficient data
        """
        key = self._build_key(category, criteria)

        if key not in self.aggregated_data or len(self.aggregated_data[key]) < 3:
            return None  # Need at least 3 peers for meaningful comparison

        peer_amounts = self.aggregated_data[key]

        # Calculate statistics
        peer_avg = mean(peer_amounts)
        peer_med = median(peer_amounts)

        # Calculate percentile
        # Count values below and at user's level
        below_count = sum(1 for amount in peer_amounts if amount < user_amount)
        equal_count = sum(1 for amount in peer_amounts if amount == user_amount)
        # Use midpoint of equal values for percentile ranking
        rank = below_count + (equal_count / 2)
        percentile = int((rank / len(peer_amounts)) * 100)

        return BenchmarkResult(
            category=category,
            user_amount=user_amount,
            peer_average=round(peer_avg, 2),
            peer_median=round(peer_med, 2),
            percentile=percentile,
            peer_count=len(peer_amounts),
        )
