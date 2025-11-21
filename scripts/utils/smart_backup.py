"""Smart backup system with activity-specific backups and rollback capability.

Based on PocketSmith backup best practices research (see docs/research/).

Key Findings:
- API access available on ALL tiers (including Free)
- Category rules CANNOT be updated/deleted via API (only list and create)
- Category rules NOT included in CSV backups
- No traditional reconciliation in PocketSmith (transaction confirmation workflow)
- Attachments not included in CSV backups
"""

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.utils.backup import BackupManager

logger = logging.getLogger(__name__)


class ActivityType(Enum):
    """Types of activities that trigger backups."""

    CATEGORY_OPTIMIZATION = "category_optimization"
    CATEGORY_MERGE = "category_merge"
    CATEGORY_DELETE = "category_delete"
    RULE_BATCH_CREATE = "rule_batch_create"
    TRANSACTION_BATCH_UPDATE = "transaction_batch_update"
    TRANSACTION_BATCH_DELETE = "transaction_batch_delete"
    ACCOUNT_DELETE = "account_delete"
    BULK_CATEGORIZATION = "bulk_categorization"
    DATA_IMPORT = "data_import"


class PocketSmithTier(Enum):
    """PocketSmith subscription tiers."""

    FREE = "free"
    FOUNDATION = "foundation"
    FLOURISH = "flourish"
    FORTUNE = "fortune"


class SmartBackupManager(BackupManager):
    """Enhanced backup manager with activity-specific backups and rollback.

    Features:
    - Activity-specific backup metadata
    - Tier requirement warnings
    - Rollback capability with limitations awareness
    - Multi-source backup (CSV, API, attachments)
    - Pre-operation snapshots
    """

    # Features requiring paid tiers (for user awareness only - API works on all tiers)
    TIER_REQUIREMENTS = {
        "unlimited_accounts": PocketSmithTier.FOUNDATION,
        "automatic_feeds": PocketSmithTier.FOUNDATION,
        "multiple_countries": PocketSmithTier.FLOURISH,
        "unlimited_connections": PocketSmithTier.FORTUNE,
    }

    def create_activity_backup(
        self,
        activity_type: ActivityType,
        description: str,
        affected_items: Optional[Dict[str, Any]] = None,
        tier_warning: Optional[str] = None,
    ) -> Path:
        """Create backup before a specific activity.

        Args:
            activity_type: Type of activity being performed
            description: Human-readable description
            affected_items: Dict of affected data (e.g., {"category_ids": [1,2,3]})
            tier_warning: Optional warning about tier requirements

        Returns:
            Path to backup directory
        """
        metadata = {
            "activity_type": activity_type.value,
            "affected_items": affected_items or {},
            "tier_warning": tier_warning,
            "can_rollback": self._can_rollback(activity_type),
            "rollback_limitations": self._get_rollback_limitations(activity_type),
        }

        backup_path = self.create_backup(description, metadata)
        logger.info(f"Created {activity_type.value} backup: {backup_path.name} - {description}")

        if tier_warning:
            logger.warning(f"Tier requirement: {tier_warning}")

        return backup_path

    def backup_category_rules(self, backup_path: Path, rules: List[Dict[str, Any]]) -> None:
        """Backup category rules (not included in PocketSmith CSV exports).

        CRITICAL: Category rules cannot be updated or deleted via API.
        Only GET (list) and POST (create) are supported.

        Args:
            backup_path: Backup directory path
            rules: List of category rule dicts from API
        """
        self.save_backup_data(backup_path, "category_rules.json", rules)

        # Save limitation warning
        warning = {
            "CRITICAL_LIMITATION": (
                "Category rules cannot be updated or deleted via PocketSmith API"
            ),
            "supported_operations": ["GET (list)", "POST (create)"],
            "unsupported_operations": ["PUT (update)", "DELETE (remove)"],
            "consequence": "Rules created via API can only be modified/deleted via web interface",
            "recommendation": "Use Agent Smith's local rule engine for full CRUD capability",
        }
        self.save_backup_data(backup_path, "category_rules_WARNING.json", warning)
        logger.warning("Category rules backed up with API limitation notice")

    def backup_transactions(self, backup_path: Path, transactions: List[Dict[str, Any]]) -> None:
        """Backup transactions with full data.

        Args:
            backup_path: Backup directory path
            transactions: List of transaction dicts from API
        """
        self.save_backup_data(backup_path, "transactions.json", transactions)
        logger.info(f"Backed up {len(transactions)} transactions")

    def backup_categories(self, backup_path: Path, categories: List[Dict[str, Any]]) -> None:
        """Backup category hierarchy.

        Args:
            backup_path: Backup directory path
            categories: List of category dicts from API
        """
        self.save_backup_data(backup_path, "categories.json", categories)
        logger.info(f"Backed up {len(categories)} categories")

    def backup_accounts(self, backup_path: Path, accounts: List[Dict[str, Any]]) -> None:
        """Backup account details.

        Args:
            backup_path: Backup directory path
            accounts: List of account dicts from API
        """
        self.save_backup_data(backup_path, "accounts.json", accounts)
        logger.info(f"Backed up {len(accounts)} accounts")

    def can_rollback(self, backup_path: Path) -> bool:
        """Check if backup can be rolled back.

        Args:
            backup_path: Backup directory path

        Returns:
            True if rollback is possible
        """
        metadata_file = backup_path / "metadata.json"
        if not metadata_file.exists():
            return False

        with open(metadata_file) as f:
            metadata = json.load(f)

        return bool(metadata.get("can_rollback", False))

    def get_rollback_limitations(self, backup_path: Path) -> List[str]:
        """Get list of rollback limitations for a backup.

        Args:
            backup_path: Backup directory path

        Returns:
            List of limitation warnings
        """
        metadata_file = backup_path / "metadata.json"
        if not metadata_file.exists():
            return ["Backup metadata not found"]

        with open(metadata_file) as f:
            metadata = json.load(f)

        limitations = metadata.get("rollback_limitations", [])
        return list(limitations) if limitations else []

    def _can_rollback(self, activity_type: ActivityType) -> bool:
        """Determine if activity can be rolled back.

        Args:
            activity_type: Type of activity

        Returns:
            True if rollback is possible
        """
        # Based on PocketSmith research
        rollback_possible = {
            ActivityType.CATEGORY_OPTIMIZATION: False,  # No undo for manual operations
            ActivityType.CATEGORY_MERGE: False,  # Cannot undo category merge
            ActivityType.CATEGORY_DELETE: False,  # Cannot restore deleted categories
            ActivityType.RULE_BATCH_CREATE: False,  # Cannot delete rules via API
            ActivityType.TRANSACTION_BATCH_UPDATE: True,  # Can restore transaction data
            ActivityType.TRANSACTION_BATCH_DELETE: True,  # Can restore deleted transactions
            ActivityType.ACCOUNT_DELETE: False,  # Cannot restore deleted accounts
            ActivityType.BULK_CATEGORIZATION: True,  # Can revert category assignments
            ActivityType.DATA_IMPORT: True,  # Can delete imported transactions
        }

        return rollback_possible.get(activity_type, False)

    def _get_rollback_limitations(self, activity_type: ActivityType) -> List[str]:
        """Get rollback limitations for activity type.

        Args:
            activity_type: Type of activity

        Returns:
            List of limitation strings
        """
        limitations = {
            ActivityType.CATEGORY_OPTIMIZATION: [
                "Category structure changes cannot be undone",
                "Merged categories cannot be unmerged",
                "Transaction category assignments can be restored",
            ],
            ActivityType.CATEGORY_MERGE: [
                "Cannot unmerge categories once merged",
                "Budgets and rules transfer to target category (may create duplicates)",
                "Transaction assignments can be restored from backup",
            ],
            ActivityType.CATEGORY_DELETE: [
                "Deleted categories cannot be restored via API",
                "Future bank imports will not auto-map to deleted category",
                "Transactions can be re-categorized from backup",
            ],
            ActivityType.RULE_BATCH_CREATE: [
                "Category rules cannot be deleted via API",
                "Must use PocketSmith web interface to remove rules",
                "Consider using Agent Smith local rules for full control",
            ],
            ActivityType.TRANSACTION_BATCH_UPDATE: [
                "Full rollback supported",
                "Restores: amounts, dates, categories, labels, notes, splits",
            ],
            ActivityType.TRANSACTION_BATCH_DELETE: [
                "Deleted transactions can be restored from backup",
                "Attachments must be restored separately (not in transaction data)",
            ],
            ActivityType.ACCOUNT_DELETE: [
                "Cannot restore deleted accounts via API",
                "Transactions can be restored but will be orphaned",
                "Must recreate account manually first",
            ],
            ActivityType.BULK_CATEGORIZATION: [
                "Full rollback supported",
                "Restores original category assignments",
            ],
            ActivityType.DATA_IMPORT: [
                "Can delete imported transactions to rollback",
                "Requires tracking import batch IDs",
            ],
        }

        return limitations.get(activity_type, ["Rollback support unknown for this activity type"])

    def get_tier_info(self) -> Dict[str, Any]:
        """Get PocketSmith tier information.

        Returns:
            Dict with tier details and feature requirements
        """
        return {
            "api_access": "Available on ALL tiers (including Free)",
            "tiers": {
                "free": {
                    "price": "Free",
                    "accounts": 2,
                    "banks": "Manual import only",
                    "budgets": 12,
                    "forecast": "6 months",
                },
                "foundation": {
                    "price": "$9.99/mo AUD (annual) or $14.95/mo",
                    "accounts": "Unlimited",
                    "banks": "6 (1 country)",
                    "budgets": "Unlimited",
                    "forecast": "10 years",
                },
                "flourish": {
                    "price": "$16.66/mo AUD (annual) or $24.95/mo",
                    "accounts": "Unlimited",
                    "banks": "18 (all countries)",
                    "budgets": "Unlimited",
                    "forecast": "30 years",
                },
                "fortune": {
                    "price": "$26.66/mo AUD (annual) or $39.95/mo",
                    "accounts": "Unlimited",
                    "banks": "Unlimited (all countries)",
                    "budgets": "Unlimited",
                    "forecast": "60 years",
                    "support": "Priority",
                },
            },
            "note": "Agent Smith works with all tiers. No API restrictions.",
        }

    def check_feature_tier(self, feature: str) -> Optional[PocketSmithTier]:
        """Check minimum tier required for a feature.

        Args:
            feature: Feature name to check

        Returns:
            Minimum tier required, or None if available on all tiers
        """
        return self.TIER_REQUIREMENTS.get(feature)
