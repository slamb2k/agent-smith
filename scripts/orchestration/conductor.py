"""Subagent conductor for intelligent orchestration.

The conductor decides when to delegate operations to subagents based on
complexity, size, and parallelization opportunities.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Operation types for conductor decision making."""

    BULK_PROCESSING = "bulk_processing"
    DEEP_ANALYSIS = "deep_analysis"
    MULTI_PERIOD = "multi_period"
    CATEGORIZATION = "categorization"
    REPORTING = "reporting"
    TAX_ANALYSIS = "tax_analysis"
    SCENARIO_MODELING = "scenario_modeling"
    OPTIMIZATION = "optimization"
    SIMPLE_QUERY = "simple_query"


def should_delegate(
    operation_type: OperationType,
    transaction_count: int,
    estimated_tokens: int,
    can_parallelize: bool,
) -> bool:
    """Decide if operation should be delegated to a subagent.

    Args:
        operation_type: Type of operation
        transaction_count: Number of transactions involved
        estimated_tokens: Estimated token count for operation
        can_parallelize: Whether operation can be parallelized

    Returns:
        True if operation should be delegated to subagent
    """
    # Always delegate these operation types
    always_delegate = {
        OperationType.BULK_PROCESSING,
        OperationType.DEEP_ANALYSIS,
        OperationType.MULTI_PERIOD,
    }
    if operation_type in always_delegate:
        return True

    # Check complexity thresholds
    if transaction_count > 100:
        return True

    if estimated_tokens > 5000:
        return True

    # Check parallelization opportunity
    if can_parallelize:
        return True

    # Simple queries stay in main context
    return False


class SubagentConductor:
    """Intelligent orchestration for subagent delegation.

    The conductor manages when and how to delegate operations to specialized
    subagents, preserving main context while handling heavy operations.
    """

    def __init__(
        self,
        transaction_threshold: int = 100,
        token_threshold: int = 5000,
        dry_run: bool = False,
    ):
        """Initialize subagent conductor.

        Args:
            transaction_threshold: Transaction count threshold for delegation
            token_threshold: Token estimate threshold for delegation
            dry_run: If True, don't actually dispatch subagents
        """
        self.transaction_threshold = transaction_threshold
        self.token_threshold = token_threshold
        self.dry_run = dry_run

    def estimate_complexity(
        self,
        operation_type: OperationType,
        transaction_count: int,
        period_months: int = 1,
        categories: int = 1,
    ) -> Dict[str, Any]:
        """Estimate computational complexity of an operation.

        Args:
            operation_type: Type of operation
            transaction_count: Number of transactions
            period_months: Number of months in analysis period
            categories: Number of categories to analyze

        Returns:
            Dict with estimated_tokens, can_parallelize, suggested_subagents
        """
        # Base token estimate: ~5 tokens per transaction
        base_tokens = transaction_count * 5

        # Operation multipliers
        multipliers = {
            OperationType.CATEGORIZATION: 3,  # Pattern matching
            OperationType.DEEP_ANALYSIS: 5,  # Detailed analysis
            OperationType.TAX_ANALYSIS: 4,  # Tax rules
            OperationType.SCENARIO_MODELING: 6,  # Complex calculations
            OperationType.REPORTING: 2,  # Formatting
            OperationType.SIMPLE_QUERY: 1,
        }
        multiplier = multipliers.get(operation_type, 2)

        estimated_tokens = base_tokens * multiplier

        # Add overhead for multi-period operations
        if period_months > 1:
            estimated_tokens = int(estimated_tokens * (1 + (period_months - 1) * 0.3))

        # Determine if can parallelize
        can_parallelize = False
        if period_months > 1:
            can_parallelize = True
        elif categories > 3:
            can_parallelize = True
        elif transaction_count > 200:
            # Can batch large transaction sets
            can_parallelize = True

        # Suggest number of subagents for parallel processing
        suggested_subagents = 1
        if can_parallelize:
            if period_months > 1:
                suggested_subagents = min(period_months, 12)
            elif categories > 3:
                suggested_subagents = min(categories, 5)
            elif transaction_count > 200:
                suggested_subagents = min((transaction_count // 100), 5)

        return {
            "estimated_tokens": estimated_tokens,
            "can_parallelize": can_parallelize,
            "suggested_subagents": suggested_subagents,
        }

    def build_subagent_prompt(
        self,
        operation_type: str,
        task_description: str,
        data_summary: str,
        intelligence_mode: str = "smart",
        tax_level: str = "smart",
        constraints: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build delegation prompt for subagent.

        Args:
            operation_type: Type of operation (categorization, analysis, etc.)
            task_description: Detailed description of task
            data_summary: Summary of data to process
            intelligence_mode: conservative|smart|aggressive
            tax_level: reference|smart|full
            constraints: Additional constraints (dry_run, max_api_calls, etc.)

        Returns:
            Formatted prompt for subagent
        """
        constraints = constraints or {}

        # Build constraints section
        constraints_lines = []
        for key, value in constraints.items():
            constraints_lines.append(f"- {key}: {value}")
        constraints_text = "\n".join(constraints_lines) if constraints_lines else "- None"

        prompt = f"""You are a specialized {operation_type} agent for Agent Smith.

CONTEXT:
- Operation: {task_description}
- Intelligence Mode: {intelligence_mode}
- Tax Level: {tax_level}

DATA:
{data_summary}

REFERENCES:
- API Documentation: ai_docs/pocketsmith-api-documentation.md
- Tax Guidelines: ai_docs/tax/ (if applicable)

TASK:
{task_description}

CONSTRAINTS:
{constraints_text}

Please complete the operation and return results in a structured format.
"""
        return prompt

    def should_delegate_operation(
        self,
        operation_type: OperationType,
        transaction_count: int,
        estimated_tokens: Optional[int] = None,
        can_parallelize: bool = False,
    ) -> bool:
        """Determine if operation should be delegated.

        Args:
            operation_type: Type of operation
            transaction_count: Number of transactions
            estimated_tokens: Token estimate (if None, will estimate)
            can_parallelize: Whether operation can be parallelized

        Returns:
            True if should delegate
        """
        if estimated_tokens is None:
            complexity = self.estimate_complexity(
                operation_type=operation_type, transaction_count=transaction_count
            )
            estimated_tokens = complexity["estimated_tokens"]
            can_parallelize = complexity["can_parallelize"]

        return should_delegate(
            operation_type=operation_type,
            transaction_count=transaction_count,
            estimated_tokens=estimated_tokens,
            can_parallelize=can_parallelize,
        )
