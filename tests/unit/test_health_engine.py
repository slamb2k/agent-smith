"""Unit tests for HealthCheckEngine."""

import pytest
from datetime import datetime
from scripts.health.engine import HealthCheckEngine, HealthCheckResult
from scripts.health.scores import HealthScore, HealthStatus


class TestHealthCheckEngine:
    """Tests for HealthCheckEngine."""

    def test_engine_initialization(self):
        """Engine initializes with all scorers."""
        engine = HealthCheckEngine()
        assert len(engine.scorers) == 6
        dimensions = {s.dimension for s in engine.scorers}
        assert "data_quality" in dimensions
        assert "category_structure" in dimensions
        assert "rule_engine" in dimensions
        assert "tax_readiness" in dimensions
        assert "automation" in dimensions
        assert "budget_alignment" in dimensions

    def test_run_all_checks(self):
        """Running all checks returns complete result."""
        engine = HealthCheckEngine()

        # Provide data for all scorers
        data = {
            "data_quality": {
                "total_transactions": 100,
                "categorized_transactions": 90,
                "transactions_with_payee": 95,
                "duplicate_count": 2,
            },
            "category_structure": {
                "total_categories": 30,
                "categories_with_transactions": 25,
                "max_depth": 3,
                "categories_at_root": 8,
                "ato_mapped_categories": 20,
                "empty_categories": 5,
            },
            "rule_engine": {
                "total_rules": 40,
                "active_rules": 38,
                "auto_categorization_rate": 0.75,
                "rule_accuracy": 0.92,
                "conflicting_rules": 1,
                "stale_rules": 2,
            },
            "tax_readiness": {
                "deductible_transactions": 50,
                "substantiated_transactions": 45,
                "ato_category_coverage": 0.80,
                "cgt_events_tracked": 3,
                "cgt_events_total": 3,
                "missing_documentation_count": 5,
                "days_to_eofy": 200,
            },
            "automation": {
                "auto_categorization_enabled": True,
                "scheduled_reports_count": 2,
                "active_alerts_count": 4,
                "rule_auto_apply_rate": 0.80,
                "manual_operations_30d": 20,
                "total_operations_30d": 100,
            },
            "budget_alignment": {
                "categories_with_budget": 8,
                "categories_on_track": 7,
                "categories_over_budget": 1,
                "total_budget": 4000.00,
                "total_spent": 3800.00,
                "goals_on_track": 2,
                "goals_total": 2,
            },
        }

        result = engine.run_all(data)

        assert isinstance(result, HealthCheckResult)
        assert len(result.scores) == 6
        assert result.overall_score > 0
        assert result.overall_status in HealthStatus
        assert len(result.top_recommendations) > 0

    def test_run_single_check(self):
        """Can run single dimension check."""
        engine = HealthCheckEngine()

        data = {
            "total_transactions": 100,
            "categorized_transactions": 80,
            "transactions_with_payee": 90,
            "duplicate_count": 5,
        }

        score = engine.run_single("data_quality", data)

        assert score.dimension == "data_quality"
        assert 0 <= score.score <= 100

    def test_overall_score_calculation(self):
        """Overall score is weighted average of dimension scores."""
        engine = HealthCheckEngine()

        # Create mock scores
        scores = [
            HealthScore(dimension="data_quality", score=80),
            HealthScore(dimension="category_structure", score=70),
            HealthScore(dimension="rule_engine", score=60),
            HealthScore(dimension="tax_readiness", score=90),
            HealthScore(dimension="automation", score=50),
            HealthScore(dimension="budget_alignment", score=85),
        ]

        overall = engine._calculate_overall(scores)
        # Should be weighted average
        assert 60 <= overall <= 80
