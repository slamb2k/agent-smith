"""Integration tests for scenario analysis workflows."""

import pytest
import os
from datetime import datetime, timedelta
from scripts.core.api_client import PocketSmithClient
from scripts.scenarios.historical import calculate_what_if_spending, compare_periods
from scripts.scenarios.projections import forecast_spending, calculate_affordability
from scripts.scenarios.optimization import detect_subscriptions, suggest_optimizations
from scripts.scenarios.cash_flow import forecast_cash_flow
from scripts.scenarios.goals import track_savings_goal
from scripts.scenarios.tax_scenarios import model_prepayment_scenario

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
    """Fetch real transactions for testing (last 90 days)."""
    user = api_client.get_user()

    # Use dynamic date range: last 90 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)

    transactions = api_client.get_transactions(
        user_id=user["id"],
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
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

        # Use last 30 days for analysis
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        # Run what-if scenario
        result = calculate_what_if_spending(
            transactions=sample_transactions,
            category_name=test_category,
            adjustment_percent=-20.0,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
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

        # Use start of 90-day window for historical baseline
        start_date = (datetime.now().date() - timedelta(days=90)).strftime("%Y-%m-%d")

        # Forecast spending
        forecast = forecast_spending(
            transactions=sample_transactions,
            category_name=top_category,
            months_forward=3,
            start_date=start_date,
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

    def test_tax_scenario_planning_workflow(self, sample_transactions):
        """Test tax scenario planning with real data."""
        # Calculate total income from transactions
        total_income = sum(
            float(txn.get("amount", 0))
            for txn in sample_transactions
            if float(txn.get("amount", 0)) > 0
        )

        # Calculate annualized income (90 days worth of data * 4)
        annualized_income = total_income * 4

        # Test prepayment scenario with realistic amounts
        expense_amount = 5000.00
        current_fy_income = annualized_income if annualized_income > 0 else 80000.00
        next_fy_income = current_fy_income * 1.1  # Assume 10% income growth

        result = model_prepayment_scenario(
            expense_amount=expense_amount,
            current_fy_income=current_fy_income,
            next_fy_projected_income=next_fy_income,
        )

        # Verify structure
        assert "expense_amount" in result
        assert "current_fy_income" in result
        assert "next_fy_income" in result
        assert "current_fy_tax_rate" in result
        assert "next_fy_tax_rate" in result
        assert "tax_saving_current_fy" in result
        assert "tax_saving_next_fy" in result
        assert "difference" in result
        assert "recommendation" in result
        assert "reason" in result

        # Verify values are reasonable
        assert result["expense_amount"] == expense_amount
        assert result["current_fy_income"] == current_fy_income
        assert result["next_fy_income"] == next_fy_income
        assert 0 <= result["current_fy_tax_rate"] <= 0.45
        assert 0 <= result["next_fy_tax_rate"] <= 0.45
        assert result["tax_saving_current_fy"] >= 0
        assert result["tax_saving_next_fy"] >= 0

        # Verify recommendation logic
        assert result["recommendation"] in ["prepay_now", "defer", "neutral"]
        assert len(result["reason"]) > 0

        # For higher income next year, should recommend prepaying now
        if next_fy_income > current_fy_income:
            # Tax rate should be higher in next FY or same
            assert result["next_fy_tax_rate"] >= result["current_fy_tax_rate"]

        print(
            f"✓ Tax scenario: ${expense_amount:.2f} expense, "
            f"Current FY income ${current_fy_income:.2f} "
            f"({result['current_fy_tax_rate']*100:.0f}% rate), "
            f"Next FY income ${next_fy_income:.2f} "
            f"({result['next_fy_tax_rate']*100:.0f}% rate), "
            f"Recommendation: {result['recommendation']}"
        )

    def test_complete_scenario_analysis(self, sample_transactions):
        """Test complete scenario analysis pipeline."""
        # Use dynamic dates: compare last 30 days to 30 days before that
        end_date = datetime.now().date()
        period2_end = end_date
        period2_start = period2_end - timedelta(days=30)
        period1_end = period2_start - timedelta(days=1)
        period1_start = period1_end - timedelta(days=30)

        # 1. Historical analysis
        period_comparison = compare_periods(
            transactions=sample_transactions,
            period1_start=period1_start.strftime("%Y-%m-%d"),
            period1_end=period1_end.strftime("%Y-%m-%d"),
            period2_start=period2_start.strftime("%Y-%m-%d"),
            period2_end=period2_end.strftime("%Y-%m-%d"),
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
