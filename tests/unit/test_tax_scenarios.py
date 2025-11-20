"""Tests for tax scenario planning."""

import pytest
from scripts.scenarios.tax_scenarios import (
    model_prepayment_scenario,
    analyze_cgt_timing,
    calculate_salary_sacrifice_benefit,
)


def test_model_prepayment_scenario():
    """Test tax impact of prepaying deductible expenses."""
    result = model_prepayment_scenario(
        expense_amount=12000.00,
        current_fy_income=150000.00,
        next_fy_projected_income=150000.00,
    )

    assert result["expense_amount"] == 12000.00
    assert result["tax_saving_current_fy"] == pytest.approx(4440.00, abs=1)  # 37% of 12k
    assert result["tax_saving_next_fy"] == pytest.approx(4440.00, abs=1)
    assert result["recommendation"] == "neutral"  # Same tax bracket both years


def test_analyze_cgt_timing_with_discount():
    """Test CGT timing analysis with 50% discount eligibility."""
    result = analyze_cgt_timing(
        purchase_price=100000.00,
        current_value=150000.00,
        purchase_date="2024-06-01",
        sale_date_option1="2025-03-01",  # 9 months (no discount)
        sale_date_option2="2025-07-01",  # 13 months (with discount)
        marginal_tax_rate=0.37,
    )

    assert result["capital_gain"] == 50000.00
    assert result["option1"]["cgt_discount_eligible"] is False
    assert result["option1"]["taxable_gain"] == 50000.00
    assert result["option2"]["cgt_discount_eligible"] is True
    assert result["option2"]["taxable_gain"] == 25000.00  # 50% discount
    assert result["cgt_savings"] > 0
    assert result["recommendation"] == "option2"


def test_calculate_salary_sacrifice_benefit():
    """Test salary sacrifice benefit calculation."""
    result = calculate_salary_sacrifice_benefit(
        gross_income=100000.00, sacrifice_amount=10000.00, super_tax_rate=0.15
    )

    assert result["sacrifice_amount"] == 10000.00
    assert result["without_sacrifice"]["taxable_income"] == 100000.00
    assert result["with_sacrifice"]["taxable_income"] == 90000.00
    assert result["with_sacrifice"]["super_tax"] == 1500.00  # 15% of 10k
    assert result["with_sacrifice"]["tax_arbitrage_benefit"] > 0
    assert result["total_tax_saving"] > 0
    assert result["worthwhile"] is True
