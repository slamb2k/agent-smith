"""Health score definitions and base classes."""

from enum import Enum


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


# Placeholder exports for __init__.py imports
# These will be implemented in subsequent tasks
HealthScore = None
DataQualityScorer = None
CategoryStructureScorer = None
RuleEngineScorer = None
TaxReadinessScorer = None
AutomationScorer = None
BudgetAlignmentScorer = None
