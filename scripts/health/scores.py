"""Health score definitions and base classes."""

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


# Placeholder exports for __init__.py imports
# These will be implemented in subsequent tasks
DataQualityScorer = None
CategoryStructureScorer = None
RuleEngineScorer = None
TaxReadinessScorer = None
AutomationScorer = None
BudgetAlignmentScorer = None
