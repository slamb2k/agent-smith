"""Categorization subagent for LLM-powered transaction categorization.

This subagent provides a wrapper around the LLMCategorizationService
for executing categorization tasks in an isolated context.

Usage:
    This script is designed to be executed by the SubagentConductor
    via Claude Code's agent delegation mechanism. It receives a
    categorization task, processes it using the LLM context, and
    returns structured results.

Example:
    python scripts/subagents/categorization_subagent.py \\
        --transactions transactions.json \\
        --categories categories.json \\
        --mode smart \\
        --output results.json
"""

import json
import logging
import argparse
from typing import List, Dict, Any

from scripts.services.llm_categorization import (
    LLMCategorizationService,
    IntelligenceMode,
)

logger = logging.getLogger(__name__)


def load_json_file(file_path: str) -> Any:
    """Load data from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    with open(file_path, "r") as f:
        return json.load(f)


def save_json_file(file_path: str, data: Any) -> None:
    """Save data to JSON file.

    Args:
        file_path: Path to output JSON file
        data: Data to save
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def categorize_transactions(
    transactions: List[Dict[str, Any]],
    categories: List[Dict[str, Any]],
    mode: IntelligenceMode,
) -> Dict[int, Dict[str, Any]]:
    """Categorize transactions using LLM.

    This function uses the LLMCategorizationService to build a prompt
    and then relies on the LLM context of this subagent to generate
    categorizations.

    Args:
        transactions: List of transaction dicts
        categories: List of available categories
        mode: Intelligence mode for threshold decisions

    Returns:
        Dict mapping transaction_id to categorization result
    """
    service = LLMCategorizationService()

    # Build the categorization prompt
    prompt = service.build_categorization_prompt(transactions, categories, mode)

    # In actual usage, the LLM (Claude) would process this prompt
    # and return a response. For now, we'll output the prompt and
    # instructions for the LLM to follow.

    print("=" * 70)
    print("CATEGORIZATION TASK")
    print("=" * 70)
    print()
    print(prompt)
    print()
    print("=" * 70)
    print("Please provide your categorization response above.")
    print("The response should follow the format specified in the prompt.")
    print("=" * 70)
    print()

    # In a real implementation, the LLM would execute the prompt
    # and we would parse the response. For testing purposes,
    # this demonstrates the integration pattern.

    # Extract transaction IDs for result structure
    transaction_ids: List[int] = [txn["id"] for txn in transactions]

    # Placeholder: In actual usage, we would get the LLM response here
    # and parse it using service.parse_categorization_response()

    # For now, return empty results to demonstrate the structure
    # Tests will mock this entire function or provide sample responses
    results: Dict[int, Dict[str, Any]] = {
        txn_id: {
            "transaction_id": txn_id,
            "category": None,
            "confidence": 0,
            "reasoning": "LLM response not available in this context",
            "source": "llm",
        }
        for txn_id in transaction_ids
    }

    return results


def main() -> None:
    """Main entry point for categorization subagent."""
    parser = argparse.ArgumentParser(
        description="Categorization subagent for LLM-powered transaction categorization"
    )
    parser.add_argument(
        "--transactions",
        required=True,
        help="Path to JSON file containing transactions to categorize",
    )
    parser.add_argument(
        "--categories",
        required=True,
        help="Path to JSON file containing available categories",
    )
    parser.add_argument(
        "--mode",
        choices=["conservative", "smart", "aggressive"],
        default="smart",
        help="Intelligence mode for categorization (default: smart)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output JSON file for categorization results",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load input data
    logger.info(f"Loading transactions from {args.transactions}")
    transactions = load_json_file(args.transactions)

    logger.info(f"Loading categories from {args.categories}")
    categories = load_json_file(args.categories)

    # Parse intelligence mode
    mode_map = {
        "conservative": IntelligenceMode.CONSERVATIVE,
        "smart": IntelligenceMode.SMART,
        "aggressive": IntelligenceMode.AGGRESSIVE,
    }
    mode = mode_map[args.mode]

    # Execute categorization
    logger.info(f"Categorizing {len(transactions)} transactions in {args.mode} mode")
    results = categorize_transactions(transactions, categories, mode)

    # Save results
    logger.info(f"Saving results to {args.output}")
    save_json_file(args.output, results)

    # Print summary
    print()
    print("=" * 70)
    print("CATEGORIZATION SUMMARY")
    print("=" * 70)
    print(f"Total transactions: {len(transactions)}")
    print(f"Results generated: {len(results)}")
    print(f"Intelligence mode: {args.mode}")
    print(f"Output saved to: {args.output}")
    print("=" * 70)

    logger.info("Categorization subagent completed successfully")


if __name__ == "__main__":
    main()
