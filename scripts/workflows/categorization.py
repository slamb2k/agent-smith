"""Categorization workflow for interactive transaction categorization."""

import logging
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from scripts.orchestration.conductor import SubagentConductor, OperationType
from scripts.core.unified_rules import UnifiedRuleEngine
from scripts.services.llm_categorization import LLMCategorizationService
from scripts.core.rule_engine import IntelligenceMode

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

    def __init__(
        self,
        client: Optional["PocketSmithClient"],
        mode: str = "smart",
        rule_engine: Optional[UnifiedRuleEngine] = None,
    ) -> None:
        """Initialize categorization workflow.

        Args:
            client: PocketSmith API client (optional for testing)
            mode: Intelligence mode (conservative|smart|aggressive)
            rule_engine: Unified rule engine (creates default if None)
        """
        self.client = client
        self.mode = mode
        self.conductor = SubagentConductor()

        # Initialize rule engine
        if rule_engine is None:
            self.rule_engine = UnifiedRuleEngine()
        else:
            self.rule_engine = rule_engine

        # Initialize LLM categorization service
        self.llm_service = LLMCategorizationService()

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

    def categorize_transaction(
        self,
        transaction: Dict[str, Any],
        available_categories: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Categorize a single transaction using hybrid flow: Rules → LLM → Labels.

        Args:
            transaction: Transaction dict with id, payee, amount, date
            available_categories: Available categories for LLM fallback

        Returns:
            Result dict with:
            - category: str | None - Matched category
            - labels: List[str] - Matched labels (sorted)
            - confidence: int - Confidence score
            - source: str - "rule", "llm", or "none"
            - llm_used: bool - Whether LLM was used
            - reasoning: str - Explanation (for LLM results)
        """
        # Phase 1: Try rule-based categorization
        rule_result = self.rule_engine.categorize_and_label(transaction)

        if rule_result["category"] is not None:
            # Rule matched - return with labels
            return {
                "category": rule_result["category"],
                "labels": rule_result["labels"],
                "confidence": rule_result["confidence"],
                "source": "rule",
                "llm_used": False,
            }

        # Phase 2: No rule match - fall back to LLM
        if available_categories is None:
            logger.warning("No categories provided for LLM fallback")
            return {
                "category": None,
                "labels": [],
                "confidence": 0,
                "source": "none",
                "llm_used": False,
            }

        # Call LLM service
        llm_results = self.llm_service.categorize_batch(
            transactions=[transaction],
            categories=available_categories,
            mode=self._get_intelligence_mode(),
        )

        if not llm_results or transaction["id"] not in llm_results:
            # LLM returned no result
            return {
                "category": None,
                "labels": [],
                "confidence": 0,
                "source": "none",
                "llm_used": True,
            }

        llm_result = llm_results[transaction["id"]]

        # Phase 3: Apply labels to LLM-categorized transaction
        # Update transaction with LLM category and re-run label rules
        transaction_with_category = transaction.copy()
        transaction_with_category["category"] = {"title": llm_result["category"]}

        label_result = self.rule_engine.categorize_and_label(transaction_with_category)

        return {
            "category": llm_result["category"],
            "labels": label_result["labels"],
            "confidence": llm_result["confidence"],
            "source": "llm",
            "llm_used": True,
            "reasoning": llm_result.get("reasoning", ""),
        }

    def _get_intelligence_mode(self) -> IntelligenceMode:
        """Convert mode string to IntelligenceMode enum."""
        mode_map = {
            "conservative": IntelligenceMode.CONSERVATIVE,
            "smart": IntelligenceMode.SMART,
            "aggressive": IntelligenceMode.AGGRESSIVE,
        }
        return mode_map.get(self.mode, IntelligenceMode.SMART)

    def _should_auto_apply(self, confidence: int, mode: IntelligenceMode) -> bool:
        """Determine if categorization should be auto-applied.

        Args:
            confidence: Confidence score (0-100)
            mode: Intelligence mode

        Returns:
            True if should auto-apply without asking user
        """
        thresholds = {
            IntelligenceMode.CONSERVATIVE: 999,  # Never auto-apply
            IntelligenceMode.SMART: 90,
            IntelligenceMode.AGGRESSIVE: 80,
        }
        return confidence >= thresholds[mode]

    def _should_ask_user(self, confidence: int, mode: IntelligenceMode) -> bool:
        """Determine if categorization should prompt user for confirmation.

        Args:
            confidence: Confidence score (0-100)
            mode: Intelligence mode

        Returns:
            True if should ask user for confirmation
        """
        if mode == IntelligenceMode.CONSERVATIVE:
            # Always ask in conservative mode
            return True

        auto_threshold = {
            IntelligenceMode.SMART: 90,
            IntelligenceMode.AGGRESSIVE: 80,
        }[mode]

        ask_threshold = {
            IntelligenceMode.SMART: 70,
            IntelligenceMode.AGGRESSIVE: 50,
        }[mode]

        # Ask if between ask_threshold and auto_threshold
        return ask_threshold <= confidence < auto_threshold

    def suggest_rule_from_llm_result(
        self, transaction: Dict[str, Any], result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Suggest a rule based on LLM categorization result.

        Args:
            transaction: Transaction that was categorized
            result: Categorization result from LLM

        Returns:
            Rule suggestion dict or None if not applicable
        """
        if result["source"] != "llm" or result["category"] is None:
            return None

        # Extract merchant name from payee
        payee = transaction.get("payee", "")
        merchant = self._extract_merchant_name(payee)

        if not merchant:
            return None

        return {
            "type": "category",
            "name": f"{merchant} → {result['category']}",
            "patterns": [merchant],
            "category": result["category"],
            "confidence": result["confidence"],
        }

    def _extract_merchant_name(self, payee: str) -> Optional[str]:
        """Extract primary merchant name from payee string.

        Args:
            payee: Full payee string

        Returns:
            Merchant name or None
        """
        if not payee:
            return None

        # Remove common suffixes and get first significant word
        payee_upper = payee.upper()

        # Remove numbers and common patterns
        cleaned = re.sub(r"\s+\d+.*$", "", payee_upper)  # Remove trailing numbers
        cleaned = re.sub(r"\s+#.*$", "", cleaned)  # Remove # and after

        # Get first word (usually the merchant)
        words = cleaned.strip().split()
        if words:
            return words[0]

        return None

    def create_rule_from_transaction(
        self, transaction: Dict[str, Any], llm_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a rule dict from transaction and LLM result.

        Args:
            transaction: Transaction dict
            llm_result: LLM categorization result

        Returns:
            Rule dict ready to be added to rules.yaml
        """
        merchant = self._extract_merchant_name(transaction.get("payee", ""))
        category = llm_result["category"]

        return {
            "type": "category",
            "name": f"{merchant} → {category}",
            "patterns": [merchant] if merchant else [],
            "category": category,
            "confidence": llm_result["confidence"],
        }
