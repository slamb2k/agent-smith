"""Tests for PocketSmith API client."""

import os
import pytest
from unittest.mock import Mock, patch
import requests
from scripts.core.api_client import PocketSmithClient


def test_api_client_requires_api_key(monkeypatch):
    """API client should raise error if no API key provided."""
    # Temporarily remove environment variable
    monkeypatch.delenv("POCKETSMITH_API_KEY", raising=False)

    with pytest.raises(ValueError, match="API key is required"):
        PocketSmithClient(api_key=None)


def test_api_client_accepts_api_key():
    """API client should initialize with valid API key."""
    client = PocketSmithClient(api_key="test_key_12345")
    assert client.api_key == "test_key_12345"


def test_api_client_sets_base_url():
    """API client should set correct base URL."""
    client = PocketSmithClient(api_key="test_key")
    assert client.base_url == "https://api.pocketsmith.com/v2"


def test_api_client_sets_default_rate_limit():
    """API client should set default rate limit delay."""
    client = PocketSmithClient(api_key="test_key")
    assert client.rate_limit_delay == 0.1  # 100ms default


@patch("scripts.core.api_client.requests.get")
def test_api_client_get_request(mock_get):
    """Test GET request with proper headers and rate limiting."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 123, "name": "Test User"}
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    result = client.get("/me")

    assert result == {"id": 123, "name": "Test User"}
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://api.pocketsmith.com/v2/me"
    assert kwargs["headers"]["X-Developer-Key"] == "test_key"


@patch("scripts.core.api_client.requests.get")
def test_api_client_handles_404(mock_get):
    """Test handling of 404 Not Found responses."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")

    with pytest.raises(requests.HTTPError):
        client.get("/nonexistent")


@patch("scripts.core.api_client.requests.get")
def test_api_client_enforces_rate_limiting(mock_get):
    """Test that rate limiting delay is enforced between requests."""
    import time

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key", rate_limit_delay=0.05)

    start = time.time()
    client.get("/me")
    client.get("/me")
    elapsed = time.time() - start

    # Should take at least rate_limit_delay (50ms)
    assert elapsed >= 0.05


@patch("scripts.core.api_client.requests.post")
def test_api_client_post_request(mock_post):
    """Test POST request with proper headers and rate limiting."""
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 456, "created": True}
    mock_post.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    result = client.post("/categories", data={"name": "Test Category"})

    assert result == {"id": 456, "created": True}
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.pocketsmith.com/v2/categories"
    assert kwargs["headers"]["X-Developer-Key"] == "test_key"
    assert kwargs["json"] == {"name": "Test Category"}


@patch("scripts.core.api_client.requests.put")
def test_api_client_put_request(mock_put):
    """Test PUT request with proper headers and rate limiting."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 456, "updated": True}
    mock_put.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    result = client.put("/categories/456", data={"name": "Updated Category"})

    assert result == {"id": 456, "updated": True}
    mock_put.assert_called_once()
    args, kwargs = mock_put.call_args
    assert args[0] == "https://api.pocketsmith.com/v2/categories/456"
    assert kwargs["headers"]["X-Developer-Key"] == "test_key"
    assert kwargs["json"] == {"name": "Updated Category"}


@patch("scripts.core.api_client.requests.delete")
def test_api_client_delete_request(mock_delete):
    """Test DELETE request with proper headers and rate limiting."""
    mock_response = Mock()
    mock_response.status_code = 204
    mock_response.text = ""
    mock_delete.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    result = client.delete("/categories/456")

    assert result is None
    mock_delete.assert_called_once()
    args, kwargs = mock_delete.call_args
    assert args[0] == "https://api.pocketsmith.com/v2/categories/456"
    assert kwargs["headers"]["X-Developer-Key"] == "test_key"


@patch("scripts.core.api_client.requests.get")
def test_get_user(mock_get):
    """Test get_user retrieves authorized user info."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 217031,
        "login": "testuser",
        "name": "Test User",
        "email": "test@example.com",
    }
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    user = client.get_user()

    assert user["id"] == 217031
    assert user["login"] == "testuser"


@patch("scripts.core.api_client.requests.get")
def test_get_transactions(mock_get):
    """Test get_transactions with filters."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "payee": "Test Store", "amount": "-50.00"},
        {"id": 2, "payee": "Income", "amount": "1000.00"},
    ]
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    transactions = client.get_transactions(
        user_id=217031, start_date="2025-01-01", end_date="2025-01-31"
    )

    assert len(transactions) == 2
    assert transactions[0]["payee"] == "Test Store"

    # Verify correct parameters passed
    args, kwargs = mock_get.call_args
    assert (
        "start_date=2025-01-01" in args[0]
        or kwargs.get("params", {}).get("start_date") == "2025-01-01"
    )


@patch("scripts.core.api_client.requests.get")
def test_get_categories(mock_get):
    """Test get_categories retrieves category tree."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 100, "title": "Income", "is_transfer": False},
        {"id": 200, "title": "Expenses", "is_transfer": False},
    ]
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    categories = client.get_categories(user_id=217031)

    assert len(categories) == 2
    assert categories[0]["title"] == "Income"
