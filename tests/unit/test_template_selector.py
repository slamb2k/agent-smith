"""Tests for template selector."""

import pytest
import shutil
from pathlib import Path
from scripts.setup.template_selector import TemplateSelector
from tests.utils import get_asset_path


@pytest.fixture
def temp_templates_dir(tmp_path):
    """Create temporary templates directory with sample template."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Create a simple test template
    test_template = templates_dir / "test.yaml"
    test_template.write_text(
        """# Test Template
metadata:
  template_name: Test
  description: Test template
  target_users: Test users

rules:
  - type: category
    name: Test Rule
    patterns: [TEST]
    category: Test > Category
    confidence: 95
"""
    )

    return templates_dir


@pytest.fixture
def temp_rules_file(tmp_path):
    """Create temporary rules file path."""
    return tmp_path / "rules.yaml"


@pytest.fixture
def template_selector(temp_templates_dir, temp_rules_file):
    """Create TemplateSelector with temporary paths."""
    selector = TemplateSelector()
    selector.templates_dir = temp_templates_dir
    selector.rules_file = temp_rules_file
    return selector


def test_list_templates():
    """Test listing available templates in layered structure."""
    selector = TemplateSelector()
    templates = selector.list_templates()

    assert isinstance(templates, dict)
    # Should have three layers
    assert "primary" in templates
    assert "living" in templates
    assert "additional" in templates

    # Each layer should be a list
    assert isinstance(templates["primary"], list)
    assert isinstance(templates["living"], list)
    assert isinstance(templates["additional"], list)

    # Primary should have at least payg-employee and sole-trader
    primary_ids = [t["id"] for t in templates["primary"]]
    assert "payg-employee" in primary_ids
    assert "sole-trader" in primary_ids

    # Living should have templates
    living_ids = [t["id"] for t in templates["living"]]
    assert "shared-hybrid" in living_ids
    assert "separated-parents" in living_ids

    # Additional should have templates
    additional_ids = [t["id"] for t in templates["additional"]]
    assert "property-investor" in additional_ids
    assert "share-investor" in additional_ids


def test_list_templates_metadata_content():
    """Test that template metadata contains expected information."""
    selector = TemplateSelector()
    templates = selector.list_templates()

    # Each template should have required metadata
    for layer in ["primary", "living", "additional"]:
        for template in templates[layer]:
            assert "id" in template
            assert "name" in template
            assert "description" in template
            assert "file" in template

    # Verify specific template content
    payg = next(t for t in templates["primary"] if t["id"] == "payg-employee")
    assert "PAYG" in payg["name"] or "Employee" in payg["name"]

    shared_hybrid = next(t for t in templates["living"] if t["id"] == "shared-hybrid")
    assert "Shared" in shared_hybrid["name"]


def test_apply_templates_file_not_found():
    """Test applying non-existent template raises error."""
    selector = TemplateSelector()

    with pytest.raises(FileNotFoundError):
        selector.apply_templates("nonexistent-primary", "shared-hybrid", [])


def test_apply_templates_merges_correctly():
    """Test that apply_templates merges templates correctly."""
    selector = TemplateSelector()

    # Apply primary + living templates
    result = selector.apply_templates("payg-employee", "shared-hybrid", [])

    # Should have merged content
    assert "categories" in result
    assert "rules" in result
    assert "labels" in result
    assert len(result["categories"]) > 0
    assert len(result["rules"]) > 0


def test_apply_templates_with_additional():
    """Test applying templates with additional layer."""
    selector = TemplateSelector()

    # Apply all three layers
    result = selector.apply_templates("payg-employee", "shared-hybrid", ["share-investor"])

    # Should have content from all templates
    assert "categories" in result
    assert len(result["categories"]) > 7  # More than just primary


def test_template_selector_initialization():
    """Test TemplateSelector initializes with correct paths."""
    selector = TemplateSelector()

    # Verify paths are set correctly
    assert selector.templates_dir.name == "templates"
    assert selector.output_file.name == "config.json"  # New composable system uses config.json
    assert "data" in str(selector.output_file)


def test_template_files_exist():
    """Test that required template files exist in layered structure."""
    selector = TemplateSelector()

    # Check primary templates exist
    primary_templates = ["payg-employee", "sole-trader"]
    for template in primary_templates:
        template_file = selector.templates_dir / "primary" / f"{template}.yaml"
        assert template_file.exists(), f"Primary template {template}.yaml not found"

    # Check living templates exist
    living_templates = ["shared-hybrid", "separated-parents"]
    for template in living_templates:
        template_file = selector.templates_dir / "living" / f"{template}.yaml"
        assert template_file.exists(), f"Living template {template}.yaml not found"


def test_template_files_valid_yaml():
    """Test that template files contain valid YAML with expected structure."""
    import yaml

    selector = TemplateSelector()

    # Test one template from each layer
    test_files = [
        selector.templates_dir / "primary" / "payg-employee.yaml",
        selector.templates_dir / "living" / "shared-hybrid.yaml",
        selector.templates_dir / "additional" / "share-investor.yaml",
    ]

    for template_file in test_files:

        # Load and validate YAML
        with open(template_file, "r") as f:
            data = yaml.safe_load(f)

        # Extract template name for error messages
        template = template_file.stem

        # Verify top-level required fields (new composable template schema)
        assert "name" in data, f"{template}.yaml missing name"
        assert "layer" in data, f"{template}.yaml missing layer"
        assert "description" in data, f"{template}.yaml missing description"
        assert "metadata" in data, f"{template}.yaml missing metadata"
        assert "rules" in data, f"{template}.yaml missing rules"
        assert "categories" in data, f"{template}.yaml missing categories"
        assert "labels" in data, f"{template}.yaml missing labels"

        # Verify metadata fields
        metadata = data["metadata"]
        assert "created" in metadata, f"{template}.yaml metadata missing created"
        assert "version" in metadata, f"{template}.yaml metadata missing version"
        assert "priority" in metadata, f"{template}.yaml metadata missing priority"

        # Verify layer is valid
        assert data["layer"] in [
            "primary",
            "living",
            "additional",
        ], f"{template}.yaml invalid layer"

        # Verify rules is a list
        assert isinstance(data["rules"], list), f"{template}.yaml rules should be a list"
