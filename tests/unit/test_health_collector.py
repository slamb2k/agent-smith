"""Unit tests for health data collection."""

import pytest
from unittest.mock import Mock, MagicMock
from scripts.health.collector import HealthDataCollector


class TestHealthDataCollector:
    """Tests for HealthDataCollector."""

    def test_collector_initialization(self):
        """Collector initializes with API client."""
        mock_client = Mock()
        collector = HealthDataCollector(api_client=mock_client)
        assert collector.api_client == mock_client

    def test_collect_data_quality_metrics(self):
        """Collects data quality metrics from transactions."""
        mock_client = Mock()
        mock_client.get_transactions.return_value = [
            {"id": 1, "category": {"id": 1}, "payee": "Store A"},
            {"id": 2, "category": {"id": 2}, "payee": "Store B"},
            {"id": 3, "category": None, "payee": ""},
            {"id": 4, "category": {"id": 1}, "payee": "Store A"},
        ]

        collector = HealthDataCollector(api_client=mock_client)
        data = collector.collect_data_quality()

        assert data["total_transactions"] == 4
        assert data["categorized_transactions"] == 3
        assert data["transactions_with_payee"] == 3
        assert "duplicate_count" in data

    def test_collect_returns_all_dimensions(self):
        """Collect all returns data for all dimensions."""
        mock_client = Mock()
        mock_client.get_transactions.return_value = []
        mock_client.get_categories.return_value = []
        mock_client.get_user.return_value = {"id": 1}

        collector = HealthDataCollector(api_client=mock_client)

        # Mock all collection methods
        collector.collect_data_quality = Mock(return_value={"total_transactions": 0})
        collector.collect_category_structure = Mock(return_value={"total_categories": 0})
        collector.collect_rule_engine = Mock(return_value={"total_rules": 0})
        collector.collect_tax_readiness = Mock(return_value={"deductible_transactions": 0})
        collector.collect_automation = Mock(return_value={"auto_categorization_enabled": False})
        collector.collect_budget_alignment = Mock(return_value={"categories_with_budget": 0})

        data = collector.collect_all()

        assert "data_quality" in data
        assert "category_structure" in data
        assert "rule_engine" in data
        assert "tax_readiness" in data
        assert "automation" in data
        assert "budget_alignment" in data
