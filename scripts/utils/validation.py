"""Data validation utilities for Agent Smith."""

import re
import logging
from datetime import datetime
from typing import Dict, Any


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when data validation fails."""

    pass


def validate_date_format(date_str: str) -> bool:
    """Validate date string is in YYYY-MM-DD format.

    Args:
        date_str: Date string to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If date format is invalid
    """
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        raise ValidationError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")

    # Verify it's a valid date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValidationError(f"Invalid date: {date_str}. {str(e)}")

    return True


def validate_transaction_data(transaction: Dict[str, Any]) -> bool:
    """Validate transaction data structure.

    Args:
        transaction: Transaction dictionary from PocketSmith API

    Returns:
        True if valid

    Raises:
        ValidationError: If transaction data is invalid
    """
    required_fields = ["id", "payee", "amount", "date"]

    for field in required_fields:
        if field not in transaction:
            raise ValidationError(f"Missing required field: {field}")

    # Validate types
    if not isinstance(transaction["id"], int):
        raise ValidationError(f"Transaction id must be int, got {type(transaction['id'])}")

    if not isinstance(transaction["payee"], str):
        raise ValidationError(f"Payee must be string, got {type(transaction['payee'])}")

    # Validate date format
    validate_date_format(transaction["date"])

    return True


def validate_category_data(category: Dict[str, Any]) -> bool:
    """Validate category data structure.

    Args:
        category: Category dictionary from PocketSmith API

    Returns:
        True if valid

    Raises:
        ValidationError: If category data is invalid
    """
    required_fields = ["id", "title"]

    for field in required_fields:
        if field not in category:
            raise ValidationError(f"Missing required field: {field}")

    # Validate types
    if not isinstance(category["id"], int):
        raise ValidationError(f"Category id must be int, got {type(category['id'])}")

    if not isinstance(category["title"], str):
        raise ValidationError(f"Category title must be string, got {type(category['title'])}")

    return True


def validate_api_key(api_key: str) -> bool:
    """Validate PocketSmith API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If API key format is invalid
    """
    if not api_key:
        raise ValidationError("API key cannot be empty")

    # PocketSmith API keys are hexadecimal and typically 128 characters
    if not re.match(r"^[a-f0-9]{128}$", api_key):
        logger.warning("API key does not match expected format (128 hex chars)")

    return True


def validate_user_id(user_id: Any) -> bool:
    """Validate user ID is a positive integer.

    Args:
        user_id: User ID to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If user ID is invalid
    """
    if not isinstance(user_id, int):
        raise ValidationError(f"User ID must be integer, got {type(user_id)}")

    if user_id <= 0:
        raise ValidationError(f"User ID must be positive, got {user_id}")

    return True
