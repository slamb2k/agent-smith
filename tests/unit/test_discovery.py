"""Tests for onboarding discovery module."""

from datetime import date
from decimal import Decimal
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
