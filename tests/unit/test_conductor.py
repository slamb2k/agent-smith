"""Tests for subagent conductor orchestration logic."""

import pytest
from scripts.orchestration.conductor import (
    SubagentConductor,
    OperationType,
    should_delegate,
)


def test_should_delegate_bulk_processing():
    """Bulk processing always delegates."""
    result = should_delegate(
        operation_type=OperationType.BULK_PROCESSING,
        transaction_count=50,
        estimated_tokens=2000,
        can_parallelize=False,
    )
    assert result is True


def test_should_delegate_high_transaction_count():
    """Over 100 transactions delegates."""
    result = should_delegate(
        operation_type=OperationType.SIMPLE_QUERY,
        transaction_count=150,
        estimated_tokens=2000,
        can_parallelize=False,
    )
    assert result is True


def test_should_delegate_high_token_estimate():
    """Over 5000 tokens delegates."""
    result = should_delegate(
        operation_type=OperationType.SIMPLE_QUERY,
        transaction_count=50,
        estimated_tokens=6000,
        can_parallelize=False,
    )
    assert result is True


def test_should_delegate_parallelizable():
    """Parallelizable operations delegate."""
    result = should_delegate(
        operation_type=OperationType.SIMPLE_QUERY,
        transaction_count=50,
        estimated_tokens=2000,
        can_parallelize=True,
    )
    assert result is True


def test_should_not_delegate_simple_query():
    """Simple queries stay in main context."""
    result = should_delegate(
        operation_type=OperationType.SIMPLE_QUERY,
        transaction_count=20,
        estimated_tokens=1000,
        can_parallelize=False,
    )
    assert result is False


def test_conductor_initialization():
    """Conductor initializes with default settings."""
    conductor = SubagentConductor()

    assert conductor.transaction_threshold == 100
    assert conductor.token_threshold == 5000
    assert conductor.dry_run is False


def test_conductor_custom_thresholds():
    """Conductor accepts custom thresholds."""
    conductor = SubagentConductor(
        transaction_threshold=200,
        token_threshold=10000,
        dry_run=True,
    )

    assert conductor.transaction_threshold == 200
    assert conductor.token_threshold == 10000
    assert conductor.dry_run is True


def test_estimate_operation_complexity():
    """Estimate tokens for an operation."""
    conductor = SubagentConductor()

    result = conductor.estimate_complexity(
        operation_type=OperationType.CATEGORIZATION,
        transaction_count=100,
        period_months=3,
    )

    assert "estimated_tokens" in result
    assert "can_parallelize" in result
    assert "suggested_subagents" in result
    assert result["estimated_tokens"] > 0


def test_build_subagent_prompt():
    """Build delegation prompt for subagent."""
    conductor = SubagentConductor()

    prompt = conductor.build_subagent_prompt(
        operation_type="categorization",
        task_description="Categorize 150 uncategorized transactions",
        data_summary="150 transactions from Nov 2025",
        intelligence_mode="smart",
        constraints={"dry_run": True},
    )

    assert "categorization agent" in prompt.lower()
    assert "150 transactions" in prompt
    assert "intelligence mode: smart" in prompt.lower()
    assert "dry_run: true" in prompt.lower()
