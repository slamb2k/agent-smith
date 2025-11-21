"""Unit tests for health monitoring integration."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from scripts.health.monitoring import HealthMonitor, MonitoringConfig


class TestHealthMonitor:
    """Tests for HealthMonitor."""

    def test_monitor_initialization(self):
        """Monitor initializes with config."""
        config = MonitoringConfig(
            weekly_check_enabled=True,
            monthly_full_check_enabled=True,
            alert_on_score_drop=True,
            score_drop_threshold=10,
        )

        monitor = HealthMonitor(config=config)
        assert monitor.config.weekly_check_enabled is True

    def test_should_run_weekly_check(self):
        """Determines when weekly check should run."""
        config = MonitoringConfig(weekly_check_enabled=True)
        monitor = HealthMonitor(config=config)

        # Last check was 8 days ago
        monitor.last_weekly_check = datetime.now() - timedelta(days=8)

        assert monitor.should_run_weekly() is True

    def test_should_not_run_if_recent(self):
        """Skip check if ran recently."""
        config = MonitoringConfig(weekly_check_enabled=True)
        monitor = HealthMonitor(config=config)

        # Last check was 2 days ago
        monitor.last_weekly_check = datetime.now() - timedelta(days=2)

        assert monitor.should_run_weekly() is False

    def test_detect_score_drop(self):
        """Detects significant score drops."""
        config = MonitoringConfig(
            alert_on_score_drop=True,
            score_drop_threshold=10,
        )
        monitor = HealthMonitor(config=config)

        previous = {"data_quality": 80, "rule_engine": 75}
        current = {"data_quality": 65, "rule_engine": 74}  # 15 point drop

        drops = monitor.detect_score_drops(previous, current)

        assert len(drops) == 1
        assert drops[0]["dimension"] == "data_quality"
        assert drops[0]["drop"] == 15

    def test_generate_monitoring_alerts(self):
        """Generates alerts from health check results."""
        config = MonitoringConfig(alert_on_score_drop=True)
        monitor = HealthMonitor(config=config)

        # Mock health check result with low scores
        mock_result = Mock()
        mock_result.overall_score = 45
        mock_result.overall_status = Mock(value="poor")
        mock_result.scores = []  # Empty list so iteration works

        alerts = monitor.generate_alerts(mock_result)

        assert len(alerts) > 0
        assert any("poor" in str(a).lower() or "health" in str(a).lower() for a in alerts)
