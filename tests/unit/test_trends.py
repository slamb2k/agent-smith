"""Tests for trend analysis."""

import pytest
from scripts.analysis.trends import calculate_monthly_trends


def test_calculate_monthly_trends():
    """Test monthly trend calculation."""
    # Format: category spending by month
    monthly_data = {
        "2025-09": {"Groceries": 500.00, "Transport": 200.00},
        "2025-10": {"Groceries": 550.00, "Transport": 180.00},
        "2025-11": {"Groceries": 600.00, "Transport": 220.00},
    }

    result = calculate_monthly_trends(monthly_data)

    assert "Groceries" in result
    assert "Transport" in result

    # Groceries: +50, +50 = avg +50/month = +10%
    groceries_trend = result["Groceries"]
    assert groceries_trend["average_change"] == pytest.approx(50.0, abs=1.0)
    assert groceries_trend["percent_change"] > 0
    assert groceries_trend["trend"] == "increasing"

    # Transport: -20, +40 = mixed
    transport_trend = result["Transport"]
    assert transport_trend["average_change"] == pytest.approx(10.0, abs=1.0)


def test_calculate_monthly_trends_handles_new_categories():
    """Test trends when categories appear mid-period."""
    monthly_data = {
        "2025-10": {"Groceries": 500.00},
        "2025-11": {"Groceries": 550.00, "Transport": 200.00},  # Transport new
    }

    result = calculate_monthly_trends(monthly_data)

    # Groceries should have trend
    assert "Groceries" in result
    assert result["Groceries"]["average_change"] == 50.0

    # Transport should show as "new"
    assert "Transport" in result
    assert result["Transport"]["trend"] == "new"
