"""Tests for categorization subagent."""

import json
import pytest
import tempfile
from pathlib import Path

from scripts.subagents.categorization_subagent import (
    load_json_file,
    save_json_file,
    categorize_transactions,
)
from scripts.services.llm_categorization import IntelligenceMode


def test_load_json_file(tmp_path):
    """Test loading JSON file."""
    test_data = {"test": "data", "number": 42}
    test_file = tmp_path / "test.json"

    with open(test_file, "w") as f:
        json.dump(test_data, f)

    loaded_data = load_json_file(str(test_file))
    assert loaded_data == test_data


def test_save_json_file(tmp_path):
    """Test saving JSON file."""
    test_data = {"test": "data", "number": 42}
    test_file = tmp_path / "output.json"

    save_json_file(str(test_file), test_data)

    with open(test_file, "r") as f:
        loaded_data = json.load(f)

    assert loaded_data == test_data


def test_categorize_transactions_structure():
    """Test categorize_transactions returns correct structure."""
    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "amount": -45.50},
        {"id": 2, "payee": "UBER", "amount": -25.00},
    ]

    categories = [
        {"title": "Groceries", "parent": "Food & Dining"},
        {"title": "Transport", "parent": "Transport"},
    ]

    results = categorize_transactions(transactions, categories, IntelligenceMode.SMART)

    # Check structure
    assert isinstance(results, dict)
    assert len(results) == 2
    assert 1 in results
    assert 2 in results

    # Check each result has required fields
    for txn_id, result in results.items():
        assert "transaction_id" in result
        assert "category" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert "source" in result
        assert result["source"] == "llm"


def test_categorize_transactions_modes():
    """Test categorize_transactions with different modes."""
    transactions = [{"id": 1, "payee": "TEST", "amount": -10.00}]
    categories = [{"title": "Test", "parent": "Test"}]

    # Test each mode
    for mode in [
        IntelligenceMode.CONSERVATIVE,
        IntelligenceMode.SMART,
        IntelligenceMode.AGGRESSIVE,
    ]:
        results = categorize_transactions(transactions, categories, mode)
        assert len(results) == 1
        assert 1 in results


def test_categorize_empty_transactions():
    """Test categorize_transactions with empty transaction list."""
    transactions = []
    categories = [{"title": "Test", "parent": "Test"}]

    results = categorize_transactions(transactions, categories, IntelligenceMode.SMART)

    assert isinstance(results, dict)
    assert len(results) == 0


def test_subagent_end_to_end(tmp_path):
    """Test end-to-end subagent workflow with file I/O."""
    # Create test data files
    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "amount": -45.50, "date": "2024-01-15"},
        {"id": 2, "payee": "UBER", "amount": -25.00, "date": "2024-01-16"},
    ]

    categories = [
        {"title": "Groceries", "parent": "Expenses > Food & Dining"},
        {"title": "Transport", "parent": "Expenses > Transport"},
    ]

    # Save test data
    txn_file = tmp_path / "transactions.json"
    cat_file = tmp_path / "categories.json"
    out_file = tmp_path / "results.json"

    save_json_file(str(txn_file), transactions)
    save_json_file(str(cat_file), categories)

    # Load data
    loaded_txns = load_json_file(str(txn_file))
    loaded_cats = load_json_file(str(cat_file))

    # Execute categorization
    results = categorize_transactions(loaded_txns, loaded_cats, IntelligenceMode.SMART)

    # Save results
    save_json_file(str(out_file), results)

    # Verify results file exists and is valid
    assert out_file.exists()
    loaded_results = load_json_file(str(out_file))

    assert isinstance(loaded_results, dict)
    assert len(loaded_results) == 2
    assert "1" in loaded_results or 1 in loaded_results
