"""Tests for enhanced categorization workflow with LLM integration."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from scripts.workflows.categorization import CategorizationWorkflow
from scripts.core.unified_rules import UnifiedRuleEngine
from scripts.services.llm_categorization import LLMCategorizationService
from scripts.core.rule_engine import IntelligenceMode


def test_workflow_initialization_with_unified_rules(tmp_path):
    """Test workflow initializes with UnifiedRuleEngine."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: Test Rule
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

    assert workflow.rule_engine is not None
    assert isinstance(workflow.rule_engine, UnifiedRuleEngine)
    assert len(workflow.rule_engine.category_rules) == 1


def test_workflow_uses_rules_first(tmp_path):
    """Test workflow tries rule-based categorization before LLM."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: Woolworths Rule
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

    transaction = {
        "id": 123,
        "payee": "WOOLWORTHS METRO 123",
        "amount": -45.50,
        "date": "2025-11-20",
    }

    result = workflow.categorize_transaction(transaction)

    # Should match via rule, not LLM
    assert result["category"] == "Groceries"
    assert result["source"] == "rule"
    assert result["confidence"] == 95
    assert result["llm_used"] is False


def test_workflow_falls_back_to_llm_when_no_rule_match(tmp_path):
    """Test workflow falls back to LLM when no rule matches."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("rules: []")

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

    # Mock LLM service to return categorization
    workflow.llm_service = Mock()
    workflow.llm_service.categorize_batch = Mock(
        return_value={
            123: {
                "transaction_id": 123,
                "category": "Shopping",
                "confidence": 85,
                "reasoning": "Unknown merchant",
                "source": "llm",
            }
        }
    )

    transaction = {
        "id": 123,
        "payee": "UNKNOWN MERCHANT XYZ",
        "amount": -45.50,
        "date": "2025-11-20",
    }

    categories = [{"title": "Shopping", "parent": ""}]
    result = workflow.categorize_transaction(transaction, available_categories=categories)

    # Should fall back to LLM
    assert result["category"] == "Shopping"
    assert result["source"] == "llm"
    assert result["confidence"] == 85
    assert result["llm_used"] is True
    assert result["reasoning"] == "Unknown merchant"


def test_workflow_applies_labels_after_categorization(tmp_path):
    """Test two-phase execution: categorization then labeling."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: Groceries Rule
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95

  - type: label
    name: Personal Groceries
    when:
      categories: [Groceries]
    labels: [Personal, Essential]
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

    transaction = {
        "id": 123,
        "payee": "WOOLWORTHS METRO 123",
        "amount": -45.50,
        "date": "2025-11-20",
    }

    result = workflow.categorize_transaction(transaction)

    # Should match category and labels
    assert result["category"] == "Groceries"
    assert result["labels"] == ["Essential", "Personal"]  # Sorted
    assert result["source"] == "rule"


def test_workflow_conservative_mode_never_auto_applies():
    """Test conservative mode never auto-applies, always asks user."""
    workflow = CategorizationWorkflow(client=None, mode="conservative")

    # High confidence should still ask user in conservative mode
    assert workflow._should_ask_user(95, IntelligenceMode.CONSERVATIVE) is True
    assert workflow._should_auto_apply(95, IntelligenceMode.CONSERVATIVE) is False


def test_workflow_smart_mode_auto_apply_threshold():
    """Test smart mode auto-applies at 90%+ confidence."""
    workflow = CategorizationWorkflow(client=None, mode="smart")

    # 90%+ should auto-apply
    assert workflow._should_auto_apply(90, IntelligenceMode.SMART) is True
    assert workflow._should_auto_apply(95, IntelligenceMode.SMART) is True

    # 70-89% should ask user
    assert workflow._should_ask_user(85, IntelligenceMode.SMART) is True
    assert workflow._should_ask_user(70, IntelligenceMode.SMART) is True
    assert workflow._should_auto_apply(85, IntelligenceMode.SMART) is False

    # Below 70% should skip
    assert workflow._should_ask_user(65, IntelligenceMode.SMART) is False


def test_workflow_aggressive_mode_auto_apply_threshold():
    """Test aggressive mode auto-applies at 80%+ confidence."""
    workflow = CategorizationWorkflow(client=None, mode="aggressive")

    # 80%+ should auto-apply
    assert workflow._should_auto_apply(80, IntelligenceMode.AGGRESSIVE) is True
    assert workflow._should_auto_apply(90, IntelligenceMode.AGGRESSIVE) is True

    # 50-79% should ask user
    assert workflow._should_ask_user(75, IntelligenceMode.AGGRESSIVE) is True
    assert workflow._should_ask_user(50, IntelligenceMode.AGGRESSIVE) is True
    assert workflow._should_auto_apply(75, IntelligenceMode.AGGRESSIVE) is False


def test_workflow_offers_rule_learning_from_llm_patterns(tmp_path):
    """Test workflow can learn rules from LLM categorization patterns."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("rules: []")

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

    # Mock LLM service to return consistent categorizations
    workflow.llm_service = Mock()
    workflow.llm_service.categorize_batch = Mock(
        return_value={
            123: {
                "transaction_id": 123,
                "category": "Groceries",
                "confidence": 90,
                "reasoning": "Woolworths is a grocery store",
                "source": "llm",
            }
        }
    )

    transaction = {
        "id": 123,
        "payee": "WOOLWORTHS METRO 123",
        "amount": -45.50,
        "date": "2025-11-20",
    }

    categories = [{"title": "Groceries", "parent": ""}]
    result = workflow.categorize_transaction(transaction, available_categories=categories)

    # Check if rule learning suggestion is present
    rule_suggestion = workflow.suggest_rule_from_llm_result(transaction, result)

    assert rule_suggestion is not None
    assert rule_suggestion["name"] == "WOOLWORTHS → Groceries"
    assert "WOOLWORTHS" in rule_suggestion["patterns"]
    assert rule_suggestion["category"] == "Groceries"
    assert rule_suggestion["confidence"] == 90


def test_workflow_batch_processing_uses_subagent_conductor(tmp_path):
    """Test batch processing delegates to SubagentConductor for LLM calls."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("rules: []")

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

    # Mock conductor
    workflow.conductor = Mock()
    workflow.conductor.should_delegate_operation = Mock(return_value=True)

    transactions = [{"id": i, "payee": f"MERCHANT {i}", "amount": -10.0} for i in range(150)]

    # Should delegate to conductor for large batch
    should_delegate = workflow.should_use_subagent(len(transactions))
    assert should_delegate is True


def test_workflow_maintains_backward_compatibility():
    """Test workflow maintains existing CategorizationWorkflow API."""
    from scripts.core.api_client import PocketSmithClient

    client = PocketSmithClient(api_key="test-key")
    workflow = CategorizationWorkflow(client, mode="smart")

    # Existing methods should still work
    assert workflow.client == client
    assert workflow.mode == "smart"
    assert hasattr(workflow, "should_use_subagent")
    assert hasattr(workflow, "build_summary")


def test_workflow_hybrid_execution_flow(tmp_path):
    """Test complete hybrid flow: Rules → LLM → User confirmation."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: Medium Confidence Rule
    patterns: [ACME]
    category: Shopping
    confidence: 75  # Medium confidence - should ask user
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

    transaction = {
        "id": 123,
        "payee": "ACME CORP",
        "amount": -45.50,
        "date": "2025-11-20",
    }

    result = workflow.categorize_transaction(transaction)

    # Rule matches with medium confidence (75%)
    assert result["category"] == "Shopping"
    assert result["source"] == "rule"
    assert result["confidence"] == 75

    # Should ask user (not auto-apply) in smart mode
    assert workflow._should_ask_user(75, IntelligenceMode.SMART) is True
    assert workflow._should_auto_apply(75, IntelligenceMode.SMART) is False


def test_workflow_handles_no_match_gracefully(tmp_path):
    """Test workflow handles transactions with no rule or LLM match."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("rules: []")

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

    # Mock LLM service to return no match
    workflow.llm_service = Mock()
    workflow.llm_service.categorize_batch = Mock(return_value={})

    transaction = {
        "id": 123,
        "payee": "UNKNOWN",
        "amount": -45.50,
        "date": "2025-11-20",
    }

    categories = [{"title": "Shopping", "parent": ""}]
    result = workflow.categorize_transaction(transaction, available_categories=categories)

    # Should indicate no match
    assert result["category"] is None
    assert result["source"] == "none"
    assert result["llm_used"] is True  # LLM was tried but returned nothing


def test_workflow_rule_creation_helper():
    """Test helper method for creating rules from transactions."""
    workflow = CategorizationWorkflow(client=None, mode="smart")

    transaction = {
        "id": 123,
        "payee": "WOOLWORTHS METRO 123",
        "amount": -45.50,
    }

    llm_result = {
        "category": "Groceries",
        "confidence": 90,
        "reasoning": "Woolworths is a grocery store",
    }

    rule_dict = workflow.create_rule_from_transaction(transaction, llm_result)

    assert rule_dict["type"] == "category"
    assert rule_dict["name"] == "WOOLWORTHS → Groceries"
    assert "WOOLWORTHS" in rule_dict["patterns"]
    assert rule_dict["category"] == "Groceries"
    assert rule_dict["confidence"] == 90
