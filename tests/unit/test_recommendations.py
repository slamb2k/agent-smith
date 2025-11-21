"""Unit tests for recommendation engine."""

import pytest
from scripts.health.recommendations import (
    RecommendationEngine,
    Recommendation,
    RecommendationPriority,
    RecommendationCategory,
)
from scripts.health.scores import HealthScore, HealthStatus


class TestRecommendation:
    """Tests for Recommendation dataclass."""

    def test_recommendation_creation(self):
        """Test creating a recommendation."""
        rec = Recommendation(
            title="Improve categorization",
            description="Add rules to increase auto-categorization rate",
            priority=RecommendationPriority.HIGH,
            category=RecommendationCategory.RULE_ENGINE,
            impact_score=15,
            effort="medium",
            command="/agent-smith-optimize rules",
        )

        assert rec.title == "Improve categorization"
        assert rec.priority == RecommendationPriority.HIGH
        assert rec.impact_score == 15


class TestRecommendationEngine:
    """Tests for RecommendationEngine."""

    def test_generate_recommendations_from_scores(self):
        """Generates prioritized recommendations from health scores."""
        engine = RecommendationEngine()

        scores = [
            HealthScore(
                dimension="data_quality",
                score=60,
                issues=["40 uncategorized transactions"],
                recommendations=["Categorize remaining transactions"],
            ),
            HealthScore(
                dimension="rule_engine",
                score=45,
                issues=["Low coverage (30%)"],
                recommendations=["Create more categorization rules"],
            ),
        ]

        recommendations = engine.generate(scores)

        assert len(recommendations) > 0
        # Higher impact recommendations should come first
        assert recommendations[0].impact_score >= recommendations[-1].impact_score

    def test_quick_wins_identified(self):
        """Quick wins (high impact, low effort) are flagged."""
        engine = RecommendationEngine()

        scores = [
            HealthScore(
                dimension="automation",
                score=30,
                issues=["Auto-categorization disabled"],
                recommendations=["Enable auto-categorization"],
            ),
        ]

        recommendations = engine.generate(scores)

        # Enabling auto-categorization should be a quick win
        quick_wins = [r for r in recommendations if r.effort == "low" and r.impact_score >= 10]
        assert len(quick_wins) > 0

    def test_recommendations_include_commands(self):
        """Recommendations include actionable commands where applicable."""
        engine = RecommendationEngine()

        scores = [
            HealthScore(
                dimension="data_quality",
                score=50,
                issues=["50 uncategorized transactions"],
                recommendations=["Run categorization"],
            ),
        ]

        recommendations = engine.generate(scores)

        # Should have at least one recommendation with a command
        with_commands = [r for r in recommendations if r.command]
        assert len(with_commands) > 0
