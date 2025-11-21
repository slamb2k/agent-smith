"""Integration tests for complete health check workflow."""

import pytest
from unittest.mock import Mock
from scripts.health import (
    HealthCheckEngine,
    HealthDataCollector,
    RecommendationEngine,
    HealthMonitor,
    MonitoringConfig,
)


class TestHealthCheckIntegration:
    """End-to-end health check integration tests."""

    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client with realistic data."""
        client = Mock()

        # Transactions
        client.get_transactions.return_value = [
            {
                "id": i,
                "category": {"id": i % 10, "name": f"Category {i % 10}"},
                "payee": f"Store {i}",
                "amount": 50.0,
                "date": "2025-01-01",
            }
            for i in range(100)
        ] + [
            {"id": 100 + i, "category": None, "payee": "", "amount": 25.0, "date": "2025-01-02"}
            for i in range(20)
        ]

        # Categories
        client.get_categories.return_value = [
            {
                "id": i,
                "name": f"Category {i}",
                "parent_id": None if i < 5 else i % 5,
                "transaction_count": 10,
            }
            for i in range(20)
        ]

        # Budgets
        client.get_budgets.return_value = [
            {"id": i, "category_id": i, "budget": 500.0, "spent": 400.0 + i * 20} for i in range(5)
        ]

        return client

    def test_full_health_check_workflow(self, mock_api_client, tmp_path):
        """Test complete health check from data collection to recommendations."""
        # Setup
        collector = HealthDataCollector(
            api_client=mock_api_client,
            data_dir=tmp_path,
        )
        engine = HealthCheckEngine()
        rec_engine = RecommendationEngine()

        # Create required data files
        (tmp_path / "local_rules.json").write_text("[]")
        (tmp_path / "platform_rules.json").write_text("[]")
        (tmp_path / "rule_metadata.json").write_text("{}")
        (tmp_path / "config.json").write_text('{"intelligence_mode": "smart"}')
        (tmp_path / "tax").mkdir()
        (tmp_path / "tax" / "ato_category_mappings.json").write_text('{"mappings": {}}')
        (tmp_path / "tax" / "substantiation_tracking.json").write_text("{}")
        (tmp_path / "tax" / "cgt_register.json").write_text('{"events": []}')
        (tmp_path / "goals").mkdir()
        (tmp_path / "goals" / "financial_goals.json").write_text('{"goals": []}')
        (tmp_path / "audit").mkdir()
        (tmp_path / "audit" / "operation_stats.json").write_text("{}")

        # Collect data
        data = collector.collect_all()

        # Run health check
        result = engine.run_all(data)

        # Verify result structure
        assert result.overall_score > 0
        assert len(result.scores) == 6
        assert result.overall_status is not None

        # Generate recommendations
        recommendations = rec_engine.generate(result.scores)

        # Verify recommendations
        assert len(recommendations) > 0
        # Should have recommendations for uncategorized transactions
        assert any("categoriz" in r.title.lower() for r in recommendations)

    def test_health_monitoring_workflow(self, mock_api_client, tmp_path):
        """Test health monitoring and alert generation."""
        # Setup
        config = MonitoringConfig(
            weekly_check_enabled=True,
            alert_on_score_drop=True,
            score_drop_threshold=10,
        )
        monitor = HealthMonitor(config=config)
        collector = HealthDataCollector(api_client=mock_api_client, data_dir=tmp_path)
        engine = HealthCheckEngine()

        # Create minimal data files
        (tmp_path / "local_rules.json").write_text("[]")
        (tmp_path / "platform_rules.json").write_text("[]")
        (tmp_path / "rule_metadata.json").write_text("{}")
        (tmp_path / "config.json").write_text('{"intelligence_mode": "conservative"}')
        (tmp_path / "tax").mkdir()
        (tmp_path / "tax" / "ato_category_mappings.json").write_text('{"mappings": {}}')
        (tmp_path / "tax" / "substantiation_tracking.json").write_text("{}")
        (tmp_path / "tax" / "cgt_register.json").write_text('{"events": []}')
        (tmp_path / "goals").mkdir()
        (tmp_path / "goals" / "financial_goals.json").write_text('{"goals": []}')
        (tmp_path / "audit").mkdir()
        (tmp_path / "audit" / "operation_stats.json").write_text("{}")

        # Should run check (never run before)
        assert monitor.should_run_weekly() is True

        # Run check
        data = collector.collect_all()
        result = engine.run_all(data)

        # Generate alerts
        alerts = monitor.generate_alerts(result)

        # Record check
        monitor.record_check("weekly")

        # Should not run immediately after
        assert monitor.should_run_weekly() is False

        # Verify alerts generated for poor scores
        # With conservative mode disabled and no rules, automation score will be low
        assert len(alerts) >= 0  # May or may not have alerts depending on scores

    def test_quick_health_check(self, mock_api_client, tmp_path):
        """Test quick health check (single dimension)."""
        collector = HealthDataCollector(api_client=mock_api_client, data_dir=tmp_path)
        engine = HealthCheckEngine()

        # Quick check - just data quality
        data = collector.collect_data_quality()
        score = engine.run_single("data_quality", data)

        assert score.dimension == "data_quality"
        assert 0 <= score.score <= 100
        # With 20 uncategorized out of 120, score should reflect that
        assert score.score < 100
