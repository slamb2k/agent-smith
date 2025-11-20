"""Optimization engine for identifying savings opportunities."""

from typing import List, Dict, Any, DefaultDict, cast
from collections import defaultdict


def detect_subscriptions(
    transactions: List[Dict[str, Any]],
    min_occurrences: int = 3,
    amount_tolerance: float = 0.10,
) -> List[Dict[str, Any]]:
    """Detect recurring subscription payments.

    Args:
        transactions: List of transaction dicts
        min_occurrences: Minimum occurrences to qualify as subscription (default 3)
        amount_tolerance: Tolerance for amount variation (default 10%)

    Returns:
        List of detected subscriptions with payee, monthly_amount, annual_cost
    """
    # Group by payee
    payee_groups: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)
    for txn in transactions:
        amount = float(txn.get("amount", 0))
        if amount >= 0:  # Skip income
            continue
        payee = txn.get("payee", "Unknown")
        payee_groups[payee].append(
            {
                "date": txn.get("date"),
                "amount": abs(amount),
            }
        )

    # Detect recurring patterns
    subscriptions = []
    for payee, txns in payee_groups.items():
        if len(txns) < min_occurrences:
            continue

        # Check if amounts are consistent
        amounts: List[float] = [float(t["amount"]) for t in txns]
        avg_amount: float = sum(amounts) / len(amounts)

        consistent = True
        for amount in amounts:
            if abs(amount - avg_amount) / avg_amount > amount_tolerance:
                consistent = False
                break

        if consistent:
            subscriptions.append(
                {
                    "payee": payee,
                    "monthly_amount": round(avg_amount, 2),
                    "annual_cost": round(avg_amount * 12, 2),
                    "occurrences": len(txns),
                }
            )

    # Sort by annual cost descending
    subscriptions.sort(key=lambda x: cast(float, x["annual_cost"]), reverse=True)
    return subscriptions


def analyze_category_trends(
    transactions: List[Dict[str, Any]],
    alert_threshold: float = 10.0,
) -> List[Dict[str, Any]]:
    """Analyze category spending trends and flag significant increases.

    Args:
        transactions: List of transaction dicts
        alert_threshold: Percent increase to flag (default 10%)

    Returns:
        List of categories with significant trend changes
    """
    from scripts.analysis.trends import calculate_monthly_trends

    # Build monthly data by category
    monthly_data: DefaultDict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for txn in transactions:
        amount = float(txn.get("amount", 0))
        if amount >= 0:  # Skip income
            continue

        date_str = txn.get("date", "")
        if len(date_str) >= 7:
            month = date_str[:7]  # YYYY-MM
        else:
            continue

        category = txn.get("category") or {}
        category_name = category.get("title", "Uncategorized")

        monthly_data[month][category_name] += abs(amount)

    # Calculate trends
    trends = calculate_monthly_trends(dict(monthly_data))

    # Filter for significant increases
    alerts = []
    for category, trend_data in trends.items():
        if trend_data["trend"] == "increasing" and trend_data["percent_change"] >= alert_threshold:
            alerts.append(
                {
                    "category": category,
                    "trend": trend_data["trend"],
                    "average_change": round(trend_data["average_change"], 2),
                    "percent_change": round(trend_data["percent_change"], 2),
                }
            )

    # Sort by percent change descending
    alerts.sort(key=lambda x: cast(float, x["percent_change"]), reverse=True)
    return alerts


def suggest_optimizations(
    transactions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate optimization suggestions based on spending patterns.

    Args:
        transactions: List of transaction dicts

    Returns:
        Dict with subscriptions, trending_up, and total_potential_savings
    """
    subscriptions = detect_subscriptions(transactions)
    trending_categories = analyze_category_trends(transactions)

    # Calculate potential savings (conservative estimate)
    subscription_savings = sum(s["annual_cost"] * 0.20 for s in subscriptions)  # 20% reduction
    trend_savings = sum(
        t["average_change"] * 12 * 0.30 for t in trending_categories
    )  # 30% reduction

    return {
        "subscriptions": subscriptions,
        "trending_up": trending_categories,
        "total_subscriptions": len(subscriptions),
        "total_trending": len(trending_categories),
        "potential_annual_savings": round(subscription_savings + trend_savings, 2),
    }
