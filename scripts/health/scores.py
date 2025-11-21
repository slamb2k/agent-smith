"""Health score definitions and base classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class HealthStatus(Enum):
    """Health status levels based on score ranges."""

    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"  # 70-89
    FAIR = "fair"  # 50-69
    POOR = "poor"  # 0-49

    @classmethod
    def from_score(cls, score: int) -> "HealthStatus":
        """Determine status from numeric score.

        Args:
            score: Health score (0-100). Values outside range are clamped.

        Returns:
            Corresponding HealthStatus
        """
        # Clamp score to valid range
        score = max(0, min(100, score))
        if score >= 90:
            return cls.EXCELLENT
        elif score >= 70:
            return cls.GOOD
        elif score >= 50:
            return cls.FAIR
        else:
            return cls.POOR

    @property
    def emoji(self) -> str:
        """Get emoji representation of status."""
        return {
            HealthStatus.EXCELLENT: "✅",
            HealthStatus.GOOD: "👍",
            HealthStatus.FAIR: "⚠️",
            HealthStatus.POOR: "❌",
        }[self]


@dataclass
class HealthScore:
    """Represents a health score for a specific dimension."""

    dimension: str
    score: int
    max_score: int = 100
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def status(self) -> HealthStatus:
        """Get status based on percentage score."""
        return HealthStatus.from_score(int(self.percentage))

    @property
    def percentage(self) -> float:
        """Calculate percentage score."""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dict representation of health score
        """
        return {
            "dimension": self.dimension,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "status": self.status.value,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseScorer(ABC):
    """Abstract base class for health dimension scorers."""

    dimension: str = "base"

    @abstractmethod
    def calculate(self, data: Dict[str, Any]) -> HealthScore:
        """Calculate health score for this dimension.

        Args:
            data: Input data for score calculation

        Returns:
            HealthScore for this dimension
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(dimension={self.dimension})"


class DataQualityScorer(BaseScorer):
    """Scores data quality: categorization, completeness, duplicates."""

    dimension = "data_quality"

    # Weight factors for each component
    CATEGORIZATION_WEIGHT = 0.5
    PAYEE_WEIGHT = 0.3
    DUPLICATE_WEIGHT = 0.2

    def calculate(self, data: Dict[str, Any]) -> HealthScore:
        """Calculate data quality score.

        Args:
            data: Dict with keys:
                - total_transactions: int
                - categorized_transactions: int
                - transactions_with_payee: int
                - duplicate_count: int

        Returns:
            HealthScore for data quality dimension
        """
        total = data.get("total_transactions", 0)
        categorized = data.get("categorized_transactions", 0)
        with_payee = data.get("transactions_with_payee", 0)
        duplicates = data.get("duplicate_count", 0)

        issues: List[str] = []
        recommendations: List[str] = []

        if total == 0:
            return HealthScore(
                dimension=self.dimension,
                score=0,
                issues=["No transactions found"],
                recommendations=["Import transactions from PocketSmith"],
            )

        # Calculate component scores
        cat_rate = categorized / total
        payee_rate = with_payee / total
        dup_rate = duplicates / total if total > 0 else 0

        # Categorization score (0-50 points)
        cat_score = cat_rate * 100 * self.CATEGORIZATION_WEIGHT
        if cat_rate < 1.0:
            uncategorized = total - categorized
            issues.append(f"{uncategorized} uncategorized transactions ({(1-cat_rate)*100:.1f}%)")
            recommendations.append("Run /agent-smith-categorize to categorize transactions")

        # Payee completeness score (0-30 points)
        payee_score = payee_rate * 100 * self.PAYEE_WEIGHT
        if payee_rate < 0.95:
            missing = total - with_payee
            issues.append(f"{missing} transactions missing payee name")
            recommendations.append("Review transactions with missing payee information")

        # Duplicate penalty (0-20 points, deducted for duplicates)
        dup_penalty = min(dup_rate * 100 * 5, 20)  # Max 20 point penalty
        dup_score = (100 * self.DUPLICATE_WEIGHT) - dup_penalty
        if duplicates > 0:
            issues.append(f"{duplicates} potential duplicate transactions detected")
            recommendations.append("Review and merge duplicate transactions")

        total_score = int(cat_score + payee_score + max(0, dup_score))

        return HealthScore(
            dimension=self.dimension,
            score=min(100, max(0, total_score)),
            issues=issues,
            recommendations=recommendations,
            details={
                "categorization_rate": cat_rate,
                "payee_rate": payee_rate,
                "duplicate_rate": dup_rate,
            },
        )


# Placeholder exports for __init__.py imports
# These will be implemented in subsequent tasks
CategoryStructureScorer = None
RuleEngineScorer = None
TaxReadinessScorer = None
AutomationScorer = None
BudgetAlignmentScorer = None
