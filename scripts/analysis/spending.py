"""Spending analysis functions."""

from typing import List, Dict, Any


def analyze_spending_by_category(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze spending by category.

    Args:
        transactions: List of transaction dicts with category info

    Returns:
        List of category summaries sorted by total spent (highest first)
    """
    # Group by category
    categories = {}

    for txn in transactions:
        # Skip income (positive amounts)
        amount = float(txn.get("amount", "0"))
        if amount >= 0:
            continue

        category = txn.get("category", {})
        category_id = category.get("id")
        category_name = category.get("title", "Uncategorized")

        if category_id not in categories:
            categories[category_id] = {
                "category_id": category_id,
                "category_name": category_name,
                "total_spent": 0.0,
                "transaction_count": 0,
            }

        # Add to total (convert negative to positive for spending)
        categories[category_id]["total_spent"] += abs(amount)
        categories[category_id]["transaction_count"] += 1

    # Convert to list and sort by total spent (descending)
    result = list(categories.values())
    result.sort(key=lambda x: x["total_spent"], reverse=True)

    return result


def analyze_spending_by_merchant(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze spending by merchant/payee.

    Args:
        transactions: List of transaction dicts

    Returns:
        List of merchant summaries sorted by total spent (highest first)
    """
    merchants = {}

    for txn in transactions:
        # Skip income
        amount = float(txn.get("amount", "0"))
        if amount >= 0:
            continue

        payee = txn.get("payee", "Unknown")

        if payee not in merchants:
            merchants[payee] = {
                "merchant": payee,
                "total_spent": 0.0,
                "transaction_count": 0,
            }

        merchants[payee]["total_spent"] += abs(amount)
        merchants[payee]["transaction_count"] += 1

    result = list(merchants.values())
    result.sort(key=lambda x: x["total_spent"], reverse=True)

    return result


def filter_transactions_by_period(
    transactions: List[Dict[str, Any]], period: str
) -> List[Dict[str, Any]]:
    """Filter transactions by time period.

    Args:
        transactions: List of transaction dicts
        period: Period string (YYYY or YYYY-MM)

    Returns:
        Filtered list of transactions
    """
    filtered = []

    for txn in transactions:
        date_str = txn.get("date", "")
        if not date_str:
            continue

        # Extract date prefix for comparison
        if len(period) == 4:  # Year: "2025"
            if date_str.startswith(period):
                filtered.append(txn)
        elif len(period) == 7:  # Month: "2025-11"
            if date_str.startswith(period):
                filtered.append(txn)

    return filtered


def get_period_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get summary statistics for a period.

    Args:
        transactions: List of transaction dicts

    Returns:
        Dict with total_income, total_expenses, net_income, transaction_count
    """
    total_income = 0.0
    total_expenses = 0.0

    for txn in transactions:
        amount = float(txn.get("amount", "0"))

        if amount > 0:
            total_income += amount
        else:
            total_expenses += abs(amount)

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_income": total_income - total_expenses,
        "transaction_count": len(transactions),
    }
