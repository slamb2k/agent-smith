#!/usr/bin/env python
"""Quick test script for Claude Agent SDK integration."""

import sys
import logging
from scripts.orchestration.llm_subagent import LLMSubagent
from scripts.services.llm_categorization import LLMCategorizationService

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


def test_simple_prompt():
    """Test simple SDK prompt execution."""
    logger.info("Testing Claude Agent SDK integration...")

    orchestrator = LLMSubagent(test_mode=False)  # Production mode
    service = LLMCategorizationService()

    # Simple categorization prompt
    transactions = [
        {"id": 1, "payee": "WOOLWORTHS METRO", "amount": -50.00, "date": "2025-11-20"},
        {"id": 2, "payee": "UBER TRIP", "amount": -25.00, "date": "2025-11-21"},
    ]

    categories = [
        {"title": "Groceries", "parent": ""},
        {"title": "Transport", "parent": ""},
        {"title": "Dining Out", "parent": ""},
    ]

    # Build categorization result (which returns marker)
    marker = service.categorize_batch(transactions, categories)

    logger.info(f"Service returned marker: {marker.get('_needs_llm')}")

    if marker.get("_needs_llm"):
        prompt = marker["_prompt"]
        transaction_ids = marker["_transaction_ids"]

        logger.info(f"Prompt preview (first 200 chars): {prompt[:200]}...")

        # Execute via SDK
        logger.info("Executing prompt via Claude Agent SDK...")
        results = orchestrator.execute_categorization(prompt, transaction_ids, service)

        logger.info("\nResults:")
        for txn_id, result in results.items():
            logger.info(
                "  Transaction %d: %s (confidence: %d%%)",
                txn_id,
                result.get("category"),
                result.get("confidence"),
            )
            logger.info(f"    Reasoning: {result.get('reasoning')}")

        return True
    else:
        logger.error("Expected _needs_llm marker but didn't get one")
        return False


if __name__ == "__main__":
    try:
        success = test_simple_prompt()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
