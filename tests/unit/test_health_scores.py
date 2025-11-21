"""Unit tests for health score system."""

import pytest
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
