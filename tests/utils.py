"""Shared test utilities."""

import os
from pathlib import Path


def get_asset_path(*path_parts: str) -> Path:
    """Get the full path to an asset file (templates, tax data, etc.).

    This function handles both development mode (running tests in the repository)
    and installed plugin mode (using CLAUDE_PLUGIN_ROOT).

    Args:
        *path_parts: Path components relative to the assets directory.
                     Example: 'templates', 'primary', 'payg-employee.yaml'
                     Or: 'tax', 'ato_category_mappings.json'

    Returns:
        Full path to the asset file

    Examples:
        >>> get_asset_path('templates', 'primary', 'payg-employee.yaml')
        PosixPath('.../agent-smith-plugin/skills/agent-smith/assets/templates/primary/payg-employee.yaml')

        >>> get_asset_path('tax', 'deduction_patterns.json')
        PosixPath('.../agent-smith-plugin/skills/agent-smith/assets/tax/deduction_patterns.json')
    """
    # When running as installed plugin, use CLAUDE_PLUGIN_ROOT
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root) / "assets" / Path(*path_parts)
    else:
        # Development mode: look in plugin directory within repository
        project_root = Path(__file__).parent.parent
        return (
            project_root
            / "agent-smith-plugin"
            / "skills"
            / "agent-smith"
            / "assets"
            / Path(*path_parts)
        )
