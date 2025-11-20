"""Historical scenario analysis for what-if modeling."""

from typing import List, Dict, Any, Optional


def calculate_what_if_spending(
    transactions: List[Dict[str, Any]],
    category_name: str,
    adjustment_percent: float,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Calculate what-if scenario with spending adjustment.

    Args:
        transactions: List of transaction dicts
        category_name: Category to adjust
        adjustment_percent: Percentage adjustment (e.g., -30 for 30% reduction)
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)

    Returns:
        Dict with actual_spent, adjusted_spent, savings, category, adjustment_percent
    """
    # Filter by date range (using ISO 8601 string comparison)
    filtered = transactions
    if start_date:
        filtered = [t for t in filtered if t.get("date", "") >= start_date]
    if end_date:
        filtered = [t for t in filtered if t.get("date", "") <= end_date]

    # Calculate actual spending for category
    actual_spent = 0.0
    for txn in filtered:
        amount = float(txn.get("amount", 0))
        if amount >= 0:  # Skip income
            continue

        category = txn.get("category") or {}
        if category.get("title") == category_name:
            actual_spent += abs(amount)

    # Calculate adjusted spending
    adjustment_multiplier = 1 + (adjustment_percent / 100.0)
    adjusted_spent = actual_spent * adjustment_multiplier
    savings = actual_spent - adjusted_spent

    return {
        "category": category_name,
        "actual_spent": round(actual_spent, 2),
        "adjusted_spent": round(adjusted_spent, 2),
        "savings": round(savings, 2),
        "adjustment_percent": adjustment_percent,
        "start_date": start_date,
        "end_date": end_date,
    }


def compare_periods(
    transactions: List[Dict[str, Any]],
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str,
) -> Dict[str, Any]:
    """Compare spending between two time periods.

    Args:
        transactions: List of transaction dicts
        period1_start: Period 1 start date (YYYY-MM-DD)
        period1_end: Period 1 end date (YYYY-MM-DD)
        period2_start: Period 2 start date (YYYY-MM-DD)
        period2_end: Period 2 end date (YYYY-MM-DD)

    Returns:
        Dict with period1_total, period2_total, difference, percent_change
    """

    def calculate_total(start: str, end: str) -> float:
        total = 0.0
        for txn in transactions:
            date = txn.get("date", "")
            # Filter by date range (using ISO 8601 string comparison)
            if start <= date <= end:
                amount = float(txn.get("amount", 0))
                if amount < 0:  # Expenses only
                    total += abs(amount)
        return total

    period1_total = calculate_total(period1_start, period1_end)
    period2_total = calculate_total(period2_start, period2_end)
    difference = period2_total - period1_total

    if period1_total > 0:
        percent_change = (difference / period1_total) * 100.0
    else:
        percent_change = 0.0

    return {
        "period1": {
            "start": period1_start,
            "end": period1_end,
            "total": round(period1_total, 2),
        },
        "period2": {
            "start": period2_start,
            "end": period2_end,
            "total": round(period2_total, 2),
        },
        "difference": round(difference, 2),
        "percent_change": round(percent_change, 2),
    }


def detect_spending_anomalies(
    transactions: List[Dict[str, Any]],
    category_name: str,
    threshold_percent: float = 50.0,
) -> List[Dict[str, Any]]:
    """Detect anomalous spending transactions.

    Finds transactions that are significantly higher than average.

    Args:
        transactions: List of transaction dicts
        category_name: Category to analyze
        threshold_percent: Percent above average to flag (default 50%)

    Returns:
        List of anomalous transactions with anomaly info
    """
    # Get all transactions for category
    category_txns = []
    for txn in transactions:
        amount = float(txn.get("amount", 0))
        if amount >= 0:  # Skip income
            continue

        category = txn.get("category") or {}
        if category.get("title") == category_name:
            category_txns.append(txn)

    if not category_txns:
        return []

    # Calculate average
    amounts = [abs(float(t.get("amount", 0))) for t in category_txns]
    average = sum(amounts) / len(amounts)

    # Protect against division by zero
    if average == 0:
        return []

    threshold = average * (1 + threshold_percent / 100.0)

    # Find anomalies
    anomalies = []
    for txn in category_txns:
        amount_abs = abs(float(txn.get("amount", 0)))
        if amount_abs > threshold:
            percent_above = ((amount_abs - average) / average) * 100.0
            anomalies.append(
                {
                    "transaction": txn,
                    "amount": amount_abs,
                    "average": round(average, 2),
                    "percent_above_average": round(percent_above, 2),
                }
            )

    return anomalies
