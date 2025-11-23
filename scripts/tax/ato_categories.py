"""ATO category mapping for Australian tax compliance."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ATOCategoryMapper:
    """Maps PocketSmith categories to ATO tax return categories."""

    def __init__(self, mappings_file: Optional[Path] = None):
        """Initialize ATO category mapper.

        Args:
            mappings_file: Path to ATO category mappings JSON file
        """
        if mappings_file is None:
            # When running as installed plugin, use CLAUDE_PLUGIN_ROOT
            plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
            if plugin_root:
                mappings_file = Path(plugin_root) / "assets" / "tax" / "ato_category_mappings.json"
            else:
                # Development mode: look in plugin directory within repository
                project_root = Path(__file__).parent.parent.parent
                mappings_file = (
                    project_root
                    / "agent-smith-plugin"
                    / "skills"
                    / "agent-smith"
                    / "assets"
                    / "tax"
                    / "ato_category_mappings.json"
                )

        self.mappings_file = Path(mappings_file)
        self.mappings: Dict[str, Dict[str, Any]] = {}
        self.ato_categories: List[Dict[str, str]] = []

        if self.mappings_file.exists():
            self.load_mappings()

    def load_mappings(self) -> None:
        """Load ATO category mappings from JSON file."""
        if not self.mappings_file.exists():
            logger.warning(f"Mappings file not found: {self.mappings_file}")
            return

        try:
            with open(self.mappings_file) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in mappings file {self.mappings_file}: {e}")
            raise ValueError(f"Failed to parse ATO category mappings: {e}") from e
        except Exception as e:
            logger.error(f"Error reading mappings file {self.mappings_file}: {e}")
            raise

        # Validate required top-level fields
        if "mappings" not in data:
            raise ValueError(f"Missing required 'mappings' field in {self.mappings_file}")
        if "ato_categories" not in data:
            raise ValueError(f"Missing required 'ato_categories' field in {self.mappings_file}")

        # Build lookup dictionary
        for idx, mapping in enumerate(data.get("mappings", [])):
            # Validate required fields
            if "pocketsmith_category" not in mapping:
                raise ValueError(f"Missing 'pocketsmith_category' in mapping {idx}")
            if "ato_category" not in mapping:
                raise ValueError(f"Missing 'ato_category' in mapping {idx}")
            if "deductible" not in mapping:
                raise ValueError(f"Missing 'deductible' in mapping {idx}")

            category = mapping["pocketsmith_category"]
            self.mappings[category] = {
                "ato_code": mapping.get("ato_code"),
                "ato_category": mapping.get("ato_category"),
                "deductible": mapping.get("deductible", False),
                "notes": mapping.get("notes", ""),
                "substantiation_required": mapping.get("substantiation_required", False),
                "threshold": mapping.get("threshold"),
            }

        self.ato_categories = data.get("ato_categories", [])

        logger.info(f"Loaded {len(self.mappings)} ATO category mappings")

    def get_ato_category(self, category_name: str) -> Dict[str, Any]:
        """Get ATO category information for a PocketSmith category.

        Args:
            category_name: PocketSmith category name

        Returns:
            Dict with ato_code, ato_category, deductible, notes, etc.
        """
        if category_name in self.mappings:
            return self.mappings[category_name]

        # Return default for unmapped categories
        return {
            "ato_code": None,
            "ato_category": "Uncategorized",
            "deductible": False,
            "notes": "No ATO category mapping found. Consult a tax professional.",
            "substantiation_required": False,
            "threshold": None,
        }

    def get_all_ato_categories(self) -> List[Dict[str, str]]:
        """Get list of all ATO tax return categories.

        Returns:
            List of dicts with code, name, schedule
        """
        return self.ato_categories

    def get_deductible_categories(self) -> List[str]:
        """Get list of PocketSmith categories that are tax deductible.

        Returns:
            List of category names
        """
        return [cat for cat, info in self.mappings.items() if info["deductible"]]
