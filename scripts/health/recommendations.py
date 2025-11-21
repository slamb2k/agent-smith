"""Recommendation engine for health improvement suggestions."""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from typing_extensions import TypedDict
from scripts.health.scores import HealthScore


class RecommendationPriority(Enum):
    """Priority levels for recommendations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationCategory(Enum):
    """Categories of recommendations."""

    DATA_QUALITY = "data_quality"
    CATEGORY_STRUCTURE = "category_structure"
    RULE_ENGINE = "rule_engine"
    TAX_READINESS = "tax_readiness"
    AUTOMATION = "automation"
    BUDGET = "budget"


class _RecommendationTemplate(TypedDict):
    """Type for recommendation template entries."""

    title: str
    category: RecommendationCategory
    effort: str
    command: str
    base_impact: int


@dataclass
class Recommendation:
    """A specific actionable recommendation."""

    title: str
    description: str
    priority: RecommendationPriority
    category: RecommendationCategory
    impact_score: int  # 0-20 points potential improvement
    effort: str  # "low", "medium", "high"
    command: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "category": self.category.value,
            "impact_score": self.impact_score,
            "effort": self.effort,
            "command": self.command,
            "details": self.details,
        }


class RecommendationEngine:
    """Engine for generating prioritized recommendations from health scores."""

    # Mapping of issues to recommendations with metadata
    RECOMMENDATION_TEMPLATES: Dict[str, _RecommendationTemplate] = {
        "uncategorized": {
            "title": "Categorize uncategorized transactions",
            "category": RecommendationCategory.DATA_QUALITY,
            "effort": "medium",
            "command": "/agent-smith-categorize",
            "base_impact": 10,
        },
        "auto-categorization": {
            "title": "Enable auto-categorization",
            "category": RecommendationCategory.AUTOMATION,
            "effort": "low",
            "command": "/agent-smith --mode=smart",
            "base_impact": 18,
        },
        "coverage": {
            "title": "Improve rule coverage",
            "category": RecommendationCategory.RULE_ENGINE,
            "effort": "medium",
            "command": "/agent-smith-optimize rules",
            "base_impact": 15,
        },
        "substantiation": {
            "title": "Add missing receipts/documentation",
            "category": RecommendationCategory.TAX_READINESS,
            "effort": "high",
            "command": "/agent-smith-tax deductions",
            "base_impact": 12,
        },
        "budget": {
            "title": "Set up category budgets",
            "category": RecommendationCategory.BUDGET,
            "effort": "medium",
            "command": "/agent-smith-analyze spending",
            "base_impact": 8,
        },
        "ato": {
            "title": "Map categories to ATO expense types",
            "category": RecommendationCategory.TAX_READINESS,
            "effort": "medium",
            "command": "/agent-smith-tax",
            "base_impact": 10,
        },
        "duplicate": {
            "title": "Review potential duplicate transactions",
            "category": RecommendationCategory.DATA_QUALITY,
            "effort": "low",
            "command": "/agent-smith-analyze",
            "base_impact": 5,
        },
        "hierarchy": {
            "title": "Organize category hierarchy",
            "category": RecommendationCategory.CATEGORY_STRUCTURE,
            "effort": "high",
            "command": "/agent-smith-optimize categories",
            "base_impact": 8,
        },
        "rule": {
            "title": "Create categorization rules",
            "category": RecommendationCategory.RULE_ENGINE,
            "effort": "medium",
            "command": "/agent-smith-optimize rules",
            "base_impact": 12,
        },
        "alert": {
            "title": "Configure budget and tax alerts",
            "category": RecommendationCategory.AUTOMATION,
            "effort": "low",
            "command": "/agent-smith",
            "base_impact": 6,
        },
        "report": {
            "title": "Set up scheduled reports",
            "category": RecommendationCategory.AUTOMATION,
            "effort": "low",
            "command": "/agent-smith-report",
            "base_impact": 5,
        },
        "cgt": {
            "title": "Complete CGT register entries",
            "category": RecommendationCategory.TAX_READINESS,
            "effort": "high",
            "command": "/agent-smith-tax cgt",
            "base_impact": 10,
        },
        "goal": {
            "title": "Review financial goals progress",
            "category": RecommendationCategory.BUDGET,
            "effort": "low",
            "command": "/agent-smith-scenario projection",
            "base_impact": 5,
        },
    }

    # Dimension weights for impact calculation
    DIMENSION_WEIGHTS = {
        "data_quality": 0.20,
        "category_structure": 0.15,
        "rule_engine": 0.20,
        "tax_readiness": 0.20,
        "automation": 0.10,
        "budget_alignment": 0.15,
    }

    def generate(self, scores: List[HealthScore]) -> List[Recommendation]:
        """Generate prioritized recommendations from health scores.

        Args:
            scores: List of health scores from all dimensions

        Returns:
            Prioritized list of recommendations
        """
        recommendations: List[Recommendation] = []

        for score in scores:
            dimension_weight = self.DIMENSION_WEIGHTS.get(score.dimension, 0.1)
            deficit = 100 - score.score

            # Generate recommendations from issues
            for issue in score.issues:
                rec = self._issue_to_recommendation(
                    issue=issue,
                    score=score,
                    dimension_weight=dimension_weight,
                    deficit=deficit,
                )
                if rec:
                    recommendations.append(rec)

            # Generate recommendations from score recommendations
            for rec_text in score.recommendations:
                rec = self._text_to_recommendation(
                    text=rec_text,
                    score=score,
                    dimension_weight=dimension_weight,
                    deficit=deficit,
                )
                if rec and not self._duplicate_exists(rec, recommendations):
                    recommendations.append(rec)

        # Sort by impact score descending
        recommendations.sort(key=lambda r: r.impact_score, reverse=True)

        return recommendations

    def _issue_to_recommendation(
        self,
        issue: str,
        score: HealthScore,
        dimension_weight: float,
        deficit: int,
    ) -> Optional[Recommendation]:
        """Convert an issue to a recommendation."""
        issue_lower = issue.lower()

        for keyword, template in self.RECOMMENDATION_TEMPLATES.items():
            if keyword in issue_lower:
                impact = self._calculate_impact(
                    template["base_impact"],
                    dimension_weight,
                    deficit,
                )
                priority = self._determine_priority(impact, deficit)

                return Recommendation(
                    title=template["title"],
                    description=issue,
                    priority=priority,
                    category=template["category"],
                    impact_score=impact,
                    effort=template["effort"],
                    command=template["command"],
                    details={"source_dimension": score.dimension},
                )

        return None

    def _text_to_recommendation(
        self,
        text: str,
        score: HealthScore,
        dimension_weight: float,
        deficit: int,
    ) -> Optional[Recommendation]:
        """Convert recommendation text to structured recommendation."""
        text_lower = text.lower()

        for keyword, template in self.RECOMMENDATION_TEMPLATES.items():
            if keyword in text_lower:
                impact = self._calculate_impact(
                    template["base_impact"],
                    dimension_weight,
                    deficit,
                )
                priority = self._determine_priority(impact, deficit)

                return Recommendation(
                    title=template["title"],
                    description=text,
                    priority=priority,
                    category=template["category"],
                    impact_score=impact,
                    effort=template["effort"],
                    command=template["command"],
                    details={"source_dimension": score.dimension},
                )

        # Generic recommendation if no template matches
        category = self._dimension_to_category(score.dimension)
        impact = self._calculate_impact(5, dimension_weight, deficit)

        return Recommendation(
            title=text[:50] + "..." if len(text) > 50 else text,
            description=text,
            priority=self._determine_priority(impact, deficit),
            category=category,
            impact_score=impact,
            effort="medium",
            details={"source_dimension": score.dimension},
        )

    def _calculate_impact(
        self,
        base_impact: int,
        dimension_weight: float,
        deficit: int,
    ) -> int:
        """Calculate impact score based on various factors."""
        # Impact increases with dimension weight and deficit
        weight_factor = dimension_weight / 0.20  # Normalize around 20%
        deficit_factor = min(deficit / 50, 1.5)  # Cap at 1.5x for 75+ deficit

        return int(base_impact * weight_factor * deficit_factor)

    def _determine_priority(self, impact: int, deficit: int) -> RecommendationPriority:
        """Determine priority based on impact and deficit."""
        if impact >= 15 or deficit >= 60:
            return RecommendationPriority.CRITICAL
        elif impact >= 10 or deficit >= 40:
            return RecommendationPriority.HIGH
        else:
            return RecommendationPriority.MEDIUM if impact >= 5 else RecommendationPriority.LOW

    def _dimension_to_category(self, dimension: str) -> RecommendationCategory:
        """Map dimension name to recommendation category."""
        mapping = {
            "data_quality": RecommendationCategory.DATA_QUALITY,
            "category_structure": RecommendationCategory.CATEGORY_STRUCTURE,
            "rule_engine": RecommendationCategory.RULE_ENGINE,
            "tax_readiness": RecommendationCategory.TAX_READINESS,
            "automation": RecommendationCategory.AUTOMATION,
            "budget_alignment": RecommendationCategory.BUDGET,
        }
        return mapping.get(dimension, RecommendationCategory.DATA_QUALITY)

    def _duplicate_exists(
        self,
        rec: Recommendation,
        existing: List[Recommendation],
    ) -> bool:
        """Check if a similar recommendation already exists."""
        for existing_rec in existing:
            if existing_rec.title == rec.title and existing_rec.category == rec.category:
                return True
        return False
