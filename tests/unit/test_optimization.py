"""Tests for optimization engine."""

import pytest
from scripts.scenarios.optimization import (
    detect_subscriptions,
    analyze_category_trends,
    suggest_optimizations,
)


def test_detect_subscriptions():
    """Test detection of recurring subscription payments."""
    transactions = [
        {"id": 1, "date": "2025-08-15", "payee": "NETFLIX", "amount": "-19.99"},
        {"id": 2, "date": "2025-09-15", "payee": "NETFLIX", "amount": "-19.99"},
        {"id": 3, "date": "2025-10-15", "payee": "NETFLIX", "amount": "-19.99"},
        {"id": 4, "date": "2025-08-20", "payee": "SPOTIFY", "amount": "-14.99"},
        {"id": 5, "date": "2025-09-20", "payee": "SPOTIFY", "amount": "-14.99"},
        {"id": 6, "date": "2025-10-20", "payee": "SPOTIFY", "amount": "-14.99"},
        {"id": 7, "date": "2025-10-01", "payee": "RANDOM SHOP", "amount": "-50.00"},
    ]

    subscriptions = detect_subscriptions(
        transactions=transactions, min_occurrences=3, amount_tolerance=0.10
    )

    assert len(subscriptions) == 2
    netflix = [s for s in subscriptions if s["payee"] == "NETFLIX"][0]
    assert netflix["monthly_amount"] == 19.99
    assert netflix["annual_cost"] == pytest.approx(239.88, abs=0.1)
    assert netflix["occurrences"] == 3


def test_analyze_category_trends():
    """Test category trend analysis with alert threshold."""
    transactions = [
        # Groceries increasing over 3 months
        {
            "id": 1,
            "date": "2025-08-15",
            "amount": "-300.00",
            "category": {"id": 1, "title": "Groceries"},
        },
        {
            "id": 2,
            "date": "2025-09-15",
            "amount": "-350.00",
            "category": {"id": 1, "title": "Groceries"},
        },
        {
            "id": 3,
            "date": "2025-10-15",
            "amount": "-400.00",
            "category": {"id": 1, "title": "Groceries"},
        },
        # Transport stable
        {
            "id": 4,
            "date": "2025-08-20",
            "amount": "-100.00",
            "category": {"id": 2, "title": "Transport"},
        },
        {
            "id": 5,
            "date": "2025-09-20",
            "amount": "-105.00",
            "category": {"id": 2, "title": "Transport"},
        },
        {
            "id": 6,
            "date": "2025-10-20",
            "amount": "-100.00",
            "category": {"id": 2, "title": "Transport"},
        },
    ]

    alerts = analyze_category_trends(transactions, alert_threshold=10.0)

    assert len(alerts) >= 1
    groceries_alert = [a for a in alerts if a["category"] == "Groceries"][0]
    assert groceries_alert["trend"] == "increasing"
    assert groceries_alert["percent_change"] > 10.0


def test_suggest_optimizations():
    """Test comprehensive optimization suggestions."""
    transactions = [
        # Subscriptions
        {"id": 1, "date": "2025-08-15", "payee": "NETFLIX", "amount": "-19.99"},
        {"id": 2, "date": "2025-09-15", "payee": "NETFLIX", "amount": "-19.99"},
        {"id": 3, "date": "2025-10-15", "payee": "NETFLIX", "amount": "-19.99"},
        # Trending category
        {
            "id": 4,
            "date": "2025-08-20",
            "amount": "-200.00",
            "category": {"id": 1, "title": "Dining"},
        },
        {
            "id": 5,
            "date": "2025-09-20",
            "amount": "-250.00",
            "category": {"id": 1, "title": "Dining"},
        },
        {
            "id": 6,
            "date": "2025-10-20",
            "amount": "-300.00",
            "category": {"id": 1, "title": "Dining"},
        },
    ]

    suggestions = suggest_optimizations(transactions)

    assert "subscriptions" in suggestions
    assert "trending_up" in suggestions
    assert suggestions["total_subscriptions"] >= 1
    assert suggestions["potential_annual_savings"] > 0
