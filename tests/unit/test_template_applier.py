"""Tests for template applier with user choice and backup support."""

import pytest
from unittest.mock import Mock, MagicMock, call
from pathlib import Path
from scripts.setup.template_applier import TemplateApplier


@pytest.fixture
def mock_api_client():
    """Create mock API client."""
    client = Mock()
    client.get_user.return_value = {"id": 217031, "login": "testuser"}
    client.get_categories.return_value = []
    client.get_category_rules.return_value = []
    client.post.return_value = {"id": 1, "title": "New Category"}
    client.create_category_rule.return_value = {"id": 1, "payee_matches": "test"}
    return client


@pytest.fixture
def mock_backup_manager():
    """Create mock backup manager."""
    manager = Mock()
    manager.create_backup.return_value = Path("/tmp/backup/2025-11-22_120000")
    manager.save_backup_data.return_value = None
    return manager


@pytest.fixture
def sample_merged_template():
    """Create sample merged template."""
    return {
        "categories": [
            {"name": "Income", "parent": None, "description": "Income category"},
            {"name": "Expenses", "parent": None, "description": "Expenses category"},
            {"name": "Expenses:Groceries", "parent": "Expenses", "description": "Grocery spending"},
        ],
        "rules": [
            {
                "id": "woolworths-groceries",
                "pattern": "woolworths",
                "category": "Expenses:Groceries",
                "confidence": "high",
                "description": "Woolworths grocery purchases",
            },
            {
                "id": "coles-groceries",
                "pattern": "coles",
                "category": "Expenses:Groceries",
                "confidence": "high",
                "description": "Coles grocery purchases",
            },
        ],
        "tax_tracking": {},
        "alerts": [],
        "labels": [],
        "metadata": {
            "templates_applied": [],
            "generated_date": "2025-11-22T12:00:00",
        },
    }


def test_applier_initialization(mock_api_client, mock_backup_manager):
    """Test TemplateApplier initialization."""
    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    assert applier.api_client == mock_api_client
    assert applier.backup_manager == mock_backup_manager
    assert applier.user_id is None


def test_applier_creates_default_backup_manager(mock_api_client):
    """Test that default BackupManager is created if not provided."""
    applier = TemplateApplier(mock_api_client)

    assert applier.backup_manager is not None


def test_invalid_strategy_raises_error(
    mock_api_client, mock_backup_manager, sample_merged_template
):
    """Test that invalid strategy raises ValueError."""
    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    with pytest.raises(ValueError, match="Invalid strategy"):
        applier.apply_template(sample_merged_template, "invalid_strategy")


def test_dry_run_doesnt_create_backup(mock_api_client, mock_backup_manager, sample_merged_template):
    """Test that dry-run mode doesn't create backup."""
    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    result = applier.apply_template(
        sample_merged_template, TemplateApplier.STRATEGY_ADD_NEW, dry_run=True
    )

    mock_backup_manager.create_backup.assert_not_called()
    assert result["dry_run"] is True
    assert result["backup_path"] is None


def test_apply_additive_reuses_existing_categories(
    mock_api_client, mock_backup_manager, sample_merged_template
):
    """Test additive strategy reuses existing categories."""
    # Setup existing categories
    mock_api_client.get_categories.return_value = [
        {"id": 100, "title": "Income", "parent_id": None},
        {"id": 101, "title": "Expenses", "parent_id": None},
    ]

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    result = applier.apply_template(
        sample_merged_template, TemplateApplier.STRATEGY_ADD_NEW, dry_run=False
    )

    # Should reuse 2 existing categories
    assert result["categories_reused"] == 2
    # Should create 1 new category (Expenses:Groceries)
    assert result["categories_created"] == 1
    # Should write 2 rules to YAML (platform rules are deprecated)
    assert result["rules_written_to_yaml"] == 2


def test_apply_additive_creates_all_new_categories(
    mock_api_client, mock_backup_manager, sample_merged_template
):
    """Test additive strategy creates all categories when none exist."""
    # No existing categories
    mock_api_client.get_categories.return_value = []

    # Mock category creation with incremental IDs
    created_ids = [200, 201, 202]
    mock_api_client.post.side_effect = [
        {"id": created_ids[0], "title": "Income"},
        {"id": created_ids[1], "title": "Expenses"},
        {"id": created_ids[2], "title": "Groceries"},
    ]

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    result = applier.apply_template(
        sample_merged_template, TemplateApplier.STRATEGY_ADD_NEW, dry_run=False
    )

    assert result["categories_reused"] == 0
    assert result["categories_created"] == 3
    # Should write 2 rules to YAML (platform rules are deprecated)
    assert result["rules_written_to_yaml"] == 2


def test_apply_smart_merge_matches_categories(
    mock_api_client, mock_backup_manager, sample_merged_template
):
    """Test smart merge matches similar categories."""
    # Setup existing categories with similar names
    mock_api_client.get_categories.return_value = [
        {"id": 100, "title": "Income", "description": "All income", "parent_id": None},
        {"id": 101, "title": "Spending", "description": "All expenses", "parent_id": None},
    ]

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    # Mock category creation for unmatched
    mock_api_client.post.return_value = {"id": 202, "title": "Groceries"}

    result = applier.apply_template(
        sample_merged_template, TemplateApplier.STRATEGY_SMART_MERGE, dry_run=False
    )

    # Should match Income exactly
    assert result["categories_matched"] >= 1
    # Should create Expenses:Groceries
    assert result["categories_created"] >= 1


def test_apply_smart_merge_writes_rules_to_yaml(mock_api_client, mock_backup_manager):
    """Test smart merge writes all rules to YAML (no deduplication with platform rules).

    NOTE: With local YAML rules, we write all template rules regardless of
    existing platform rules. The rule engine handles priority/deduplication.
    """
    template = {
        "categories": [
            {"name": "Groceries", "parent": None, "description": "Grocery spending"},
        ],
        "rules": [
            {
                "id": "woolworths-rule",
                "pattern": "woolworths",
                "category": "Groceries",
                "confidence": "high",
                "description": "Woolworths purchases",
            },
            {
                "id": "coles-rule",
                "pattern": "coles",
                "category": "Groceries",
                "confidence": "high",
                "description": "Coles purchases",
            },
        ],
        "metadata": {},
    }

    # Setup existing category with one platform rule already
    mock_api_client.get_categories.return_value = [
        {"id": 100, "title": "Groceries", "parent_id": None},
    ]
    mock_api_client.get_category_rules.return_value = [
        {"id": 1, "payee_matches": "woolworths"},  # Existing platform rule
    ]

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    result = applier.apply_template(template, TemplateApplier.STRATEGY_SMART_MERGE, dry_run=False)

    # Should write both rules to YAML (platform rules are separate)
    assert result["rules_written_to_yaml"] == 2


def test_apply_replace_creates_fresh_categories(
    mock_api_client, mock_backup_manager, sample_merged_template
):
    """Test replace strategy creates all categories fresh."""
    # Setup existing categories (should be ignored)
    mock_api_client.get_categories.return_value = [
        {"id": 100, "title": "Old Category", "parent_id": None},
    ]

    # Mock category creation
    created_ids = [300, 301, 302]
    mock_api_client.post.side_effect = [
        {"id": created_ids[0], "title": "Income"},
        {"id": created_ids[1], "title": "Expenses"},
        {"id": created_ids[2], "title": "Groceries"},
    ]

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    result = applier.apply_template(
        sample_merged_template, TemplateApplier.STRATEGY_REPLACE, dry_run=False
    )

    # Should create all 3 categories fresh
    assert result["categories_created"] == 3
    # Should archive existing
    assert result["categories_archived"] == 1
    # Should write all rules to YAML (platform rules are deprecated)
    assert result["rules_written_to_yaml"] == 2


def test_backup_created_before_modifications(
    mock_api_client, mock_backup_manager, sample_merged_template
):
    """Test that backup is created before any modifications."""
    mock_api_client.get_categories.return_value = [
        {"id": 100, "title": "Existing", "parent_id": None},
    ]

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    applier.apply_template(sample_merged_template, TemplateApplier.STRATEGY_ADD_NEW, dry_run=False)

    # Verify backup was created
    mock_backup_manager.create_backup.assert_called_once()
    call_args = mock_backup_manager.create_backup.call_args

    assert "Template application" in call_args[1]["description"]
    assert call_args[1]["metadata"]["strategy"] == TemplateApplier.STRATEGY_ADD_NEW
    assert call_args[1]["metadata"]["user_id"] == 217031

    # Verify backup data was saved
    assert mock_backup_manager.save_backup_data.call_count == 2


def test_statistics_returned_correctly(
    mock_api_client, mock_backup_manager, sample_merged_template
):
    """Test that statistics are returned with all required fields."""
    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    result = applier.apply_template(
        sample_merged_template, TemplateApplier.STRATEGY_ADD_NEW, dry_run=False
    )

    # Verify all required fields present
    assert "backup_path" in result
    assert "strategy" in result
    assert "dry_run" in result
    assert result["strategy"] == TemplateApplier.STRATEGY_ADD_NEW
    assert result["dry_run"] is False


def test_rules_skipped_when_category_not_found(mock_api_client, mock_backup_manager):
    """Test that rules are written to YAML even if category doesn't exist yet.

    NOTE: With local rules, we write rules to YAML regardless of whether
    categories exist in PocketSmith. The category field is just a reference.
    """
    template = {
        "categories": [
            {"name": "Income", "parent": None, "description": "Income"},
        ],
        "rules": [
            {
                "id": "test-rule",
                "pattern": "test",
                "category": "NonExistent",  # Category not in template
                "confidence": "high",
                "description": "Test rule for non-existent category",
            },
        ],
        "metadata": {},
    }

    mock_api_client.get_categories.return_value = []
    mock_api_client.post.return_value = {"id": 100, "title": "Income"}

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    result = applier.apply_template(template, TemplateApplier.STRATEGY_ADD_NEW, dry_run=False)

    # Rule should still be written to YAML (category is just a reference)
    assert result["rules_written_to_yaml"] == 1


def test_hierarchical_categories_handled_correctly(mock_api_client, mock_backup_manager):
    """Test that hierarchical categories are created with proper parent_id."""
    template = {
        "categories": [
            {"name": "Expenses", "parent": None, "description": "All expenses"},
            {"name": "Expenses:Food", "parent": "Expenses", "description": "Food expenses"},
        ],
        "rules": [],
        "metadata": {},
    }

    mock_api_client.get_categories.return_value = []
    mock_api_client.post.side_effect = [
        {"id": 100, "title": "Expenses"},
        {"id": 101, "title": "Food", "parent_id": 100},
    ]

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    applier.apply_template(template, TemplateApplier.STRATEGY_ADD_NEW, dry_run=False)

    # Verify parent_id was set correctly in second category
    calls = mock_api_client.post.call_args_list
    assert len(calls) == 2
    second_call_data = calls[1][1]["data"]
    assert second_call_data["parent_id"] == 100


def test_dry_run_doesnt_call_api_mutations(
    mock_api_client, mock_backup_manager, sample_merged_template
):
    """Test that dry-run doesn't call any mutation APIs."""
    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    applier.apply_template(sample_merged_template, TemplateApplier.STRATEGY_ADD_NEW, dry_run=True)

    # Should fetch data but not create anything
    mock_api_client.get_user.assert_called_once()
    mock_api_client.get_categories.assert_called_once()
    mock_api_client.post.assert_not_called()
    mock_api_client.create_category_rule.assert_not_called()


def test_build_category_map_handles_hierarchy(mock_api_client, mock_backup_manager):
    """Test that category map correctly handles parent-child relationships."""
    categories = [
        {"id": 1, "title": "Parent", "parent_id": None},
        {"id": 2, "title": "Child", "parent_id": 1},
    ]

    applier = TemplateApplier(mock_api_client, mock_backup_manager)
    category_map = applier._build_category_map(categories)

    assert "Parent" in category_map
    assert "Parent:Child" in category_map
    assert category_map["Parent"]["id"] == 1
    assert category_map["Parent:Child"]["id"] == 2


def test_find_similar_category_substring_match(mock_api_client, mock_backup_manager):
    """Test fuzzy matching finds categories with substring matches."""
    template_cat = {"name": "Food", "description": "Food expenses"}
    existing = [
        {"id": 1, "title": "Food & Dining", "description": "All food related", "parent_id": None},
        {"id": 2, "title": "Transport", "description": "Transport costs", "parent_id": None},
    ]

    applier = TemplateApplier(mock_api_client, mock_backup_manager)
    match = applier._find_similar_category(template_cat, existing)

    assert match is not None
    assert match["id"] == 1


def test_find_similar_category_no_match(mock_api_client, mock_backup_manager):
    """Test fuzzy matching returns None when no match found."""
    template_cat = {"name": "Groceries", "description": "Grocery shopping"}
    existing = [
        {"id": 1, "title": "Transport", "description": "Transport costs", "parent_id": None},
    ]

    applier = TemplateApplier(mock_api_client, mock_backup_manager)
    match = applier._find_similar_category(template_cat, existing)

    assert match is None


def test_rule_exists_exact_match(mock_api_client, mock_backup_manager):
    """Test rule existence check with exact match."""
    rules_map = {
        100: ["woolworths", "coles"],
    }

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    assert applier._rule_exists(100, "woolworths", rules_map) is True
    assert applier._rule_exists(100, "aldi", rules_map) is False


def test_rule_exists_case_insensitive(mock_api_client, mock_backup_manager):
    """Test rule existence check is case-insensitive."""
    rules_map = {
        100: ["Woolworths"],
    }

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    assert applier._rule_exists(100, "woolworths", rules_map) is True
    assert applier._rule_exists(100, "WOOLWORTHS", rules_map) is True


def test_empty_template_handled_gracefully(mock_api_client, mock_backup_manager):
    """Test that empty template is handled without errors."""
    template = {
        "categories": [],
        "rules": [],
        "metadata": {},
    }

    applier = TemplateApplier(mock_api_client, mock_backup_manager)

    result = applier.apply_template(template, TemplateApplier.STRATEGY_ADD_NEW, dry_run=False)

    assert result["categories_created"] == 0
    assert result["categories_reused"] == 0
    assert result["rules_created"] == 0
