"""Cash flow forecasting and planning."""

from typing import List, Dict, Any
from datetime import datetime
from dateutil.relativedelta import relativedelta


def forecast_cash_flow(
    transactions: List[Dict[str, Any]],
    months_forward: int,
    starting_balance: float = 0.0,
) -> Dict[str, Any]:
    """Forecast cash flow based on historical patterns.

    Args:
        transactions: List of transaction dicts
        months_forward: Number of months to project
        starting_balance: Starting account balance

    Returns:
        Dict with average income/expenses and monthly projections
    """
    # Calculate historical averages
    total_income = 0.0
    total_expenses = 0.0
    income_count = 0
    expense_count = 0

    for txn in transactions:
        if txn.get("is_transfer", False):
            continue

        amount = float(txn.get("amount", 0))
        if amount > 0:
            total_income += amount
            income_count += 1
        elif amount < 0:
            total_expenses += abs(amount)
            expense_count += 1

    # Calculate monthly averages (assume data spans multiple months)
    months_of_data = max(1, len(set(t.get("date", "")[:7] for t in transactions)))
    avg_monthly_income = total_income / months_of_data
    avg_monthly_expenses = total_expenses / months_of_data
    avg_monthly_surplus = avg_monthly_income - avg_monthly_expenses

    # Generate projections
    projections = []
    current_balance = starting_balance
    base_date = datetime.now()

    for i in range(months_forward):
        month_date = base_date + relativedelta(months=i + 1)
        month_str = month_date.strftime("%Y-%m")

        current_balance += avg_monthly_surplus

        projections.append(
            {
                "month": month_str,
                "income": round(avg_monthly_income, 2),
                "expenses": round(avg_monthly_expenses, 2),
                "surplus": round(avg_monthly_surplus, 2),
                "ending_balance": round(current_balance, 2),
            }
        )

    return {
        "starting_balance": starting_balance,
        "average_monthly_income": round(avg_monthly_income, 2),
        "average_monthly_expenses": round(avg_monthly_expenses, 2),
        "average_monthly_surplus": round(avg_monthly_surplus, 2),
        "months_forward": months_forward,
        "projections": projections,
        "ending_balance": round(current_balance, 2),
    }


def identify_cash_flow_gaps(
    transactions: List[Dict[str, Any]],
    months_forward: int = 12,
    minimum_balance: float = 1000.00,
) -> Dict[str, Any]:
    """Identify potential cash flow gaps where balance drops below minimum.

    Args:
        transactions: List of transaction dicts
        months_forward: Months to analyze (default 12)
        minimum_balance: Minimum acceptable balance

    Returns:
        Dict with gap months and recommendations
    """
    forecast = forecast_cash_flow(
        transactions=transactions,
        months_forward=months_forward,
        starting_balance=0.0,  # Conservative: assume zero starting
    )

    gap_months = []
    for projection in forecast["projections"]:
        if projection["ending_balance"] < minimum_balance:
            gap_months.append(
                {
                    "month": projection["month"],
                    "projected_balance": projection["ending_balance"],
                    "shortfall": round(minimum_balance - projection["ending_balance"], 2),
                }
            )

    has_gaps = len(gap_months) > 0

    if has_gaps:
        total_shortfall = sum(g["shortfall"] for g in gap_months)
        recommendation = (
            f"Build emergency fund of ${total_shortfall:.2f} to cover {len(gap_months)} "
            f"month(s) with projected balance below ${minimum_balance:.2f}"
        )
    else:
        recommendation = "Cash flow healthy - no gaps projected"

    return {
        "minimum_balance": minimum_balance,
        "months_analyzed": months_forward,
        "has_gaps": has_gaps,
        "gap_count": len(gap_months),
        "gap_months": gap_months,
        "recommendation": recommendation,
    }


def model_emergency_fund(
    monthly_expenses: float,
    current_savings: float,
    target_months: int = 6,
) -> Dict[str, Any]:
    """Model emergency fund adequacy and requirements.

    Args:
        monthly_expenses: Average monthly expenses
        current_savings: Current emergency fund balance
        target_months: Target months of expenses to cover (default 6)

    Returns:
        Dict with target amount, current status, and recommendations
    """
    target_amount = monthly_expenses * target_months
    shortfall = max(0, target_amount - current_savings)
    coverage_months = current_savings / monthly_expenses if monthly_expenses > 0 else 0
    is_adequate = current_savings >= target_amount

    if is_adequate:
        status = "adequate"
        recommendation = f"Emergency fund covers {coverage_months:.1f} months of expenses"
    elif coverage_months >= 3:
        status = "partial"
        recommendation = (
            f"Increase emergency fund by ${shortfall:.2f} to reach "
            f"{target_months} months coverage"
        )
    else:
        status = "critical"
        recommendation = (
            f"URGENT: Build emergency fund by ${shortfall:.2f} "
            f"(currently only {coverage_months:.1f} months)"
        )

    return {
        "monthly_expenses": monthly_expenses,
        "target_months": target_months,
        "target_amount": round(target_amount, 2),
        "current_savings": current_savings,
        "shortfall": round(shortfall, 2),
        "coverage_months": round(coverage_months, 1),
        "is_adequate": is_adequate,
        "status": status,
        "recommendation": recommendation,
    }
