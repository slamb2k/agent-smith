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
