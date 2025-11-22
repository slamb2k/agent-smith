"""Tests for onboarding discovery module."""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock
from scripts.onboarding.discovery import (
    DiscoveryAnalyzer,
    DiscoveryReport,
    AccountSummary,
    CategorySummary,
    TransactionSummary,
)


def test_discovery_report_structure():
    """Test DiscoveryReport dataclass structure."""
    report = DiscoveryReport(
        user_id=12345,
        user_email="test@example.com",
        accounts=[],
        categories=[],
        transactions=TransactionSummary(
            total_count=0,
            uncategorized_count=0,
            date_range_start=None,
            date_range_end=None,
            by_account={},
        ),
        baseline_health_score=None,
        recommendation="simple",
    )

    assert report.user_id == 12345
    assert report.user_email == "test@example.com"
    assert report.recommendation == "simple"


def test_account_summary_creation():
    """Test AccountSummary dataclass."""
    account = AccountSummary(
        id=123,
        name="Personal Checking",
        institution="Test Bank",
        transaction_count=100,
        uncategorized_count=50,
    )

    assert account.id == 123
    assert account.name == "Personal Checking"
    assert account.uncategorized_count == 50


def test_category_summary_creation():
    """Test CategorySummary dataclass."""
    category = CategorySummary(
        id=456,
        title="Groceries",
        parent_title=None,
        transaction_count=25,
        total_amount=Decimal("-500.00"),
    )

    assert category.id == 456
    assert category.title == "Groceries"
    assert category.total_amount == Decimal("-500.00")


def test_discovery_analyzer_fetch_accounts():
    """Test fetching account summaries."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 12345,
        "login": "test@example.com",
    }
    mock_client.get_accounts.return_value = [
        {
            "id": 100,
            "title": "Checking",
            "institution": {"title": "Test Bank"},
        },
        {
            "id": 200,
            "title": "Savings",
            "institution": {"title": "Test Bank"},
        },
    ]

    analyzer = DiscoveryAnalyzer(client=mock_client)
    accounts = analyzer._fetch_accounts()

    assert len(accounts) == 2
    assert accounts[0].id == 100
    assert accounts[0].name == "Checking"
    assert accounts[0].institution == "Test Bank"


def test_discovery_analyzer_fetch_categories():
    """Test fetching category summaries."""
    mock_client = Mock()
    mock_client.get_user.return_value = {"id": 12345}
    mock_client.get_categories.return_value = [
        {
            "id": 300,
            "title": "Groceries",
            "parent_id": None,
        },
        {
            "id": 301,
            "title": "Supermarket",
            "parent_id": 300,
        },
    ]

    analyzer = DiscoveryAnalyzer(client=mock_client)
    categories = analyzer._fetch_categories()

    assert len(categories) == 2
    assert categories[0].id == 300
    assert categories[0].title == "Groceries"
    assert categories[0].parent_title is None


def test_discovery_analyzer_fetch_transactions():
    """Test fetching transaction summary."""
    mock_client = Mock()
    mock_client.get_user.return_value = {"id": 12345}
    mock_client.get_transactions.return_value = [
        {
            "id": 1,
            "payee": "Woolworths",
            "amount": -50.00,
            "date": "2025-11-01",
            "category": {"id": 300},
            "transaction_account": {"id": 100},
        },
        {
            "id": 2,
            "payee": "Unknown",
            "amount": -25.00,
            "date": "2025-11-15",
            "category": None,
            "transaction_account": {"id": 100},
        },
    ]

    analyzer = DiscoveryAnalyzer(client=mock_client)
    summary = analyzer._fetch_transaction_summary()

    assert summary.total_count == 2
    assert summary.uncategorized_count == 1
    assert summary.date_range_start == date(2025, 11, 1)
    assert summary.date_range_end == date(2025, 11, 15)
