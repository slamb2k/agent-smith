"""Tests for PocketSmith API client."""
import os
import pytest
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
