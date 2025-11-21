"""Integration tests for orchestration and workflows."""

import os
import pytest
from scripts.orchestration.conductor import (
    SubagentConductor,
    OperationType,
    ContextManager,
    ResultAggregator,
)
from scripts.workflows.categorization import CategorizationWorkflow
from scripts.core.api_client import PocketSmithClient


pytestmark = pytest.mark.integration


@pytest.fixture
def api_client():
    """Create API client with real credentials."""
    api_key = os.getenv("POCKETSMITH_API_KEY")
    if not api_key:
        pytest.skip("POCKETSMITH_API_KEY not set - skipping integration tests")

    return PocketSmithClient(api_key=api_key)


class TestOrchestrationIntegration:
    """Test orchestration with real workflow scenarios."""

    def test_conductor_categorization_workflow(self, api_client):
        """Test conductor with categorization workflow."""
        # Initialize context
        user = api_client.get_user()
        context = ContextManager(user_id=str(user["id"]))
        context.set_preference("intelligence_mode", "smart")

        # Create categorization workflow
        workflow = CategorizationWorkflow(api_client, mode="smart")

        # Check if should delegate (simulate 150 transactions)
        should_delegate = workflow.should_use_subagent(transaction_count=150)
        assert should_delegate is True

        print("✓ Conductor correctly delegates large categorization batch")

    def test_conductor_small_operation_direct(self, api_client):
        """Test conductor keeps small operations in main context."""
        workflow = CategorizationWorkflow(api_client, mode="smart")

        # Check if should delegate (simulate 20 transactions)
        should_delegate = workflow.should_use_subagent(transaction_count=20)
        assert should_delegate is False

        print("✓ Conductor correctly handles small operations directly")

    def test_complexity_estimation(self):
        """Test operation complexity estimation."""
        conductor = SubagentConductor()

        # Estimate categorization complexity with large transaction count
        result = conductor.estimate_complexity(
            operation_type=OperationType.CATEGORIZATION,
            transaction_count=250,  # > 200 enables parallelization
            period_months=1,
        )

        assert result["estimated_tokens"] > 0
        assert "can_parallelize" in result
        assert "suggested_subagents" in result

        # Large transaction count should enable parallelization
        assert result["can_parallelize"] is True

        print(f"✓ Estimated {result['estimated_tokens']} tokens for 250 transactions")

    def test_context_preservation_across_operations(self, api_client):
        """Test context preservation across multiple operations."""
        user = api_client.get_user()
        context = ContextManager(user_id=str(user["id"]))

        # Set preferences
        context.set_preference("intelligence_mode", "aggressive")
        context.set_preference("tax_level", "full")

        # Simulate operation
        context.update_session_state("last_operation", "categorization")
        context.update_session_state("transactions_processed", 150)

        # Verify preservation
        assert context.get_preference("intelligence_mode") == "aggressive"
        assert context.get_preference("tax_level") == "full"
        assert context.get_session_state("transactions_processed") == 150

        print("✓ Context preserved across operations")

    def test_result_aggregation_parallel_batches(self):
        """Test result aggregation from parallel subagents."""
        aggregator = ResultAggregator()

        # Simulate 3 parallel batches
        aggregator.add_result("batch1", "success", {"categorized": 50, "skipped": 5})
        aggregator.add_result("batch2", "success", {"categorized": 45, "skipped": 3})
        aggregator.add_result("batch3", "success", {"categorized": 40, "skipped": 7})

        # Merge results
        merged = aggregator.merge_results(operation_type="categorization")

        assert merged["status"] == "success"
        assert merged["total_operations"] == 3
        assert merged["successful_operations"] == 3
        assert merged["aggregated_data"]["categorized"] == 135
        assert merged["aggregated_data"]["skipped"] == 15

        print("✓ Successfully aggregated results from 3 parallel batches")

    def test_subagent_prompt_building(self, api_client):
        """Test subagent prompt includes all necessary context."""
        conductor = SubagentConductor()
        # Get user to ensure API works, but don't need user data
        api_client.get_user()

        prompt = conductor.build_subagent_prompt(
            operation_type="categorization",
            task_description="Categorize 150 uncategorized transactions",
            data_summary="150 transactions from November 2025",
            intelligence_mode="smart",
            tax_level="full",
            constraints={"dry_run": True, "max_api_calls": 100},
        )

        # Verify prompt structure
        assert "categorization agent" in prompt.lower()
        assert "150 transactions" in prompt
        assert "intelligence mode: smart" in prompt.lower()
        assert "tax level: full" in prompt.lower()
        assert "dry_run: true" in prompt.lower()
        assert "max_api_calls: 100" in prompt

        print("✓ Subagent prompt built with complete context")
