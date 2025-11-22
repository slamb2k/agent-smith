"""Tests for batch categorization workflow."""

import pytest
from scripts.workflows.categorization import CategorizationWorkflow
from scripts.core.unified_rules import UnifiedRuleEngine
from pathlib import Path


def test_categorize_transactions_batch_all_rules_match(tmp_path):
    """Test batch where all transactions match rules."""
    # Setup rules
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95

  - type: category
    name: UBER → Transport
    patterns: [UBER]
    category: Transport
    confidence: 90
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS METRO", "amount": -50.00},
        {"id": 2, "payee": "UBER TRIP", "amount": -25.00},
    ]

    categories = [{"title": "Groceries"}, {"title": "Transport"}]

    result = workflow.categorize_transactions_batch(transactions, categories)

    # Both should match rules
    assert result["stats"]["total"] == 2
    assert result["stats"]["rule_matches"] == 2
    assert result["stats"]["llm_categorized"] == 0
    assert result["stats"]["skipped"] == 0

    # Check results
    assert result["results"][1]["category"] == "Groceries"
    assert result["results"][1]["source"] == "rule"
    assert result["results"][1]["llm_used"] is False

    assert result["results"][2]["category"] == "Transport"
    assert result["results"][2]["source"] == "rule"


def test_categorize_transactions_batch_uncategorized(tmp_path):
    """Test batch with uncategorized transactions (no rule match)."""
    # Setup minimal rules (won't match our transactions)
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

    # Enable test mode for LLM orchestrator
    workflow.llm_orchestrator.test_mode = True

    transactions = [
        {"id": 1, "payee": "UNKNOWN MERCHANT 1", "amount": -50.00},
        {"id": 2, "payee": "UNKNOWN MERCHANT 2", "amount": -25.00},
    ]

    categories = [{"title": "Shopping"}]

    result = workflow.categorize_transactions_batch(transactions, categories)

    # No rule matches, should use LLM
    assert result["stats"]["total"] == 2
    assert result["stats"]["rule_matches"] == 0
    assert result["stats"]["llm_categorized"] == 2

    # Check LLM results (mock from test mode)
    assert result["results"][1]["source"] == "llm"
    assert result["results"][1]["llm_used"] is True
    assert result["results"][1]["category"] == "Test Category"
    assert result["results"][1]["confidence"] == 85


def test_categorize_transactions_batch_mixed(tmp_path):
    """Test batch with mix of rule matches and uncategorized."""
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
        {"id": 2, "payee": "UNKNOWN", "amount": -25.00},
        {"id": 3, "payee": "WOOLWORTHS METRO", "amount": -30.00},
    ]

    categories = [{"title": "Groceries"}]

    result = workflow.categorize_transactions_batch(transactions, categories)

    # 2 rule matches, 1 LLM
    assert result["stats"]["total"] == 3
    assert result["stats"]["rule_matches"] == 2
    assert result["stats"]["llm_categorized"] == 1

    assert result["results"][1]["source"] == "rule"
    assert result["results"][2]["source"] == "llm"
    assert result["results"][3]["source"] == "rule"


def test_categorize_transactions_batch_sizing():
    """Test that batch size is determined by intelligence mode."""
    workflow_conservative = CategorizationWorkflow(client=None, mode="conservative")
    workflow_smart = CategorizationWorkflow(client=None, mode="smart")
    workflow_aggressive = CategorizationWorkflow(client=None, mode="aggressive")

    # Enable test mode
    workflow_conservative.llm_orchestrator.test_mode = True
    workflow_smart.llm_orchestrator.test_mode = True
    workflow_aggressive.llm_orchestrator.test_mode = True

    # Create 100 uncategorized transactions
    transactions = [{"id": i, "payee": f"UNKNOWN {i}", "amount": -10.00} for i in range(100)]

    categories = [{"title": "Shopping"}]

    # Conservative: batch size 20 (5 batches)
    result = workflow_conservative.categorize_transactions_batch(transactions, categories)
    assert result["stats"]["llm_categorized"] == 100

    # Smart: batch size 50 (2 batches)
    result = workflow_smart.categorize_transactions_batch(transactions, categories)
    assert result["stats"]["llm_categorized"] == 100

    # Aggressive: batch size 100 (1 batch)
    result = workflow_aggressive.categorize_transactions_batch(transactions, categories)
    assert result["stats"]["llm_categorized"] == 100


def test_categorize_transactions_batch_empty():
    """Test batch with empty transaction list."""
    workflow = CategorizationWorkflow(client=None, mode="smart")

    result = workflow.categorize_transactions_batch([], [])

    assert result["stats"]["total"] == 0
    assert result["stats"]["rule_matches"] == 0
    assert result["stats"]["llm_categorized"] == 0
    assert len(result["results"]) == 0
