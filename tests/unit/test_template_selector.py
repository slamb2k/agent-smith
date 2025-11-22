"""Tests for template selector."""

import pytest
import shutil
from pathlib import Path
from scripts.setup.template_selector import TemplateSelector


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


def test_list_templates(template_selector):
    """Test listing available templates."""
    templates = template_selector.list_templates()

    assert isinstance(templates, dict)
    assert "simple" in templates
    assert "separated-families" in templates
    assert "shared-household" in templates
    assert "advanced" in templates

    # Check template metadata structure
    for template_key, template_info in templates.items():
        assert "name" in template_info
        assert "description" in template_info
        assert "best_for" in template_info


def test_list_templates_metadata_content():
    """Test that template metadata contains expected information."""
    selector = TemplateSelector()
    templates = selector.list_templates()

    # Verify Simple template
    simple = templates["simple"]
    assert "Single Person" in simple["name"]
    assert "individual" in simple["description"].lower()

    # Verify Separated Families template
    sep_families = templates["separated-families"]
    assert "Separated" in sep_families["name"]
    assert (
        "child support" in sep_families["description"].lower()
        or "kids" in sep_families["description"].lower()
    )

    # Verify Shared Household template
    shared = templates["shared-household"]
    assert "Shared" in shared["name"]
    assert "shared" in shared["description"].lower() or "couples" in shared["best_for"].lower()

    # Verify Advanced template
    advanced = templates["advanced"]
    assert "Advanced" in advanced["name"]
    assert (
        "tax" in advanced["description"].lower() or "investment" in advanced["description"].lower()
    )


def test_apply_template_file_not_found(template_selector):
    """Test applying non-existent template raises error."""
    with pytest.raises(FileNotFoundError):
        template_selector.apply_template("nonexistent")


def test_apply_template_without_backup(template_selector, temp_templates_dir, temp_rules_file):
    """Test applying template without backup."""
    # Create test template
    test_template = temp_templates_dir / "test.yaml"
    test_template.write_text("test content")

    # Apply template
    template_selector.apply_template("test", backup=False)

    # Verify template was copied
    assert temp_rules_file.exists()
    assert temp_rules_file.read_text() == "test content"

    # Verify no backup was created
    backup_file = temp_rules_file.with_suffix(".yaml.backup")
    assert not backup_file.exists()


def test_apply_template_with_backup(template_selector, temp_templates_dir, temp_rules_file):
    """Test applying template with backup of existing rules."""
    # Create existing rules file
    temp_rules_file.write_text("existing rules")

    # Create test template
    test_template = temp_templates_dir / "test.yaml"
    test_template.write_text("new template content")

    # Apply template with backup
    template_selector.apply_template("test", backup=True)

    # Verify template was copied
    assert temp_rules_file.exists()
    assert temp_rules_file.read_text() == "new template content"

    # Verify backup was created
    backup_file = temp_rules_file.with_suffix(".yaml.backup")
    assert backup_file.exists()
    assert backup_file.read_text() == "existing rules"


def test_apply_template_no_existing_rules(template_selector, temp_templates_dir, temp_rules_file):
    """Test applying template when no rules.yaml exists."""
    # Create test template
    test_template = temp_templates_dir / "test.yaml"
    test_template.write_text("template content")

    # Apply template (backup=True should not fail even with no existing file)
    template_selector.apply_template("test", backup=True)

    # Verify template was copied
    assert temp_rules_file.exists()
    assert temp_rules_file.read_text() == "template content"

    # Verify no backup was created (no existing file to backup)
    backup_file = temp_rules_file.with_suffix(".yaml.backup")
    assert not backup_file.exists()


def test_template_selector_initialization():
    """Test TemplateSelector initializes with correct paths."""
    selector = TemplateSelector()

    # Verify paths are set correctly
    assert selector.templates_dir.name == "templates"
    assert selector.rules_file.name == "rules.yaml"
    assert "data" in str(selector.templates_dir)
    assert "data" in str(selector.rules_file)


def test_template_files_exist():
    """Test that all required template files exist."""
    selector = TemplateSelector()

    # Check all template files exist
    templates = ["simple", "separated-families", "shared-household", "advanced"]
    for template in templates:
        template_file = selector.templates_dir / f"{template}.yaml"
        assert template_file.exists(), f"Template file {template}.yaml not found"


def test_template_files_valid_yaml():
    """Test that all template files contain valid YAML with expected structure."""
    import yaml

    selector = TemplateSelector()
    templates = ["simple", "separated-families", "shared-household", "advanced"]

    for template in templates:
        template_file = selector.templates_dir / f"{template}.yaml"

        # Load and validate YAML
        with open(template_file, "r") as f:
            data = yaml.safe_load(f)

        # Verify structure
        assert "metadata" in data, f"{template}.yaml missing metadata"
        assert "rules" in data, f"{template}.yaml missing rules"

        # Verify metadata fields
        metadata = data["metadata"]
        assert "template_name" in metadata, f"{template}.yaml metadata missing template_name"
        assert "description" in metadata, f"{template}.yaml metadata missing description"
        assert "target_users" in metadata, f"{template}.yaml metadata missing target_users"

        # Verify rules is a list
        assert isinstance(data["rules"], list), f"{template}.yaml rules should be a list"

        # Verify at least some rules exist
        assert len(data["rules"]) > 0, f"{template}.yaml has no rules"

        # Verify rule structure
        for rule in data["rules"]:
            assert "type" in rule, f"{template}.yaml rule missing type"
            assert rule["type"] in ["category", "label"], f"{template}.yaml invalid rule type"
            assert "name" in rule, f"{template}.yaml rule missing name"
