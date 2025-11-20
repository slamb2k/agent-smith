"""Tax reporting and summary generation."""

import logging
from typing import Dict, Any, List, Optional
from scripts.tax.ato_categories import ATOCategoryMapper

logger = logging.getLogger(__name__)


def calculate_gst(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate GST paid on business expenses.

    GST in Australia is 10% of the base price, or 1/11 of the GST-inclusive price.

    Args:
        transactions: List of transaction dicts

    Returns:
        Dict with:
        - total_gst_paid: Total GST paid (1/11 of deductible expenses)
        - eligible_for_credit: GST eligible for input tax credits
        - transaction_count: Number of transactions with GST
    """
    mapper = ATOCategoryMapper()

    total_gst = 0.0
    gst_eligible = 0.0
    gst_transaction_count = 0

    for txn in transactions:
        # Skip income
        amount = float(txn.get("amount", "0"))
        if amount >= 0:
            continue

        amount_abs = abs(amount)

        # Check if deductible
        category = txn.get("category", {})
        category_name = category.get("title", "Uncategorized")
        ato_info = mapper.get_ato_category(category_name)

        if ato_info["deductible"]:
            # GST is 1/11 of GST-inclusive amount
            gst_amount = amount_abs / 11.0
            total_gst += gst_amount
            gst_eligible += gst_amount
            gst_transaction_count += 1

    return {
        "total_gst_paid": round(total_gst, 2),
        "eligible_for_credit": round(gst_eligible, 2),
        "transaction_count": gst_transaction_count,
    }


def generate_tax_summary(
    transactions: List[Dict[str, Any]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_gst: bool = False,
) -> Dict[str, Any]:
    """Generate tax summary from transactions.

    Args:
        transactions: List of transaction dicts
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
        include_gst: Whether to include GST calculations

    Returns:
        Dict with tax summary including:
        - total_expenses: Total expense amount
        - deductible_expenses: Total deductible amount
        - non_deductible_expenses: Total non-deductible amount
        - by_ato_category: List of ATO categories with totals
        - transaction_count: Number of transactions processed
        - gst_summary: GST information if include_gst is True
    """
    mapper = ATOCategoryMapper()

    # Filter by date range if provided
    filtered_txns = transactions
    if start_date or end_date:
        filtered_txns = []
        for txn in transactions:
            txn_date = txn.get("date", "")
            if start_date and txn_date < start_date:
                continue
            if end_date and txn_date > end_date:
                continue
            filtered_txns.append(txn)

    # Process transactions
    total_expenses = 0.0
    deductible_expenses = 0.0
    non_deductible_expenses = 0.0
    ato_breakdown: Dict[str, Dict[str, Any]] = {}

    for txn in filtered_txns:
        # Skip income (positive amounts)
        amount = float(txn.get("amount", "0"))
        if amount >= 0:
            continue

        amount_abs = abs(amount)
        total_expenses += amount_abs

        # Get ATO category mapping
        category = txn.get("category", {})
        category_name = category.get("title", "Uncategorized")
        ato_info = mapper.get_ato_category(category_name)

        # Track deductible vs non-deductible
        if ato_info["deductible"]:
            deductible_expenses += amount_abs
        else:
            non_deductible_expenses += amount_abs

        # Build ATO category breakdown
        ato_code = ato_info["ato_code"]
        if ato_code:
            if ato_code not in ato_breakdown:
                ato_breakdown[ato_code] = {
                    "ato_code": ato_code,
                    "ato_category": ato_info["ato_category"],
                    "total": 0.0,
                    "transaction_count": 0,
                    "deductible": ato_info["deductible"],
                }

            ato_breakdown[ato_code]["total"] += amount_abs
            ato_breakdown[ato_code]["transaction_count"] += 1

    # Convert to list and sort by total descending
    ato_categories = list(ato_breakdown.values())
    ato_categories.sort(key=lambda x: x["total"], reverse=True)

    result = {
        "total_expenses": total_expenses,
        "deductible_expenses": deductible_expenses,
        "non_deductible_expenses": non_deductible_expenses,
        "by_ato_category": ato_categories,
        "transaction_count": len([t for t in filtered_txns if float(t.get("amount", "0")) < 0]),
        "date_range": {
            "start": start_date,
            "end": end_date,
        },
    }

    # Add GST calculation if requested
    if include_gst:
        result["gst_summary"] = calculate_gst(filtered_txns)

    return result
