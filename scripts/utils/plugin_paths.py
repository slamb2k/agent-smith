"""Plugin-aware path resolution utilities.

This module provides centralized path resolution for Agent Smith, supporting both:
1. Development mode: Running from the repository
2. Plugin mode: Running as an installed Claude Code plugin
"""

import os
from pathlib import Path
from typing import Optional


def get_plugin_root() -> Optional[Path]:
    """Get the plugin root directory if running as an installed plugin.

    Returns:
        Path to plugin root if CLAUDE_PLUGIN_ROOT is set, None otherwise
    """
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    return Path(plugin_root) if plugin_root else None


def get_project_root() -> Path:
    """Get the project root directory.

    In plugin mode, returns CLAUDE_PLUGIN_ROOT.
    In development mode, returns the repository root (3 levels up from this file).

    Returns:
        Path to project root directory
    """
    plugin_root = get_plugin_root()
    if plugin_root:
        return plugin_root
    else:
        # Development mode: scripts/utils/plugin_paths.py -> go up 3 levels
        return Path(__file__).parent.parent.parent


def get_asset_path(*path_parts: str) -> Path:
    """Get the full path to an asset file (templates, tax data, etc.).

    This function handles both development mode (running from repository)
    and installed plugin mode (using CLAUDE_PLUGIN_ROOT).

    Args:
        *path_parts: Path components relative to the assets directory.
                     Example: 'templates', 'primary', 'payg-employee.yaml'
                     Or: 'tax', 'ato_category_mappings.json'

    Returns:
        Full path to the asset file
    """
    plugin_root = get_plugin_root()
    if plugin_root:
        # Plugin mode: assets/ is directly under plugin root
        return plugin_root / "assets" / Path(*path_parts)
    else:
        # Development mode: assets/ is in agent-smith-plugin/skills/agent-smith/
        return (
            get_project_root()
            / "agent-smith-plugin"
            / "skills"
            / "agent-smith"
            / "assets"
            / Path(*path_parts)
        )


def get_data_path(*path_parts: str) -> Path:
    """Get the full path to a data file (config, rules, backups, etc.).

    Data files are always stored in the user's working directory (USER_CWD),
    NOT in the plugin directory. This allows users to have their own data
    separate from the plugin installation.

    Args:
        *path_parts: Path components relative to the data directory.
                     Example: 'config.json'
                     Or: 'backups', '2025-11-23_backup.tar.gz'

    Returns:
        Full path to the data file in user's working directory
    """
    # Always use USER_CWD for data files (or current directory if not set)
    user_cwd = os.environ.get("USER_CWD", os.getcwd())
    return Path(user_cwd) / "data" / Path(*path_parts)


def get_script_path(*path_parts: str) -> Path:
    """Get the full path to a Python script in the scripts/ directory.

    Args:
        *path_parts: Path components relative to the scripts directory.
                     Example: 'onboarding', 'discovery.py'
                     Or: 'core', 'api_client.py'

    Returns:
        Full path to the script file
    """
    plugin_root = get_plugin_root()
    if plugin_root:
        return plugin_root / "scripts" / Path(*path_parts)
    else:
        return get_project_root() / "scripts" / Path(*path_parts)
