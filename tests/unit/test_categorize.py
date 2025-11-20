"""Tests for categorization operations."""

import pytest
from unittest.mock import Mock, patch
from scripts.operations.categorize import categorize_transaction, categorize_batch
from scripts.core.rule_engine import Rule, RuleEngine, IntelligenceMode


def test_categorize_transaction_with_auto_apply():
    """Test categorization auto-applies high-confidence rule."""
    rule = Rule(name="Woolworths", payee_regex="WOOLWORTHS.*", category_id=100, confidence=95)
    engine = RuleEngine()
    engine.add_rule(rule)
    engine.intelligence_mode = IntelligenceMode.SMART

    transaction = {"id": 12345, "payee": "WOOLWORTHS EPPING", "amount": "-50.00"}

    result = categorize_transaction(transaction, engine, dry_run=True)

    assert result["matched"] is True
    assert result["rule_name"] == "Woolworths"
    assert result["category_id"] == 100
    assert result["auto_applied"] is True
    assert result["confidence"] == 95


def test_categorize_transaction_with_approval_required():
    """Test categorization asks for approval on medium confidence."""
    rule = Rule(name="Maybe Groceries", payee_regex="SHOP.*", category_id=100, confidence=75)
    engine = RuleEngine()
    engine.add_rule(rule)
    engine.intelligence_mode = IntelligenceMode.SMART

    transaction = {"id": 12345, "payee": "SHOP LOCAL", "amount": "-50.00"}

    result = categorize_transaction(transaction, engine, dry_run=True)

    assert result["matched"] is True
    assert result["auto_applied"] is False
    assert result["requires_approval"] is True


def test_categorize_transaction_no_match():
    """Test categorization handles no matching rule."""
    engine = RuleEngine()
    engine.add_rule(Rule(name="Woolworths", payee_regex="WOOLWORTHS.*", category_id=100))

    transaction = {"id": 12345, "payee": "UNKNOWN MERCHANT", "amount": "-50.00"}

    result = categorize_transaction(transaction, engine, dry_run=True)

    assert result["matched"] is False
    assert result["category_id"] is None


@patch("scripts.operations.categorize.PocketSmithClient")
def test_categorize_batch_dry_run(mock_client):
    """Test batch categorization in dry-run mode."""
    engine = RuleEngine()
    engine.add_rule(
        Rule(name="Woolworths", payee_regex="WOOLWORTHS.*", category_id=100, confidence=95)
    )

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS EPPING", "amount": "-50.00"},
        {"id": 2, "payee": "WOOLWORTHS HORNSBY", "amount": "-75.00"},
        {"id": 3, "payee": "UNKNOWN MERCHANT", "amount": "-20.00"},
    ]

    results = categorize_batch(transactions, engine, dry_run=True)

    assert len(results) == 3
    assert results[0]["matched"] is True
    assert results[1]["matched"] is True
    assert results[2]["matched"] is False
    assert sum(1 for r in results if r["auto_applied"]) == 2
