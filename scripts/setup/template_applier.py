"""Template applier with user choice and backup support."""

import argparse
import json
import logging
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from scripts.utils.backup import BackupManager
from scripts.core.api_client import PocketSmithClient


logger = logging.getLogger(__name__)

# Magic number for dry-run category IDs (offset to avoid conflicts with real IDs)
DRY_RUN_ID_OFFSET = 9999999


class TemplateApplier:
    """Apply merged templates to PocketSmith with user choice.

    Provides three application strategies:
    - Add New Only: Keep all existing, add from templates (safest)
    - Smart Merge: Intelligently combine existing with templates
    - Archive & Replace: Backup existing, apply templates fresh (risky)
    """

    STRATEGY_ADD_NEW = "add_new"
    STRATEGY_SMART_MERGE = "smart_merge"
    STRATEGY_REPLACE = "replace"

    def __init__(
        self, api_client: PocketSmithClient, backup_manager: Optional[BackupManager] = None
    ):
        """Initialize with API client and backup manager.

        Args:
            api_client: PocketSmith API client
            backup_manager: Backup manager (creates default if None)
        """
        self.api_client = api_client
        self.backup_manager = backup_manager or BackupManager()
        self.user_id: Optional[int] = None

        logger.info("TemplateApplier initialized")

    def apply_template(
        self, merged_template: Dict[str, Any], strategy: str, dry_run: bool = False
    ) -> Dict[str, Any]:
        """Apply merged template to PocketSmith.

        Args:
            merged_template: Merged template from TemplateMerger
            strategy: One of STRATEGY_ADD_NEW, STRATEGY_SMART_MERGE, STRATEGY_REPLACE
            dry_run: If True, preview changes without applying

        Returns:
            dict with statistics and backup_path

        Raises:
            ValueError: If invalid strategy provided
        """
        if strategy not in [
            self.STRATEGY_ADD_NEW,
            self.STRATEGY_SMART_MERGE,
            self.STRATEGY_REPLACE,
        ]:
            raise ValueError(f"Invalid strategy: {strategy}")

        logger.info(f"Applying template with strategy: {strategy} (dry_run={dry_run})")

        # Get user ID if not cached
        if self.user_id is None:
            user = self.api_client.get_user()
            self.user_id = user["id"]

        # Fetch existing PocketSmith data
        existing_categories = self._fetch_existing_categories()
        existing_rules = self._fetch_existing_rules(existing_categories)

        # Create backup before any modifications
        backup_path = None
        if not dry_run:
            backup_path = self._create_backup(existing_categories, existing_rules, strategy)

        # Apply strategy
        if strategy == self.STRATEGY_ADD_NEW:
            stats = self._apply_additive(merged_template, existing_categories, dry_run)
        elif strategy == self.STRATEGY_SMART_MERGE:
            stats = self._apply_smart_merge(merged_template, existing_categories, dry_run)
        else:  # STRATEGY_REPLACE
            stats = self._apply_replace(merged_template, existing_categories, dry_run)

        stats["backup_path"] = str(backup_path) if backup_path else None
        stats["strategy"] = strategy
        stats["dry_run"] = dry_run

        logger.info(f"Template application complete: {stats}")
        return stats

    def _fetch_existing_categories(self) -> List[Dict[str, Any]]:
        """Fetch existing categories from PocketSmith."""
        assert self.user_id is not None
        logger.info(f"Fetching existing categories for user {self.user_id}")
        return self.api_client.get_categories(self.user_id)

    def _fetch_existing_rules(self, categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fetch existing rules for all categories."""
        logger.info("Fetching existing rules for all categories")
        all_rules = []

        for category in categories:
            try:
                rules = self.api_client.get_category_rules(category["id"])
                for rule in rules:
                    rule["category_name"] = category["title"]  # Add category name for reference
                all_rules.extend(rules)
            except Exception as e:
                logger.warning(f"Failed to fetch rules for category {category['id']}: {e}")

        logger.info(f"Fetched {len(all_rules)} existing rules")
        return all_rules

    def _create_backup(
        self, categories: List[Dict[str, Any]], rules: List[Dict[str, Any]], strategy: str
    ) -> Path:
        """Create backup of existing data before modifications."""
        backup_path = self.backup_manager.create_backup(
            description=f"Template application - {strategy}",
            metadata={
                "user_id": self.user_id,
                "operation": "template_application",
                "strategy": strategy,
                "categories_count": len(categories),
                "rules_count": len(rules),
            },
        )

        self.backup_manager.save_backup_data(backup_path, "categories.json", categories)
        self.backup_manager.save_backup_data(backup_path, "rules.json", rules)

        logger.info(f"Created backup: {backup_path}")
        return backup_path

    def _apply_additive(
        self,
        merged_template: Dict[str, Any],
        existing_categories: List[Dict[str, Any]],
        dry_run: bool,
    ) -> Dict[str, Any]:
        """Add New Only strategy: Keep all existing, add from templates (safest).

        - Reuses existing categories by name match
        - Creates only new categories
        - Creates all rules from template

        Args:
            merged_template: Template to apply
            existing_categories: Existing PocketSmith categories
            dry_run: If True, don't actually create anything

        Returns:
            Statistics dictionary
        """
        logger.info("Applying additive strategy")

        # Build map of existing category names to IDs
        existing_map = self._build_category_map(existing_categories)

        stats = {
            "categories_created": 0,
            "categories_reused": 0,
            "rules_created": 0,
            "rules_skipped": 0,
            "label_only_rules": 0,
        }

        # Track category name to ID mapping (for both existing and newly created)
        category_id_map: Dict[str, int] = {}

        # First pass: Create/reuse categories
        for template_cat in merged_template.get("categories", []):
            cat_name = template_cat["name"]

            if cat_name in existing_map:
                # Reuse existing category
                category_id_map[cat_name] = existing_map[cat_name]["id"]
                stats["categories_reused"] += 1
                logger.debug(f"Reusing existing category: {cat_name}")
            else:
                # Create new category
                if not dry_run:
                    try:
                        created_cat = self._create_category(template_cat, category_id_map)
                        category_id_map[cat_name] = created_cat["id"]
                        stats["categories_created"] += 1
                        logger.debug(f"Creating new category: {cat_name}")
                    except Exception as e:
                        # Handle title conflicts gracefully
                        # HTTPError has 'response' attribute with .text property
                        response_text = getattr(e, "response", None)
                        response_text = response_text.text if response_text else ""
                        if "Title has already been taken" in response_text:
                            logger.warning(
                                f"Category '{cat_name}' title conflicts "
                                f"with existing category - skipping"
                            )
                            stats["categories_skipped"] = stats.get("categories_skipped", 0) + 1
                        else:
                            raise
                else:
                    # In dry run, use placeholder ID so rules can be validated
                    category_id_map[cat_name] = 9999999 + len(category_id_map)
                    stats["categories_created"] += 1
                    logger.debug(f"Creating new category: {cat_name}")

        # Second pass: Create rules
        # Track label-only rules separately (not created via PocketSmith API)
        for rule in merged_template.get("rules", []):
            target_category = rule.get("target_category")

            # Label-only rules (no category) are stored locally, not in PocketSmith
            if not target_category:
                stats["label_only_rules"] += 1
                logger.debug(f"Label-only rule (local engine): {rule.get('id', 'unknown')}")
                continue

            if target_category not in category_id_map:
                stats["rules_skipped"] += 1
                logger.warning(f"Skipping rule - category not found: {target_category}")
                continue

            if not dry_run:
                self._create_rule(rule, category_id_map[target_category])
            stats["rules_created"] += 1

        return stats

    def _apply_smart_merge(
        self,
        merged_template: Dict[str, Any],
        existing_categories: List[Dict[str, Any]],
        dry_run: bool,
    ) -> Dict[str, Any]:
        """Smart Merge strategy: Intelligently combine existing with templates.

        - Maps template categories to existing where semantic match found
        - Creates new categories for unmatched templates
        - Deduplicates rules based on payee_matches

        Args:
            merged_template: Template to apply
            existing_categories: Existing PocketSmith categories
            dry_run: If True, don't actually create anything

        Returns:
            Statistics dictionary
        """
        logger.info("Applying smart merge strategy")

        existing_map = self._build_category_map(existing_categories)

        stats = {
            "categories_created": 0,
            "categories_matched": 0,
            "rules_created": 0,
            "rules_skipped": 0,
            "label_only_rules": 0,
        }

        category_id_map: Dict[str, int] = {}

        # Smart matching: Try to match template categories to existing
        for template_cat in merged_template.get("categories", []):
            cat_name = template_cat["name"]

            # Exact match
            if cat_name in existing_map:
                category_id_map[cat_name] = existing_map[cat_name]["id"]
                stats["categories_matched"] += 1
                logger.debug(f"Exact match: {cat_name}")
                continue

            # Fuzzy match: Check for similar names
            matched = self._find_similar_category(template_cat, existing_categories)
            if matched:
                category_id_map[cat_name] = matched["id"]
                stats["categories_matched"] += 1
                logger.debug(f"Fuzzy match: {cat_name} -> {matched['title']}")
            else:
                # Create new category
                if not dry_run:
                    created_cat = self._create_category(template_cat, category_id_map)
                    category_id_map[cat_name] = created_cat["id"]
                else:
                    # In dry run, use placeholder ID so rules can be validated
                    category_id_map[cat_name] = 9999999 + len(category_id_map)
                stats["categories_created"] += 1
                logger.debug(f"Creating new category: {cat_name}")

        # Fetch existing rules to check for duplicates
        existing_rules_map = self._build_rules_map(existing_categories)

        # Create rules with deduplication
        # Track label-only rules separately (not created via PocketSmith API)
        for rule in merged_template.get("rules", []):
            target_category = rule.get("target_category")

            # Label-only rules (no category) are stored locally, not in PocketSmith
            if not target_category:
                stats["label_only_rules"] += 1
                logger.debug(f"Label-only rule (local engine): {rule.get('id', 'unknown')}")
                continue

            if target_category not in category_id_map:
                stats["rules_skipped"] += 1
                logger.warning(f"Skipping rule - category not found: {target_category}")
                continue

            category_id = category_id_map[target_category]
            payee_pattern = rule.get("payee_pattern", "")

            # Check if similar rule already exists
            if self._rule_exists(category_id, payee_pattern, existing_rules_map):
                stats["rules_skipped"] += 1
                logger.debug(f"Skipping duplicate rule: {payee_pattern}")
                continue

            if not dry_run:
                self._create_rule(rule, category_id)
            stats["rules_created"] += 1

        return stats

    def _apply_replace(
        self,
        merged_template: Dict[str, Any],
        existing_categories: List[Dict[str, Any]],
        dry_run: bool,
    ) -> Dict[str, Any]:
        """Archive & Replace strategy: Backup existing, apply templates fresh (risky).

        Note: PocketSmith API doesn't support deleting categories or rules,
        so this strategy creates fresh categories with template names.
        Existing categories remain but are not used.

        Args:
            merged_template: Template to apply
            existing_categories: Existing PocketSmith categories (for backup only)
            dry_run: If True, don't actually create anything

        Returns:
            Statistics dictionary
        """
        logger.info("Applying replace strategy (creates fresh, existing data backed up)")

        stats = {
            "categories_created": 0,
            "categories_archived": len(existing_categories),
            "rules_created": 0,
        }

        category_id_map: Dict[str, int] = {}

        # Create all template categories fresh
        for template_cat in merged_template.get("categories", []):
            if not dry_run:
                created_cat = self._create_category(template_cat, category_id_map)
                category_id_map[template_cat["name"]] = created_cat["id"]
            stats["categories_created"] += 1

        # Create all template rules
        for rule in merged_template.get("rules", []):
            target_category = rule.get("target_category")

            if not target_category or target_category not in category_id_map:
                logger.warning(f"Skipping rule - category not found: {target_category}")
                continue

            if not dry_run:
                self._create_rule(rule, category_id_map[target_category])
            stats["rules_created"] += 1

        return stats

    def _build_category_map(self, categories: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Build map of category name to category object.

        Handles hierarchical categories by creating full path names.
        """
        # First, flatten the hierarchy (categories can have nested children)
        flat_categories = []

        def flatten_cats(
            cat_list: List[Dict[str, Any]], parent_id_map: Dict[int, str] | None = None
        ) -> Dict[int, str]:
            if parent_id_map is None:
                parent_id_map = {}
            for cat in cat_list:
                flat_categories.append(cat)
                # Build a map of id -> title for parent lookup
                parent_id_map[cat["id"]] = cat.get("title", cat.get("name", ""))
                if cat.get("children"):
                    flatten_cats(cat["children"], parent_id_map)
            return parent_id_map

        parent_id_map = flatten_cats(categories)

        # Now build the category map with full paths
        category_map = {}
        for cat in flat_categories:
            # Use 'title' from API response (not 'name')
            name = cat.get("title", cat.get("name", ""))

            # Handle parent hierarchy
            if cat.get("parent_id"):
                # Look up parent name from our map
                parent_name = parent_id_map.get(cat["parent_id"])
                if parent_name:
                    name = f"{parent_name}:{name}"

            category_map[name] = cat

        return category_map

    def _build_rules_map(self, categories: List[Dict[str, Any]]) -> Dict[int, List[str]]:
        """Build map of category_id to list of payee patterns."""
        rules_map: Dict[int, List[str]] = {}

        # Flatten categories to include children
        def flatten_cats(cat_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            result: List[Dict[str, Any]] = []
            for cat in cat_list:
                result.append(cat)
                if cat.get("children"):
                    result.extend(flatten_cats(cat["children"]))
            return result

        flat_categories = flatten_cats(categories)

        for category in flat_categories:
            try:
                rules = self.api_client.get_category_rules(category["id"])
                rules_map[category["id"]] = [r.get("payee_matches", "") for r in rules]
            except Exception as e:
                logger.warning(f"Failed to fetch rules for category {category['id']}: {e}")

        return rules_map

    def _find_similar_category(
        self, template_cat: Dict[str, Any], existing_categories: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find similar category using fuzzy matching.

        Matches on:
        - Name similarity (case-insensitive)
        - Description similarity
        """
        template_name = template_cat["name"].lower()
        template_desc = template_cat.get("description", "").lower()

        for existing in existing_categories:
            existing_name = existing.get("title", "").lower()

            # Check for substring match
            if template_name in existing_name or existing_name in template_name:
                return existing

            # Check description similarity
            existing_desc = existing.get("description", "").lower()
            if template_desc and existing_desc:
                if template_desc in existing_desc or existing_desc in template_desc:
                    return existing

        return None

    def _rule_exists(
        self, category_id: int, payee_pattern: str, rules_map: Dict[int, List[str]]
    ) -> bool:
        """Check if a similar rule already exists."""
        existing_patterns = rules_map.get(category_id, [])

        # Exact match
        if payee_pattern in existing_patterns:
            return True

        # Case-insensitive match
        pattern_lower = payee_pattern.lower()
        for existing in existing_patterns:
            if existing.lower() == pattern_lower:
                return True

        return False

    def _create_category(
        self, template_cat: Dict[str, Any], category_id_map: Dict[str, int]
    ) -> Dict[str, Any]:
        """Create a category via API.

        Note: This is a simplified implementation.
        PocketSmith API category creation requires POST to /users/{id}/categories
        with specific payload format.

        For now, this logs the intent. Full implementation would require:
        - POST /users/{user_id}/categories
        - Handle parent_id resolution
        - Handle category type (expense/income)
        """
        assert self.user_id is not None

        cat_name = template_cat["name"]
        parent_name = template_cat.get("parent")

        # Prepare API payload
        payload: Dict[str, Any] = {
            "title": cat_name.split(":")[-1],  # Use last part for nested categories
            "colour": template_cat.get("colour", "#3498db"),
        }

        # Resolve parent_id if parent exists
        if parent_name and parent_name in category_id_map:
            payload["parent_id"] = category_id_map[parent_name]

        logger.info(f"Creating category: {cat_name} (payload: {payload})")

        # Create via API
        created: Dict[str, Any] = self.api_client.post(
            f"/users/{self.user_id}/categories", data=payload
        )

        return created

    def _create_rule(self, rule: Dict[str, Any], category_id: int) -> Dict[str, Any]:
        """Create a category rule via API.

        PocketSmith API only supports simple keyword matching via payee_matches.
        Complex rules should be stored in local rule engine.
        """
        payee_pattern = rule.get("payee_pattern", "")

        if not payee_pattern:
            logger.warning("Skipping rule with empty payee_pattern")
            return {}

        logger.info(f"Creating rule for category {category_id}: {payee_pattern}")

        created_rule = self.api_client.create_category_rule(
            category_id=category_id, payee_matches=payee_pattern
        )
        return created_rule


def main() -> None:
    """CLI interface for template application."""
    parser = argparse.ArgumentParser(description="Apply merged templates to PocketSmith account")
    parser.add_argument(
        "--template", type=Path, required=True, help="Path to merged template JSON file"
    )
    parser.add_argument(
        "--strategy",
        choices=["add_new", "smart_merge", "replace"],
        default="add_new",
        help="Application strategy (default: add_new)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--apply", action="store_true", help="Apply changes (opposite of dry-run)")

    args = parser.parse_args()

    # Determine dry_run mode
    dry_run = args.dry_run or not args.apply

    # Load merged template
    if not args.template.exists():
        print(f"Error: Template file not found: {args.template}", file=sys.stderr)
        sys.exit(1)

    with open(args.template, "r") as f:
        merged_template = json.load(f)

    # Initialize API client
    try:
        api_client = PocketSmithClient()
    except Exception as e:
        print(f"Error: Failed to initialize PocketSmith client: {e}", file=sys.stderr)
        print("Make sure .env file exists with POCKETSMITH_API_KEY", file=sys.stderr)
        sys.exit(1)

    # Initialize backup manager
    backup_manager = BackupManager()

    # Initialize applier
    applier = TemplateApplier(api_client=api_client, backup_manager=backup_manager)

    # Display preview header
    print("=" * 70)
    if dry_run:
        print("Template Application Preview (DRY RUN)")
    else:
        print("Template Application")
    print("=" * 70)
    print(f"Strategy: {args.strategy}")
    print()

    # Apply template
    try:
        result = applier.apply_template(
            merged_template=merged_template, strategy=args.strategy, dry_run=dry_run
        )

        # Display results
        print("\nSummary:")
        print(f"  • {result.get('categories_created', 0)} categories created")
        print(f"  • {result.get('categories_reused', 0)} categories reused")
        print(f"  • {result.get('rules_created', 0)} rules created")
        print(f"  • {result.get('rules_skipped', 0)} rules skipped")

        if not dry_run and result.get("backup_path"):
            print(f"  • Backup saved: {result['backup_path']}")

        print()
        templates_applied = merged_template.get("metadata", {}).get("templates_applied", [])
        if templates_applied:
            print("Templates Applied:")
            for t in templates_applied:
                print(f"  ✓ {t['name']} ({t['layer']}, priority {t['priority']})")

        if dry_run:
            print("\nTo apply these changes, run with --apply flag")
        else:
            print("\n✓ Template application complete!")

    except Exception as e:
        print(f"\nError during template application: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
