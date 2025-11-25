"""Tests for template merging logic."""

import pytest
from pathlib import Path
from scripts.setup.template_merger import TemplateMerger
from scripts.setup.template_schema import TemplateLoader
from tests.utils import get_asset_path


def test_merge_single_template():
    """Test merging a single template."""
    loader = TemplateLoader()
    merger = TemplateMerger()

    template = loader.load_from_file(get_asset_path("templates", "primary", "payg-employee.yaml"))
    result = merger.merge([template])

    assert len(result["categories"]) == 7
    assert len(result["rules"]) == 5
    assert "templates_applied" in result["metadata"]
    assert len(result["metadata"]["templates_applied"]) == 1


def test_merge_multiple_templates():
    """Test merging primary + living templates."""
    loader = TemplateLoader()
    merger = TemplateMerger()

    primary = loader.load_from_file(get_asset_path("templates", "primary", "payg-employee.yaml"))
    living = loader.load_from_file(get_asset_path("templates", "living", "shared-hybrid.yaml"))

    result = merger.merge([primary, living])

    # Should have categories from both
    assert len(result["categories"]) > 7  # More than just primary

    # Should have rules from both
    assert len(result["rules"]) > 5

    # Should track both templates
    assert len(result["metadata"]["templates_applied"]) == 2


def test_merge_deduplicates_categories():
    """Test that duplicate category names are deduplicated."""
    merger = TemplateMerger()

    # Create two templates with overlapping categories
    template1 = {
        "name": "Template 1",
        "layer": "primary",
        "categories": [{"name": "Income", "parent": None, "description": "Income category"}],
        "rules": [],
        "tax_tracking": {},
        "alerts": [],
        "labels": [],
        "metadata": {"priority": 1},
    }

    template2 = {
        "name": "Template 2",
        "layer": "additional",
        "categories": [
            {"name": "Income", "parent": None, "description": "Different income"},
            {"name": "Expenses", "parent": None, "description": "Expenses category"},
        ],
        "rules": [],
        "tax_tracking": {},
        "alerts": [],
        "labels": [],
        "metadata": {"priority": 3},
    }

    result = merger.merge([template1, template2])

    # Should only have 2 categories (Income deduplicated)
    assert len(result["categories"]) == 2
    category_names = [c["name"] for c in result["categories"]]
    assert category_names.count("Income") == 1


def test_merge_respects_priority():
    """Test that templates are merged in priority order."""
    loader = TemplateLoader()
    merger = TemplateMerger()

    primary = loader.load_from_file(get_asset_path("templates", "primary", "payg-employee.yaml"))
    additional = loader.load_from_file(
        get_asset_path("templates", "additional", "share-investor.yaml")
    )

    # Additional template has higher priority number (3 vs 1)
    # But primary should still be first in merged list
    result = merger.merge([primary, additional])

    templates_applied = result["metadata"]["templates_applied"]
    assert templates_applied[0]["name"] == "PAYG Employee"
    assert templates_applied[1]["name"] == "Share/ETF Investor"


def test_merge_deduplicates_labels():
    """Test that duplicate label names are deduplicated."""
    merger = TemplateMerger()

    # Create two templates with overlapping labels
    template1 = {
        "name": "Template 1",
        "layer": "primary",
        "categories": [],
        "rules": [],
        "tax_tracking": {},
        "alerts": [],
        "labels": [
            {
                "name": "Tax Deductible",
                "description": "Expense claimable on tax return",
                "color": "green",
                "auto_apply": False,
            }
        ],
        "metadata": {"priority": 1},
    }

    template2 = {
        "name": "Template 2",
        "layer": "additional",
        "categories": [],
        "rules": [],
        "tax_tracking": {},
        "alerts": [],
        "labels": [
            {
                "name": "Tax Deductible",
                "description": "Tax deductible expense",
                "color": "green",
                "auto_apply": False,
            },
            {
                "name": "GST Applicable",
                "description": "Includes GST component",
                "color": "blue",
                "auto_apply": True,
            },
        ],
        "metadata": {"priority": 3},
    }

    result = merger.merge([template1, template2])

    # Should only have 2 labels (Tax Deductible deduplicated)
    assert len(result["labels"]) == 2
    label_names = [label["name"] for label in result["labels"]]
    assert label_names.count("Tax Deductible") == 1
    assert "GST Applicable" in label_names


def test_merge_preserves_all_unique_labels():
    """Test that all unique labels across templates are preserved."""
    loader = TemplateLoader()
    merger = TemplateMerger()

    primary = loader.load_from_file(get_asset_path("templates", "primary", "payg-employee.yaml"))
    living = loader.load_from_file(get_asset_path("templates", "living", "shared-hybrid.yaml"))

    result = merger.merge([primary, living])

    # Get all unique label names
    label_names = [label["name"] for label in result["labels"]]

    # Should have labels from both templates (deduplicated)
    # PAYG has: Tax Deductible, Requires Receipt, Work Expense
    # Shared-hybrid has: Shared Expense, Contributor: {partner_a_name}, etc.

    # Check for labels from primary template
    assert "Tax Deductible" in label_names
    assert "Requires Receipt" in label_names
    assert "Work Expense" in label_names

    # Check for labels from living template
    assert "Shared Expense" in label_names

    # No duplicates
    assert len(label_names) == len(set(label_names))


def test_merge_tracks_configuration_labels():
    """Test that labels requiring configuration are tracked."""
    loader = TemplateLoader()
    merger = TemplateMerger()

    living = loader.load_from_file(get_asset_path("templates", "living", "shared-hybrid.yaml"))

    result = merger.merge([living])

    # Find labels that require configuration
    config_labels = [label for label in result["labels"] if label.get("requires_configuration")]

    # Shared-hybrid template has 4 labels requiring configuration
    assert len(config_labels) == 4

    # Verify configuration_prompt is preserved
    for label in config_labels:
        assert "configuration_prompt" in label
        assert isinstance(label["configuration_prompt"], str)


def test_merge_normalizes_rule_field_names():
    """Test that merger normalizes YAML field names to applier format."""
    merger = TemplateMerger()

    # Create template with YAML field names ('category' and 'pattern')
    template = {
        "name": "Test Template",
        "layer": "primary",
        "categories": [],
        "rules": [
            {
                "category": "Groceries",
                "pattern": "^WOOLWORTHS",
                "confidence": 95,
                "type": "simple",
            },
            {
                "category": "Transport",
                "pattern": "^UBER",
                "confidence": 90,
                "type": "simple",
            },
        ],
        "tax_tracking": {},
        "alerts": [],
        "labels": [],
        "metadata": {"priority": 1},
    }

    result = merger.merge([template])

    # Verify rules were normalized
    assert len(result["rules"]) == 2

    # Check first rule
    rule1 = result["rules"][0]
    assert "target_category" in rule1
    assert rule1["target_category"] == "Groceries"
    assert "payee_pattern" in rule1
    assert rule1["payee_pattern"] == "^WOOLWORTHS"
    assert "category" not in rule1  # Old field name removed
    assert "pattern" not in rule1  # Old field name removed
    assert rule1["confidence"] == 95  # Other fields preserved
    assert rule1["type"] == "simple"

    # Check second rule
    rule2 = result["rules"][1]
    assert "target_category" in rule2
    assert rule2["target_category"] == "Transport"
    assert "payee_pattern" in rule2
    assert rule2["payee_pattern"] == "^UBER"
    assert "category" not in rule2
    assert "pattern" not in rule2


def test_merge_labels_with_real_templates():
    """Test label merging with actual template files."""
    loader = TemplateLoader()
    merger = TemplateMerger()

    # Load templates from all three layers
    primary = loader.load_from_file(get_asset_path("templates", "primary", "sole-trader.yaml"))
    living = loader.load_from_file(get_asset_path("templates", "living", "shared-hybrid.yaml"))
    additional = loader.load_from_file(
        get_asset_path("templates", "additional", "property-investor.yaml")
    )

    result = merger.merge([primary, living, additional])

    # Should have labels from all templates (deduplicated)
    label_names = [label["name"] for label in result["labels"]]

    # No duplicate labels
    assert len(label_names) == len(set(label_names))

    # Should have labels from each template
    assert len(result["labels"]) > 0

    # All labels should have required fields
    for label in result["labels"]:
        assert "name" in label
        assert "description" in label
        assert "color" in label
