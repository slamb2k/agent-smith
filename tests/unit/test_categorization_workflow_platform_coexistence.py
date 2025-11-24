"""Tests for categorization workflow handling already-categorized transactions.

This test file covers Option 4: Smart processing of all transactions regardless of
existing categorization status.

Scenarios:
1. Uncategorized transaction → apply category + labels (existing behavior)
2. Already-categorized with matching local rule → apply labels only
3. Already-categorized with conflicting local rule → flag for review
4. Label-only rule on already-categorized → apply labels regardless
"""

import pytest
from unittest.mock import Mock, MagicMock
from scripts.workflows.categorization import CategorizationWorkflow
from scripts.core.unified_rules import UnifiedRuleEngine


@pytest.fixture
def mock_client():
    """Create mock API client."""
    client = Mock()
    client.get_user.return_value = {"id": 123}
    return client


@pytest.fixture
def mock_rule_engine():
    """Create mock rule engine."""
    engine = Mock(spec=UnifiedRuleEngine)
    return engine


def test_uncategorized_transaction_applies_category_and_labels(mock_client, mock_rule_engine):
    """Test that uncategorized transactions get category + labels from rules.

    This is existing behavior - should continue to work.
    """
    # Setup: Transaction with no category
    transaction = {
        "id": 1,
        "payee": "WOOLWORTHS",
        "amount": -50.00,
        "category": None,  # No existing category
    }

    # Setup: Rule matches and provides category + labels
    mock_rule_engine.categorize_and_label.return_value = {
        "category": "Groceries",
        "labels": ["Personal", "Essential"],
        "confidence": 95,
        "rule_id": "woolworths-groceries",
    }

    # Execute
    workflow = CategorizationWorkflow(client=mock_client, mode="smart")
    workflow.rule_engine = mock_rule_engine

    result = workflow.categorize_single_transaction(
        transaction=transaction, available_categories=[{"id": 100, "title": "Groceries"}]
    )

    # Verify: Category and labels applied
    assert result["category"] == "Groceries"
    assert result["labels"] == ["Personal", "Essential"]
    assert result["confidence"] == 95
    assert result["source"] == "rule"


def test_already_categorized_matching_rule_applies_labels_only(mock_client, mock_rule_engine):
    """Test that already-categorized transactions with matching rules get labels added.

    NEW BEHAVIOR (Option 4):
    - Transaction already has "Groceries" category (from platform rule)
    - Local rule also says "Groceries"
    - Result: Don't change category, but DO apply labels
    """
    # Setup: Transaction already categorized as "Groceries"
    transaction = {
        "id": 2,
        "payee": "WOOLWORTHS",
        "amount": -50.00,
        "category": {"id": 100, "title": "Groceries"},  # Already categorized
    }

    # Setup: Local rule matches and ALSO says "Groceries"
    mock_rule_engine.categorize_and_label.return_value = {
        "category": "Groceries",  # Same as existing
        "labels": ["Personal", "Essential"],
        "confidence": 95,
        "rule_id": "woolworths-groceries",
    }

    # Execute
    workflow = CategorizationWorkflow(client=mock_client, mode="smart")
    workflow.rule_engine = mock_rule_engine

    result = workflow.categorize_single_transaction(
        transaction=transaction, available_categories=[{"id": 100, "title": "Groceries"}]
    )

    # Verify: Category unchanged, but labels applied
    assert result["category"] == "Groceries"
    assert result["labels"] == ["Personal", "Essential"]
    assert result["confidence"] == 95
    assert result["source"] == "rule"
    assert result.get("needs_review") is None or result["needs_review"] is False


def test_already_categorized_conflicting_rule_flags_for_review(mock_client, mock_rule_engine):
    """Test that already-categorized transactions with conflicting rules are flagged.

    NEW BEHAVIOR (Option 4):
    - Transaction already has "Dining Out" category (from platform rule)
    - Local rule says "Groceries"
    - Result: Flag for review, don't change category
    """
    # Setup: Transaction already categorized as "Dining Out"
    transaction = {
        "id": 3,
        "payee": "WOOLWORTHS",
        "amount": -50.00,
        "category": {"id": 200, "title": "Dining Out"},  # Platform rule applied this
    }

    # Setup: Local rule says "Groceries" (conflict!)
    mock_rule_engine.categorize_and_label.return_value = {
        "category": "Groceries",  # Different from existing
        "labels": ["Personal", "Essential"],
        "confidence": 95,
        "rule_id": "woolworths-groceries",
    }

    # Execute
    workflow = CategorizationWorkflow(client=mock_client, mode="smart")
    workflow.rule_engine = mock_rule_engine

    result = workflow.categorize_single_transaction(
        transaction=transaction,
        available_categories=[
            {"id": 100, "title": "Groceries"},
            {"id": 200, "title": "Dining Out"},
        ],
    )

    # Verify: Category unchanged, flagged for review
    assert result["category"] == "Dining Out"  # Keep existing
    assert result["needs_review"] is True
    assert result["source"] == "conflict"
    assert result["suggested_category"] == "Groceries"  # What rule suggested
    assert result["confidence"] == 95  # From rule


def test_label_only_rule_applies_labels_regardless_of_category(mock_client, mock_rule_engine):
    """Test that label-only rules apply labels even if transaction is already categorized.

    NEW BEHAVIOR (Option 4):
    - Transaction already has "Transport" category
    - Label-only rule says "Business" (no category specified)
    - Result: Apply labels, don't touch category
    """
    # Setup: Transaction already categorized as "Transport"
    transaction = {
        "id": 4,
        "payee": "UBER",
        "amount": -25.00,
        "category": {"id": 300, "title": "Transport"},  # Already categorized
    }

    # Setup: Label-only rule (no category field)
    mock_rule_engine.categorize_and_label.return_value = {
        "category": None,  # Label-only rule doesn't set category
        "labels": ["Business", "Tax Deductible"],
        "confidence": 90,
        "rule_id": "business-transport",
    }

    # Execute
    workflow = CategorizationWorkflow(client=mock_client, mode="smart")
    workflow.rule_engine = mock_rule_engine

    result = workflow.categorize_single_transaction(
        transaction=transaction, available_categories=[{"id": 300, "title": "Transport"}]
    )

    # Verify: Category unchanged, labels applied
    assert result["category"] == "Transport"  # Keep existing
    assert result["labels"] == ["Business", "Tax Deductible"]
    assert result["confidence"] == 90
    assert result["source"] == "rule"
    assert result.get("needs_review") is None or result["needs_review"] is False


def test_batch_processing_handles_mixed_scenarios(mock_client, mock_rule_engine):
    """Test that batch processing correctly handles all four scenarios.

    This tests the full batch workflow with a mix of:
    - Uncategorized transactions
    - Already-categorized with matching rules
    - Already-categorized with conflicts
    - Label-only rules
    """
    # Setup: Mix of transactions
    transactions = [
        # Scenario 1: Uncategorized
        {
            "id": 1,
            "payee": "WOOLWORTHS",
            "amount": -50.00,
            "category": None,
        },
        # Scenario 2: Already categorized, matching
        {
            "id": 2,
            "payee": "COLES",
            "amount": -40.00,
            "category": {"id": 100, "title": "Groceries"},
        },
        # Scenario 3: Already categorized, conflict
        {
            "id": 3,
            "payee": "IGA",
            "amount": -30.00,
            "category": {"id": 200, "title": "Dining Out"},  # Wrong!
        },
        # Scenario 4: Label-only rule
        {
            "id": 4,
            "payee": "UBER",
            "amount": -25.00,
            "category": {"id": 300, "title": "Transport"},
        },
    ]

    # Setup: Mock rule engine responses
    def mock_categorize(txn):
        if "WOOLWORTHS" in txn["payee"]:
            return {
                "category": "Groceries",
                "labels": ["Personal"],
                "confidence": 95,
                "rule_id": "woolworths",
            }
        elif "COLES" in txn["payee"]:
            return {
                "category": "Groceries",
                "labels": ["Personal"],
                "confidence": 95,
                "rule_id": "coles",
            }
        elif "IGA" in txn["payee"]:
            return {
                "category": "Groceries",
                "labels": ["Personal"],
                "confidence": 95,
                "rule_id": "iga",
            }
        elif "UBER" in txn["payee"]:
            return {
                "category": None,
                "labels": ["Business"],
                "confidence": 90,
                "rule_id": "business",
            }
        return {"category": None, "labels": [], "confidence": 0, "rule_id": None}

    mock_rule_engine.categorize_and_label.side_effect = mock_categorize

    # Execute
    workflow = CategorizationWorkflow(client=mock_client, mode="smart")
    workflow.rule_engine = mock_rule_engine

    results = workflow.categorize_transactions_batch(
        transactions=transactions,
        available_categories=[
            {"id": 100, "title": "Groceries"},
            {"id": 200, "title": "Dining Out"},
            {"id": 300, "title": "Transport"},
        ],
    )

    # Verify stats
    assert results["stats"]["total"] == 4
    assert results["stats"]["rule_matches"] == 3  # 3 matched (txn1, txn2, txn4)
    assert results["stats"]["conflicts"] == 1  # IGA conflict (txn3)

    # Verify individual results
    txn_results = results["results"]

    # Scenario 1: Uncategorized → category + labels
    assert txn_results[1]["category"] == "Groceries"
    assert txn_results[1]["labels"] == ["Personal"]

    # Scenario 2: Matching → labels only
    assert txn_results[2]["category"] == "Groceries"
    assert txn_results[2]["labels"] == ["Personal"]
    assert txn_results[2].get("needs_review") is None or not txn_results[2]["needs_review"]

    # Scenario 3: Conflict → flag for review
    assert txn_results[3]["category"] == "Dining Out"  # Keep existing
    assert txn_results[3]["needs_review"] is True
    assert txn_results[3]["suggested_category"] == "Groceries"

    # Scenario 4: Label-only → labels only
    assert txn_results[4]["category"] == "Transport"  # Keep existing
    assert txn_results[4]["labels"] == ["Business"]
    assert txn_results[4].get("needs_review") is None or not txn_results[4]["needs_review"]
