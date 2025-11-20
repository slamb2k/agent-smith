"""Tests for rule engine."""

import pytest
import uuid
from datetime import datetime
from scripts.core.rule_engine import Rule, RuleEngine, RuleType


def test_rule_initialization_with_minimal_fields():
    """Test Rule can be created with minimal required fields."""
    rule = Rule(
        name="Test Rule",
        payee_regex="WOOLWORTHS.*",
        category_id=12345,
    )

    assert rule.name == "Test Rule"
    assert rule.payee_regex == "WOOLWORTHS.*"
    assert rule.category_id == 12345
    assert rule.rule_type == RuleType.LOCAL
    assert rule.confidence == 100
    assert rule.priority == 100
    assert isinstance(rule.rule_id, str)
    assert len(rule.rule_id) == 36  # UUID format


def test_rule_initialization_with_all_fields():
    """Test Rule initialization with all optional fields."""
    rule_id = str(uuid.uuid4())
    rule = Rule(
        rule_id=rule_id,
        name="Complex Rule",
        payee_regex="COLES.*",
        category_id=12346,
        rule_type=RuleType.SESSION,
        amount_min=10.0,
        amount_max=500.0,
        account_ids=[1, 2, 3],
        excludes=["COLES PETROL"],
        confidence=95,
        priority=200,
        requires_approval=True,
        tags=["groceries", "test"],
    )

    assert rule.rule_id == rule_id
    assert rule.name == "Complex Rule"
    assert rule.amount_min == 10.0
    assert rule.amount_max == 500.0
    assert rule.account_ids == [1, 2, 3]
    assert rule.excludes == ["COLES PETROL"]
    assert rule.confidence == 95
    assert rule.priority == 200
    assert rule.requires_approval is True
    assert rule.tags == ["groceries", "test"]


def test_rule_matches_simple_payee():
    """Test rule matches transaction with simple payee pattern."""
    rule = Rule(
        name="Woolworths",
        payee_regex="WOOLWORTHS.*",
        category_id=12345,
    )

    transaction = {
        "payee": "WOOLWORTHS EPPING",
        "amount": "-50.00",
    }

    assert rule.match_transaction(transaction) is True


def test_rule_does_not_match_different_payee():
    """Test rule doesn't match transaction with different payee."""
    rule = Rule(
        name="Woolworths",
        payee_regex="WOOLWORTHS.*",
        category_id=12345,
    )

    transaction = {
        "payee": "COLES SUPERMARKET",
        "amount": "-50.00",
    }

    assert rule.match_transaction(transaction) is False


def test_rule_matches_with_amount_range():
    """Test rule matches only within amount range."""
    rule = Rule(
        name="Small Purchases",
        payee_regex=".*",
        category_id=12345,
        amount_min=10.0,
        amount_max=100.0,
    )

    # Within range
    assert rule.match_transaction({"payee": "TEST", "amount": "-50.00"}) is True

    # Below range
    assert rule.match_transaction({"payee": "TEST", "amount": "-5.00"}) is False

    # Above range
    assert rule.match_transaction({"payee": "TEST", "amount": "-150.00"}) is False


def test_rule_excludes_pattern():
    """Test rule excludes transactions matching exclusion pattern."""
    rule = Rule(
        name="Woolworths Non-Petrol",
        payee_regex="WOOLWORTHS.*",
        category_id=12345,
        excludes=["WOOLWORTHS PETROL"],
    )

    # Should match
    assert rule.match_transaction({"payee": "WOOLWORTHS EPPING", "amount": "-50.00"}) is True

    # Should be excluded
    assert rule.match_transaction({"payee": "WOOLWORTHS PETROL", "amount": "-50.00"}) is False
