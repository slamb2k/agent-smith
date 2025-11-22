"""Template merging logic for composable template system."""

from typing import Dict, Any, List, Set
from datetime import datetime


class TemplateMerger:
    """Merges multiple templates into a single configuration."""

    def merge(self, templates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple templates into single configuration.

        Templates are merged in priority order (lower priority number = higher precedence).
        Categories are deduplicated by name.
        Labels are deduplicated by name.
        Rules, alerts are appended from all templates.
        Tax tracking is merged with later templates overriding earlier ones.

        Args:
            templates: List of template dictionaries to merge

        Returns:
            Merged configuration dictionary
        """
        # Sort by priority (lower number = higher priority)
        sorted_templates = sorted(
            templates, key=lambda t: t.get("metadata", {}).get("priority", 999)
        )

        merged: Dict[str, Any] = {
            "categories": [],
            "rules": [],
            "tax_tracking": {},
            "alerts": [],
            "labels": [],
            "metadata": {
                "templates_applied": [],
                "generated_date": datetime.now().isoformat(),
            },
        }

        # Track category names to avoid duplicates
        seen_categories: Set[str] = set()

        # Track label names to avoid duplicates
        seen_labels: Set[str] = set()

        for template in sorted_templates:
            # Merge categories (deduplicate by name)
            for category in template.get("categories", []):
                cat_name = category["name"]
                if cat_name not in seen_categories:
                    merged["categories"].append(category)
                    seen_categories.add(cat_name)

            # Merge labels (deduplicate by name)
            for label in template.get("labels", []):
                label_name = label["name"]
                if label_name not in seen_labels:
                    merged["labels"].append(label)
                    seen_labels.add(label_name)

            # Append all rules (no deduplication)
            merged["rules"].extend(template.get("rules", []))

            # Merge tax tracking (later templates override)
            merged["tax_tracking"].update(template.get("tax_tracking", {}))

            # Append all alerts
            merged["alerts"].extend(template.get("alerts", []))

            # Track which templates were applied
            merged["metadata"]["templates_applied"].append(
                {
                    "name": template["name"],
                    "layer": template["layer"],
                    "priority": template.get("metadata", {}).get("priority", 999),
                }
            )

        return merged
