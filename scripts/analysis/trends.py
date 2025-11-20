"""Trend detection and analysis."""

from typing import Any, Dict


def calculate_monthly_trends(
    monthly_data: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, Any]]:
    """Calculate trends across months for each category.

    Args:
        monthly_data: Dict of {month: {category: amount}}

    Returns:
        Dict of {category: {average_change, percent_change, trend}}
    """
    # Sort months chronologically
    months = sorted(monthly_data.keys())

    if len(months) < 2:
        return {}

    # Track each category across months
    categories: set[str] = set()
    for month_categories in monthly_data.values():
        categories.update(month_categories.keys())

    trends = {}

    for category in categories:
        amounts = []
        for month in months:
            amount = monthly_data[month].get(category, None)
            if amount is not None:
                amounts.append(amount)

        # Need at least 2 data points for trend
        if len(amounts) < 2:
            trends[category] = {
                "average_change": 0.0,
                "percent_change": 0.0,
                "trend": "new",
            }
            continue

        # Calculate changes between consecutive months
        changes = []
        for i in range(1, len(amounts)):
            changes.append(amounts[i] - amounts[i - 1])

        average_change = sum(changes) / len(changes)

        # Calculate percent change from first to last
        first_amount = amounts[0]
        last_amount = amounts[-1]
        percent_change = (
            ((last_amount - first_amount) / first_amount * 100) if first_amount > 0 else 0
        )

        # Determine trend direction
        if average_change > 5:
            trend = "increasing"
        elif average_change < -5:
            trend = "decreasing"
        else:
            trend = "stable"

        trends[category] = {
            "average_change": average_change,
            "percent_change": percent_change,
            "trend": trend,
        }

    return trends
