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
