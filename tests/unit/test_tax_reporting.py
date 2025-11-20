"""Tests for tax reporting."""

import pytest
from scripts.tax.reporting import generate_tax_summary


def test_generate_tax_summary():
    """Test generating tax summary from transactions."""
    transactions = [
        {
            "id": 1,
            "payee": "Office Warehouse",
            "amount": "-150.00",
            "date": "2025-07-01",
            "category": {"id": 100, "title": "Office Supplies"},
        },
        {
            "id": 2,
            "payee": "Woolworths",
            "amount": "-50.00",
            "date": "2025-07-05",
            "category": {"id": 200, "title": "Groceries"},
        },
        {
            "id": 3,
            "payee": "BP Petrol",
            "amount": "-80.00",
            "date": "2025-07-10",
            "category": {"id": 300, "title": "Transport"},
        },
    ]

    result = generate_tax_summary(transactions)

    # Check structure
    assert "total_expenses" in result
    assert "deductible_expenses" in result
    assert "non_deductible_expenses" in result
    assert "by_ato_category" in result

    # Check totals
    assert result["total_expenses"] == 280.00
    assert result["deductible_expenses"] == 230.00  # Office + Transport
    assert result["non_deductible_expenses"] == 50.00  # Groceries

    # Check ATO category breakdown
    ato_categories = result["by_ato_category"]
    assert len(ato_categories) == 2  # D1 (Transport) and D5 (Office)

    # Find Office Supplies category (D5)
    d5_category = next(c for c in ato_categories if c["ato_code"] == "D5")
    assert d5_category["total"] == 150.00
    assert d5_category["transaction_count"] == 1


def test_generate_tax_summary_with_date_range():
    """Test filtering transactions by financial year."""
    transactions = [
        {
            "id": 1,
            "payee": "Office Warehouse",
            "amount": "-150.00",
            "date": "2024-07-01",  # FY 2024-25
            "category": {"id": 100, "title": "Office Supplies"},
        },
        {
            "id": 2,
            "payee": "Tech Store",
            "amount": "-200.00",
            "date": "2025-06-30",  # FY 2024-25
            "category": {"id": 100, "title": "Office Supplies"},
        },
        {
            "id": 3,
            "payee": "Old Purchase",
            "amount": "-100.00",
            "date": "2023-06-30",  # FY 2022-23 (should be excluded)
            "category": {"id": 100, "title": "Office Supplies"},
        },
    ]

    result = generate_tax_summary(transactions, start_date="2024-07-01", end_date="2025-06-30")

    assert result["total_expenses"] == 350.00
    assert result["transaction_count"] == 2


def test_generate_tax_summary_excludes_income():
    """Test that income transactions are excluded from expense summary."""
    transactions = [
        {
            "id": 1,
            "payee": "Salary",
            "amount": "5000.00",
            "date": "2025-07-01",
            "category": {"id": 1, "title": "Income"},
        },
        {
            "id": 2,
            "payee": "Office",
            "amount": "-150.00",
            "date": "2025-07-05",
            "category": {"id": 100, "title": "Office Supplies"},
        },
    ]

    result = generate_tax_summary(transactions)

    assert result["total_expenses"] == 150.00
    assert result["transaction_count"] == 1
