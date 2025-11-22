"""Tests for LLM categorization service."""

import pytest
from scripts.services.llm_categorization import LLMCategorizationService, IntelligenceMode


def test_build_categorization_prompt():
    """Test building LLM prompt for categorization."""
    service = LLMCategorizationService()

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "amount": -45.50, "date": "2024-01-15"},
        {"id": 2, "payee": "UBER TRIP", "amount": -25.00, "date": "2024-01-16"},
    ]

    categories = [
        {"title": "Groceries", "parent": "Expenses > Food & Dining"},
        {"title": "Transport", "parent": "Expenses > Transport"},
    ]

    prompt = service.build_categorization_prompt(transactions, categories)

    # Verify all key information is in prompt
    assert "WOOLWORTHS" in prompt
    assert "UBER TRIP" in prompt
    assert "Groceries" in prompt
    assert "Transport" in prompt
    assert "confidence" in prompt.lower()
    assert "45.50" in prompt
    assert "25.00" in prompt


def test_parse_llm_response():
    """Test parsing LLM categorization response."""
    service = LLMCategorizationService()

    llm_response = """
    Transaction 1: WOOLWORTHS
    Category: Groceries
    Confidence: 95%
    Reasoning: Woolworths is a major grocery chain

    Transaction 2: UBER TRIP
    Category: Transport
    Confidence: 90%
    Reasoning: Uber is a ride-sharing service
    """

    transaction_ids = [1, 2]

    results = service.parse_categorization_response(llm_response, transaction_ids)

    assert len(results) == 2
    assert results[1]["transaction_id"] == 1
    assert results[1]["category"] == "Groceries"
    assert results[1]["confidence"] == 95
    assert "Woolworths" in results[1]["reasoning"]
    assert results[2]["transaction_id"] == 2
    assert results[2]["category"] == "Transport"
    assert results[2]["confidence"] == 90


def test_categorize_batch_basic():
    """Test categorize_batch method returns expected structure."""
    service = LLMCategorizationService()

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "amount": -45.50},
        {"id": 2, "payee": "UBER", "amount": -25.00},
    ]

    categories = [
        {"title": "Groceries", "parent": "Food & Dining"},
        {"title": "Transport", "parent": "Transport"},
    ]

    # Mock LLM response parsing
    def mock_parse(response, txn_ids):
        return {
            1: {
                "transaction_id": 1,
                "category": "Groceries",
                "confidence": 95,
                "reasoning": "Test",
            },
            2: {
                "transaction_id": 2,
                "category": "Transport",
                "confidence": 90,
                "reasoning": "Test",
            },
        }

    service.parse_categorization_response = mock_parse

    results = service.categorize_batch(transactions, categories, mode=IntelligenceMode.SMART)

    # Should return dict keyed by transaction ID
    assert isinstance(results, dict)
    assert 1 in results
    assert 2 in results
    assert results[1]["category"] == "Groceries"
    assert results[1]["confidence"] == 95


def test_intelligence_mode_conservative():
    """Test conservative mode never auto-applies."""
    service = LLMCategorizationService()

    # Conservative should ALWAYS require approval
    assert service._should_auto_apply(100, IntelligenceMode.CONSERVATIVE) is False
    assert service._should_auto_apply(95, IntelligenceMode.CONSERVATIVE) is False
    assert service._should_auto_apply(50, IntelligenceMode.CONSERVATIVE) is False


def test_intelligence_mode_smart():
    """Test smart mode thresholds."""
    service = LLMCategorizationService()

    # Smart: ≥90% auto-apply, 70-89% ask, <70% skip
    assert service._should_auto_apply(95, IntelligenceMode.SMART) is True
    assert service._should_auto_apply(90, IntelligenceMode.SMART) is True
    assert service._should_auto_apply(85, IntelligenceMode.SMART) is False
    assert service._should_auto_apply(70, IntelligenceMode.SMART) is False
    assert service._should_auto_apply(50, IntelligenceMode.SMART) is False

    assert service._should_ask_user(85, IntelligenceMode.SMART) is True
    assert service._should_ask_user(70, IntelligenceMode.SMART) is True
    assert service._should_ask_user(50, IntelligenceMode.SMART) is False


def test_intelligence_mode_aggressive():
    """Test aggressive mode thresholds."""
    service = LLMCategorizationService()

    # Aggressive: ≥80% auto-apply, 50-79% ask, <50% skip
    assert service._should_auto_apply(95, IntelligenceMode.AGGRESSIVE) is True
    assert service._should_auto_apply(80, IntelligenceMode.AGGRESSIVE) is True
    assert service._should_auto_apply(75, IntelligenceMode.AGGRESSIVE) is False
    assert service._should_auto_apply(50, IntelligenceMode.AGGRESSIVE) is False

    assert service._should_ask_user(75, IntelligenceMode.AGGRESSIVE) is True
    assert service._should_ask_user(50, IntelligenceMode.AGGRESSIVE) is True
    assert service._should_ask_user(45, IntelligenceMode.AGGRESSIVE) is False


def test_categorize_batch_filters_by_mode():
    """Test that categorize_batch respects intelligence mode filtering."""
    service = LLMCategorizationService()

    transactions = [
        {"id": 1, "payee": "HIGH CONFIDENCE", "amount": -45.50},
        {"id": 2, "payee": "MEDIUM CONFIDENCE", "amount": -25.00},
        {"id": 3, "payee": "LOW CONFIDENCE", "amount": -10.00},
    ]

    categories = [{"title": "Test", "parent": "Test"}]

    # Mock LLM response with different confidence levels
    def mock_parse(response, txn_ids):
        return {
            1: {
                "transaction_id": 1,
                "category": "Test",
                "confidence": 95,
                "reasoning": "High",
            },
            2: {
                "transaction_id": 2,
                "category": "Test",
                "confidence": 75,
                "reasoning": "Medium",
            },
            3: {
                "transaction_id": 3,
                "category": "Test",
                "confidence": 50,
                "reasoning": "Low",
            },
        }

    service.parse_categorization_response = mock_parse

    # Smart mode: only return high confidence (≥90%) in auto_apply
    results = service.categorize_batch(transactions, categories, mode=IntelligenceMode.SMART)

    # All transactions should be present but with different action flags
    assert len(results) == 3
    # Transaction 1 (95%) should auto-apply
    assert results[1]["confidence"] == 95
    # Transaction 2 (75%) should ask
    assert results[2]["confidence"] == 75
    # Transaction 3 (50%) should skip
    assert results[3]["confidence"] == 50


def test_build_prompt_includes_mode():
    """Test prompt includes intelligence mode context."""
    service = LLMCategorizationService()

    transactions = [{"id": 1, "payee": "TEST", "amount": -10.00}]
    categories = [{"title": "Test", "parent": "Test"}]

    prompt = service.build_categorization_prompt(
        transactions, categories, mode=IntelligenceMode.CONSERVATIVE
    )

    # Should mention that conservative mode requires high confidence
    assert "conservative" in prompt.lower() or "high confidence" in prompt.lower()


def test_parse_response_handles_missing_fields():
    """Test parser handles incomplete LLM responses gracefully."""
    service = LLMCategorizationService()

    # Response missing confidence and reasoning
    llm_response = """
    Transaction 1: WOOLWORTHS
    Category: Groceries
    """

    transaction_ids = [1]
    results = service.parse_categorization_response(llm_response, transaction_ids)

    assert len(results) == 1
    assert results[1]["transaction_id"] == 1
    assert results[1]["category"] == "Groceries"
    # Should have default confidence
    assert "confidence" in results[1]
    assert results[1]["confidence"] > 0


def test_parse_response_handles_json_format():
    """Test parser can handle JSON-formatted responses."""
    service = LLMCategorizationService()

    llm_response = """
    [
        {
            "transaction_id": 1,
            "category": "Groceries",
            "confidence": 95,
            "reasoning": "Woolworths is a grocery store"
        },
        {
            "transaction_id": 2,
            "category": "Transport",
            "confidence": 90,
            "reasoning": "Uber is transportation"
        }
    ]
    """

    transaction_ids = [1, 2]
    results = service.parse_categorization_response(llm_response, transaction_ids)

    assert len(results) == 2
    assert results[1]["category"] == "Groceries"
    assert results[1]["confidence"] == 95
    assert results[2]["category"] == "Transport"
    assert results[2]["confidence"] == 90
