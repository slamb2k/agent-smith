"""Tests for template YAML schema validation."""

import pytest
from pathlib import Path
from scripts.setup.template_schema import TemplateLoader, TemplateValidationError


def test_load_valid_template():
    """Test loading a valid template YAML file."""
    loader = TemplateLoader()

    # Create minimal valid template
    template_yaml = """
name: Test Template
layer: primary
description: Test description

categories:
  - name: Test Category
    parent: null
    description: Test category

rules:
  - id: test-rule
    pattern: "test.*pattern"
    category: "Test Category"
    confidence: high
    description: "Test rule"

tax_tracking:
  bas_enabled: false

alerts: []

labels:
  - name: Test Label
    description: Test label description
    color: green

dependencies:
  requires: []
  conflicts_with: []

metadata:
  created: "2025-11-22"
  version: "1.0.0"
  priority: 1
"""

    template = loader.load_from_string(template_yaml)
    assert template["name"] == "Test Template"
    assert template["layer"] == "primary"
    assert len(template["categories"]) == 1
    assert len(template["rules"]) == 1
    assert len(template["labels"]) == 1


def test_load_template_missing_required_field():
    """Test that loading template without required fields fails."""
    loader = TemplateLoader()

    # Missing 'name' field
    invalid_yaml = """
layer: primary
description: Test
"""

    with pytest.raises(TemplateValidationError, match="Missing required field: name"):
        loader.load_from_string(invalid_yaml)


def test_load_template_invalid_layer():
    """Test that invalid layer value is rejected."""
    loader = TemplateLoader()

    invalid_yaml = """
name: Test
layer: invalid_layer
description: Test

categories: []
rules: []
tax_tracking: {}
alerts: []
labels: []

dependencies:
  requires: []
  conflicts_with: []

metadata:
  created: "2025-11-22"
  version: "1.0.0"
  priority: 1
"""

    with pytest.raises(TemplateValidationError, match="Invalid layer"):
        loader.load_from_string(invalid_yaml)


def test_load_template_from_file():
    """Test loading template from file path."""
    loader = TemplateLoader()

    # Test that existing template file loads successfully
    template = loader.load_from_file(Path("templates/primary/payg-employee.yaml"))
    assert template["name"] == "PAYG Employee"
    assert template["layer"] == "primary"

    # Test that non-existent file raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        loader.load_from_file(Path("templates/primary/non-existent-template.yaml"))


def test_label_validation_valid():
    """Test that valid label structure passes validation."""
    loader = TemplateLoader()

    template_yaml = """
name: Test Template
layer: primary
description: Test

categories: []
rules: []
tax_tracking: {}
alerts: []

labels:
  - name: Tax Deductible
    description: Expense claimable on tax return
    color: green
  - name: GST Applicable
    description: Includes GST component
    color: blue
    auto_apply: true

dependencies:
  requires: []
  conflicts_with: []

metadata:
  created: "2025-11-22"
  version: "1.0.0"
  priority: 1
"""

    template = loader.load_from_string(template_yaml)
    assert len(template["labels"]) == 2
    assert template["labels"][0]["name"] == "Tax Deductible"
    assert template["labels"][1]["auto_apply"] is True


def test_label_validation_missing_required_field():
    """Test that labels missing required fields fail validation."""
    loader = TemplateLoader()

    # Missing 'description' field in label
    invalid_yaml = """
name: Test
layer: primary
description: Test

categories: []
rules: []
tax_tracking: {}
alerts: []

labels:
  - name: Test Label
    color: green

dependencies:
  requires: []
  conflicts_with: []

metadata:
  created: "2025-11-22"
  version: "1.0.0"
  priority: 1
"""

    with pytest.raises(TemplateValidationError, match="Label missing required field"):
        loader.load_from_string(invalid_yaml)


def test_label_validation_with_optional_fields():
    """Test that labels with optional fields validate correctly."""
    loader = TemplateLoader()

    template_yaml = """
name: Test
layer: primary
description: Test

categories: []
rules: []
tax_tracking: {}
alerts: []

labels:
  - name: Contributor
    description: Paid by contributor
    color: orange
    auto_apply: false
    requires_configuration: true
    configuration_prompt: "Enter contributor name:"

dependencies:
  requires: []
  conflicts_with: []

metadata:
  created: "2025-11-22"
  version: "1.0.0"
  priority: 1
"""

    template = loader.load_from_string(template_yaml)
    label = template["labels"][0]
    assert label["auto_apply"] is False
    assert label["requires_configuration"] is True
    assert label["configuration_prompt"] == "Enter contributor name:"


def test_load_payg_employee_template():
    """Test loading the actual PAYG employee template."""
    loader = TemplateLoader()

    template_path = Path("templates/primary/payg-employee.yaml")
    template = loader.load_from_file(template_path)

    # Verify structure
    assert template["name"] == "PAYG Employee"
    assert template["layer"] == "primary"
    assert len(template["categories"]) == 7
    assert len(template["rules"]) == 5
    assert len(template["alerts"]) == 2

    # Verify labels section exists and has correct structure
    assert "labels" in template
    assert len(template["labels"]) == 3
    label_names = [label["name"] for label in template["labels"]]
    assert "Tax Deductible" in label_names
    assert "Requires Receipt" in label_names
    assert "Work Expense" in label_names

    # Verify Work Expense label is auto-apply
    work_expense_label = next(
        label for label in template["labels"] if label["name"] == "Work Expense"
    )
    assert work_expense_label["auto_apply"] is True

    # Verify rules have labels
    uniform_rule = next(rule for rule in template["rules"] if rule["id"] == "uniform-expense")
    assert "labels" in uniform_rule
    assert "Tax Deductible" in uniform_rule["labels"]
    assert "Work Expense" in uniform_rule["labels"]

    work_tools_rule = next(rule for rule in template["rules"] if rule["id"] == "work-tools")
    assert "labels" in work_tools_rule
    assert "Tax Deductible" in work_tools_rule["labels"]
    assert "Requires Receipt" in work_tools_rule["labels"]
    assert "Work Expense" in work_tools_rule["labels"]

    work_vehicle_rule = next(rule for rule in template["rules"] if rule["id"] == "work-vehicle")
    assert "labels" in work_vehicle_rule
    assert "Tax Deductible" in work_vehicle_rule["labels"]
    assert "Requires Receipt" in work_vehicle_rule["labels"]
    assert "Work Expense" in work_vehicle_rule["labels"]

    # Verify tax tracking config
    assert template["tax_tracking"]["bas_enabled"] is False
    assert template["tax_tracking"]["work_expense_threshold"] == 300

    # Verify conflicts
    assert "sole-trader" in template["dependencies"]["conflicts_with"]


def test_load_sole_trader_template():
    """Test loading the sole trader template."""
    loader = TemplateLoader()

    template_path = Path("templates/primary/sole-trader.yaml")
    template = loader.load_from_file(template_path)

    # Verify structure
    assert template["name"] == "Sole Trader / Contractor"
    assert template["layer"] == "primary"
    assert len(template["categories"]) == 9
    assert len(template["rules"]) == 5
    assert len(template["alerts"]) == 3

    # Verify labels section
    assert "labels" in template
    assert len(template["labels"]) == 5
    label_names = [label["name"] for label in template["labels"]]
    assert "Tax Deductible" in label_names
    assert "GST Applicable" in label_names
    assert "Business Use" in label_names
    assert "Home Office" in label_names
    assert "Input Tax Credit" in label_names

    # Verify GST Applicable is auto-apply
    gst_label = next(label for label in template["labels"] if label["name"] == "GST Applicable")
    assert gst_label["auto_apply"] is True

    # Verify Business Use is auto-apply
    business_label = next(label for label in template["labels"] if label["name"] == "Business Use")
    assert business_label["auto_apply"] is True

    # Verify rules have appropriate labels
    abn_payment_rule = next(
        rule for rule in template["rules"] if rule["id"] == "abn-payment-detection"
    )
    assert "labels" in abn_payment_rule
    assert "Business Use" in abn_payment_rule["labels"]
    assert "GST Applicable" in abn_payment_rule["labels"]

    home_office_rule = next(
        rule for rule in template["rules"] if rule["id"] == "home-office-percentage"
    )
    assert "labels" in home_office_rule
    assert "Tax Deductible" in home_office_rule["labels"]
    assert "Business Use" in home_office_rule["labels"]
    assert "Home Office" in home_office_rule["labels"]

    office_supplies_rule = next(
        rule for rule in template["rules"] if rule["id"] == "office-supplies"
    )
    assert "labels" in office_supplies_rule
    assert "Tax Deductible" in office_supplies_rule["labels"]
    assert "Business Use" in office_supplies_rule["labels"]
    assert "GST Applicable" in office_supplies_rule["labels"]

    professional_dev_rule = next(
        rule for rule in template["rules"] if rule["id"] == "professional-development"
    )
    assert "labels" in professional_dev_rule
    assert "Tax Deductible" in professional_dev_rule["labels"]
    assert "Business Use" in professional_dev_rule["labels"]
    assert "GST Applicable" in professional_dev_rule["labels"]

    marketing_rule = next(rule for rule in template["rules"] if rule["id"] == "marketing-expense")
    assert "labels" in marketing_rule
    assert "Tax Deductible" in marketing_rule["labels"]
    assert "Business Use" in marketing_rule["labels"]
    assert "GST Applicable" in marketing_rule["labels"]

    # Verify BAS tracking
    assert template["tax_tracking"]["bas_enabled"] is True
    assert template["tax_tracking"]["bas_frequency"] == "quarterly"
    assert template["tax_tracking"]["gst_method"] == "cash"
    assert template["tax_tracking"]["instant_asset_threshold"] == 20000

    # Verify conflicts
    assert "payg-employee" in template["dependencies"]["conflicts_with"]
    assert "small-business" in template["dependencies"]["conflicts_with"]


def test_load_single_template():
    """Test loading the single person template."""
    loader = TemplateLoader()
    template = loader.load_from_file(Path("templates/living/single.yaml"))

    assert template["name"] == "Single Person"
    assert template["layer"] == "living"
    assert template["metadata"]["priority"] == 2
    assert len(template["categories"]) == 4
    assert len(template["rules"]) == 3
    assert len(template["labels"]) == 0  # No labels for single person


def test_load_shared_hybrid_template():
    """Test loading the shared hybrid template."""
    loader = TemplateLoader()
    template = loader.load_from_file(Path("templates/living/shared-hybrid.yaml"))

    assert template["name"] == "Shared Household - Hybrid Finances"
    assert template["layer"] == "living"
    assert template["tax_tracking"]["expense_splitting_enabled"] is True
    assert template["tax_tracking"]["default_split_ratio"] == 0.5

    # Verify contributor labels are present
    assert len(template["labels"]) == 5
    label_names = [label["name"] for label in template["labels"]]
    assert "Shared Expense" in label_names
    assert "Contributor: {partner_a_name}" in label_names
    assert "Contributor: {partner_b_name}" in label_names
    assert "Personal: {partner_a_name}" in label_names
    assert "Personal: {partner_b_name}" in label_names

    # Verify contributor labels require configuration
    contributor_a = next(
        label for label in template["labels"] if label["name"] == "Contributor: {partner_a_name}"
    )
    assert contributor_a["requires_configuration"] is True
    assert "Partner A" in contributor_a["configuration_prompt"]
    assert contributor_a["color"] == "orange"

    contributor_b = next(
        label for label in template["labels"] if label["name"] == "Contributor: {partner_b_name}"
    )
    assert contributor_b["requires_configuration"] is True
    assert "Partner B" in contributor_b["configuration_prompt"]
    assert contributor_b["color"] == "cyan"

    # Verify shared-expense-labeling rule (new label-based approach)
    shared_expense_rule = next(
        rule for rule in template["rules"] if rule["id"] == "shared-expense-labeling"
    )
    assert "labels" in shared_expense_rule
    assert "Shared Expense" in shared_expense_rule["labels"]
    assert shared_expense_rule["split_percentage"] == 50


def test_load_separated_parents_template():
    """Test loading the separated parents template."""
    loader = TemplateLoader()
    template = loader.load_from_file(Path("templates/living/separated-parents.yaml"))

    assert template["name"] == "Separated/Divorced Parents"
    assert template["layer"] == "living"
    # New label-based approach uses standard categories, not custom ones
    assert len(template["categories"]) == 0
    assert template["tax_tracking"]["child_support_documentation"] is True
    assert template["tax_tracking"]["custody_expense_tracking"] is True

    # Verify labels including contributor and child labels
    assert len(template["labels"]) >= 6  # At least the core labels
    label_names = [label["name"] for label in template["labels"]]
    assert "Child Support" in label_names
    assert "Custody Period" in label_names
    assert "Shared Child Expense" in label_names
    assert "Contributor: {parent_a_name}" in label_names
    assert "Contributor: {parent_b_name}" in label_names
    # Child name labels are configurable and may vary in the template

    # Verify parent contributor labels
    parent_a = next(
        label for label in template["labels"] if label["name"] == "Contributor: {parent_a_name}"
    )
    assert parent_a["requires_configuration"] is True
    assert "Parent A" in parent_a["configuration_prompt"]
    assert parent_a["color"] == "orange"

    parent_b = next(
        label for label in template["labels"] if label["name"] == "Contributor: {parent_b_name}"
    )
    assert parent_b["requires_configuration"] is True
    assert "Parent B" in parent_b["configuration_prompt"]
    assert parent_b["color"] == "cyan"

    # Verify child labels
    child_1 = next(label for label in template["labels"] if label["name"] == "Kids: {child_1_name}")
    assert child_1["requires_configuration"] is True
    assert "first child" in child_1["configuration_prompt"]
    assert child_1["color"] == "pink"

    child_2 = next(label for label in template["labels"] if label["name"] == "Kids: {child_2_name}")
    assert child_2["requires_configuration"] is True
    assert "second child" in child_2["configuration_prompt"]
    assert child_2["color"] == "lightgreen"

    # Verify rules have labels
    child_support_payment_rule = next(
        rule for rule in template["rules"] if rule["id"] == "child-support-payment"
    )
    assert "labels" in child_support_payment_rule
    assert "Child Support" in child_support_payment_rule["labels"]

    child_support_received_rule = next(
        rule for rule in template["rules"] if rule["id"] == "child-support-received"
    )
    assert "labels" in child_support_received_rule
    assert "Child Support" in child_support_received_rule["labels"]


def test_load_property_investor_template():
    """Test loading the property investor template."""
    loader = TemplateLoader()
    template = loader.load_from_file(Path("templates/additional/property-investor.yaml"))

    # Verify structure
    assert template["name"] == "Property Investor"
    assert template["layer"] == "additional"
    assert template["metadata"]["priority"] == 3
    assert len(template["categories"]) == 7
    assert len(template["rules"]) == 5
    assert len(template["alerts"]) == 3

    # Verify tax tracking
    assert template["tax_tracking"]["negative_gearing_calculation"] is True
    assert template["tax_tracking"]["cgt_cost_base_tracking"] is True
    assert template["tax_tracking"]["cgt_discount_eligible"] is True
    assert template["tax_tracking"]["cgt_discount_holding_period"] == 365
    assert template["tax_tracking"]["depreciation_schedule_tracking"] is True

    # Verify labels section
    assert len(template["labels"]) == 5
    label_names = [label["name"] for label in template["labels"]]
    assert "Tax Deductible" in label_names
    assert "Negative Gearing" in label_names
    assert "Capital Improvement" in label_names
    assert "Repairs vs Improvements" in label_names
    assert "Property: {address}" in label_names

    # Verify property address label requires configuration
    property_label = next(
        label for label in template["labels"] if label["name"] == "Property: {address}"
    )
    assert property_label["requires_configuration"] is True
    assert property_label["configuration_prompt"] == "Enter property address:"
    assert property_label["color"] == "brown"
    assert property_label["auto_apply"] is False

    # Verify rules have appropriate labels
    rental_income_rule = next(rule for rule in template["rules"] if rule["id"] == "rental-income")
    assert "labels" in rental_income_rule
    assert "Property: {address}" in rental_income_rule["labels"]

    property_loan_rule = next(
        rule for rule in template["rules"] if rule["id"] == "property-loan-interest"
    )
    assert "labels" in property_loan_rule
    assert "Tax Deductible" in property_loan_rule["labels"]
    assert "Property: {address}" in property_loan_rule["labels"]

    council_rates_rule = next(rule for rule in template["rules"] if rule["id"] == "council-rates")
    assert "labels" in council_rates_rule
    assert "Tax Deductible" in council_rates_rule["labels"]
    assert "Property: {address}" in council_rates_rule["labels"]

    property_repairs_rule = next(
        rule for rule in template["rules"] if rule["id"] == "property-repairs"
    )
    assert "labels" in property_repairs_rule
    assert "Tax Deductible" in property_repairs_rule["labels"]
    assert "Property: {address}" in property_repairs_rule["labels"]
    assert "Repairs vs Improvements" in property_repairs_rule["labels"]

    property_mgmt_rule = next(
        rule for rule in template["rules"] if rule["id"] == "property-management-fee"
    )
    assert "labels" in property_mgmt_rule
    assert "Tax Deductible" in property_mgmt_rule["labels"]
    assert "Property: {address}" in property_mgmt_rule["labels"]


def test_load_share_investor_template():
    """Test loading the share investor template."""
    loader = TemplateLoader()
    template = loader.load_from_file(Path("templates/additional/share-investor.yaml"))

    # Verify structure
    assert template["name"] == "Share/ETF Investor"
    assert template["layer"] == "additional"
    assert template["metadata"]["priority"] == 3
    assert len(template["categories"]) == 4
    assert len(template["rules"]) == 4
    assert len(template["alerts"]) == 3

    # Verify tax tracking
    assert template["tax_tracking"]["dividend_tracking"] is True
    assert template["tax_tracking"]["franking_credit_extraction"] is True
    assert template["tax_tracking"]["cgt_tracking"] is True
    assert template["tax_tracking"]["cgt_discount_eligible"] is True
    assert template["tax_tracking"]["cgt_discount_holding_period"] == 365
    assert template["tax_tracking"]["wash_sale_detection"] is True
    assert template["tax_tracking"]["wash_sale_period"] == 30

    # Verify labels section
    assert len(template["labels"]) == 4
    label_names = [label["name"] for label in template["labels"]]
    assert "Tax Deductible" in label_names
    assert "Capital Gain" in label_names
    assert "Capital Loss" in label_names
    assert "Franked Dividend" in label_names

    # Verify Capital Gain label is auto-apply
    capital_gain_label = next(
        label for label in template["labels"] if label["name"] == "Capital Gain"
    )
    assert capital_gain_label["auto_apply"] is True
    assert capital_gain_label["color"] == "gold"
    assert capital_gain_label["description"] == "Capital gains event (CGT applicable)"

    # Verify Franked Dividend label is auto-apply
    franked_dividend_label = next(
        label for label in template["labels"] if label["name"] == "Franked Dividend"
    )
    assert franked_dividend_label["auto_apply"] is True
    assert franked_dividend_label["color"] == "teal"

    # Verify rules have appropriate labels
    franked_dividends_rule = next(
        rule for rule in template["rules"] if rule["id"] == "franked-dividends"
    )
    assert "labels" in franked_dividends_rule
    assert "Franked Dividend" in franked_dividends_rule["labels"]

    unfranked_dividends_rule = next(
        rule for rule in template["rules"] if rule["id"] == "unfranked-dividends"
    )
    # Unfranked dividends should not have labels (they're not franked)
    if "labels" in unfranked_dividends_rule:
        assert "Franked Dividend" not in unfranked_dividends_rule["labels"]

    share_sale_rule = next(rule for rule in template["rules"] if rule["id"] == "share-sale")
    assert "labels" in share_sale_rule
    assert "Capital Gain" in share_sale_rule["labels"]

    brokerage_rule = next(rule for rule in template["rules"] if rule["id"] == "brokerage")
    assert "labels" in brokerage_rule
    assert "Tax Deductible" in brokerage_rule["labels"]
