"""Health check engine for comprehensive system evaluation."""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime

from scripts.health.scores import (
    HealthScore,
    HealthStatus,
    BaseScorer,
    DataQualityScorer,
    CategoryStructureScorer,
    RuleEngineScorer,
    TaxReadinessScorer,
    AutomationScorer,
    BudgetAlignmentScorer,
)


@dataclass
class HealthCheckResult:
    """Complete health check result."""

    scores: List[HealthScore]
    overall_score: int
    overall_status: HealthStatus
    top_recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "overall_score": self.overall_score,
            "overall_status": self.overall_status.value,
            "scores": [s.to_dict() for s in self.scores],
            "top_recommendations": self.top_recommendations,
            "timestamp": self.timestamp.isoformat(),
        }


class HealthCheckEngine:
    """Engine for running health checks across all dimensions."""

    # Dimension weights for overall score calculation
    WEIGHTS = {
        "data_quality": 0.20,
        "category_structure": 0.15,
        "rule_engine": 0.20,
        "tax_readiness": 0.20,
        "automation": 0.10,
        "budget_alignment": 0.15,
    }

    def __init__(self) -> None:
        """Initialize engine with all scorers."""
        self.scorers: List[BaseScorer] = [
            DataQualityScorer(),
            CategoryStructureScorer(),
            RuleEngineScorer(),
            TaxReadinessScorer(),
            AutomationScorer(),
            BudgetAlignmentScorer(),
        ]
        self._scorer_map = {s.dimension: s for s in self.scorers}

    def run_all(self, data: Dict[str, Dict[str, Any]]) -> HealthCheckResult:
        """Run all health checks.

        Args:
            data: Dict mapping dimension names to their input data

        Returns:
            Complete HealthCheckResult
        """
        scores: List[HealthScore] = []

        for scorer in self.scorers:
            dimension_data = data.get(scorer.dimension, {})
            score = scorer.calculate(dimension_data)
            scores.append(score)

        overall = self._calculate_overall(scores)
        top_recs = self._prioritize_recommendations(scores)

        return HealthCheckResult(
            scores=scores,
            overall_score=overall,
            overall_status=HealthStatus.from_score(overall),
            top_recommendations=top_recs[:5],  # Top 5 recommendations
        )

    def run_single(self, dimension: str, data: Dict[str, Any]) -> HealthScore:
        """Run health check for single dimension.

        Args:
            dimension: Dimension name (e.g., 'data_quality')
            data: Input data for the scorer

        Returns:
            HealthScore for the dimension

        Raises:
            ValueError: If dimension not found
        """
        scorer = self._scorer_map.get(dimension)
        if not scorer:
            raise ValueError(f"Unknown dimension: {dimension}")

        return scorer.calculate(data)

    def _calculate_overall(self, scores: List[HealthScore]) -> int:
        """Calculate weighted overall score.

        Args:
            scores: List of dimension scores

        Returns:
            Overall score (0-100)
        """
        total_weight: float = 0.0
        weighted_sum: float = 0.0

        for score in scores:
            weight = self.WEIGHTS.get(score.dimension, 0.1)
            weighted_sum += score.score * weight
            total_weight += weight

        if total_weight == 0:
            return 0

        return int(weighted_sum / total_weight)

    def _prioritize_recommendations(self, scores: List[HealthScore]) -> List[str]:
        """Prioritize recommendations by impact.

        Args:
            scores: All dimension scores

        Returns:
            Prioritized list of recommendations
        """
        # Sort scores by impact (weight * deficit from 100)
        scored_recs: List[tuple] = []

        for score in scores:
            weight = self.WEIGHTS.get(score.dimension, 0.1)
            deficit = 100 - score.score
            impact = weight * deficit

            for rec in score.recommendations:
                scored_recs.append((impact, score.dimension, rec))

        # Sort by impact descending
        scored_recs.sort(key=lambda x: x[0], reverse=True)

        # Return unique recommendations
        seen = set()
        result = []
        for _, dimension, rec in scored_recs:
            if rec not in seen:
                seen.add(rec)
                result.append(rec)

        return result
