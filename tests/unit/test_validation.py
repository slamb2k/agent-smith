"""Tests for validation utility."""

import pytest
from scripts.utils.validation import (
    validate_date_format,
    validate_transaction_data,
    validate_category_data,
    ValidationError,
)


def test_validate_date_format_accepts_valid_dates():
    """Test date validation accepts YYYY-MM-DD format."""
    assert validate_date_format("2025-01-15") is True
    assert validate_date_format("2025-12-31") is True


def test_validate_date_format_rejects_invalid_dates():
    """Test date validation rejects invalid formats."""
    with pytest.raises(ValidationError):
        validate_date_format("2025/01/15")

    with pytest.raises(ValidationError):
        validate_date_format("15-01-2025")

    with pytest.raises(ValidationError):
        validate_date_format("2025-13-01")  # Invalid month


def test_validate_transaction_data_accepts_valid_transaction():
    """Test transaction validation accepts valid data."""
    transaction = {
        "id": 12345,
        "payee": "Test Store",
        "amount": "-50.00",
        "date": "2025-01-15",
        "transaction_account": {"id": 100},
    }

    assert validate_transaction_data(transaction) is True


def test_validate_transaction_data_rejects_missing_fields():
    """Test transaction validation rejects missing required fields."""
    transaction = {
        "id": 12345,
        # Missing payee, amount, date
    }

    with pytest.raises(ValidationError, match="Missing required field"):
        validate_transaction_data(transaction)


def test_validate_category_data_accepts_valid_category():
    """Test category validation accepts valid data."""
    category = {"id": 100, "title": "Groceries", "is_transfer": False}

    assert validate_category_data(category) is True


def test_validate_category_data_rejects_invalid_category():
    """Test category validation rejects invalid data."""
    category = {"id": "invalid", "title": "Test"}  # Should be int

    with pytest.raises(ValidationError):
        validate_category_data(category)
