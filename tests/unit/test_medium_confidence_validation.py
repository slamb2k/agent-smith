"""Tests for medium-confidence validation (Case 2)."""

import pytest
from scripts.workflows.categorization import CategorizationWorkflow
from scripts.core.unified_rules import UnifiedRuleEngine
from scripts.core.rule_engine import IntelligenceMode


def test_should_validate_with_llm_smart_mode():
    """Test validation threshold in smart mode (70-89%)."""
    workflow = CategorizationWorkflow(client=None, mode="smart")
    mode = IntelligenceMode.SMART

    # Below range: no validation
    assert workflow._should_validate_with_llm(69, mode) is False

    # Within range: validate
    assert workflow._should_validate_with_llm(70, mode) is True
    assert workflow._should_validate_with_llm(80, mode) is True
    assert workflow._should_validate_with_llm(89, mode) is True

    # Above range: no validation (auto-apply)
    assert workflow._should_validate_with_llm(90, mode) is False
    assert workflow._should_validate_with_llm(95, mode) is False


def test_should_validate_with_llm_aggressive_mode():
    """Test validation threshold in aggressive mode (50-79%)."""
    workflow = CategorizationWorkflow(client=None, mode="aggressive")
    mode = IntelligenceMode.AGGRESSIVE

    # Below range: no validation
    assert workflow._should_validate_with_llm(49, mode) is False

    # Within range: validate
    assert workflow._should_validate_with_llm(50, mode) is True
    assert workflow._should_validate_with_llm(65, mode) is True
    assert workflow._should_validate_with_llm(79, mode) is True

    # Above range: no validation (auto-apply)
    assert workflow._should_validate_with_llm(80, mode) is False
    assert workflow._should_validate_with_llm(90, mode) is False


def test_should_validate_with_llm_conservative_mode():
    """Test that conservative mode never validates (user reviews all)."""
    workflow = CategorizationWorkflow(client=None, mode="conservative")
    mode = IntelligenceMode.CONSERVATIVE

    # Conservative never validates with LLM
    assert workflow._should_validate_with_llm(50, mode) is False
    assert workflow._should_validate_with_llm(70, mode) is False
    assert workflow._should_validate_with_llm(90, mode) is False


def test_batch_with_medium_confidence_validation(tmp_path):
    """Test batch categorization with medium confidence validation."""
    # Create rule with medium confidence (75%)
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: UBER → Transport
    patterns: [UBER]
    category: Transport
    confidence: 75
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)
    workflow.llm_orchestrator.test_mode = True

    transactions = [
        {"id": 1, "payee": "UBER TRIP", "amount": -25.00},
    ]

    categories = [{"title": "Transport"}]

    result = workflow.categorize_transactions_batch(transactions, categories)

    # Should have 1 rule match
    assert result["stats"]["rule_matches"] == 1

    # Should have been validated (75% is in 70-89% range for smart)
    assert result["stats"]["llm_validated"] == 1

    # Validation should have confirmed (mock returns CONFIRM with confidence 90)
    assert result["results"][1]["category"] == "Transport"
    assert result["results"][1]["confidence"] == 90  # Upgraded from 75


def test_batch_with_high_confidence_no_validation(tmp_path):
    """Test that high confidence rules are not validated."""
    # Create rule with high confidence (95%)
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)
    workflow.llm_orchestrator.test_mode = True

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "amount": -50.00},
    ]

    categories = [{"title": "Groceries"}]

    result = workflow.categorize_transactions_batch(transactions, categories)

    # Should have 1 rule match
    assert result["stats"]["rule_matches"] == 1

    # Should NOT have been validated (95% is above 90% threshold)
    assert result["stats"]["llm_validated"] == 0

    # Confidence should remain 95
    assert result["results"][1]["confidence"] == 95


def test_batch_validation_confirms(tmp_path):
    """Test LLM validation that confirms the rule."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: Test Rule
    patterns: [TEST]
    category: TestCategory
    confidence: 75
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)
    workflow.llm_orchestrator.test_mode = True

    transactions = [{"id": 1, "payee": "TEST MERCHANT", "amount": -10.00}]
    categories = [{"title": "TestCategory"}]

    result = workflow.categorize_transactions_batch(transactions, categories)

    # Should be validated and confirmed
    assert result["stats"]["llm_validated"] == 1
    assert result["results"][1]["category"] == "TestCategory"
    assert result["results"][1]["confidence"] == 90  # Mock confirmation upgrades to 90


def test_batch_mixed_confidence_levels(tmp_path):
    """Test batch with mix of high, medium, and low confidence."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: High Confidence
    patterns: [HIGH]
    category: HighConf
    confidence: 95

  - type: category
    name: Medium Confidence
    patterns: [MEDIUM]
    category: MediumConf
    confidence: 75

  - type: category
    name: Low Confidence
    patterns: [LOW]
    category: LowConf
    confidence: 60
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)
    workflow.llm_orchestrator.test_mode = True

    transactions = [
        {"id": 1, "payee": "HIGH CONFIDENCE", "amount": -10.00},
        {"id": 2, "payee": "MEDIUM CONFIDENCE", "amount": -10.00},
        {"id": 3, "payee": "LOW CONFIDENCE", "amount": -10.00},
    ]

    categories = [
        {"title": "HighConf"},
        {"title": "MediumConf"},
        {"title": "LowConf"},
    ]

    result = workflow.categorize_transactions_batch(transactions, categories)

    # All 3 should match rules
    assert result["stats"]["rule_matches"] == 3

    # Only medium confidence (75%) should be validated
    assert result["stats"]["llm_validated"] == 1

    # Check confidence values
    assert result["results"][1]["confidence"] == 95  # High: unchanged
    assert result["results"][2]["confidence"] == 90  # Medium: validated and upgraded
    assert result["results"][3]["confidence"] == 60  # Low: unchanged
