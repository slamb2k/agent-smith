"""LLM Subagent orchestration using Claude Agent SDK.

This module handles LLM operations via the Claude Agent SDK.
Services return _needs_llm markers, and this orchestrator executes them.
"""

import logging
import asyncio
from typing import Dict, Any, List, cast
from claude_agent_sdk import query, ClaudeAgentOptions

logger = logging.getLogger(__name__)


class LLMSubagent:
    """Orchestrates LLM operations via Claude Agent SDK.

    This is a coordination layer that:
    1. Detects _needs_llm markers from service methods
    2. Delegates prompts to Claude via Agent SDK (in production)
    3. Parses responses back into structured results

    In production mode, uses Claude Agent SDK for real LLM calls.
    In test mode, returns mock responses for unit testing.
    """

    def __init__(self, test_mode: bool = False) -> None:
        """Initialize subagent orchestrator.

        Args:
            test_mode: If True, return test responses instead of calling SDK
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

        # Production mode: Use Claude Agent SDK
        logger.info(
            f"Executing categorization for {len(transaction_ids)} transactions via Claude Agent SDK"
        )

        llm_response = self._execute_prompt_sync(prompt)

        # Parse response using service parsing method
        return cast(
            Dict[int, Dict[str, Any]],
            service.parse_categorization_response(llm_response, transaction_ids),
        )

    def execute_validation(
        self,
        prompt: str,
        transaction_ids: List[int],
        validations: List[Dict[str, Any]],
        service: Any,
    ) -> Dict[int, Dict[str, Any]]:
        """Execute validation prompt via LLM.

        Args:
            prompt: Validation prompt from service
            transaction_ids: Transaction IDs (in order)
            validations: Original validation request dicts for parsing
            service: LLMCategorizationService instance for parsing

        Returns:
            Dict mapping transaction IDs to validation results
        """
        if self.test_mode:
            logger.info(
                f"TEST MODE: Would execute validation for {len(transaction_ids)} transactions"
            )
            return self._mock_validation_response(transaction_ids)

        # Production mode: Use Claude Agent SDK
        logger.info(
            f"Executing validation for {len(transaction_ids)} transactions via Claude Agent SDK"
        )

        llm_response = self._execute_prompt_sync(prompt)

        # Parse response using service batch parsing method
        return cast(
            Dict[int, Dict[str, Any]],
            service.parse_validation_batch_response(llm_response, validations),
        )

    def _execute_prompt_sync(self, prompt: str) -> str:
        """Execute a prompt synchronously using Claude Agent SDK.

        Args:
            prompt: The prompt to execute

        Returns:
            Complete LLM response as string
        """
        # Run async SDK call in sync context
        return asyncio.run(self._execute_prompt_async(prompt))

    async def _execute_prompt_async(self, prompt: str) -> str:
        """Execute a prompt asynchronously using Claude Agent SDK.

        Args:
            prompt: The prompt to execute

        Returns:
            Complete LLM response as string
        """
        # Configure SDK options for financial categorization
        options = ClaudeAgentOptions(
            system_prompt="You are a financial analysis expert helping categorize transactions.",
            allowed_tools=[],  # No tools needed for simple categorization
            permission_mode="default",
        )

        # Collect response chunks - only text content
        response_chunks = []
        async for message in query(prompt=prompt, options=options):
            # Extract text content from message objects
            if hasattr(message, "text"):
                response_chunks.append(message.text)
            elif hasattr(message, "content"):
                # Handle content array format
                if isinstance(message.content, list):
                    for item in message.content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            # Dict with 'text' key
                            response_chunks.append(item.get("text", ""))
                        elif hasattr(item, "text"):
                            # TextBlock object with .text attribute
                            response_chunks.append(item.text)
                elif isinstance(message.content, str):
                    response_chunks.append(message.content)
        # Join all chunks into complete response
        return "".join(response_chunks)

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
