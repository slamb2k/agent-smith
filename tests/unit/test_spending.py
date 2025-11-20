"""Tests for spending analysis."""

import pytest
from datetime import datetime
from scripts.analysis.spending import analyze_spending_by_category, analyze_spending_by_merchant


def test_analyze_spending_by_category_sums_amounts():
    """Test spending analysis correctly sums transaction amounts by category."""
    transactions = [
        {
            "id": 1,
            "payee": "WOOLWORTHS",
            "amount": "-50.00",
            "date": "2025-11-01",
            "category": {"id": 100, "title": "Groceries"},
        },
        {
            "id": 2,
            "payee": "COLES",
            "amount": "-30.00",
            "date": "2025-11-05",
            "category": {"id": 100, "title": "Groceries"},
        },
        {
            "id": 3,
            "payee": "SHELL",
            "amount": "-45.00",
            "date": "2025-11-10",
            "category": {"id": 200, "title": "Transport"},
        },
    ]

    result = analyze_spending_by_category(transactions)

    assert len(result) == 2
    assert result[0]["category_id"] == 100
    assert result[0]["category_name"] == "Groceries"
    assert result[0]["total_spent"] == 80.00
    assert result[0]["transaction_count"] == 2
    assert result[1]["category_id"] == 200
    assert result[1]["total_spent"] == 45.00


def test_analyze_spending_excludes_income():
    """Test spending analysis only includes expenses (negative amounts)."""
    transactions = [
        {
            "id": 1,
            "payee": "SALARY",
            "amount": "5000.00",
            "date": "2025-11-01",
            "category": {"id": 1, "title": "Income"},
        },
        {
            "id": 2,
            "payee": "WOOLWORTHS",
            "amount": "-50.00",
            "date": "2025-11-05",
            "category": {"id": 100, "title": "Groceries"},
        },
    ]

    result = analyze_spending_by_category(transactions)

    assert len(result) == 1
    assert result[0]["category_name"] == "Groceries"


def test_analyze_spending_sorts_by_amount_desc():
    """Test spending analysis returns categories sorted by total spent (descending)."""
    transactions = [
        {
            "id": 1,
            "payee": "SHOP1",
            "amount": "-10.00",
            "date": "2025-11-01",
            "category": {"id": 100, "title": "Cat A"},
        },
        {
            "id": 2,
            "payee": "SHOP2",
            "amount": "-50.00",
            "date": "2025-11-05",
            "category": {"id": 200, "title": "Cat B"},
        },
        {
            "id": 3,
            "payee": "SHOP3",
            "amount": "-30.00",
            "date": "2025-11-10",
            "category": {"id": 300, "title": "Cat C"},
        },
    ]

    result = analyze_spending_by_category(transactions)

    assert result[0]["total_spent"] == 50.00  # Cat B first
    assert result[1]["total_spent"] == 30.00  # Cat C second
    assert result[2]["total_spent"] == 10.00  # Cat A last


def test_analyze_spending_by_merchant():
    """Test spending analysis by merchant."""
    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "amount": "-50.00", "date": "2025-11-01"},
        {"id": 2, "payee": "WOOLWORTHS", "amount": "-30.00", "date": "2025-11-05"},
        {"id": 3, "payee": "COLES", "amount": "-45.00", "date": "2025-11-10"},
    ]

    result = analyze_spending_by_merchant(transactions)

    assert len(result) == 2
    assert result[0]["merchant"] == "WOOLWORTHS"
    assert result[0]["total_spent"] == 80.00
    assert result[0]["transaction_count"] == 2
    assert result[1]["merchant"] == "COLES"
    assert result[1]["total_spent"] == 45.00
