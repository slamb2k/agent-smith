"""Tests for LLM subagent orchestration layer."""

import pytest
from scripts.orchestration.llm_subagent import LLMSubagent
from scripts.services.llm_categorization import LLMCategorizationService
from scripts.core.rule_engine import IntelligenceMode


def test_llm_subagent_init():
    """Test LLMSubagent initialization."""
    orchestrator = LLMSubagent(test_mode=True)
    assert orchestrator.test_mode is True

    orchestrator_prod = LLMSubagent(test_mode=False)
    assert orchestrator_prod.test_mode is False


def test_execute_categorization_test_mode():
    """Test categorization execution in test mode."""
    orchestrator = LLMSubagent(test_mode=True)
    service = LLMCategorizationService()

    transaction_ids = [1, 2, 3]
    prompt = "Test categorization prompt"

    result = orchestrator.execute_categorization(
        prompt=prompt,
        transaction_ids=transaction_ids,
        service=service,
    )

    # Should return mock results for all transaction IDs
    assert len(result) == 3
    assert 1 in result
    assert 2 in result
    assert 3 in result

    # Check structure of mock result
    assert result[1]["transaction_id"] == 1
    assert result[1]["category"] == "Test Category"
    assert result[1]["confidence"] == 85
    assert result[1]["source"] == "llm"


def test_execute_validation_test_mode():
    """Test validation execution in test mode."""
    orchestrator = LLMSubagent(test_mode=True)
    service = LLMCategorizationService()

    transaction_ids = [1, 2]
    prompt = "Test validation prompt"
    validations = [
        {
            "transaction": {"id": 1, "payee": "Test 1"},
            "suggested_category": "Category A",
            "confidence": 75,
        },
        {
            "transaction": {"id": 2, "payee": "Test 2"},
            "suggested_category": "Category B",
            "confidence": 80,
        },
    ]

    result = orchestrator.execute_validation(
        prompt=prompt,
        transaction_ids=transaction_ids,
        validations=validations,
        service=service,
    )

    # Should return mock results for all transaction IDs
    assert len(result) == 2
    assert 1 in result
    assert 2 in result

    # Check structure of mock validation result
    assert result[1]["validation"] == "CONFIRM"
    assert result[1]["confidence"] == 90
    assert result[1]["category"] == "Original Category"


def test_execute_categorization_production_mode(monkeypatch):
    """Test categorization uses SDK in production mode."""
    orchestrator = LLMSubagent(test_mode=False)
    service = LLMCategorizationService()

    transaction_ids = [1, 2]
    prompt = "Test prompt"

    # Mock the SDK call to avoid actual LLM calls during testing
    def mock_execute_prompt_sync(self, p):
        return ""  # Empty response will be parsed by service

    monkeypatch.setattr(LLMSubagent, "_execute_prompt_sync", mock_execute_prompt_sync)

    # Should attempt SDK call and parse result
    result = orchestrator.execute_categorization(
        prompt=prompt,
        transaction_ids=transaction_ids,
        service=service,
    )

    # Should return parsed results (even if empty from mock)
    assert isinstance(result, dict)


def test_execute_validation_production_mode(monkeypatch):
    """Test validation uses SDK in production mode with batch parsing."""
    orchestrator = LLMSubagent(test_mode=False)
    service = LLMCategorizationService()

    transaction_ids = [1]
    prompt = "Test prompt"
    validations = [
        {
            "transaction": {"id": 1, "payee": "Test"},
            "suggested_category": "Groceries",
            "confidence": 75,
        }
    ]

    # Mock the SDK call to avoid actual LLM calls during testing
    def mock_execute_prompt_sync(self, p):
        # Return a validation response
        return "1. CONFIRM\nAdjusted Confidence: 90\nReasoning: Transaction matches pattern"

    monkeypatch.setattr(LLMSubagent, "_execute_prompt_sync", mock_execute_prompt_sync)

    result = orchestrator.execute_validation(
        prompt=prompt,
        transaction_ids=transaction_ids,
        validations=validations,
        service=service,
    )

    # Should parse the SDK response
    assert isinstance(result, dict)
    assert 1 in result
    assert result[1]["validation"] == "CONFIRM"
    assert result[1]["confidence"] == 90
