"""Goal tracking and progress monitoring."""

from typing import List, Dict, Any
from datetime import datetime, timedelta


def track_savings_goal(
    goal_name: str,
    target_amount: float,
    current_amount: float,
    target_date: str,
    monthly_contribution: float,
) -> Dict[str, Any]:
    """Track progress toward savings goal.

    Args:
        goal_name: Name of the goal
        target_amount: Target savings amount
        current_amount: Current savings balance
        target_date: Target completion date (YYYY-MM-DD)
        monthly_contribution: Monthly savings contribution

    Returns:
        Dict with progress, on_track status, and projections
    """
    remaining_amount = target_amount - current_amount
    percent_complete = (current_amount / target_amount * 100) if target_amount > 0 else 0

    # Calculate months remaining
    target = datetime.strptime(target_date, "%Y-%m-%d")
    today = datetime.now()
    months_remaining = (target.year - today.year) * 12 + (target.month - today.month)

    # Calculate if on track
    if months_remaining <= 0:
        on_track = current_amount >= target_amount
        required_monthly = 0.0
        shortfall = 0.0
    else:
        required_monthly = remaining_amount / months_remaining
        on_track = monthly_contribution >= required_monthly
        shortfall = max(0, required_monthly - monthly_contribution)

    # Project completion
    if monthly_contribution > 0:
        months_to_complete = remaining_amount / monthly_contribution
        projected_completion = today.replace(day=1) + timedelta(days=30 * months_to_complete)
        projected_completion_str = projected_completion.strftime("%Y-%m-%d")
    else:
        months_to_complete = None
        projected_completion_str = None

    return {
        "goal_name": goal_name,
        "target_amount": target_amount,
        "current_amount": current_amount,
        "remaining_amount": round(remaining_amount, 2),
        "percent_complete": round(percent_complete, 1),
        "target_date": target_date,
        "months_remaining": months_remaining,
        "monthly_contribution": monthly_contribution,
        "required_monthly": round(required_monthly, 2),
        "on_track": on_track,
        "monthly_shortfall": round(shortfall, 2) if not on_track else 0.0,
        "projected_completion": projected_completion_str,
    }


def track_spending_reduction_goal(
    goal_name: str,
    category_name: str,
    transactions: List[Dict[str, Any]],
    target_monthly: float,
    start_date: str,
) -> Dict[str, Any]:
    """Track progress toward spending reduction goal.

    Args:
        goal_name: Name of the goal
        category_name: Category to track
        transactions: List of transaction dicts
        target_monthly: Target monthly spending amount
        start_date: Goal start date (YYYY-MM-DD)

    Returns:
        Dict with actual spending, target, and progress
    """
    # Calculate actual spending since start date
    total_spent = 0.0
    months_tracked = 0

    for txn in transactions:
        if txn.get("date", "") < start_date:
            continue

        amount = float(txn.get("amount", 0))
        if amount >= 0:  # Skip income
            continue

        category = txn.get("category") or {}
        if category.get("title") == category_name:
            total_spent += abs(amount)

    # Estimate months tracked
    start = datetime.strptime(start_date, "%Y-%m-%d")
    today = datetime.now()
    months_tracked = max(1, (today.year - start.year) * 12 + (today.month - start.month))

    actual_monthly = total_spent / months_tracked
    variance = actual_monthly - target_monthly
    on_track = actual_monthly <= target_monthly
    percent_of_target = (actual_monthly / target_monthly * 100) if target_monthly > 0 else 0

    return {
        "goal_name": goal_name,
        "category_name": category_name,
        "target_monthly": target_monthly,
        "actual_monthly": round(actual_monthly, 2),
        "variance": round(variance, 2),
        "percent_of_target": round(percent_of_target, 1),
        "on_track": on_track,
        "months_tracked": months_tracked,
        "total_spent": round(total_spent, 2),
    }


def generate_goal_report(goals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate comprehensive report for all goals.

    Args:
        goals: List of goal tracking results

    Returns:
        Dict with summary statistics and goal list
    """
    total_goals = len(goals)
    on_track_count = sum(1 for g in goals if g.get("on_track", False))
    off_track_count = total_goals - on_track_count

    # Calculate overall progress (for savings goals)
    savings_goals = [g for g in goals if "target_amount" in g]
    if savings_goals:
        total_target = sum(g["target_amount"] for g in savings_goals)
        total_current = sum(g["current_amount"] for g in savings_goals)
        overall_progress = (total_current / total_target * 100) if total_target > 0 else 0
    else:
        overall_progress = 0.0

    return {
        "total_goals": total_goals,
        "on_track": on_track_count,
        "off_track": off_track_count,
        "overall_progress": round(overall_progress, 1),
        "goals": goals,
    }
