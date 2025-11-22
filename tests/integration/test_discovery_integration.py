"""Integration tests for discovery module."""

import pytest
from scripts.core.api_client import PocketSmithClient
from scripts.onboarding.discovery import DiscoveryAnalyzer


@pytest.mark.integration
def test_discovery_with_real_api():
    """Test discovery with real PocketSmith API."""
    client = PocketSmithClient()
    analyzer = DiscoveryAnalyzer(client=client)

    report = analyzer.analyze(include_health_check=False)

    # Basic assertions
    assert report.user_id > 0
    assert report.user_email
    assert isinstance(report.accounts, list)
    assert isinstance(report.categories, list)
    assert report.transactions.total_count >= 0
    assert report.recommendation in ["simple", "separated-families", "shared-household", "advanced"]

    # Print summary for manual verification
    print(f"\n{'='*60}")
    print(f"Discovery Report for {report.user_email}")
    print(f"{'='*60}")
    print(f"User ID: {report.user_id}")
    print(f"Accounts: {len(report.accounts)}")
    print(f"Categories: {len(report.categories)}")
    print(f"Transactions: {report.transactions.total_count}")
    print(f"Uncategorized: {report.transactions.uncategorized_count}")
    print(
        f"Date Range: {report.transactions.date_range_start} to "
        f"{report.transactions.date_range_end}"
    )
    print(f"Recommended Template: {report.recommendation}")
    print(f"{'='*60}")
