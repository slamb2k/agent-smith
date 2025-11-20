"""Tests for goal tracking system."""

import pytest
from scripts.scenarios.goals import (
    track_savings_goal,
    track_spending_reduction_goal,
    generate_goal_report,
)


def test_track_savings_goal():
    """Test savings goal progress tracking."""
    result = track_savings_goal(
        goal_name="Emergency Fund",
        target_amount=20000.00,
        current_amount=12000.00,
        target_date="2026-12-31",
        monthly_contribution=500.00,
    )

    assert result["goal_name"] == "Emergency Fund"
    assert result["target_amount"] == 20000.00
    assert result["current_amount"] == 12000.00
    assert result["remaining_amount"] == 8000.00
    assert result["percent_complete"] == 60.0
    assert result["on_track"] is not None
    assert "months_remaining" in result


def test_track_spending_reduction_goal():
    """Test spending reduction goal tracking."""
    transactions = [
        {
            "id": 1,
            "date": "2025-10-01",
            "amount": "-300.00",
            "category": {"id": 1, "title": "Dining"},
        },
        {
            "id": 2,
            "date": "2025-11-01",
            "amount": "-250.00",
            "category": {"id": 1, "title": "Dining"},
        },
    ]

    result = track_spending_reduction_goal(
        goal_name="Reduce Dining",
        category_name="Dining",
        transactions=transactions,
        target_monthly=200.00,
        start_date="2025-10-01",
    )

    assert result["goal_name"] == "Reduce Dining"
    assert result["category_name"] == "Dining"
    assert result["target_monthly"] == 200.00
    assert result["actual_monthly"] > 200.00  # Currently overspending
    assert result["on_track"] is False


def test_generate_goal_report():
    """Test comprehensive goal report generation."""
    goals = [
        {
            "goal_name": "Emergency Fund",
            "target_amount": 20000.00,
            "current_amount": 15000.00,
            "on_track": True,
        },
        {
            "goal_name": "Vacation",
            "target_amount": 5000.00,
            "current_amount": 2000.00,
            "on_track": False,
        },
    ]

    report = generate_goal_report(goals)

    assert report["total_goals"] == 2
    assert report["on_track"] == 1
    assert report["off_track"] == 1
    assert report["overall_progress"] > 0
    assert len(report["goals"]) == 2
