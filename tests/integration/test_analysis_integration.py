"""Integration tests for analysis workflows."""

import pytest
import os
from scripts.core.api_client import PocketSmithClient
from scripts.analysis.spending import (
    analyze_spending_by_category,
    filter_transactions_by_period,
    get_period_summary,
)
from scripts.reporting.formatters import format_markdown, format_csv, format_json

pytestmark = pytest.mark.integration


@pytest.fixture
def api_client():
    """Create API client with real credentials."""
    api_key = os.getenv("POCKETSMITH_API_KEY")
    if not api_key:
        pytest.skip("POCKETSMITH_API_KEY not set - skipping integration tests")
    return PocketSmithClient(api_key=api_key)


def test_end_to_end_spending_analysis(api_client):
    """Test complete spending analysis workflow with real API data."""
    # Fetch real transactions
    user = api_client.get_user()
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2025-11-01", end_date="2025-11-30"
    )

    assert len(transactions) > 0, "Need transactions for integration test"

    # Filter by period
    filtered = filter_transactions_by_period(transactions, period="2025-11")
    assert len(filtered) > 0

    # Analyze by category
    category_analysis = analyze_spending_by_category(filtered)
    assert len(category_analysis) > 0
    assert "category_name" in category_analysis[0]
    assert "total_spent" in category_analysis[0]

    # Get period summary
    summary = get_period_summary(filtered)
    assert summary["total_expenses"] >= 0
    assert summary["transaction_count"] == len(filtered)

    print(
        f"✓ End-to-end analysis: {len(filtered)} transactions, "
        f"{len(category_analysis)} categories, ${summary['total_expenses']:.2f} spent"
    )


def test_multi_format_report_generation(api_client):
    """Test generating reports in multiple formats."""
    # Fetch transactions
    user = api_client.get_user()
    transactions = api_client.get_transactions(user_id=user["id"], per_page=50)

    # Analyze
    categories = analyze_spending_by_category(transactions)
    summary = get_period_summary(transactions)

    report_data = {
        "period": "2025-11",
        "summary": summary,
        "categories": categories[:5],  # Top 5
    }

    # Test all formats
    markdown_report = format_markdown(report_data, report_type="spending")
    assert "# Spending Report" in markdown_report
    assert len(markdown_report) > 100

    csv_report = format_csv(report_data, report_type="spending")
    assert "category_name" in csv_report

    json_report = format_json(report_data)
    assert '"period"' in json_report
    assert '"summary"' in json_report

    print(
        f"✓ Multi-format reports generated: MD ({len(markdown_report)} chars), "
        f"CSV ({len(csv_report)} chars), JSON ({len(json_report)} chars)"
    )
