"""Initialize data directory from assets templates."""

import shutil
from pathlib import Path


def initialize_data_from_assets() -> None:
    """Copy seed files from assets/ to data/ if data/ is empty.

    This ensures the skill has working runtime data on first run.
    Seed files that remain in assets/ (tax mappings, etc.) are referenced directly.
    """
    project_root = Path(__file__).parent.parent.parent
    assets_dir = project_root / "assets"
    data_dir = project_root / "data"

    # Ensure data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)

    # Files to copy from assets to data for runtime use
    seed_files = [
        ("config.json", "config.json"),
        ("local_rules.json", "local_rules.json"),
        ("platform_rules.json", "platform_rules.json"),
        ("onboarding_state.json", "onboarding_state.json"),
    ]

    for source_name, dest_name in seed_files:
        source = assets_dir / source_name
        dest = data_dir / dest_name

        # Only copy if destination doesn't exist (don't overwrite user data)
        if source.exists() and not dest.exists():
            shutil.copy2(source, dest)
            print(f"Initialized {dest} from {source}")

    # Create empty subdirectories if they don't exist
    subdirs = [
        "cache",
        "tax",
        "merchants",
        "scenarios",
        "scenarios/scenario_results",
        "health",
        "health/health_history",
        "goals",
        "investments",
        "alerts",
        "audit",
    ]

    for subdir in subdirs:
        (data_dir / subdir).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    initialize_data_from_assets()
