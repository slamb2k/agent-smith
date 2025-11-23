"""Template selector for composable template system."""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, List, Any

from scripts.setup.template_merger import TemplateMerger


class TemplateSelector:
    """Select and merge composable rule templates."""

    def __init__(self) -> None:
        """Initialize template selector."""
        # When running as installed plugin, use CLAUDE_PLUGIN_ROOT
        plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if plugin_root:
            self.templates_dir = Path(plugin_root) / "assets" / "templates"
        else:
            # Development mode: look in plugin directory within repository
            self.templates_dir = (
                Path(__file__).parent.parent.parent
                / "agent-smith-plugin"
                / "skills"
                / "agent-smith"
                / "assets"
                / "templates"
            )
        self.output_file = Path(__file__).parent.parent.parent / "data" / "config.json"

    def list_templates(self) -> Dict[str, List[Dict[str, str]]]:
        """List available templates by layer.

        Returns:
            Dict with 'primary', 'living', 'additional' keys, each containing list of template info
        """
        templates: Dict[str, List[Dict[str, str]]] = {
            "primary": [],
            "living": [],
            "additional": [],
        }

        for layer in ["primary", "living", "additional"]:
            layer_dir = self.templates_dir / layer
            if not layer_dir.exists():
                continue

            for template_file in sorted(layer_dir.glob("*.yaml")):
                with open(template_file) as f:
                    data: Any = yaml.safe_load(f)

                templates[layer].append(
                    {
                        "id": template_file.stem,
                        "name": (
                            data.get("name", template_file.stem)
                            if isinstance(data, dict)
                            else template_file.stem
                        ),
                        "description": (
                            data.get("description", "").strip() if isinstance(data, dict) else ""
                        ),
                        "file": str(template_file),
                    }
                )

        return templates

    def load_template(self, template_path: Path) -> Dict[str, Any]:
        """Load a template YAML file.

        Args:
            template_path: Path to template YAML file

        Returns:
            Template data dictionary
        """
        with open(template_path) as f:
            data: Any = yaml.safe_load(f)
            if not isinstance(data, dict):
                return {}
            return data

    def apply_templates(
        self,
        primary: str,
        living: str,
        additional: List[str],
    ) -> Dict[str, Any]:
        """Apply selected templates and merge them.

        Args:
            primary: Primary template ID (e.g., 'payg-employee')
            living: Living template ID (e.g., 'single')
            additional: List of additional template IDs (e.g., ['property-investor'])

        Returns:
            Merged configuration dictionary

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        templates_to_merge: List[Dict[str, Any]] = []

        # Load primary template
        primary_file = self.templates_dir / "primary" / f"{primary}.yaml"
        if not primary_file.exists():
            raise FileNotFoundError(f"Primary template not found: {primary}")
        templates_to_merge.append(self.load_template(primary_file))

        # Load living template
        living_file = self.templates_dir / "living" / f"{living}.yaml"
        if not living_file.exists():
            raise FileNotFoundError(f"Living template not found: {living}")
        templates_to_merge.append(self.load_template(living_file))

        # Load additional templates
        for addon in additional:
            addon_file = self.templates_dir / "additional" / f"{addon}.yaml"
            if not addon_file.exists():
                raise FileNotFoundError(f"Additional template not found: {addon}")
            templates_to_merge.append(self.load_template(addon_file))

        # Merge templates
        merger = TemplateMerger()
        merged_config = merger.merge(templates_to_merge)

        return merged_config

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save merged configuration to JSON.

        Args:
            config: Merged configuration dictionary
        """
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✓ Configuration saved to {self.output_file}")


def main() -> None:
    """Interactive composable template selection."""
    selector = TemplateSelector()

    print("=" * 70)
    print("Agent Smith - Composable Template Setup")
    print("=" * 70)
    print()

    templates = selector.list_templates()

    # Select primary template
    print("STEP 1: Select PRIMARY income structure (choose ONE):")
    print()
    for i, template in enumerate(templates["primary"], 1):
        print(f"{i}. {template['name']}")
        if template["description"]:
            print(f"   {template['description']}")
    print()

    primary_choice = input(f"Select primary template (1-{len(templates['primary'])}): ").strip()
    try:
        primary_idx = int(primary_choice) - 1
        primary_id = templates["primary"][primary_idx]["id"]
    except (ValueError, IndexError):
        print("Invalid choice. Exiting.")
        return

    # Select living template
    print()
    print("STEP 2: Select LIVING arrangement (choose ONE):")
    print()
    for i, template in enumerate(templates["living"], 1):
        print(f"{i}. {template['name']}")
        if template["description"]:
            print(f"   {template['description']}")
    print()

    living_choice = input(f"Select living template (1-{len(templates['living'])}): ").strip()
    try:
        living_idx = int(living_choice) - 1
        living_id = templates["living"][living_idx]["id"]
    except (ValueError, IndexError):
        print("Invalid choice. Exiting.")
        return

    # Select additional templates
    print()
    print("STEP 3: Select ADDITIONAL income sources (choose MULTIPLE or 0 for none):")
    print()
    for i, template in enumerate(templates["additional"], 1):
        print(f"{i}. {template['name']}")
        if template["description"]:
            print(f"   {template['description']}")
    print()

    additional_choices = input(
        "Select additional templates (comma-separated, or 0 for none): "
    ).strip()

    additional_ids: List[str] = []
    if additional_choices and additional_choices != "0":
        for choice in additional_choices.split(","):
            try:
                idx = int(choice.strip()) - 1
                additional_ids.append(templates["additional"][idx]["id"])
            except (ValueError, IndexError):
                print(f"Warning: Skipping invalid choice '{choice}'")

    # Apply templates
    print()
    print("Applying templates:")
    print(f"  Primary: {primary_id}")
    print(f"  Living: {living_id}")
    if additional_ids:
        print(f"  Additional: {', '.join(additional_ids)}")
    else:
        print("  Additional: (none)")
    print()

    merged_config = selector.apply_templates(primary_id, living_id, additional_ids)
    selector.save_config(merged_config)

    print()
    print("✓ Templates applied successfully!")
    print()
    print("Merged configuration includes:")
    print(f"  - {len(merged_config.get('categories', []))} categories")
    print(f"  - {len(merged_config.get('rules', []))} categorization rules")
    print(f"  - {len(merged_config.get('labels', []))} labels")
    print(f"  - {len(merged_config.get('alerts', []))} alerts")
    print()
    print("Next steps:")
    print("1. Review data/config.json and customize for your needs")
    print("2. Run: /agent-smith-categorize --mode=dry-run to test")


if __name__ == "__main__":
    main()
