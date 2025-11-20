"""Tests for historical scenario analysis."""

import pytest
from scripts.scenarios.historical import (
    calculate_what_if_spending,
    compare_periods,
    detect_spending_anomalies,
)


def test_what_if_spending_reduction():
    """Test what-if scenario with spending reduction."""
    transactions = [
        {
            "id": 1,
            "date": "2025-10-01",
            "amount": "-100.00",
            "category": {"id": 1, "title": "Dining"},
        },
        {
            "id": 2,
            "date": "2025-10-05",
            "amount": "-150.00",
            "category": {"id": 1, "title": "Dining"},
        },
        {
            "id": 3,
            "date": "2025-10-10",
            "amount": "-50.00",
            "category": {"id": 2, "title": "Groceries"},
        },
    ]

    # What if we reduced dining by 30%?
    result = calculate_what_if_spending(
        transactions=transactions,
        category_name="Dining",
        adjustment_percent=-30.0,
        start_date="2025-10-01",
        end_date="2025-10-31",
    )

    assert result["category"] == "Dining"
    assert result["actual_spent"] == 250.00
    assert result["adjusted_spent"] == 175.00  # 30% reduction
    assert result["savings"] == 75.00
    assert result["adjustment_percent"] == -30.0


def test_compare_periods_yoy():
    """Test year-over-year period comparison."""
    transactions = [
        {"id": 1, "date": "2024-10-15", "amount": "-100.00"},
        {"id": 2, "date": "2024-10-20", "amount": "-150.00"},
        {"id": 3, "date": "2025-10-15", "amount": "-120.00"},
        {"id": 4, "date": "2025-10-20", "amount": "-180.00"},
    ]

    result = compare_periods(
        transactions=transactions,
        period1_start="2024-10-01",
        period1_end="2024-10-31",
        period2_start="2025-10-01",
        period2_end="2025-10-31",
    )

    assert result["period1"]["total"] == 250.00
    assert result["period2"]["total"] == 300.00
    assert result["difference"] == 50.00
    assert result["percent_change"] == 20.0


def test_detect_spending_anomalies():
    """Test anomaly detection for unusual spending."""
    transactions = [
        {
            "id": 1,
            "date": "2025-10-01",
            "amount": "-50.00",
            "category": {"id": 1, "title": "Dining"},
        },
        {
            "id": 2,
            "date": "2025-10-05",
            "amount": "-60.00",
            "category": {"id": 1, "title": "Dining"},
        },
        {
            "id": 3,
            "date": "2025-10-10",
            "amount": "-55.00",
            "category": {"id": 1, "title": "Dining"},
        },
        {
            "id": 4,
            "date": "2025-10-15",
            "amount": "-200.00",
            "category": {"id": 1, "title": "Dining"},
        },  # Anomaly
    ]

    anomalies = detect_spending_anomalies(
        transactions=transactions, category_name="Dining", threshold_percent=50.0
    )

    assert len(anomalies) == 1
    assert anomalies[0]["amount"] == 200.00
    assert anomalies[0]["percent_above_average"] > 100.0
