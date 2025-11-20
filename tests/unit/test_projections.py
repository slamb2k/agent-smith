"""Tests for future projection scenarios."""

import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scripts.scenarios.projections import (
    forecast_spending,
    calculate_affordability,
    model_savings_goal,
)


def test_forecast_spending_3_months():
    """Test spending forecast based on historical average."""
    transactions = [
        # 3 months of dining data
        {
            "id": 1,
            "date": "2025-08-15",
            "amount": "-300.00",
            "category": {"id": 1, "title": "Dining"},
        },
        {
            "id": 2,
            "date": "2025-09-15",
            "amount": "-320.00",
            "category": {"id": 1, "title": "Dining"},
        },
        {
            "id": 3,
            "date": "2025-10-15",
            "amount": "-310.00",
            "category": {"id": 1, "title": "Dining"},
        },
    ]

    result = forecast_spending(
        transactions=transactions, category_name="Dining", months_forward=3, start_date="2025-08-01"
    )

    assert result["category"] == "Dining"
    assert result["historical_average"] == 310.00  # Avg of 300, 320, 310
    assert result["months_forward"] == 3
    assert len(result["projections"]) == 3

    # Calculate expected first month (should be next month from now)
    expected_first_month = (datetime.now() + relativedelta(months=1)).strftime("%Y-%m")

    # Conservative scenario (10% higher)
    assert result["projections"][0]["month"] == expected_first_month
    assert result["projections"][0]["conservative"] == pytest.approx(341.0, abs=1)
    assert result["projections"][0]["realistic"] == pytest.approx(310.0, abs=1)
    assert result["projections"][0]["optimistic"] == pytest.approx(279.0, abs=1)


def test_calculate_affordability_affordable():
    """Test affordability analysis for affordable expense."""
    transactions = [
        {"id": 1, "amount": "5000.00"},  # Income
        {"id": 2, "amount": "-2000.00"},  # Expenses
    ]

    result = calculate_affordability(
        transactions=transactions, new_expense_monthly=500.00, months_to_analyze=3
    )

    assert result["current_monthly_surplus"] == 3000.00
    assert result["projected_monthly_surplus"] == 2500.00
    assert result["affordable"] is True
    assert len(result["cash_flow_projections"]) == 3
    assert result["cash_flow_projections"][2]["cumulative_impact"] == -1500.00


def test_model_savings_goal_feasible():
    """Test savings goal modeling when feasible."""
    result = model_savings_goal(
        current_savings=5000.00,
        goal_amount=20000.00,
        target_date="2026-12-31",
        monthly_income=5000.00,
        monthly_expenses=3000.00,
    )

    assert result["remaining_amount"] == 15000.00
    assert result["months_to_goal"] > 0
    assert result["required_monthly_savings"] > 0
    assert result["feasible"] is True


def test_model_savings_goal_not_feasible():
    """Test savings goal modeling when not feasible."""
    result = model_savings_goal(
        current_savings=1000.00,
        goal_amount=50000.00,
        target_date="2026-01-31",
        monthly_income=4000.00,
        monthly_expenses=3800.00,
    )

    assert result["feasible"] is False
    assert result["monthly_shortfall"] > 0
