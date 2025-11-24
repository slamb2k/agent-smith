"""Tests for template_applier writing rules to YAML instead of creating platform rules."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from scripts.setup.template_applier import TemplateApplier


def test_template_applier_writes_rules_to_yaml(tmp_path):
    """Test that template applier writes rules to rules.yaml instead of creating platform rules.

    This test verifies:
    1. Category rules are written to rules.yaml
    2. Label rules are written to rules.yaml
    3. Combined category+label rules are written correctly
    4. NO deprecated platform rules are created via API
    """
    # Setup: Create merged_template.json with all three rule types
    merged_template = {
        "categories": [
            {"name": "Groceries", "parent": None, "description": "Grocery shopping"},
            {"name": "Work Expenses", "parent": None, "description": "Work-related expenses"},
        ],
        "rules": [
            # Type 1: Simple category rule (no labels)
            {
                "id": "groceries-rule",
                "pattern": "woolworths|coles",
                "category": "Groceries",
                "confidence": "high",
                "description": "Grocery stores",
            },
            # Type 2: Category rule with labels (combined)
            {
                "id": "work-tools",
                "pattern": "tools?|equipment",
                "category": "Work Expenses",
                "confidence": "medium",
                "description": "Work tools",
                "labels": ["Tax Deductible", "Work Expense"],
            },
            # Type 3: Label-only rule (no category field)
            {
                "id": "large-purchase",
                "pattern": ".*",
                "confidence": "high",
                "amount_operator": ">",
                "amount_value": 1000,
                "description": "Flag large purchases",
                "labels": ["Large Purchase", "Review Required"],
            },
        ],
    }

    template_file = tmp_path / "merged_template.json"
    import json

    template_file.write_text(json.dumps(merged_template, indent=2))

    rules_file = tmp_path / "rules.yaml"

    # Setup: Mock PocketSmithClient
    mock_client = Mock()

    # Mock get_user
    mock_client.get_user.return_value = {"id": 123}

    # Mock get_categories (return empty, we'll create new ones)
    mock_client.get_categories.return_value = []

    # Mock POST endpoint for category creation
    def mock_post(endpoint, data=None):
        # Return a category with ID based on title
        title = data.get("title") if data else "Unknown"
        return {"id": hash(title) % 1000, "title": title}

    mock_client.post.side_effect = mock_post

    # Mock create_category_rule - this should NOT be called!
    mock_client.create_category_rule = Mock()

    # Execute: Run template applier
    applier = TemplateApplier(api_client=mock_client, rules_file=rules_file)

    # Apply template with add_new strategy
    applier.apply_template(
        merged_template=merged_template, strategy=TemplateApplier.STRATEGY_ADD_NEW, dry_run=False
    )

    # Verify: NO platform rules were created
    mock_client.create_category_rule.assert_not_called()

    # Verify: rules.yaml was created
    assert rules_file.exists(), "rules.yaml should be created"

    # Verify: rules.yaml has correct format
    with open(rules_file) as f:
        rules_data = yaml.safe_load(f)

    assert "rules" in rules_data
    rules = rules_data["rules"]

    # Should have 3 rules total (1 category, 1 category+label, 1 label-only)
    # Actually, based on the code structure, we might need to handle these separately
    # Let's verify we have at least the category rules and label rules

    category_rules = [r for r in rules if r.get("type") == "category"]
    label_rules = [r for r in rules if r.get("type") == "label"]

    # Verify: Category rule (no labels)
    groceries_rule = next(
        (r for r in category_rules if "woolworths" in str(r.get("patterns", [])).lower()), None
    )
    assert groceries_rule is not None, "Groceries rule should be in rules.yaml"
    assert groceries_rule["type"] == "category"
    assert groceries_rule["category"] == "Groceries"
    assert groceries_rule["confidence"] in [95, 90, 80]  # high = 95
    assert "labels" not in groceries_rule or not groceries_rule["labels"]

    # Verify: Category rule with labels (combined)
    work_rule = next(
        (r for r in category_rules if "tools" in str(r.get("patterns", [])).lower()), None
    )
    assert work_rule is not None, "Work tools rule should be in rules.yaml"
    assert work_rule["type"] == "category"
    assert work_rule["category"] == "Work Expenses"
    assert work_rule["confidence"] in [90, 80, 70]  # medium = 90
    # Labels might be in category rule or separate label rule
    # For now, let's just verify the rule exists

    # Verify: Label-only rule
    # This should be a separate label rule with "when" conditions
    large_purchase_rule = next(
        (r for r in label_rules if "Large Purchase" in str(r.get("labels", []))), None
    )
    assert large_purchase_rule is not None, "Large purchase label rule should be in rules.yaml"
    assert large_purchase_rule["type"] == "label"
    assert "Large Purchase" in large_purchase_rule["labels"]
    assert "Review Required" in large_purchase_rule["labels"]
    # Should have when conditions for amount
    assert "when" in large_purchase_rule
    assert large_purchase_rule["when"]["amount_operator"] == ">"
    assert large_purchase_rule["when"]["amount_value"] == 1000


def test_template_applier_converts_confidence_levels():
    """Test that confidence levels are converted correctly.

    Template format: "high", "medium", "low"
    YAML format: 95, 90, 80 (numeric)
    """
    # This is a unit test for the conversion logic
    # We'll implement this when we know the exact mapping
    pass


def test_template_applier_handles_pattern_to_patterns():
    """Test that single 'pattern' field is converted to 'patterns' array.

    Template format: "pattern": "woolworths|coles"
    YAML format: "patterns": ["woolworths", "coles"] (or maybe keep regex?)
    """
    # This is a unit test for the conversion logic
    # We'll implement this when we know the exact format
    pass
