"""Tests for report formatters."""

import pytest
import csv
import io
import json
from scripts.reporting.formatters import format_markdown, format_csv, format_json


def test_format_markdown_spending_report():
    """Test Markdown formatter for spending report."""
    data = {
        "period": "2025-11",
        "summary": {
            "total_income": 5000.00,
            "total_expenses": 2500.00,
            "net_income": 2500.00,
        },
        "categories": [
            {"category_name": "Groceries", "total_spent": 500.00, "transaction_count": 15},
            {"category_name": "Transport", "total_spent": 300.00, "transaction_count": 8},
        ],
    }

    result = format_markdown(data, report_type="spending")

    assert "# Spending Report - 2025-11" in result
    assert "Total Income: $5,000.00" in result
    assert "Total Expenses: $2,500.00" in result
    assert "Net Income: $2,500.00" in result
    assert "| Groceries | $500.00 | 15 |" in result
    assert "| Transport | $300.00 | 8 |" in result


def test_format_csv_spending_report():
    """Test CSV formatter for spending report."""
    data = {
        "categories": [
            {"category_name": "Groceries", "total_spent": 500.00, "transaction_count": 15},
            {"category_name": "Transport", "total_spent": 300.00, "transaction_count": 8},
        ],
    }

    result = format_csv(data, report_type="spending")

    # Parse CSV to verify
    reader = csv.DictReader(io.StringIO(result))
    rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["category_name"] == "Groceries"
    assert rows[0]["total_spent"] == "500.00"
    assert rows[0]["transaction_count"] == "15"


def test_format_json_spending_report():
    """Test JSON formatter."""
    data = {
        "period": "2025-11",
        "categories": [
            {"category_name": "Groceries", "total_spent": 500.00},
        ],
    }

    result = format_json(data)

    # Parse to verify valid JSON
    parsed = json.loads(result)
    assert parsed["period"] == "2025-11"
    assert len(parsed["categories"]) == 1
