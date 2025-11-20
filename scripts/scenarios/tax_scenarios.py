"""Tax scenario planning for optimization."""

from typing import Dict, Any
from datetime import datetime, date


def model_prepayment_scenario(
    expense_amount: float,
    current_fy_income: float,
    next_fy_projected_income: float,
) -> Dict[str, Any]:
    """Model tax impact of prepaying deductible expenses.

    Args:
        expense_amount: Amount to prepay
        current_fy_income: Current financial year income
        next_fy_projected_income: Next FY projected income

    Returns:
        Dict with tax savings comparison and recommendation
    """

    # Tax brackets (2025 Australian tax rates)
    def get_tax_rate(income: float) -> float:
        if income <= 18200:
            return 0.0
        elif income <= 45000:
            return 0.19
        elif income <= 120000:
            return 0.325
        elif income <= 180000:
            return 0.37
        else:
            return 0.45

    current_rate = get_tax_rate(current_fy_income)
    next_rate = get_tax_rate(next_fy_projected_income)

    tax_saving_current = expense_amount * current_rate
    tax_saving_next = expense_amount * next_rate
    difference = tax_saving_current - tax_saving_next

    # Recommendation
    if difference > 100:
        recommendation = "prepay_now"
        reason = f"Save ${difference:.2f} by claiming in current FY (higher tax bracket)"
    elif difference < -100:
        recommendation = "defer"
        reason = (
            f"Save ${abs(difference):.2f} by claiming in next FY (higher projected tax bracket)"
        )
    else:
        recommendation = "neutral"
        reason = "Minimal tax difference between financial years"

    return {
        "expense_amount": expense_amount,
        "current_fy_income": current_fy_income,
        "next_fy_income": next_fy_projected_income,
        "current_fy_tax_rate": current_rate,
        "next_fy_tax_rate": next_rate,
        "tax_saving_current_fy": round(tax_saving_current, 2),
        "tax_saving_next_fy": round(tax_saving_next, 2),
        "difference": round(difference, 2),
        "recommendation": recommendation,
        "reason": reason,
    }


def analyze_cgt_timing(
    purchase_price: float,
    current_value: float,
    purchase_date: str,
    sale_date_option1: str,
    sale_date_option2: str,
    marginal_tax_rate: float,
) -> Dict[str, Any]:
    """Analyze CGT impact of different sale timing options.

    Args:
        purchase_price: Original purchase price
        current_value: Current market value
        purchase_date: Purchase date (YYYY-MM-DD)
        sale_date_option1: First sale timing option (YYYY-MM-DD)
        sale_date_option2: Second sale timing option (YYYY-MM-DD)
        marginal_tax_rate: Marginal tax rate (e.g., 0.37)

    Returns:
        Dict comparing CGT outcomes for both timing options
    """
    purchase = datetime.strptime(purchase_date, "%Y-%m-%d").date()
    option1 = datetime.strptime(sale_date_option1, "%Y-%m-%d").date()
    option2 = datetime.strptime(sale_date_option2, "%Y-%m-%d").date()

    capital_gain = current_value - purchase_price

    def calculate_cgt(sale_date: date) -> tuple:
        holding_days = (sale_date - purchase).days
        eligible_for_discount = holding_days > 365

        if eligible_for_discount:
            taxable_gain = capital_gain * 0.5  # 50% CGT discount
        else:
            taxable_gain = capital_gain

        cgt_payable = taxable_gain * marginal_tax_rate
        return holding_days, eligible_for_discount, taxable_gain, cgt_payable

    days1, discount1, taxable1, cgt1 = calculate_cgt(option1)
    days2, discount2, taxable2, cgt2 = calculate_cgt(option2)

    savings = cgt1 - cgt2

    if savings > 0:
        recommendation = "option2"
        reason = f"Option 2 saves ${savings:.2f} in CGT"
    elif savings < 0:
        recommendation = "option1"
        reason = f"Option 1 saves ${abs(savings):.2f} in CGT"
    else:
        recommendation = "neutral"
        reason = "No CGT difference between options"

    return {
        "purchase_price": purchase_price,
        "current_value": current_value,
        "capital_gain": round(capital_gain, 2),
        "option1": {
            "sale_date": sale_date_option1,
            "holding_days": days1,
            "cgt_discount_eligible": discount1,
            "taxable_gain": round(taxable1, 2),
            "cgt_payable": round(cgt1, 2),
        },
        "option2": {
            "sale_date": sale_date_option2,
            "holding_days": days2,
            "cgt_discount_eligible": discount2,
            "taxable_gain": round(taxable2, 2),
            "cgt_payable": round(cgt2, 2),
        },
        "cgt_savings": round(abs(savings), 2),
        "recommendation": recommendation,
        "reason": reason,
    }


def calculate_salary_sacrifice_benefit(
    gross_income: float,
    sacrifice_amount: float,
    super_tax_rate: float = 0.15,
) -> Dict[str, Any]:
    """Calculate net benefit of salary sacrificing to superannuation.

    Args:
        gross_income: Annual gross income
        sacrifice_amount: Amount to salary sacrifice
        super_tax_rate: Super contributions tax rate (default 15%)

    Returns:
        Dict with tax comparison and tax arbitrage benefit
    """

    # Tax brackets (Australian 2025)
    def calculate_income_tax(income: float) -> float:
        if income <= 18200:
            return 0
        elif income <= 45000:
            return (income - 18200) * 0.19
        elif income <= 120000:
            return 5092 + (income - 45000) * 0.325
        elif income <= 180000:
            return 29467 + (income - 120000) * 0.37
        else:
            return 51667 + (income - 180000) * 0.45

    # Without salary sacrifice
    tax_without = calculate_income_tax(gross_income)
    net_without = gross_income - tax_without

    # With salary sacrifice
    reduced_income = gross_income - sacrifice_amount
    tax_with = calculate_income_tax(reduced_income)
    super_tax = sacrifice_amount * super_tax_rate
    net_with = reduced_income - tax_with + (sacrifice_amount - super_tax)

    # Tax arbitrage: difference between income tax saved and super tax paid
    # Note: This represents tax savings, not additional take-home pay since
    # the sacrificed amount goes into super (locked until preservation age)
    tax_arbitrage_benefit = net_with - net_without

    return {
        "gross_income": gross_income,
        "sacrifice_amount": sacrifice_amount,
        "without_sacrifice": {
            "taxable_income": gross_income,
            "income_tax": round(tax_without, 2),
            "net_income": round(net_without, 2),
        },
        "with_sacrifice": {
            "taxable_income": reduced_income,
            "income_tax": round(tax_with, 2),
            "super_tax": round(super_tax, 2),
            "tax_arbitrage_benefit": round(tax_arbitrage_benefit, 2),
        },
        "total_tax_saving": round(abs(tax_arbitrage_benefit), 2),
        "worthwhile": tax_arbitrage_benefit > 0,
    }
