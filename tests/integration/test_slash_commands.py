"""Integration tests for Agent Smith slash commands."""

import pytest
from pathlib import Path


pytestmark = pytest.mark.integration


class TestSlashCommands:
    """Test slash command files exist and are properly formatted."""

    def test_install_command_exists(self):
        """Install command file exists in plugin directory."""
        cmd_path = Path("agent-smith-plugin/commands/install.md")
        assert cmd_path.exists(), "install.md command file not found in plugin"

    def test_install_command_content(self):
        """Install command has proper content structure."""
        cmd_path = Path("agent-smith-plugin/commands/install.md")
        content = cmd_path.read_text()

        # Check for key sections
        assert "Agent Smith" in content
        assert "onboarding" in content.lower() or "installation" in content.lower()
        assert "PocketSmith" in content

    def test_commands_directory_structure(self):
        """Commands directory in plugin has all required command files."""
        commands_dir = Path("agent-smith-plugin/commands")
        assert commands_dir.exists(), "Plugin commands directory not found"

        # These are the actual command files in the plugin
        expected_commands = [
            "install.md",
            "categorize.md",
            "analyze.md",
            "scenario.md",
            "report.md",
            "optimize.md",
            "tax.md",
            "health.md",
        ]

        for cmd_file in expected_commands:
            cmd_path = commands_dir / cmd_file
            assert cmd_path.exists(), f"Command file {cmd_file} not found in plugin"
