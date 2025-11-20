"""Tests for cash flow forecasting."""

import pytest
from scripts.scenarios.cash_flow import (
    forecast_cash_flow,
    identify_cash_flow_gaps,
    model_emergency_fund,
)


def test_forecast_cash_flow_6_months():
    """Test cash flow forecast with income and expenses."""
    transactions = [
        # Regular income
        {"id": 1, "date": "2025-10-15", "amount": "5000.00", "is_transfer": False},
        {"id": 2, "date": "2025-09-15", "amount": "5000.00", "is_transfer": False},
        {"id": 3, "date": "2025-08-15", "amount": "5000.00", "is_transfer": False},
        # Regular expenses
        {"id": 4, "date": "2025-10-20", "amount": "-3000.00", "is_transfer": False},
        {"id": 5, "date": "2025-09-20", "amount": "-3000.00", "is_transfer": False},
        {"id": 6, "date": "2025-08-20", "amount": "-3000.00", "is_transfer": False},
    ]

    result = forecast_cash_flow(
        transactions=transactions, months_forward=6, starting_balance=10000.00
    )

    assert result["starting_balance"] == 10000.00
    assert result["average_monthly_income"] == 5000.00
    assert result["average_monthly_expenses"] == 3000.00
    assert result["average_monthly_surplus"] == 2000.00
    assert len(result["projections"]) == 6

    # Check first month projection
    month1 = result["projections"][0]
    assert month1["income"] == 5000.00
    assert month1["expenses"] == 3000.00
    assert month1["surplus"] == 2000.00
    assert month1["ending_balance"] == 12000.00  # 10k starting + 2k surplus


def test_identify_cash_flow_gaps():
    """Test identification of cash flow gaps."""
    # Deficit scenario
    transactions = [
        {"id": 1, "date": "2025-10-15", "amount": "3000.00", "is_transfer": False},
        {"id": 2, "date": "2025-10-20", "amount": "-4000.00", "is_transfer": False},
    ]

    result = identify_cash_flow_gaps(
        transactions=transactions, months_forward=3, minimum_balance=1000.00
    )

    assert result["has_gaps"] is True
    assert result["gap_count"] > 0
    assert len(result["gap_months"]) > 0


def test_model_emergency_fund_adequate():
    """Test emergency fund modeling when adequate."""
    result = model_emergency_fund(
        monthly_expenses=3000.00, current_savings=20000.00, target_months=6
    )

    assert result["target_amount"] == 18000.00
    assert result["is_adequate"] is True
    assert result["status"] == "adequate"
    assert result["coverage_months"] > 6.0


def test_model_emergency_fund_critical():
    """Test emergency fund modeling when critically low."""
    result = model_emergency_fund(
        monthly_expenses=3000.00, current_savings=5000.00, target_months=6
    )

    assert result["shortfall"] == 13000.00
    assert result["is_adequate"] is False
    assert result["status"] == "critical"
    assert result["coverage_months"] < 3.0
