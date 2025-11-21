"""Unit tests for health score system."""

import pytest

from scripts.health.scores import BaseScorer, HealthStatus, HealthScore


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_status_from_score_excellent(self):
        """Score 90-100 should be EXCELLENT."""
        assert HealthStatus.from_score(90) == HealthStatus.EXCELLENT
        assert HealthStatus.from_score(100) == HealthStatus.EXCELLENT

    def test_status_from_score_good(self):
        """Score 70-89 should be GOOD."""
        assert HealthStatus.from_score(70) == HealthStatus.GOOD
        assert HealthStatus.from_score(89) == HealthStatus.GOOD

    def test_status_from_score_fair(self):
        """Score 50-69 should be FAIR."""
        assert HealthStatus.from_score(50) == HealthStatus.FAIR
        assert HealthStatus.from_score(69) == HealthStatus.FAIR

    def test_status_from_score_poor(self):
        """Score below 50 should be POOR."""
        assert HealthStatus.from_score(0) == HealthStatus.POOR
        assert HealthStatus.from_score(49) == HealthStatus.POOR

    def test_emoji_property(self):
        """Each status should have correct emoji."""
        assert HealthStatus.EXCELLENT.emoji == "✅"
        assert HealthStatus.GOOD.emoji == "👍"
        assert HealthStatus.FAIR.emoji == "⚠️"
        assert HealthStatus.POOR.emoji == "❌"

    def test_from_score_clamps_high_values(self):
        """Scores above 100 should be clamped to 100 (EXCELLENT)."""
        assert HealthStatus.from_score(101) == HealthStatus.EXCELLENT
        assert HealthStatus.from_score(150) == HealthStatus.EXCELLENT
        assert HealthStatus.from_score(1000) == HealthStatus.EXCELLENT

    def test_from_score_clamps_negative_values(self):
        """Negative scores should be clamped to 0 (POOR)."""
        assert HealthStatus.from_score(-1) == HealthStatus.POOR
        assert HealthStatus.from_score(-50) == HealthStatus.POOR
        assert HealthStatus.from_score(-1000) == HealthStatus.POOR


class TestHealthScore:
    """Tests for HealthScore dataclass."""

    def test_health_score_creation(self):
        """Test creating a health score."""
        score = HealthScore(
            dimension="data_quality",
            score=85,
            max_score=100,
            issues=["10 uncategorized transactions"],
            recommendations=["Categorize remaining transactions"],
        )

        assert score.dimension == "data_quality"
        assert score.score == 85
        assert score.status == HealthStatus.GOOD
        assert len(score.issues) == 1
        assert len(score.recommendations) == 1

    def test_health_score_percentage(self):
        """Test percentage calculation."""
        score = HealthScore(dimension="test", score=75, max_score=100)
        assert score.percentage == 75.0

        score2 = HealthScore(dimension="test", score=15, max_score=20)
        assert score2.percentage == 75.0

    def test_health_score_to_dict(self):
        """Test serialization to dict."""
        score = HealthScore(
            dimension="rule_engine",
            score=60,
            max_score=100,
            issues=["Low coverage"],
        )

        data = score.to_dict()
        assert data["dimension"] == "rule_engine"
        assert data["score"] == 60
        assert data["status"] == "fair"
        assert "timestamp" in data


class TestBaseScorer:
    """Tests for BaseScorer abstract class."""

    def test_concrete_scorer_must_implement_calculate(self):
        """Concrete scorers must implement calculate method."""

        class IncompleteScorer(BaseScorer):
            dimension = "incomplete"

        with pytest.raises(TypeError):
            IncompleteScorer()

    def test_concrete_scorer_works(self):
        """A properly implemented scorer should work."""

        class TestScorer(BaseScorer):
            dimension = "test_dimension"

            def calculate(self, data):
                return HealthScore(
                    dimension=self.dimension,
                    score=100,
                    max_score=100,
                )

        scorer = TestScorer()
        result = scorer.calculate({})
        assert result.dimension == "test_dimension"
        assert result.score == 100


class TestDataQualityScorer:
    """Tests for DataQualityScorer."""

    def test_perfect_data_quality(self):
        """All transactions categorized = 100 score."""
        from scripts.health.scores import DataQualityScorer

        scorer = DataQualityScorer()
        data = {
            "total_transactions": 100,
            "categorized_transactions": 100,
            "transactions_with_payee": 100,
            "duplicate_count": 0,
        }

        result = scorer.calculate(data)
        assert result.dimension == "data_quality"
        assert result.score == 100
        assert result.status == HealthStatus.EXCELLENT
        assert len(result.issues) == 0

    def test_uncategorized_transactions_reduce_score(self):
        """Uncategorized transactions reduce score."""
        from scripts.health.scores import DataQualityScorer

        scorer = DataQualityScorer()
        data = {
            "total_transactions": 100,
            "categorized_transactions": 80,
            "transactions_with_payee": 100,
            "duplicate_count": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 100
        assert "uncategorized" in result.issues[0].lower()

    def test_duplicates_reduce_score(self):
        """Duplicate transactions reduce score."""
        from scripts.health.scores import DataQualityScorer

        scorer = DataQualityScorer()
        data = {
            "total_transactions": 100,
            "categorized_transactions": 100,
            "transactions_with_payee": 100,
            "duplicate_count": 10,
        }

        result = scorer.calculate(data)
        assert result.score < 100
        assert any("duplicate" in issue.lower() for issue in result.issues)

    def test_missing_payees_reduce_score(self):
        """Missing payee names reduce score."""
        from scripts.health.scores import DataQualityScorer

        scorer = DataQualityScorer()
        data = {
            "total_transactions": 100,
            "categorized_transactions": 100,
            "transactions_with_payee": 70,
            "duplicate_count": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 100
        assert any("payee" in issue.lower() for issue in result.issues)

    def test_empty_data_returns_zero(self):
        """No transactions = 0 score."""
        from scripts.health.scores import DataQualityScorer

        scorer = DataQualityScorer()
        data = {
            "total_transactions": 0,
            "categorized_transactions": 0,
            "transactions_with_payee": 0,
            "duplicate_count": 0,
        }

        result = scorer.calculate(data)
        assert result.score == 0


class TestCategoryStructureScorer:
    """Tests for CategoryStructureScorer."""

    def test_good_category_structure(self):
        """Well-organized categories score high."""
        from scripts.health.scores import CategoryStructureScorer

        scorer = CategoryStructureScorer()
        data = {
            "total_categories": 30,
            "categories_with_transactions": 25,
            "max_depth": 3,
            "categories_at_root": 8,
            "ato_mapped_categories": 20,
            "empty_categories": 5,
        }

        result = scorer.calculate(data)
        assert result.dimension == "category_structure"
        assert result.score >= 70
        assert result.status in [HealthStatus.GOOD, HealthStatus.EXCELLENT]

    def test_too_many_root_categories_penalized(self):
        """Too many root categories indicates poor organization."""
        from scripts.health.scores import CategoryStructureScorer

        scorer = CategoryStructureScorer()
        data = {
            "total_categories": 50,
            "categories_with_transactions": 50,
            "max_depth": 1,  # All flat
            "categories_at_root": 50,  # All at root
            "ato_mapped_categories": 10,
            "empty_categories": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 70
        assert any(
            "root" in issue.lower() or "hierarchy" in issue.lower() for issue in result.issues
        )

    def test_many_empty_categories_penalized(self):
        """Many unused categories reduce score."""
        from scripts.health.scores import CategoryStructureScorer

        scorer = CategoryStructureScorer()
        data = {
            "total_categories": 50,
            "categories_with_transactions": 10,
            "max_depth": 3,
            "categories_at_root": 10,
            "ato_mapped_categories": 10,
            "empty_categories": 40,
        }

        result = scorer.calculate(data)
        assert result.score < 70
        assert any("empty" in issue.lower() or "unused" in issue.lower() for issue in result.issues)

    def test_poor_ato_mapping_penalized(self):
        """Poor ATO category mapping reduces tax readiness."""
        from scripts.health.scores import CategoryStructureScorer

        scorer = CategoryStructureScorer()
        data = {
            "total_categories": 30,
            "categories_with_transactions": 30,
            "max_depth": 3,
            "categories_at_root": 8,
            "ato_mapped_categories": 5,  # Only 5 of 30 mapped
            "empty_categories": 0,
        }

        result = scorer.calculate(data)
        # Score should be reduced due to poor ATO mapping
        assert any("ato" in issue.lower() or "tax" in issue.lower() for issue in result.issues)


class TestRuleEngineScorer:
    """Tests for RuleEngineScorer."""

    def test_high_coverage_high_accuracy(self):
        """High rule coverage and accuracy = excellent score."""
        from scripts.health.scores import RuleEngineScorer

        scorer = RuleEngineScorer()
        data = {
            "total_rules": 50,
            "active_rules": 48,
            "auto_categorization_rate": 0.85,
            "rule_accuracy": 0.95,
            "conflicting_rules": 0,
            "stale_rules": 2,
        }

        result = scorer.calculate(data)
        assert result.dimension == "rule_engine"
        assert result.score >= 80
        assert result.status in [HealthStatus.GOOD, HealthStatus.EXCELLENT]

    def test_low_coverage_penalized(self):
        """Low auto-categorization rate reduces score."""
        from scripts.health.scores import RuleEngineScorer

        scorer = RuleEngineScorer()
        data = {
            "total_rules": 10,
            "active_rules": 10,
            "auto_categorization_rate": 0.20,  # Only 20% auto-categorized
            "rule_accuracy": 0.90,
            "conflicting_rules": 0,
            "stale_rules": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 70
        assert any("coverage" in issue.lower() for issue in result.issues)

    def test_conflicting_rules_penalized(self):
        """Conflicting rules reduce score."""
        from scripts.health.scores import RuleEngineScorer

        scorer = RuleEngineScorer()
        data = {
            "total_rules": 50,
            "active_rules": 50,
            "auto_categorization_rate": 0.80,
            "rule_accuracy": 0.90,
            "conflicting_rules": 10,
            "stale_rules": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 90
        assert any("conflict" in issue.lower() for issue in result.issues)

    def test_low_accuracy_penalized(self):
        """Low rule accuracy (high override rate) reduces score."""
        from scripts.health.scores import RuleEngineScorer

        scorer = RuleEngineScorer()
        data = {
            "total_rules": 50,
            "active_rules": 50,
            "auto_categorization_rate": 0.80,
            "rule_accuracy": 0.60,  # 40% override rate
            "conflicting_rules": 0,
            "stale_rules": 0,
        }

        result = scorer.calculate(data)
        # Low accuracy (60%) significantly reduces the score compared to high accuracy (95%)
        # Coverage: 40pts, Accuracy: 24pts (60% * 40), Health: 20pts = 84 total
        assert result.score < 90  # Below excellent threshold due to low accuracy
        assert any(
            "accuracy" in issue.lower() or "override" in issue.lower() for issue in result.issues
        )
