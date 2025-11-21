"""Categorization workflow for interactive transaction categorization."""

import logging
from typing import TYPE_CHECKING, Any, Dict, List

from scripts.orchestration.conductor import SubagentConductor, OperationType

if TYPE_CHECKING:
    from scripts.core.api_client import PocketSmithClient

logger = logging.getLogger(__name__)


def parse_categorize_args(args: List[str]) -> Dict[str, Any]:
    """Parse arguments for categorization command.

    Args:
        args: Command line arguments

    Returns:
        Dict with parsed arguments
    """
    parsed = {
        "mode": "smart",
        "period": None,
        "account": None,
        "dry_run": False,
    }

    for arg in args:
        if arg.startswith("--mode="):
            parsed["mode"] = arg.split("=", 1)[1]
        elif arg.startswith("--period="):
            parsed["period"] = arg.split("=", 1)[1]
        elif arg.startswith("--account="):
            parsed["account"] = arg.split("=", 1)[1]
        elif arg == "--dry-run":
            parsed["dry_run"] = True

    return parsed


class CategorizationWorkflow:
    """Interactive workflow for transaction categorization.

    Guides users through categorizing uncategorized transactions with
    AI assistance and rule learning.
    """

    def __init__(self, client: "PocketSmithClient", mode: str = "smart") -> None:
        """Initialize categorization workflow.

        Args:
            client: PocketSmith API client
            mode: Intelligence mode (conservative|smart|aggressive)
        """
        self.client = client
        self.mode = mode
        self.conductor = SubagentConductor()

    def should_use_subagent(self, transaction_count: int) -> bool:
        """Determine if should use subagent for categorization.

        Args:
            transaction_count: Number of transactions to categorize

        Returns:
            True if should delegate to subagent
        """
        return self.conductor.should_delegate_operation(
            operation_type=OperationType.CATEGORIZATION,
            transaction_count=transaction_count,
        )

    def build_summary(self, results: Dict[str, Any], total: int) -> str:
        """Build human-readable summary of categorization results.

        Args:
            results: Categorization results dict
            total: Total transactions processed

        Returns:
            Formatted summary string
        """
        categorized = results.get("categorized", 0)
        skipped = results.get("skipped", 0)
        rules_applied = results.get("rules_applied", 0)
        new_rules = results.get("new_rules", 0)

        percent = (categorized / total * 100) if total > 0 else 0

        summary = f"""Categorization Complete:
- Categorized: {categorized}/{total} ({percent:.1f}%)
- Skipped: {skipped}
- Rules applied: {rules_applied}
- New rules created: {new_rules}
"""
        return summary
