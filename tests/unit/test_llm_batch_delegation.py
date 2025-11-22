"""Tests for LLM batch delegation infrastructure."""

import pytest
from scripts.services.llm_categorization import LLMCategorizationService
from scripts.core.rule_engine import IntelligenceMode


def test_categorize_batch_returns_prompt_marker():
    """Test that categorize_batch returns _needs_llm marker."""
    service = LLMCategorizationService()

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "amount": -50.00, "date": "2024-01-15"},
        {"id": 2, "payee": "UBER", "amount": -25.00, "date": "2024-01-16"},
    ]

    categories = [
        {"title": "Groceries"},
        {"title": "Transport"},
    ]

    result = service.categorize_batch(transactions, categories, IntelligenceMode.SMART)

    # Should return marker dict, not actual results
    assert isinstance(result, dict)
    assert result["_needs_llm"] is True
    assert "_prompt" in result
    assert "_transaction_ids" in result
    assert result["_transaction_ids"] == [1, 2]
    assert isinstance(result["_prompt"], str)
    assert len(result["_prompt"]) > 0


def test_categorize_batch_empty_transactions():
    """Test categorize_batch with empty transaction list."""
    service = LLMCategorizationService()

    result = service.categorize_batch([], [], IntelligenceMode.SMART)

    # Should return empty dict for empty input
    assert result == {}


def test_validate_batch_builds_combined_prompt():
    """Test that validate_batch combines multiple validation prompts."""
    service = LLMCategorizationService()

    validations = [
        {
            "transaction": {"id": 1, "payee": "UBER", "amount": -25.00, "date": "2024-01-15"},
            "suggested_category": "Transport",
            "confidence": 75,
        },
        {
            "transaction": {"id": 2, "payee": "CHEMIST", "amount": -30.00, "date": "2024-01-16"},
            "suggested_category": "Health & Medical",
            "confidence": 80,
        },
    ]

    result = service.validate_batch(validations)

    # Should return marker dict
    assert isinstance(result, dict)
    assert result["_needs_llm"] is True
    assert "_prompt" in result
    assert "_transaction_ids" in result
    assert "_type" in result
    assert result["_type"] == "validation"
    assert result["_transaction_ids"] == [1, 2]

    # Prompt should contain validation content
    prompt = result["_prompt"]
    assert "Validate the following" in prompt
    assert "UBER" in prompt
    assert "CHEMIST" in prompt
    assert "Transport" in prompt
    assert "Health & Medical" in prompt
    assert "75" in prompt or "75%" in prompt
    assert "80" in prompt or "80%" in prompt


def test_validate_batch_empty_validations():
    """Test validate_batch with empty validation list."""
    service = LLMCategorizationService()

    result = service.validate_batch([])

    # Should return empty dict for empty input
    assert result == {}


def test_validate_batch_prompt_structure():
    """Test that validation prompt has proper structure."""
    service = LLMCategorizationService()

    validations = [
        {
            "transaction": {"id": 1, "payee": "UBER", "amount": -25.00, "date": "2024-01-15"},
            "suggested_category": "Transport",
            "confidence": 75,
        },
    ]

    result = service.validate_batch(validations)
    prompt = result["_prompt"]

    # Should have numbering
    assert "1." in prompt

    # Should ask for validation in order
    assert "in order" in prompt.lower() or "1, 2, 3" in prompt


def test_categorize_batch_includes_all_transaction_ids():
    """Test that all transaction IDs are included in marker."""
    service = LLMCategorizationService()

    transactions = [
        {"id": 101, "payee": "TX1", "amount": -10.00, "date": "2024-01-01"},
        {"id": 202, "payee": "TX2", "amount": -20.00, "date": "2024-01-02"},
        {"id": 303, "payee": "TX3", "amount": -30.00, "date": "2024-01-03"},
    ]

    categories = [{"title": "Category"}]

    result = service.categorize_batch(transactions, categories)

    assert result["_transaction_ids"] == [101, 202, 303]
