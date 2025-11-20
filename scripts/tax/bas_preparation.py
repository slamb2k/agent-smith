"""BAS (Business Activity Statement) preparation for Level 3 tax intelligence.

This module generates BAS worksheets with GST calculations for quarterly reporting.

IMPORTANT SCOPE:
- This tool covers GST reporting ONLY (G1, G10, G11, 1A, 1B, 1C labels)
- Assumes cash method of accounting (records when payment received/made)
- Does NOT cover PAYG withholding (W1, W2), PAYG instalments, FBT, or fuel tax credits
- Other BAS labels must be completed separately via ATO systems

Key BAS Fields:
- G1: Total sales (GST-inclusive)
- G10: Capital purchases >= $1000 GST-exclusive (equipment, assets)
- G11: Non-capital purchases < $1000 GST-exclusive (consumables, services)
- 1A: GST on sales (1/11 of GST-inclusive sales)
- 1B: GST on purchases (1/11 of GST-inclusive purchases)
- 1C: Net GST (1A - 1B) - positive means you owe, negative means refund

GST Calculations:
- GST in Australia is 10% of base price, or 1/11 of GST-inclusive price
- Formula: GST = GST-inclusive amount / 11

Capital vs Non-Capital:
- Capital: Assets >= $1000 (GST-exclusive) that provide lasting benefit
  Examples: computers, furniture, machinery, vehicles
- Non-Capital: Consumables and services < $1000
  Examples: office supplies, utilities, repairs, professional fees

GST-Free Categories (excluded from BAS):
- Wages and salaries
- Health insurance, life insurance
- Workers compensation insurance
- Residential rent
- Superannuation contributions
- Loan repayments (principal)

Input-Taxed Categories (excluded from BAS):
- Bank fees and charges
- Interest income/expense
- Financial services charges
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# GST-free categories (no GST applicable)
GST_FREE_CATEGORIES = {
    "Wages & Salaries",
    "Salaries",
    "Payroll",
    "Employee Wages",
    "Health Insurance",
    "Life Insurance",
    "Workers Compensation",
    "Workers Comp",
    "Residential Rent",
    "Rent - Residential",
    "Superannuation",
    "Super Contributions",
    "Loan Repayment",
    "Loan Principal",
    "Mortgage Repayment",
    "Transfer",
    "Transfers",
}

# Input-taxed categories (financial services - no GST applicable)
INPUT_TAXED_CATEGORIES = {
    "Bank Fees",
    "Bank Charges",
    "Interest",
    "Interest Income",
    "Interest Expense",
    "Loan Interest",
    "Mortgage Interest",
    "Financial Services",
}

# Capital asset categories (typically > $1000)
CAPITAL_ASSET_CATEGORIES = {
    "Office Equipment",
    "Computer Equipment",
    "Furniture & Fittings",
    "Furniture",
    "Machinery",
    "Tools & Equipment",
    "Vehicles",
    "Vehicle Purchase",
    "Property",
    "Buildings",
    "Plant & Equipment",
}

# Capital threshold (GST-exclusive)
CAPITAL_THRESHOLD = 1000.0


def is_gst_free(category_name: str) -> bool:
    """Check if a category is GST-free or input-taxed.

    Args:
        category_name: Category title

    Returns:
        True if category is GST-free or input-taxed (excluded from BAS)
    """
    return category_name in GST_FREE_CATEGORIES or category_name in INPUT_TAXED_CATEGORIES


def is_capital_purchase(category_name: str, gst_exclusive_amount: float) -> bool:
    """Determine if a purchase is capital or non-capital.

    Capital purchases are assets >= $1000 (GST-exclusive) that provide
    lasting benefit to the business.

    Args:
        category_name: Category title
        gst_exclusive_amount: Amount excluding GST

    Returns:
        True if capital purchase, False if non-capital
    """
    # Known capital asset categories - always check threshold
    if category_name in CAPITAL_ASSET_CATEGORIES:
        return gst_exclusive_amount >= CAPITAL_THRESHOLD

    # Not a typical capital category
    # Conservative approach: only classify as capital if amount is significantly
    # above threshold to avoid incorrect G10 classification
    return gst_exclusive_amount >= (CAPITAL_THRESHOLD * 1.5)


def calculate_gst_exclusive_amount(gst_inclusive_amount: float) -> float:
    """Calculate GST-exclusive amount from GST-inclusive amount.

    GST = 10% of base price
    GST-inclusive = base price + 10% = base price * 1.1
    Therefore: base price = GST-inclusive / 1.1

    Args:
        gst_inclusive_amount: GST-inclusive amount

    Returns:
        GST-exclusive amount (base price)
    """
    return gst_inclusive_amount / 1.1


def calculate_gst_amount(gst_inclusive_amount: float) -> float:
    """Calculate GST from GST-inclusive amount.

    GST in Australia is 1/11 of GST-inclusive price.

    Args:
        gst_inclusive_amount: GST-inclusive amount

    Returns:
        GST component
    """
    return gst_inclusive_amount / 11.0


def generate_bas_worksheet(
    transactions: List[Dict[str, Any]],
    start_date: str,
    end_date: str,
) -> Dict[str, Any]:
    """Generate BAS worksheet for a reporting period.

    SCOPE: This function covers GST reporting only (G1, G10, G11, 1A, 1B, 1C).
    It assumes cash method of accounting. Other BAS labels (W1, W2, PAYG instalments,
    FBT, fuel tax credits) must be completed separately.

    Args:
        transactions: List of transaction dicts
        start_date: Period start date (YYYY-MM-DD)
        end_date: Period end date (YYYY-MM-DD, inclusive)

    Returns:
        Dict with BAS fields:
            - period: {start_date, end_date}
            - G1_total_sales: Total GST-inclusive sales
            - G10_capital_purchases: Total capital purchases (GST-inclusive)
            - G11_non_capital_purchases: Total non-capital purchases (GST-inclusive)
            - 1A_gst_on_sales: GST collected on sales (1/11 of G1)
            - 1B_gst_on_purchases: GST paid on purchases (1/11 of G10+G11)
            - 1C_net_gst: Net GST position (1A - 1B)
            - summary: Transaction counts and statistics
            - disclaimer: Level 3 tax advice disclaimer
    """
    # Initialize BAS totals
    g1_total_sales = 0.0
    g10_capital_purchases = 0.0
    g11_non_capital_purchases = 0.0

    # Track counts for summary
    total_transactions = 0
    sales_count = 0
    purchase_count = 0
    capital_purchase_count = 0
    non_capital_purchase_count = 0

    # Process transactions
    for txn in transactions:
        # Filter by date range (inclusive of end date)
        txn_date = txn.get("date", "")
        if txn_date < start_date or txn_date > end_date:
            continue

        # Skip transfers
        if txn.get("is_transfer", False):
            continue

        # Get transaction details
        amount = float(txn.get("amount", 0))
        category = txn.get("category") or {}
        category_name = category.get("title", "Uncategorized")

        # Skip GST-free categories
        if is_gst_free(category_name):
            continue

        # Process sales (positive amounts)
        if amount > 0:
            g1_total_sales += amount
            sales_count += 1
            total_transactions += 1
            continue

        # Process purchases (negative amounts)
        if amount < 0:
            amount_abs = abs(amount)

            # Calculate GST-exclusive amount for capital classification
            gst_exclusive = calculate_gst_exclusive_amount(amount_abs)

            # Classify as capital or non-capital
            if is_capital_purchase(category_name, gst_exclusive):
                g10_capital_purchases += amount_abs
                capital_purchase_count += 1
            else:
                g11_non_capital_purchases += amount_abs
                non_capital_purchase_count += 1

            purchase_count += 1
            total_transactions += 1

    # Calculate GST amounts
    # 1A: GST on sales (1/11 of GST-inclusive sales)
    gst_on_sales = calculate_gst_amount(g1_total_sales)

    # 1B: GST on purchases (1/11 of GST-inclusive purchases)
    total_purchases = g10_capital_purchases + g11_non_capital_purchases
    gst_on_purchases = calculate_gst_amount(total_purchases)

    # 1C: Net GST (GST on sales minus GST on purchases)
    # Positive = you owe GST to ATO
    # Negative = ATO owes you a refund
    net_gst = gst_on_sales - gst_on_purchases

    # Build result
    result = {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "G1_total_sales": round(g1_total_sales, 2),
        "G10_capital_purchases": round(g10_capital_purchases, 2),
        "G11_non_capital_purchases": round(g11_non_capital_purchases, 2),
        "1A_gst_on_sales": round(gst_on_sales, 2),
        "1B_gst_on_purchases": round(gst_on_purchases, 2),
        "1C_net_gst": round(net_gst, 2),
        "summary": {
            "total_transactions": total_transactions,
            "sales_count": sales_count,
            "purchase_count": purchase_count,
            "capital_purchase_count": capital_purchase_count,
            "non_capital_purchase_count": non_capital_purchase_count,
        },
        "disclaimer": (
            "This BAS worksheet is generated using Level 3 (Full Compliance Suite) "
            "tax intelligence. SCOPE: This covers GST reporting ONLY (G1, G10, G11, "
            "1A, 1B, 1C labels) using cash method of accounting. Other BAS labels "
            "(W1, W2, PAYG withholding, PAYG instalments, FBT, fuel tax credits) "
            "must be completed separately. While this tool provides comprehensive "
            "GST calculations based on ATO guidelines, it is not a substitute for "
            "professional advice. Always consult a registered tax agent before "
            "lodging your BAS to ensure accuracy and compliance with current tax law."
        ),
    }

    logger.info(
        f"Generated BAS worksheet for {start_date} to {end_date}: "
        f"Net GST = ${net_gst:.2f} ({total_transactions} transactions)"
    )

    return result
