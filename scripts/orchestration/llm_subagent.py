"""LLM Subagent orchestration for Claude Code delegation.

This module handles delegation to Claude Code's LLM via the Task tool.
Services return _needs_llm markers, and this orchestrator executes them.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class LLMSubagent:
    """Orchestrates LLM operations via Claude Code Task tool.

    This is a coordination layer that:
    1. Detects _needs_llm markers from service methods
    2. Delegates prompts to Claude Code (via Task tool in production)
    3. Parses responses back into structured results

    In production, this would use Claude Code's Task tool.
    For testing, it returns placeholder responses.
    """

    def __init__(self, test_mode: bool = False) -> None:
        """Initialize subagent orchestrator.

        Args:
            test_mode: If True, return test responses instead of delegating
        """
        self.test_mode = test_mode

    def execute_categorization(
        self,
        prompt: str,
        transaction_ids: List[int],
        service: Any,
    ) -> Dict[int, Dict[str, Any]]:
        """Execute categorization prompt via LLM.

        Args:
            prompt: Categorization prompt from service
            transaction_ids: Transaction IDs (in order)
            service: LLMCategorizationService instance for parsing

        Returns:
            Dict mapping transaction IDs to categorization results
        """
        if self.test_mode:
            logger.info(
                f"TEST MODE: Would execute categorization for {len(transaction_ids)} transactions"
            )
            return self._mock_categorization_response(transaction_ids)

        # TODO: In production, use Task tool to delegate to Claude Code
        # from claude_code import Task
        # llm_response = Task.execute(prompt)

        # For now, log that delegation would occur
        logger.warning(
            f"Production LLM delegation not yet implemented. "
            f"Would delegate categorization for {len(transaction_ids)} transactions"
        )

        # Return empty results (will be replaced with actual delegation)
        return {}

    def execute_validation(
        self,
        prompt: str,
        transaction_ids: List[int],
        service: Any,
    ) -> Dict[int, Dict[str, Any]]:
        """Execute validation prompt via LLM.

        Args:
            prompt: Validation prompt from service
            transaction_ids: Transaction IDs (in order)
            service: LLMCategorizationService instance for parsing

        Returns:
            Dict mapping transaction IDs to validation results
        """
        if self.test_mode:
            logger.info(
                f"TEST MODE: Would execute validation for {len(transaction_ids)} transactions"
            )
            return self._mock_validation_response(transaction_ids)

        # TODO: In production, use Task tool to delegate to Claude Code
        # from claude_code import Task
        # llm_response = Task.execute(prompt)

        # For now, log that delegation would occur
        logger.warning(
            f"Production LLM delegation not yet implemented. "
            f"Would delegate validation for {len(transaction_ids)} transactions"
        )

        # Return empty results (will be replaced with actual delegation)
        return {}

    def _mock_categorization_response(
        self,
        transaction_ids: List[int],
    ) -> Dict[int, Dict[str, Any]]:
        """Generate mock categorization response for testing.

        Args:
            transaction_ids: Transaction IDs to mock

        Returns:
            Mock categorization results
        """
        results = {}
        for txn_id in transaction_ids:
            results[txn_id] = {
                "transaction_id": txn_id,
                "category": "Test Category",
                "confidence": 85,
                "reasoning": "Mock categorization for testing",
                "source": "llm",
            }
        return results

    def _mock_validation_response(
        self,
        transaction_ids: List[int],
    ) -> Dict[int, Dict[str, Any]]:
        """Generate mock validation response for testing.

        Args:
            transaction_ids: Transaction IDs to mock

        Returns:
            Mock validation results
        """
        results = {}
        for txn_id in transaction_ids:
            results[txn_id] = {
                "validation": "CONFIRM",
                "confidence": 90,
                "reasoning": "Mock validation for testing",
                "category": "Original Category",
            }
        return results
