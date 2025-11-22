"""Template selector for initial Agent Smith setup."""

import shutil
from pathlib import Path
from typing import Dict


class TemplateSelector:
    """Select and apply rule templates based on household type."""

    def __init__(self) -> None:
        """Initialize template selector."""
        self.templates_dir = Path(__file__).parent.parent.parent / "data" / "templates"
        self.rules_file = Path(__file__).parent.parent.parent / "data" / "rules.yaml"

    def list_templates(self) -> Dict[str, Dict[str, str]]:
        """List available templates with metadata.

        Returns:
            Dict mapping template names to metadata
        """
        templates = {
            "simple": {
                "name": "Simple - Single Person",
                "description": "Basic categories for individual financial tracking",
                "best_for": "Single person, no shared expenses",
            },
            "separated-families": {
                "name": "Separated Families",
                "description": "Kids expenses, child support, contributor tracking",
                "best_for": "Divorced/separated parents with shared custody",
            },
            "shared-household": {
                "name": "Shared Household",
                "description": "Shared expense tracking with approval workflows",
                "best_for": "Couples, roommates, or families",
            },
            "advanced": {
                "name": "Advanced",
                "description": "Tax optimization and investment management",
                "best_for": "Business owners, investors, complex finances",
            },
        }

        return templates

    def apply_template(self, template_name: str, backup: bool = True) -> None:
        """Apply a template to rules.yaml.

        Args:
            template_name: Name of template (simple, separated-families, etc.)
            backup: Whether to backup existing rules.yaml

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_file = self.templates_dir / f"{template_name}.yaml"

        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")

        # Backup existing rules if requested
        if backup and self.rules_file.exists():
            backup_file = self.rules_file.with_suffix(".yaml.backup")
            shutil.copy(self.rules_file, backup_file)
            print(f"Backed up existing rules to {backup_file}")

        # Copy template to rules.yaml
        shutil.copy(template_file, self.rules_file)
        print(f"Applied template: {template_name}")
        print(f"Rules file: {self.rules_file}")


def main() -> None:
    """Interactive template selection."""
    selector = TemplateSelector()

    print("=" * 70)
    print("Agent Smith - Rule Template Setup")
    print("=" * 70)
    print()

    templates = selector.list_templates()

    print("Available templates:")
    for i, (key, info) in enumerate(templates.items(), 1):
        print(f"\n{i}. {info['name']}")
        print(f"   {info['description']}")
        print(f"   Best for: {info['best_for']}")

    print()
    choice = input("Select template (1-4): ").strip()

    template_map = {
        "1": "simple",
        "2": "separated-families",
        "3": "shared-household",
        "4": "advanced",
    }

    template_name = template_map.get(choice)

    if not template_name:
        print("Invalid choice. Exiting.")
        return

    print()
    print(f"Applying template: {templates[template_name]['name']}")
    selector.apply_template(template_name)

    print()
    print("✓ Template applied successfully!")
    print()
    print("Next steps:")
    print("1. Review data/rules.yaml and customize for your needs")
    print("2. Update merchant patterns for your region")
    print("3. Adjust account names to match your PocketSmith setup")
    print("4. Run: /agent-smith-categorize --mode=dry-run to test")


if __name__ == "__main__":
    main()
