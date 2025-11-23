"""Template merging logic for composable template system."""

import argparse
import json
import os
import sys
import yaml
from pathlib import Path
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


def load_template(template_path: Path) -> Dict[str, Any]:
    """Load a YAML template file."""
    with open(template_path, "r") as f:
        data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Template file {template_path} must contain a YAML dictionary")
        return data


def get_plugin_assets_dir() -> Path:
    """Get the plugin assets directory, supporting both dev and installed modes."""
    # Check if running from plugin
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root) / "assets"

    # Development mode - check if we're in the plugin structure
    script_dir = Path(__file__).parent

    # If scripts/setup/template_merger.py, go up to find assets
    if (script_dir.parent.parent / "assets" / "templates").exists():
        return script_dir.parent.parent / "assets"

    # Otherwise use agent-smith-plugin structure
    return script_dir.parent.parent / "agent-smith-plugin" / "skills" / "agent-smith" / "assets"


def main() -> None:
    """CLI interface for template merging."""
    parser = argparse.ArgumentParser(
        description="Merge Agent Smith templates into a single configuration"
    )
    parser.add_argument(
        "--primary",
        required=True,
        help="Primary income template (e.g., payg-employee, sole-trader)",
    )
    parser.add_argument(
        "--living",
        help="Living arrangement templates, comma-separated (e.g., shared-hybrid)",
    )
    parser.add_argument(
        "--additional",
        help="Additional income templates, comma-separated (e.g., property-investor)",
    )
    parser.add_argument(
        "--config", type=Path, help="Path to template_config.json with label customizations"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="Output path for merged template JSON"
    )

    args = parser.parse_args()

    # Get templates directory
    templates_dir = get_plugin_assets_dir() / "templates"

    if not templates_dir.exists():
        print(f"Error: Templates directory not found: {templates_dir}", file=sys.stderr)
        sys.exit(1)

    # Load templates
    templates = []

    # Load primary template
    primary_file = templates_dir / "primary" / f"{args.primary}.yaml"
    if not primary_file.exists():
        print(f"Error: Primary template not found: {primary_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading primary: {args.primary}")
    templates.append(load_template(primary_file))

    # Load living templates
    if args.living:
        for living in args.living.split(","):
            living = living.strip()
            living_file = templates_dir / "living" / f"{living}.yaml"
            if not living_file.exists():
                print(f"Error: Living template not found: {living_file}", file=sys.stderr)
                sys.exit(1)
            print(f"Loading living: {living}")
            templates.append(load_template(living_file))

    # Load additional templates
    if args.additional:
        for additional in args.additional.split(","):
            additional = additional.strip()
            additional_file = templates_dir / "additional" / f"{additional}.yaml"
            if not additional_file.exists():
                print(f"Error: Additional template not found: {additional_file}", file=sys.stderr)
                sys.exit(1)
            print(f"Loading additional: {additional}")
            templates.append(load_template(additional_file))

    # Merge templates
    print("\nMerging templates...")
    merger = TemplateMerger()
    merged = merger.merge(templates)

    # Save merged template
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(merged, f, indent=2)

    print(f"\n✓ Merged template saved to: {args.output}")
    print("\nTemplates merged:")
    for t in merged["metadata"]["templates_applied"]:
        print(f"  • {t['name']} ({t['layer']}, priority {t['priority']})")

    print("\nSummary:")
    print(f"  • {len(merged['categories'])} categories")
    print(f"  • {len(merged['rules'])} rules")
    print(f"  • {len(merged['labels'])} labels")
    print(f"  • {len(merged['alerts'])} alerts")


if __name__ == "__main__":
    main()
