"""Integration tests for scenario analysis workflows."""

import pytest
import os
from scripts.core.api_client import PocketSmithClient
from scripts.scenarios.historical import calculate_what_if_spending, compare_periods
from scripts.scenarios.projections import forecast_spending, calculate_affordability
from scripts.scenarios.optimization import detect_subscriptions, suggest_optimizations
from scripts.scenarios.cash_flow import forecast_cash_flow
from scripts.scenarios.goals import track_savings_goal

pytestmark = pytest.mark.integration


@pytest.fixture
def api_client():
    """Create API client with real credentials."""
    api_key = os.getenv("POCKETSMITH_API_KEY")
    if not api_key:
        pytest.skip("POCKETSMITH_API_KEY not set - skipping integration tests")
    return PocketSmithClient(api_key=api_key)


@pytest.fixture
def sample_transactions(api_client):
    """Fetch real transactions for testing."""
    user = api_client.get_user()
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2025-08-01", end_date="2025-11-30"
    )
    return transactions


class TestScenarioAnalysisWorkflows:
    """Test end-to-end scenario analysis workflows."""

    def test_historical_what_if_analysis(self, sample_transactions):
        """Test historical what-if scenario with real data."""
        # Get a category from real data
        categories = set()
        for txn in sample_transactions[:50]:
            category = txn.get("category") or {}
            cat_name = category.get("title")
            if cat_name:
                categories.add(cat_name)

        if not categories:
            pytest.skip("No categorized transactions in sample data")

        test_category = list(categories)[0]

        # Run what-if scenario
        result = calculate_what_if_spending(
            transactions=sample_transactions,
            category_name=test_category,
            adjustment_percent=-20.0,
            start_date="2025-10-01",
            end_date="2025-10-31",
        )

        assert result["category"] == test_category
        assert result["actual_spent"] >= 0
        assert result["adjusted_spent"] == pytest.approx(result["actual_spent"] * 0.8, abs=0.1)
        assert result["savings"] >= 0

        savings = result["savings"]
        print(f"✓ What-if: {test_category} - ${savings:.2f} savings with 20% reduction")

    def test_spending_forecast_workflow(self, sample_transactions):
        """Test spending forecast with real data."""
        # Get top category
        categories = {}
        for txn in sample_transactions:
            amount = float(txn.get("amount", 0))
            if amount >= 0:
                continue
            category = txn.get("category") or {}
            cat_name = category.get("title", "Uncategorized")
            categories[cat_name] = categories.get(cat_name, 0) + abs(amount)

        if not categories:
            pytest.skip("No expenses in sample data")

        top_category = max(categories.items(), key=lambda x: x[1])[0]

        # Forecast spending
        forecast = forecast_spending(
            transactions=sample_transactions,
            category_name=top_category,
            months_forward=3,
            start_date="2025-08-01",
        )

        assert forecast["category"] == top_category
        assert forecast["historical_average"] > 0
        assert len(forecast["projections"]) == 3

        print(f"✓ Forecast: {top_category} - ${forecast['historical_average']:.2f}/month average")

    def test_subscription_detection_workflow(self, sample_transactions):
        """Test subscription detection with real data."""
        subscriptions = detect_subscriptions(
            transactions=sample_transactions,
            min_occurrences=2,  # Lower threshold for test data
            amount_tolerance=0.15,
        )

        # May or may not find subscriptions depending on data
        assert isinstance(subscriptions, list)

        if subscriptions:
            assert "payee" in subscriptions[0]
            assert "monthly_amount" in subscriptions[0]
            assert "annual_cost" in subscriptions[0]
            print(f"✓ Detected {len(subscriptions)} subscription(s)")
        else:
            print("✓ No subscriptions detected in sample data")

    def test_cash_flow_forecast_workflow(self, sample_transactions):
        """Test cash flow forecasting with real data."""
        forecast = forecast_cash_flow(
            transactions=sample_transactions, months_forward=6, starting_balance=5000.00
        )

        assert forecast["starting_balance"] == 5000.00
        assert forecast["average_monthly_income"] >= 0
        assert forecast["average_monthly_expenses"] >= 0
        assert len(forecast["projections"]) == 6

        print(
            f"✓ Cash flow: ${forecast['average_monthly_income']:.2f} income, "
            f"${forecast['average_monthly_expenses']:.2f} expenses, "
            f"${forecast['average_monthly_surplus']:.2f} surplus"
        )

    def test_optimization_suggestions_workflow(self, sample_transactions):
        """Test optimization suggestions with real data."""
        suggestions = suggest_optimizations(transactions=sample_transactions)

        assert "subscriptions" in suggestions
        assert "trending_up" in suggestions
        assert "total_subscriptions" in suggestions
        assert "potential_annual_savings" in suggestions

        print(
            f"✓ Optimization: {suggestions['total_subscriptions']} subscriptions, "
            f"{suggestions['total_trending']} trending categories, "
            f"${suggestions['potential_annual_savings']:.2f} potential savings"
        )

    def test_complete_scenario_analysis(self, sample_transactions):
        """Test complete scenario analysis pipeline."""
        # 1. Historical analysis
        period_comparison = compare_periods(
            transactions=sample_transactions,
            period1_start="2025-08-01",
            period1_end="2025-08-31",
            period2_start="2025-10-01",
            period2_end="2025-10-31",
        )

        # 2. Future projections
        affordability = calculate_affordability(
            transactions=sample_transactions, new_expense_monthly=500.00, months_to_analyze=3
        )

        # 3. Optimization
        optimizations = suggest_optimizations(transactions=sample_transactions)

        # 4. Goal tracking
        goal = track_savings_goal(
            goal_name="Test Goal",
            target_amount=10000.00,
            current_amount=5000.00,
            target_date="2026-12-31",
            monthly_contribution=250.00,
        )

        # Verify all components work together
        assert "difference" in period_comparison
        assert "affordable" in affordability
        assert "potential_annual_savings" in optimizations
        assert "on_track" in goal

        print("✓ Complete scenario analysis pipeline successful")
