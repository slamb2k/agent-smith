"""Tests for platform rule deprecation warnings and migration."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from scripts.core.rule_engine import RuleEngine


class TestPlatformRuleDeprecation:
    """Test suite for platform rule deprecation."""

    @pytest.fixture
    def temp_rules_dir(self, tmp_path):
        """Create temporary rules directory."""
        rules_dir = tmp_path / "data"
        rules_dir.mkdir(parents=True)
        return rules_dir

    @pytest.fixture
    def rule_engine(self, temp_rules_dir):
        """Create RuleEngine with temp files."""
        local_rules = temp_rules_dir / "local_rules.json"
        platform_rules = temp_rules_dir / "platform_rules.json"
        return RuleEngine(rules_file=local_rules, platform_rules_file=platform_rules)

    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client."""
        client = MagicMock()
        client.create_category_rule.return_value = {
            "id": 12345,
            "payee_matches": "WOOLWORTHS",
        }
        return client

    def test_create_platform_rule_logs_deprecation_warning(
        self, rule_engine, mock_api_client, caplog
    ):
        """Test that create_platform_rule logs a deprecation warning."""
        with caplog.at_level(logging.WARNING):
            rule_engine.create_platform_rule(
                api_client=mock_api_client,
                category_id=100,
                payee_contains="WOOLWORTHS",
            )

        # Verify warning was logged
        assert any(
            "DEPRECATED" in record.message and "platform rule" in record.message.lower()
            for record in caplog.records
        ), "Expected deprecation warning for platform rule creation"

    def test_create_platform_rule_mentions_unified_engine(
        self, rule_engine, mock_api_client, caplog
    ):
        """Test that deprecation warning mentions UnifiedRuleEngine."""
        with caplog.at_level(logging.WARNING):
            rule_engine.create_platform_rule(
                api_client=mock_api_client,
                category_id=100,
                payee_contains="WOOLWORTHS",
            )

        # Verify warning mentions UnifiedRuleEngine or YAML
        assert any(
            "UnifiedRuleEngine" in record.message or "YAML" in record.message
            for record in caplog.records
        ), "Expected deprecation warning to mention UnifiedRuleEngine or YAML"

    def test_create_platform_rule_still_works(self, rule_engine, mock_api_client, temp_rules_dir):
        """Test that create_platform_rule still functions despite deprecation."""
        result = rule_engine.create_platform_rule(
            api_client=mock_api_client,
            category_id=100,
            payee_contains="WOOLWORTHS",
        )

        # Verify rule was created
        assert result["rule_id"] == 12345
        assert result["category_id"] == 100
        assert result["payee_contains"] == "WOOLWORTHS"
        assert "created_at" in result

        # Verify tracking file was created
        platform_rules_file = temp_rules_dir / "platform_rules.json"
        assert platform_rules_file.exists()

        # Verify content
        with open(platform_rules_file) as f:
            platform_rules = json.load(f)

        assert len(platform_rules) == 1
        assert platform_rules[0]["rule_id"] == 12345

    def test_sync_platform_rules_logs_warning(self, rule_engine, mock_api_client, caplog):
        """Test that sync_platform_rules logs a warning about platform rules."""
        # Setup mock
        mock_api_client.get_user.return_value = {"id": 1}
        mock_api_client.get_categories.return_value = [{"id": 100, "title": "Groceries"}]
        mock_api_client.get_category_rules.return_value = [
            {"id": 12345, "payee_matches": "WOOLWORTHS"}
        ]

        with caplog.at_level(logging.INFO):
            rule_engine.sync_platform_rules(mock_api_client)

        # Verify sync completed
        assert any(
            "Synced" in record.message and "platform rules" in record.message
            for record in caplog.records
        )


class TestMigrationUtilityExists:
    """Test that migration utility script exists and is executable."""

    def test_migration_script_exists(self):
        """Test that migration script exists."""
        migration_script = (
            Path(__file__).parent.parent.parent
            / "scripts"
            / "migrations"
            / "migrate_platform_to_local.py"
        )
        assert migration_script.exists(), f"Migration script should exist at {migration_script}"

    def test_migration_script_has_main_function(self):
        """Test that migration script has a main() function."""
        # Import the migration module
        from scripts.migrations.migrate_platform_to_local import main

        assert callable(main), "Migration script should have a callable main() function"


class TestMigrationGuideExists:
    """Test that migration guide documentation exists."""

    def test_migration_guide_exists(self):
        """Test that migration guide exists."""
        guide_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "guides"
            / "platform-to-local-migration.md"
        )
        assert guide_path.exists(), f"Migration guide should exist at {guide_path}"

    def test_migration_guide_has_content(self):
        """Test that migration guide has meaningful content."""
        guide_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "guides"
            / "platform-to-local-migration.md"
        )

        content = guide_path.read_text()

        # Verify key sections exist
        assert "# Migrating from Platform Rules to Local Rules" in content
        assert "Why Migrate?" in content
        assert "YAML" in content or "yaml" in content
        assert "UnifiedRuleEngine" in content
        assert len(content) > 500, "Migration guide should have substantial content"
