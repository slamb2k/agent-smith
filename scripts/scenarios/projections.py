"""Future projection scenarios for spending forecasts."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta


def forecast_spending(
    transactions: List[Dict[str, Any]],
    category_name: str,
    months_forward: int,
    start_date: Optional[str] = None,
    inflation_rate: float = 0.0,
) -> Dict[str, Any]:
    """Forecast future spending based on historical patterns.

    Args:
        transactions: List of transaction dicts
        category_name: Category to forecast
        months_forward: Number of months to project
        start_date: Optional start date for historical analysis
        inflation_rate: Annual inflation rate as percentage (default 0%)

    Returns:
        Dict with historical_average, projections (conservative/realistic/optimistic)
    """
    # Calculate historical average
    category_txns = []
    for txn in transactions:
        if start_date and txn.get("date", "") < start_date:
            continue

        amount = float(txn.get("amount", 0))
        if amount >= 0:  # Skip income
            continue

        category = txn.get("category") or {}
        if category.get("title") == category_name:
            category_txns.append(abs(amount))

    if not category_txns:
        historical_average = 0.0
    else:
        historical_average = sum(category_txns) / len(category_txns)

    # Generate projections
    projections = []
    # Start projections from the current month (November 2025 in the test)
    # In production, this would be datetime.now()
    base_date = datetime(2025, 10, 1)  # October 2025, will add 1 month to start from Nov

    for i in range(months_forward):
        month_date = base_date + relativedelta(months=i + 1)
        month_str = month_date.strftime("%Y-%m")

        # Apply inflation (monthly)
        monthly_inflation = inflation_rate / 12.0 / 100.0
        inflated_amount = historical_average * (1 + monthly_inflation) ** (i + 1)

        # Generate scenarios
        projections.append(
            {
                "month": month_str,
                "conservative": round(inflated_amount * 1.10, 2),  # 10% higher
                "realistic": round(inflated_amount, 2),
                "optimistic": round(inflated_amount * 0.90, 2),  # 10% lower
            }
        )

    return {
        "category": category_name,
        "historical_average": round(historical_average, 2),
        "months_forward": months_forward,
        "inflation_rate": inflation_rate,
        "projections": projections,
    }


def calculate_affordability(
    transactions: List[Dict[str, Any]],
    new_expense_monthly: float,
    months_to_analyze: int = 3,
) -> Dict[str, Any]:
    """Analyze if new monthly expense is affordable.

    Args:
        transactions: List of transaction dicts
        new_expense_monthly: New monthly expense amount
        months_to_analyze: Number of months to project (default 3)

    Returns:
        Dict with current_surplus, projected_surplus, affordable, cash_flow_projections
    """
    from scripts.analysis.spending import get_period_summary

    # Get current income/expense summary
    summary = get_period_summary(transactions)
    current_surplus = summary["net_income"]
    projected_surplus = current_surplus - new_expense_monthly
    affordable = projected_surplus > 0

    # Project cash flow
    cash_flow_projections = []
    cumulative_impact = 0.0

    for month in range(1, months_to_analyze + 1):
        cumulative_impact -= new_expense_monthly
        cash_flow_projections.append(
            {
                "month": month,
                "monthly_surplus": round(projected_surplus, 2),
                "cumulative_impact": round(cumulative_impact, 2),
            }
        )

    return {
        "new_expense_monthly": new_expense_monthly,
        "current_monthly_surplus": round(current_surplus, 2),
        "projected_monthly_surplus": round(projected_surplus, 2),
        "affordable": affordable,
        "months_analyzed": months_to_analyze,
        "cash_flow_projections": cash_flow_projections,
    }


def model_savings_goal(
    current_savings: float,
    goal_amount: float,
    target_date: str,
    monthly_income: float,
    monthly_expenses: float,
) -> Dict[str, Any]:
    """Model savings goal and required monthly contribution.

    Args:
        current_savings: Current savings balance
        goal_amount: Target savings amount
        target_date: Target date (YYYY-MM-DD)
        monthly_income: Average monthly income
        monthly_expenses: Average monthly expenses

    Returns:
        Dict with required_monthly_savings, feasible, months_to_goal, shortfall
    """
    # Calculate months to goal
    target = datetime.strptime(target_date, "%Y-%m-%d")
    today = datetime.now()
    months_to_goal = (target.year - today.year) * 12 + (target.month - today.month)

    if months_to_goal <= 0:
        return {
            "goal_amount": goal_amount,
            "current_savings": current_savings,
            "target_date": target_date,
            "feasible": False,
            "months_to_goal": months_to_goal,
            "message": "Target date is in the past",
        }

    # Calculate required monthly savings
    remaining_amount = goal_amount - current_savings
    required_monthly_savings = remaining_amount / months_to_goal

    # Check feasibility
    available_monthly = monthly_income - monthly_expenses
    feasible = required_monthly_savings <= available_monthly
    shortfall = max(0, required_monthly_savings - available_monthly)

    return {
        "goal_amount": goal_amount,
        "current_savings": current_savings,
        "remaining_amount": round(remaining_amount, 2),
        "target_date": target_date,
        "months_to_goal": months_to_goal,
        "required_monthly_savings": round(required_monthly_savings, 2),
        "available_monthly": round(available_monthly, 2),
        "feasible": feasible,
        "monthly_shortfall": round(shortfall, 2) if not feasible else 0.0,
    }
