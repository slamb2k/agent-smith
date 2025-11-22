#!/usr/bin/env python3
"""Migrate platform rules to local YAML rules.

This script fetches existing platform rules from PocketSmith API,
converts them to local YAML format, and appends them to rules.yaml.

Usage:
    uv run python scripts/migrations/migrate_platform_to_local.py [--dry-run]
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from scripts.core.api_client import PocketSmithClient
from scripts.core.rule_engine import RuleEngine

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fetch_platform_rules(client: PocketSmithClient) -> List[Dict[str, Any]]:
    """Fetch all platform rules from PocketSmith API.

    Args:
        client: PocketSmith API client

    Returns:
        List of platform rule dicts with rule_id, category_id, payee_contains
    """
    engine = RuleEngine()
    engine.sync_platform_rules(client)

    # Load the synced rules
    platform_rules_file = Path(__file__).parent.parent.parent / "data" / "platform_rules.json"

    if not platform_rules_file.exists():
        logger.warning("No platform rules found")
        return []

    with open(platform_rules_file) as f:
        rules: List[Dict[str, Any]] = json.load(f)

    logger.info(f"Found {len(rules)} platform rules")
    return rules


def fetch_category_mapping(client: PocketSmithClient) -> Dict[int, str]:
    """Fetch category ID to name mapping.

    Args:
        client: PocketSmith API client

    Returns:
        Dict mapping category_id -> category_name
    """
    user = client.get_user()
    categories = client.get_categories(user_id=user["id"])

    mapping = {}
    for category in categories:
        mapping[category["id"]] = category["title"]

    logger.info(f"Loaded {len(mapping)} categories")
    return mapping


def convert_platform_to_yaml(
    platform_rules: List[Dict[str, Any]], category_mapping: Dict[int, str]
) -> List[Dict[str, Any]]:
    """Convert platform rules to YAML format.

    Args:
        platform_rules: List of platform rule dicts
        category_mapping: Dict mapping category_id -> category_name

    Returns:
        List of YAML rule dicts
    """
    yaml_rules = []

    for rule in platform_rules:
        category_id = rule["category_id"]
        payee_contains = rule["payee_contains"]
        category_name = category_mapping.get(category_id, f"Unknown (ID: {category_id})")

        yaml_rule = {
            "type": "category",
            "name": f"{payee_contains} → {category_name}",
            "patterns": [payee_contains],
            "category": category_name,
            "confidence": 95,  # Platform rules are exact matches
            "metadata": {
                "migrated_from_platform": True,
                "original_rule_id": rule["rule_id"],
                "migrated_at": datetime.now().isoformat(),
            },
        }

        yaml_rules.append(yaml_rule)

    logger.info(f"Converted {len(yaml_rules)} rules to YAML format")
    return yaml_rules


def backup_existing_rules(rules_file: Path) -> Optional[Path]:
    """Create a backup of existing rules.yaml.

    Args:
        rules_file: Path to rules.yaml

    Returns:
        Path to backup file or None if no file to backup
    """
    if not rules_file.exists():
        logger.info("No existing rules.yaml to backup")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = rules_file.parent / f"rules.yaml.backup_{timestamp}"

    # Copy existing file
    backup_file.write_text(rules_file.read_text())

    logger.info(f"Backed up rules.yaml to {backup_file}")
    return backup_file


def append_rules_to_yaml(yaml_rules: List[Dict[str, Any]], rules_file: Path) -> None:
    """Append converted rules to rules.yaml.

    Args:
        yaml_rules: List of YAML rule dicts
        rules_file: Path to rules.yaml
    """
    # Load existing rules if file exists
    existing_rules = []
    if rules_file.exists():
        with open(rules_file) as f:
            content = yaml.safe_load(f)
            if content:
                existing_rules = content

    # Append new rules
    all_rules = existing_rules + yaml_rules

    # Write back
    rules_file.parent.mkdir(parents=True, exist_ok=True)
    with open(rules_file, "w") as f:
        yaml.dump(all_rules, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Appended {len(yaml_rules)} rules to {rules_file}")


def main() -> int:
    """Main migration function.

    Returns:
        Exit code (0 = success, 1 = error)
    """
    dry_run = "--dry-run" in sys.argv

    try:
        # Initialize client
        logger.info("Initializing PocketSmith client...")
        client = PocketSmithClient()

        # Fetch platform rules
        logger.info("Fetching platform rules from API...")
        platform_rules = fetch_platform_rules(client)

        if not platform_rules:
            logger.info("No platform rules to migrate")
            return 0

        # Fetch category mapping
        logger.info("Fetching category mapping...")
        category_mapping = fetch_category_mapping(client)

        # Convert to YAML
        logger.info("Converting platform rules to YAML format...")
        yaml_rules = convert_platform_to_yaml(platform_rules, category_mapping)

        if dry_run:
            logger.info("DRY RUN: Would convert the following rules:")
            print(yaml.dump(yaml_rules, default_flow_style=False, sort_keys=False))
            return 0

        # Backup existing rules
        rules_file = Path(__file__).parent.parent.parent / "data" / "rules.yaml"
        backup_file = backup_existing_rules(rules_file)

        # Append to rules.yaml
        logger.info("Appending rules to rules.yaml...")
        append_rules_to_yaml(yaml_rules, rules_file)

        # Success message
        logger.info("=" * 60)
        logger.info("Migration complete!")
        logger.info(f"- Migrated {len(yaml_rules)} platform rules to {rules_file}")
        if backup_file:
            logger.info(f"- Backup created at {backup_file}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Review the converted rules in data/rules.yaml")
        logger.info("2. Test with: uv run python scripts/operations/categorize_batch.py --dry-run")
        logger.info("3. Platform rules will continue to work in PocketSmith")
        logger.info("4. See docs/guides/platform-to-local-migration.md for more info")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
