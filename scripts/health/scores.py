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


class CategoryStructureScorer(BaseScorer):
    """Scores category structure: hierarchy, usage, ATO alignment."""

    dimension = "category_structure"

    HIERARCHY_WEIGHT = 0.3
    USAGE_WEIGHT = 0.4
    ATO_WEIGHT = 0.3

    IDEAL_ROOT_CATEGORIES = 10
    IDEAL_MAX_DEPTH = 3

    def calculate(self, data: Dict[str, Any]) -> HealthScore:
        """Calculate category structure score.

        Args:
            data: Dict with keys:
                - total_categories: int
                - categories_with_transactions: int
                - max_depth: int
                - categories_at_root: int
                - ato_mapped_categories: int
                - empty_categories: int

        Returns:
            HealthScore for category structure dimension
        """
        total = data.get("total_categories", 0)
        used = data.get("categories_with_transactions", 0)
        max_depth = data.get("max_depth", 1)
        root_count = data.get("categories_at_root", 0)
        ato_mapped = data.get("ato_mapped_categories", 0)
        empty = data.get("empty_categories", 0)

        issues: List[str] = []
        recommendations: List[str] = []

        if total == 0:
            return HealthScore(
                dimension=self.dimension,
                score=0,
                issues=["No categories found"],
                recommendations=["Set up category structure in PocketSmith"],
            )

        # Hierarchy score (0-30 points)
        hierarchy_score = 100 * self.HIERARCHY_WEIGHT

        # Penalize too many root categories
        if root_count > self.IDEAL_ROOT_CATEGORIES * 2:
            penalty = min(15, (root_count - self.IDEAL_ROOT_CATEGORIES) * 0.5)
            hierarchy_score -= penalty
            issues.append(
                f"{root_count} root-level categories (ideal: {self.IDEAL_ROOT_CATEGORIES})"
            )
            recommendations.append("Consolidate categories into a hierarchical structure")

        # Penalize flat structure
        if max_depth < 2 and total > 15:
            hierarchy_score -= 10
            issues.append("Flat category structure lacks hierarchy")
            recommendations.append("Create parent categories to organize related expenses")

        # Usage score (0-40 points)
        usage_rate = used / total if total > 0 else 0
        usage_score = usage_rate * 100 * self.USAGE_WEIGHT

        if empty > total * 0.3:
            issues.append(f"{empty} empty/unused categories ({empty/total*100:.0f}%)")
            recommendations.append("Archive or delete unused categories")

        # ATO alignment score (0-30 points)
        ato_rate = ato_mapped / used if used > 0 else 0
        ato_score = ato_rate * 100 * self.ATO_WEIGHT

        if ato_rate < 0.5:
            issues.append(f"Only {ato_mapped} categories mapped to ATO tax categories")
            recommendations.append("Map categories to ATO expense types for tax reporting")

        total_score = int(hierarchy_score + usage_score + ato_score)

        return HealthScore(
            dimension=self.dimension,
            score=min(100, max(0, total_score)),
            issues=issues,
            recommendations=recommendations,
            details={
                "usage_rate": usage_rate,
                "ato_mapping_rate": ato_rate,
                "hierarchy_depth": max_depth,
                "root_categories": root_count,
            },
        )


# Placeholder exports for __init__.py imports
# These will be implemented in subsequent tasks
RuleEngineScorer = None
TaxReadinessScorer = None
AutomationScorer = None
BudgetAlignmentScorer = None
