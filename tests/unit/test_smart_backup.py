"""Tests for smart backup system."""

import json
from pathlib import Path

import pytest

from scripts.utils.smart_backup import (
    ActivityType,
    PocketSmithTier,
    SmartBackupManager,
)


class TestSmartBackupManager:
    def test_create_activity_backup(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)

        backup_path = manager.create_activity_backup(
            activity_type=ActivityType.BULK_CATEGORIZATION,
            description="Categorize 50 transactions",
            affected_items={"transaction_count": 50},
        )

        assert backup_path.exists()
        metadata_file = backup_path / "metadata.json"
        assert metadata_file.exists()

        with open(metadata_file) as f:
            metadata = json.load(f)

        assert metadata["activity_type"] == "bulk_categorization"
        assert metadata["description"] == "Categorize 50 transactions"
        assert metadata["affected_items"]["transaction_count"] == 50
        assert metadata["can_rollback"] is True

    def test_backup_category_rules_includes_warning(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)
        backup_path = manager.create_backup("Test")

        rules = [{"id": 1, "payee_matches": "Woolworths", "category_id": 10}]
        manager.backup_category_rules(backup_path, rules)

        # Check rules backup
        rules_file = backup_path / "category_rules.json"
        assert rules_file.exists()

        # Check warning file
        warning_file = backup_path / "category_rules_WARNING.json"
        assert warning_file.exists()

        with open(warning_file) as f:
            warning = json.load(f)

        assert "CRITICAL_LIMITATION" in warning
        assert "cannot be updated or deleted" in warning["CRITICAL_LIMITATION"]

    def test_rollback_capability_by_activity(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)

        # Can rollback
        rollback_true = manager.create_activity_backup(ActivityType.BULK_CATEGORIZATION, "Test")
        assert manager.can_rollback(rollback_true) is True

        # Cannot rollback
        rollback_false = manager.create_activity_backup(ActivityType.CATEGORY_DELETE, "Test")
        assert manager.can_rollback(rollback_false) is False

    def test_rollback_limitations_category_merge(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)
        backup_path = manager.create_activity_backup(ActivityType.CATEGORY_MERGE, "Test")

        limitations = manager.get_rollback_limitations(backup_path)

        assert len(limitations) > 0
        assert any("Cannot unmerge" in lim for lim in limitations)

    def test_rollback_limitations_rule_batch_create(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)
        backup_path = manager.create_activity_backup(ActivityType.RULE_BATCH_CREATE, "Test")

        limitations = manager.get_rollback_limitations(backup_path)

        assert any("cannot be deleted via API" in lim for lim in limitations)
        assert any("web interface" in lim for lim in limitations)

    def test_backup_transactions(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)
        backup_path = manager.create_backup("Test")

        transactions = [
            {"id": 1, "amount": 50.00, "payee": "Woolworths"},
            {"id": 2, "amount": -25.00, "payee": "Coles"},
        ]

        manager.backup_transactions(backup_path, transactions)

        txn_file = backup_path / "transactions.json"
        assert txn_file.exists()

        with open(txn_file) as f:
            saved = json.load(f)

        assert len(saved) == 2
        assert saved[0]["payee"] == "Woolworths"

    def test_backup_categories(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)
        backup_path = manager.create_backup("Test")

        categories = [{"id": 1, "title": "Groceries"}, {"id": 2, "title": "Transport"}]

        manager.backup_categories(backup_path, categories)

        cat_file = backup_path / "categories.json"
        assert cat_file.exists()

        with open(cat_file) as f:
            saved = json.load(f)

        assert len(saved) == 2

    def test_get_tier_info(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)
        tier_info = manager.get_tier_info()

        assert tier_info["api_access"] == "Available on ALL tiers (including Free)"
        assert "free" in tier_info["tiers"]
        assert "foundation" in tier_info["tiers"]
        assert tier_info["tiers"]["free"]["accounts"] == 2

    def test_check_feature_tier(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)

        # Feature requiring paid tier
        tier = manager.check_feature_tier("unlimited_accounts")
        assert tier == PocketSmithTier.FOUNDATION

        # Feature not in requirements (available on all tiers)
        tier = manager.check_feature_tier("api_access")
        assert tier is None

    def test_tier_warning_in_backup(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)

        backup_path = manager.create_activity_backup(
            ActivityType.BULK_CATEGORIZATION,
            "Test",
            tier_warning="This feature requires Foundation tier or higher",
        )

        metadata_file = backup_path / "metadata.json"
        with open(metadata_file) as f:
            metadata = json.load(f)

        assert metadata["tier_warning"] == "This feature requires Foundation tier or higher"

    def test_activity_type_enum_values(self):
        assert ActivityType.CATEGORY_OPTIMIZATION.value == "category_optimization"
        assert ActivityType.BULK_CATEGORIZATION.value == "bulk_categorization"
        assert ActivityType.RULE_BATCH_CREATE.value == "rule_batch_create"

    def test_all_activity_types_have_limitations(self, tmp_path):
        manager = SmartBackupManager(backup_root=tmp_path)

        for activity in ActivityType:
            limitations = manager._get_rollback_limitations(activity)
            assert len(limitations) > 0
            assert isinstance(limitations, list)
