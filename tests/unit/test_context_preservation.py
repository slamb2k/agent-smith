"""Tests for context preservation and result aggregation."""

import pytest
from scripts.orchestration.conductor import SubagentConductor, ContextManager, ResultAggregator


def test_context_manager_initialization():
    """Context manager initializes with session state."""
    context = ContextManager(user_id="test-user-123")

    assert context.user_id == "test-user-123"
    assert context.preferences == {}
    assert context.session_state == {}


def test_context_manager_set_preference():
    """Store user preferences."""
    context = ContextManager(user_id="test-user")

    context.set_preference("intelligence_mode", "smart")
    context.set_preference("tax_level", "full")

    assert context.get_preference("intelligence_mode") == "smart"
    assert context.get_preference("tax_level") == "full"


def test_context_manager_session_state():
    """Manage session state across operations."""
    context = ContextManager(user_id="test-user")

    context.update_session_state("last_operation", "categorization")
    context.update_session_state("transactions_processed", 150)

    assert context.get_session_state("last_operation") == "categorization"
    assert context.get_session_state("transactions_processed") == 150


def test_result_aggregator_initialization():
    """Result aggregator initializes empty."""
    aggregator = ResultAggregator()

    assert aggregator.results == []
    assert aggregator.total_operations == 0


def test_result_aggregator_add_result():
    """Add individual subagent result."""
    aggregator = ResultAggregator()

    aggregator.add_result(
        operation="categorization",
        status="success",
        data={"categorized": 50, "skipped": 5},
    )

    assert aggregator.total_operations == 1
    assert len(aggregator.results) == 1
    assert aggregator.results[0]["operation"] == "categorization"


def test_result_aggregator_merge_results():
    """Merge multiple subagent results."""
    aggregator = ResultAggregator()

    # Add results from 3 parallel subagents
    aggregator.add_result("batch1", "success", {"categorized": 30})
    aggregator.add_result("batch2", "success", {"categorized": 40})
    aggregator.add_result("batch3", "success", {"categorized": 25})

    merged = aggregator.merge_results(operation_type="categorization")

    assert merged["status"] == "success"
    assert merged["total_operations"] == 3
    assert merged["aggregated_data"]["categorized"] == 95


def test_result_aggregator_handle_partial_failure():
    """Handle results with partial failures."""
    aggregator = ResultAggregator()

    aggregator.add_result("batch1", "success", {"categorized": 30})
    aggregator.add_result("batch2", "error", {"error": "API timeout"})
    aggregator.add_result("batch3", "success", {"categorized": 25})

    merged = aggregator.merge_results(operation_type="categorization")

    assert merged["status"] == "partial"
    assert merged["successful_operations"] == 2
    assert merged["failed_operations"] == 1


def test_conductor_with_context_preservation():
    """Conductor preserves context during delegation."""
    conductor = SubagentConductor()
    context = ContextManager(user_id="test-user")
    context.set_preference("intelligence_mode", "aggressive")

    prompt = conductor.build_subagent_prompt(
        operation_type="categorization",
        task_description="Categorize transactions",
        data_summary="100 transactions",
        intelligence_mode=context.get_preference("intelligence_mode"),
    )

    assert "Intelligence Mode: aggressive" in prompt
