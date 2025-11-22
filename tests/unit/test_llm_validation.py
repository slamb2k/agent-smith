"""Tests for LLM validation functionality."""

import pytest
from scripts.services.llm_categorization import LLMCategorizationService


def test_build_validation_prompt():
    """Test building LLM validation prompt."""
    service = LLMCategorizationService()

    transaction = {
        "payee": "UBER MEDICAL CENTRE",
        "amount": -80.00,
        "date": "2024-01-15",
    }

    prompt = service.build_validation_prompt(
        transaction=transaction,
        suggested_category="Transport",
        rule_confidence=75,
    )

    # Verify key information is in prompt
    assert "UBER MEDICAL CENTRE" in prompt
    assert "80.00" in prompt
    assert "Transport" in prompt
    assert "75" in prompt
    assert "CONFIRM" in prompt or "REJECT" in prompt
    assert "Reasoning" in prompt


def test_parse_validation_response_confirm():
    """Test parsing LLM validation response that confirms."""
    service = LLMCategorizationService()

    llm_response = """
    Validation: CONFIRM
    Adjusted Confidence: 90%
    Reasoning: This is clearly a transport expense from Uber.
    """

    result = service.parse_validation_response(
        llm_response=llm_response,
        original_category="Transport",
        original_confidence=75,
    )

    assert result["validation"] == "CONFIRM"
    assert result["category"] == "Transport"  # Should keep original
    assert result["confidence"] == 90
    assert "transport" in result["reasoning"].lower()


def test_parse_validation_response_reject():
    """Test parsing LLM validation response that rejects."""
    service = LLMCategorizationService()

    llm_response = """
    Validation: REJECT
    Suggested Category: Medical & Healthcare
    Adjusted Confidence: 90%
    Reasoning: Despite having 'UBER' in the name, this is a medical centre, not transportation.
    """

    result = service.parse_validation_response(
        llm_response=llm_response,
        original_category="Transport",
        original_confidence=75,
    )

    assert result["validation"] == "REJECT"
    assert result["category"] == "Medical & Healthcare"  # Should use suggested
    assert result["confidence"] == 90
    assert "medical" in result["reasoning"].lower()


def test_parse_validation_response_missing_fields():
    """Test parsing validation response with missing fields."""
    service = LLMCategorizationService()

    llm_response = """
    Validation: CONFIRM
    """

    result = service.parse_validation_response(
        llm_response=llm_response,
        original_category="Transport",
        original_confidence=75,
    )

    assert result["validation"] == "CONFIRM"
    assert result["category"] == "Transport"
    assert result["confidence"] == 75  # Should default to original
    assert "reasoning" in result


def test_parse_validation_response_unknown_status():
    """Test parsing validation response with unclear status."""
    service = LLMCategorizationService()

    llm_response = """
    This categorization seems okay but I'm not entirely sure.
    Adjusted Confidence: 80%
    Reasoning: Needs more context.
    """

    result = service.parse_validation_response(
        llm_response=llm_response,
        original_category="Transport",
        original_confidence=75,
    )

    assert result["validation"] == "UNKNOWN"
    assert result["confidence"] == 80
    assert result["category"] == "Transport"


def test_validation_workflow_integration():
    """Test complete validation workflow."""
    service = LLMCategorizationService()

    # Simulate medium-confidence rule match
    transaction = {
        "payee": "UBER MEDICAL CENTRE",
        "amount": -80.00,
        "date": "2024-01-15",
    }

    # Build validation prompt
    prompt = service.build_validation_prompt(
        transaction=transaction,
        suggested_category="Transport",
        rule_confidence=75,
    )

    assert isinstance(prompt, str)
    assert len(prompt) > 0

    # Simulate LLM rejection and new suggestion
    llm_response = """
    Validation: REJECT
    Suggested Category: Medical & Healthcare
    Adjusted Confidence: 95%
    Reasoning: This is a medical facility, not a ride-sharing service.
    """

    result = service.parse_validation_response(
        llm_response=llm_response,
        original_category="Transport",
        original_confidence=75,
    )

    # Result should have upgraded category and confidence
    assert result["validation"] == "REJECT"
    assert result["category"] == "Medical & Healthcare"
    assert result["confidence"] == 95
    assert result["confidence"] > 75  # Confidence upgraded


def test_parse_validation_batch_response_mixed():
    """Test parsing batch validation response with mixed CONFIRM/REJECT."""
    service = LLMCategorizationService()

    validations = [
        {
            "transaction": {"id": 1, "payee": "Woolworths"},
            "suggested_category": "Groceries",
            "confidence": 75,
        },
        {
            "transaction": {"id": 2, "payee": "UBER MEDICAL CENTRE"},
            "suggested_category": "Transport",
            "confidence": 70,
        },
        {
            "transaction": {"id": 3, "payee": "Shell"},
            "suggested_category": "Transport",
            "confidence": 80,
        },
    ]

    llm_response = """
1. CONFIRM
Adjusted Confidence: 90
Reasoning: Clear grocery expense

2. REJECT
Suggested Category: Medical & Healthcare
Adjusted Confidence: 95
Reasoning: This is a medical facility

3. CONFIRM
Adjusted Confidence: 85
Reasoning: Standard fuel purchase
"""

    results = service.parse_validation_batch_response(llm_response, validations)

    # Check all three validations were parsed
    assert len(results) == 3
    assert 1 in results
    assert 2 in results
    assert 3 in results

    # Transaction 1: CONFIRM
    assert results[1]["validation"] == "CONFIRM"
    assert results[1]["category"] == "Groceries"
    assert results[1]["confidence"] == 90

    # Transaction 2: REJECT with new category
    assert results[2]["validation"] == "REJECT"
    assert results[2]["category"] == "Medical & Healthcare"
    assert results[2]["confidence"] == 95

    # Transaction 3: CONFIRM
    assert results[3]["validation"] == "CONFIRM"
    assert results[3]["category"] == "Transport"
    assert results[3]["confidence"] == 85


def test_parse_validation_batch_response_missing_responses():
    """Test batch parsing when LLM doesn't respond to all validations."""
    service = LLMCategorizationService()

    validations = [
        {
            "transaction": {"id": 1, "payee": "Woolworths"},
            "suggested_category": "Groceries",
            "confidence": 75,
        },
        {
            "transaction": {"id": 2, "payee": "Coles"},
            "suggested_category": "Groceries",
            "confidence": 80,
        },
    ]

    # LLM only responds to first validation
    llm_response = """
1. CONFIRM
Adjusted Confidence: 90
Reasoning: Clear grocery expense
"""

    results = service.parse_validation_batch_response(llm_response, validations)

    # Should still have entries for both
    assert len(results) == 2

    # Transaction 1: parsed from response
    assert results[1]["validation"] == "CONFIRM"
    assert results[1]["confidence"] == 90

    # Transaction 2: default CONFIRM (no response)
    assert results[2]["validation"] == "CONFIRM"
    assert results[2]["category"] == "Groceries"
    assert results[2]["confidence"] == 80  # Original confidence
    assert "No validation response" in results[2]["reasoning"]


def test_parse_validation_batch_response_empty():
    """Test batch parsing with empty validation list."""
    service = LLMCategorizationService()

    validations = []
    llm_response = "Some response"

    results = service.parse_validation_batch_response(llm_response, validations)

    # Should return empty dict
    assert results == {}


def test_validate_batch_returns_marker():
    """Test validate_batch returns proper marker dict."""
    service = LLMCategorizationService()

    validations = [
        {
            "transaction": {"id": 1, "payee": "Woolworths"},
            "suggested_category": "Groceries",
            "confidence": 75,
        }
    ]

    result = service.validate_batch(validations)

    # Should return marker dict
    assert result["_needs_llm"] is True
    assert "_prompt" in result
    assert "_transaction_ids" in result
    assert "_validations" in result  # New: validations for parsing
    assert result["_type"] == "validation"

    # Should include transaction ID
    assert result["_transaction_ids"] == [1]

    # Should include original validations
    assert result["_validations"] == validations

    # Prompt should contain validation instructions
    assert "Woolworths" in result["_prompt"]
    assert "Groceries" in result["_prompt"]
    assert "75" in result["_prompt"]
