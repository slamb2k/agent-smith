"""Integration tests for Agent Smith slash commands."""

import pytest
from pathlib import Path


pytestmark = pytest.mark.integration


class TestSlashCommands:
    """Test slash command files exist and are properly formatted."""

    def test_main_command_exists(self):
        """Main agent-smith command file exists."""
        cmd_path = Path(".claude/commands/agent-smith.md")
        assert cmd_path.exists(), "agent-smith.md command file not found"

    def test_main_command_content(self):
        """Main command has proper content structure."""
        cmd_path = Path(".claude/commands/agent-smith.md")
        content = cmd_path.read_text()

        # Check for key sections
        assert "Agent Smith" in content
        assert "financial management" in content.lower()
        assert "PocketSmith" in content

        # Check for subcommands reference
        assert "categorize" in content.lower()
        assert "analyze" in content.lower()
        assert "scenario" in content.lower()

    def test_commands_directory_structure(self):
        """Commands directory has all 8 slash command files."""
        commands_dir = Path(".claude/commands")
        assert commands_dir.exists()

        expected_commands = [
            "agent-smith.md",
            "agent-smith-categorize.md",
            "agent-smith-analyze.md",
            "agent-smith-scenario.md",
            "agent-smith-report.md",
            "agent-smith-optimize.md",
            "agent-smith-tax.md",
            "agent-smith-health.md",
        ]

        for cmd_file in expected_commands:
            cmd_path = commands_dir / cmd_file
            assert cmd_path.exists(), f"Command file {cmd_file} not found"
