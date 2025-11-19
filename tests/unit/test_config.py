"""Tests for configuration validation."""
import os
from pathlib import Path


def test_env_sample_exists():
    """Verify .env.sample template exists."""
    env_sample = Path(__file__).parent.parent.parent / ".env.sample"
    assert env_sample.exists(), ".env.sample template must exist"


def test_env_sample_contains_required_fields():
    """Verify .env.sample has all required configuration fields."""
    env_sample = Path(__file__).parent.parent.parent / ".env.sample"
    content = env_sample.read_text()

    required_fields = [
        "POCKETSMITH_API_KEY",
        "TAX_INTELLIGENCE_LEVEL",
        "DEFAULT_INTELLIGENCE_MODE",
        "TAX_JURISDICTION",
        "FINANCIAL_YEAR_END",
    ]

    for field in required_fields:
        assert field in content, f"{field} must be in .env.sample"


def test_env_sample_has_no_real_credentials():
    """Verify .env.sample doesn't contain real API keys."""
    env_sample = Path(__file__).parent.parent.parent / ".env.sample"
    content = env_sample.read_text()

    # Real API keys are hexadecimal and long
    assert "<Your" in content or "your-" in content, \
        ".env.sample should use placeholders, not real keys"
