"""Unit tests for health score system."""

from scripts.health.scores import HealthStatus, HealthScore


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
