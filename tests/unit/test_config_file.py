"""Tests for configuration file handling."""

import json
from pathlib import Path
import pytest


def test_config_file_exists():
    """Test that default config.json exists."""
    config_file = Path(__file__).parent.parent.parent / "data" / "config.json"
    assert config_file.exists(), "data/config.json should exist with defaults"


def test_config_file_is_valid_json():
    """Test that config.json is valid JSON."""
    config_file = Path(__file__).parent.parent.parent / "data" / "config.json"

    with open(config_file) as f:
        config = json.load(f)

    assert isinstance(config, dict)


def test_config_has_required_fields():
    """Test that config has all required fields."""
    config_file = Path(__file__).parent.parent.parent / "data" / "config.json"

    with open(config_file) as f:
        config = json.load(f)

    required_fields = [
        "tax_level",
        "intelligence_mode",
        "alerts_enabled",
        "backup_before_mutations",
        "auto_archive",
    ]

    for field in required_fields:
        assert field in config, f"Config must include {field}"


def test_config_default_values():
    """Test config default values match design spec."""
    config_file = Path(__file__).parent.parent.parent / "data" / "config.json"

    with open(config_file) as f:
        config = json.load(f)

    assert config["tax_level"] in ["reference", "smart", "full"]
    assert config["intelligence_mode"] in ["conservative", "smart", "aggressive"]
    assert isinstance(config["backup_before_mutations"], bool)
