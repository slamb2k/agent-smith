"""Integration tests for PocketSmith API client.

These tests require:
- Valid POCKETSMITH_API_KEY in .env
- Active internet connection
- Run with: pytest -m integration
"""
import os
import pytest
from scripts.core.api_client import PocketSmithClient


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def api_client():
    """Create API client with real credentials."""
    api_key = os.getenv("POCKETSMITH_API_KEY")
    if not api_key:
        pytest.skip("POCKETSMITH_API_KEY not set - skipping integration tests")

    return PocketSmithClient(api_key=api_key)


def test_get_user_returns_real_data(api_client):
    """Test that get_user returns actual user data from API."""
    user = api_client.get_user()

    # Verify response structure
    assert "id" in user
    assert "login" in user
    assert isinstance(user["id"], int)

    print(f"✓ Connected as user: {user.get('login')} (ID: {user['id']})")


def test_get_categories_returns_data(api_client):
    """Test that get_categories returns category tree."""
    user = api_client.get_user()
    user_id = user["id"]

    categories = api_client.get_categories(user_id=user_id)

    # Should return list of categories
    assert isinstance(categories, list)
    assert len(categories) > 0

    # Each category should have required fields
    for cat in categories[:5]:  # Check first 5
        assert "id" in cat
        assert "title" in cat

    print(f"✓ Retrieved {len(categories)} categories")


def test_get_transactions_with_filters(api_client):
    """Test getting transactions with date filters."""
    user = api_client.get_user()
    user_id = user["id"]

    # Get recent transactions
    transactions = api_client.get_transactions(
        user_id=user_id,
        start_date="2025-01-01",
        end_date="2025-12-31",
        per_page=10
    )

    # Should return list (may be empty)
    assert isinstance(transactions, list)

    if transactions:
        # Check structure of first transaction
        tx = transactions[0]
        assert "id" in tx
        assert "payee" in tx
        assert "amount" in tx

        print(f"✓ Retrieved {len(transactions)} transactions")
    else:
        print("✓ No transactions in date range (valid response)")


def test_rate_limiting_works(api_client):
    """Test that rate limiting delays requests appropriately."""
    import time

    # Make multiple requests and verify timing
    start = time.time()

    for _ in range(3):
        api_client.get_user()

    elapsed = time.time() - start

    # Should take at least 2 * rate_limit_delay (0.1s default)
    # 3 requests = 2 delays minimum
    assert elapsed >= 0.2, "Rate limiting should delay requests"

    print(f"✓ Rate limiting working (3 requests took {elapsed:.2f}s)")
