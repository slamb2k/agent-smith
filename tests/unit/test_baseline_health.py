"""Tests for baseline health check."""

from unittest.mock import Mock, MagicMock
from scripts.onboarding.baseline_health import BaselineHealthChecker
from scripts.onboarding.discovery import DiscoveryAnalyzer


def test_baseline_health_checker_creation():
    """Test BaselineHealthChecker initialization."""
    mock_client = Mock()
    checker = BaselineHealthChecker(client=mock_client, user_id=123)

    assert checker.client == mock_client
    assert checker.user_id == 123


def test_run_baseline_check():
    """Test running baseline health check."""
    mock_client = Mock()
    mock_client.get_user.return_value = {"id": 12345}

    # Mock transactions data for data_quality collection
    mock_client.get_transactions.return_value = [
        {
            "id": 1,
            "payee": "Store",
            "amount": -50.00,
            "date": "2025-11-01",
            "category": {"id": 300, "name": "Groceries"},
        },
        {"id": 2, "payee": "Shop", "amount": -25.00, "date": "2025-11-02", "category": None},
    ]

    # Mock categories data for category_structure collection
    mock_client.get_categories.return_value = [
        {"id": 300, "title": "Groceries", "parent_id": None, "transaction_count": 1},
        {"id": 301, "title": "Dining", "parent_id": None, "transaction_count": 0},
    ]

    # Mock budgets (optional method)
    mock_client.get_budgets = Mock(return_value=[])

    checker = BaselineHealthChecker(client=mock_client, user_id=12345)
    score = checker.run_baseline_check()

    assert isinstance(score, int)
    assert 0 <= score <= 100


def test_discovery_analyze_with_health_check():
    """Test discovery analyze with health check integration."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 12345,
        "login": "test@example.com",
    }

    # Mock transaction accounts (note: different from get_accounts)
    mock_client.get_transaction_accounts.return_value = [
        {"id": 100, "name": "Checking", "institution": {"title": "Test Bank"}},
    ]

    # Mock categories
    mock_client.get_categories.return_value = [
        {"id": 300, "title": "Groceries", "parent_id": None, "transaction_count": 1},
    ]

    # Mock transactions
    mock_client.get_transactions.return_value = [
        {
            "id": 1,
            "payee": "Store",
            "amount": -50.00,
            "date": "2025-11-01",
            "category": {"id": 300, "name": "Groceries"},
            "transaction_account": {"id": 100},
        },
    ]

    # Mock budgets
    mock_client.get_budgets = Mock(return_value=[])

    analyzer = DiscoveryAnalyzer(client=mock_client)
    report = analyzer.analyze(include_health_check=True)

    assert report.user_id == 12345
    assert report.user_email == "test@example.com"
    assert report.baseline_health_score is not None
    assert isinstance(report.baseline_health_score, int)
    assert 0 <= report.baseline_health_score <= 100


def test_discovery_analyze_without_health_check():
    """Test discovery analyze without health check."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 12345,
        "login": "test@example.com",
    }

    # Mock transaction accounts
    mock_client.get_transaction_accounts.return_value = [
        {"id": 100, "name": "Checking", "institution": {"title": "Test Bank"}},
    ]

    # Mock categories
    mock_client.get_categories.return_value = [
        {"id": 300, "title": "Groceries", "parent_id": None, "transaction_count": 1},
    ]

    # Mock transactions
    mock_client.get_transactions.return_value = [
        {
            "id": 1,
            "payee": "Store",
            "amount": -50.00,
            "date": "2025-11-01",
            "category": {"id": 300},
            "transaction_account": {"id": 100},
        },
    ]

    analyzer = DiscoveryAnalyzer(client=mock_client)
    report = analyzer.analyze(include_health_check=False)

    assert report.user_id == 12345
    assert report.user_email == "test@example.com"
    assert report.baseline_health_score is None
