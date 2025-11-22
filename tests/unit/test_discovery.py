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
    mock_client.get_transaction_accounts.return_value = [
        {
            "id": 100,
            "name": "Checking",
            "institution": {"title": "Test Bank"},
        },
        {
            "id": 200,
            "name": "Savings",
            "institution": {"title": "Test Bank"},
        },
    ]

    analyzer = DiscoveryAnalyzer(client=mock_client)
    accounts = analyzer._fetch_accounts(user_id=12345)

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
    categories = analyzer._fetch_categories(user_id=12345)

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
    summary = analyzer._fetch_transaction_summary(user_id=12345)

    assert summary.total_count == 2
    assert summary.uncategorized_count == 1
    assert summary.date_range_start == date(2025, 11, 1)
    assert summary.date_range_end == date(2025, 11, 15)


def test_recommend_template_simple():
    """Test simple template recommendation for single user."""
    mock_client = Mock()
    mock_client.get_user.return_value = {"id": 12345}
    mock_client.get_accounts.return_value = [
        {"id": 100, "title": "Checking", "institution": {"title": "Bank"}},
    ]
    mock_client.get_categories.return_value = [
        {"id": 300, "title": "Groceries", "parent_id": None},
    ]
    mock_client.get_transactions.return_value = []

    analyzer = DiscoveryAnalyzer(client=mock_client)
    recommendation = analyzer._recommend_template(
        accounts=[AccountSummary(100, "Checking", "Bank", 0, 0)],
        categories=[CategorySummary(300, "Groceries", None, 0, Decimal("0"))],
    )

    assert recommendation == "simple"


def test_recommend_template_shared_household():
    """Test shared household template for joint accounts."""
    accounts = [
        AccountSummary(100, "Joint Savings", "Bank", 50, 10),
        AccountSummary(200, "Personal", "Bank", 30, 5),
    ]
    categories = [
        CategorySummary(300, "Groceries", None, 25, Decimal("-500")),
        CategorySummary(301, "Shared Expense", None, 15, Decimal("-300")),
    ]

    analyzer = DiscoveryAnalyzer(client=None)
    recommendation = analyzer._recommend_template(accounts, categories)

    assert recommendation == "shared-household"


def test_recommend_template_separated_families():
    """Test separated families template for child support tracking."""
    accounts = [
        AccountSummary(100, "Personal", "Bank", 50, 10),
    ]
    categories = [
        CategorySummary(300, "Child Support", None, 10, Decimal("-800")),
        CategorySummary(301, "Kids Activities", None, 5, Decimal("-200")),
    ]

    analyzer = DiscoveryAnalyzer(client=None)
    recommendation = analyzer._recommend_template(accounts, categories)

    assert recommendation == "separated-families"


def test_recommend_template_advanced():
    """Test advanced template for investment tracking."""
    accounts = [
        AccountSummary(100, "Personal", "Bank", 100, 20),
        AccountSummary(200, "Business", "Bank", 50, 10),
    ]
    categories = [
        CategorySummary(300, "Investment", None, 15, Decimal("5000")),
        CategorySummary(301, "Capital Gains", None, 3, Decimal("1200")),
        CategorySummary(302, "Business Expenses", None, 25, Decimal("-3000")),
    ]

    analyzer = DiscoveryAnalyzer(client=None)
    recommendation = analyzer._recommend_template(accounts, categories)

    assert recommendation == "advanced"


def test_recommend_template_separated_families_substring():
    """Test separated families with substring matching."""
    accounts = [AccountSummary(100, "Personal", "Bank", 50, 10)]
    categories = [
        CategorySummary(300, "Child Support Payments", None, 10, Decimal("-800")),
    ]

    analyzer = DiscoveryAnalyzer(client=None)
    recommendation = analyzer._recommend_template(accounts, categories)

    assert recommendation == "separated-families"


def test_recommend_template_advanced_substring():
    """Test advanced template with substring matching for 'My Investment Portfolio'."""
    accounts = [AccountSummary(100, "Personal", "Bank", 100, 20)]
    categories = [
        CategorySummary(300, "My Investment Portfolio", None, 15, Decimal("5000")),
    ]

    analyzer = DiscoveryAnalyzer(client=None)
    recommendation = analyzer._recommend_template(accounts, categories)

    assert recommendation == "advanced"


def test_recommend_template_shared_household_substring():
    """Test shared household with substring matching for 'Joint Household Bills'."""
    accounts = [
        AccountSummary(100, "Personal", "Bank", 50, 10),
        AccountSummary(200, "Other", "Bank", 30, 5),
    ]
    categories = [
        CategorySummary(300, "Joint Household Bills", None, 15, Decimal("-300")),
    ]

    analyzer = DiscoveryAnalyzer(client=None)
    recommendation = analyzer._recommend_template(accounts, categories)

    assert recommendation == "shared-household"


def test_recommend_template_case_insensitive_substring():
    """Test case-insensitive substring matching with 'MY INVESTMENT ACCOUNT'."""
    accounts = [AccountSummary(100, "Personal", "Bank", 100, 20)]
    categories = [
        CategorySummary(300, "MY INVESTMENT ACCOUNT", None, 15, Decimal("5000")),
    ]

    analyzer = DiscoveryAnalyzer(client=None)
    recommendation = analyzer._recommend_template(accounts, categories)

    assert recommendation == "advanced"


def test_discovery_analyzer_analyze():
    """Test complete discovery analysis."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 12345,
        "login": "test@example.com",
    }
    mock_client.get_transaction_accounts.return_value = [
        {"id": 100, "name": "Checking", "institution": {"title": "Test Bank"}},
    ]
    mock_client.get_categories.return_value = [
        {"id": 300, "title": "Groceries", "parent_id": None},
    ]
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
    report = analyzer.analyze()

    assert report.user_id == 12345
    assert report.user_email == "test@example.com"
    assert len(report.accounts) == 1
    assert report.accounts[0].transaction_count == 1
    assert len(report.categories) == 1
    assert report.transactions.total_count == 1
    assert report.transactions.uncategorized_count == 0
    assert report.recommendation == "simple"
