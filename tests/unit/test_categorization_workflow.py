"""Tests for categorization workflow."""

import pytest
from scripts.workflows.categorization import (
    CategorizationWorkflow,
    parse_categorize_args,
)


def test_parse_categorize_args_defaults():
    """Parse categorization args with defaults."""
    args = parse_categorize_args([])

    assert args["mode"] == "smart"
    assert args["period"] is None
    assert args["account"] is None
    assert args["dry_run"] is False


def test_parse_categorize_args_with_mode():
    """Parse mode argument."""
    args = parse_categorize_args(["--mode=aggressive"])

    assert args["mode"] == "aggressive"


def test_parse_categorize_args_with_period():
    """Parse period argument."""
    args = parse_categorize_args(["--period=2025-11"])

    assert args["period"] == "2025-11"


def test_parse_categorize_args_with_dry_run():
    """Parse dry-run flag."""
    args = parse_categorize_args(["--dry-run"])

    assert args["dry_run"] is True


def test_categorization_workflow_initialization():
    """Workflow initializes with API client."""
    from scripts.core.api_client import PocketSmithClient

    client = PocketSmithClient(api_key="test-key")
    workflow = CategorizationWorkflow(client)

    assert workflow.client == client
    assert workflow.mode == "smart"


def test_categorization_workflow_should_use_subagent():
    """Determine if should use subagent for categorization."""
    from scripts.core.api_client import PocketSmithClient

    client = PocketSmithClient(api_key="test-key")
    workflow = CategorizationWorkflow(client)

    # Large transaction count should delegate
    result = workflow.should_use_subagent(transaction_count=150)
    assert result is True

    # Small transaction count should not
    result = workflow.should_use_subagent(transaction_count=20)
    assert result is False


def test_categorization_workflow_build_summary():
    """Build summary of categorization results."""
    from scripts.core.api_client import PocketSmithClient

    client = PocketSmithClient(api_key="test-key")
    workflow = CategorizationWorkflow(client)

    results = {
        "categorized": 85,
        "skipped": 15,
        "rules_applied": 12,
        "new_rules": 3,
    }

    summary = workflow.build_summary(results, total=100)

    assert "85/100" in summary
    assert "85.0%" in summary
    assert "Rules applied: 12" in summary
    assert "New rules created: 3" in summary
