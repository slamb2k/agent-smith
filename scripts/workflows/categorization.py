"""Categorization workflow for interactive transaction categorization."""

import logging
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from scripts.orchestration.conductor import SubagentConductor, OperationType
from scripts.orchestration.llm_subagent import LLMSubagent
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

        # Initialize LLM subagent orchestrator
        self.llm_orchestrator = LLMSubagent(test_mode=False)

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

    def _orchestrate_llm_call(
        self,
        marker_result: Dict[str, Any],
    ) -> Dict[int, Dict[str, Any]]:
        """Orchestrate LLM call by detecting marker and delegating.

        Args:
            marker_result: Result from service method (may contain _needs_llm marker)

        Returns:
            Actual LLM results (or empty dict if no marker)
        """
        # Check if this is a marker dict
        if not isinstance(marker_result, dict) or not marker_result.get("_needs_llm"):
            # Return empty dict if not a marker (shouldn't happen in normal flow)
            return {}

        # Extract marker data
        prompt = marker_result["_prompt"]
        transaction_ids = marker_result["_transaction_ids"]
        operation_type = marker_result.get("_type", "categorization")

        # Delegate to appropriate orchestrator method
        if operation_type == "validation":
            validations = marker_result.get("_validations", [])
            return self.llm_orchestrator.execute_validation(
                prompt=prompt,
                transaction_ids=transaction_ids,
                validations=validations,
                service=self.llm_service,
            )
        else:
            return self.llm_orchestrator.execute_categorization(
                prompt=prompt,
                transaction_ids=transaction_ids,
                service=self.llm_service,
            )

    def _execute_batch_categorization(
        self,
        transactions: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
    ) -> Dict[int, Dict[str, Any]]:
        """Execute batch categorization with LLM orchestration.

        Args:
            transactions: List of transactions to categorize
            categories: Available categories

        Returns:
            Dict mapping transaction IDs to categorization results
        """
        # Get marker result from service
        marker_result = self.llm_service.categorize_batch(
            transactions=transactions,
            categories=categories,
            mode=IntelligenceMode(self.mode),
        )

        # Orchestrate LLM call
        return self._orchestrate_llm_call(marker_result)

    def _execute_batch_validation(
        self,
        validations: List[Dict[str, Any]],
        available_categories: List[Dict[str, Any]],
    ) -> Dict[int, Dict[str, Any]]:
        """Execute batch validation with LLM orchestration.

        Args:
            validations: List of validation dicts
            available_categories: Available categories for alternative suggestions

        Returns:
            Dict mapping transaction IDs to validation results
        """
        # Get marker result from service
        marker_result = self.llm_service.validate_batch(validations, available_categories)

        # Orchestrate LLM call
        return self._orchestrate_llm_call(marker_result)

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

    def categorize_single_transaction(
        self,
        transaction: Dict[str, Any],
        available_categories: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Categorize a single transaction with smart platform coexistence (Option 4).

        This handles already-categorized transactions intelligently:
        - Uncategorized: Apply category + labels from rules
        - Already categorized + matching rule: Apply labels only
        - Already categorized + conflicting rule: Flag for review
        - Label-only rule: Apply labels regardless

        Args:
            transaction: Transaction dict with id, payee, amount, date, category
            available_categories: Available categories

        Returns:
            Result dict with:
            - category: str - Category (existing or from rule)
            - labels: List[str] - Matched labels (sorted)
            - confidence: int - Confidence score
            - source: str - "rule", "conflict", or "none"
            - needs_review: bool - Whether transaction needs manual review
            - suggested_category: str - What rule suggested (if conflict)
        """
        # Apply rule engine
        rule_result = self.rule_engine.categorize_and_label(transaction)

        # Get existing category if any
        existing_category = None
        if transaction.get("category"):
            if isinstance(transaction["category"], dict):
                existing_category = transaction["category"].get("title")
            else:
                existing_category = transaction["category"]

        # Case 1: Uncategorized transaction
        if existing_category is None:
            if rule_result["category"] is not None:
                # Rule matched - apply category + labels
                return {
                    "category": rule_result["category"],
                    "labels": rule_result["labels"],
                    "confidence": rule_result["confidence"],
                    "source": "rule",
                    "llm_used": False,
                }
            else:
                # No rule match, no existing category
                return {
                    "category": None,
                    "labels": rule_result["labels"],  # May have label-only rules
                    "confidence": 0,
                    "source": "none",
                    "llm_used": False,
                }

        # Case 2: Already categorized
        if rule_result["category"] is None:
            # Label-only rule - apply labels, keep existing category
            return {
                "category": existing_category,
                "labels": rule_result["labels"],
                "confidence": rule_result["confidence"],
                "source": "rule",
                "llm_used": False,
            }
        elif rule_result["category"] == existing_category:
            # Category matches - apply labels only
            return {
                "category": existing_category,
                "labels": rule_result["labels"],
                "confidence": rule_result["confidence"],
                "source": "rule",
                "llm_used": False,
            }
        else:
            # Category conflict - flag for review
            return {
                "category": existing_category,
                "labels": [],
                "confidence": rule_result["confidence"],
                "source": "conflict",
                "needs_review": True,
                "suggested_category": rule_result["category"],
                "llm_used": False,
            }

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

    def categorize_transactions_batch(
        self,
        transactions: List[Dict[str, Any]],
        available_categories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Categorize multiple transactions using batch processing.

        This implements the hybrid workflow:
        1. Apply rules to all transactions
        2. Batch uncategorized transactions → LLM (Case 1)
        3. Batch medium-confidence validations → LLM (Case 2)
        4. Apply labels to all categorized transactions

        Args:
            transactions: List of transaction dicts
            available_categories: Available categories for LLM

        Returns:
            Dict with:
            - results: Dict[int, Dict] - Categorization results per transaction
            - stats: Dict - Processing statistics
        """
        mode = self._get_intelligence_mode()

        # Batch size based on intelligence mode
        batch_sizes = {
            IntelligenceMode.CONSERVATIVE: 20,
            IntelligenceMode.SMART: 50,
            IntelligenceMode.AGGRESSIVE: 100,
        }
        batch_size = batch_sizes[mode]

        results = {}
        stats = {
            "total": len(transactions),
            "rule_matches": 0,
            "llm_categorized": 0,
            "llm_validated": 0,
            "skipped": 0,
            "conflicts": 0,
        }

        # Phase 1: Apply rules to all transactions (Option 4: smart coexistence)
        logger.info(f"Applying rules to {len(transactions)} transactions...")
        uncategorized = []
        needs_validation = []

        for txn in transactions:
            # Use new smart categorization that handles already-categorized transactions
            result = self.categorize_single_transaction(txn, available_categories)

            # Store result
            results[txn["id"]] = result

            # Update stats
            if result["source"] == "conflict":
                stats["conflicts"] += 1
            elif result["source"] == "rule":
                stats["rule_matches"] += 1
            elif result["source"] == "none" and result["category"] is None:
                # Truly uncategorized - needs LLM
                uncategorized.append(txn)
                continue  # Don't count as rule match

            # Check if medium confidence (needs validation)
            if result.get("category") and result["source"] == "rule":
                if self._should_validate_with_llm(result["confidence"], mode):
                    needs_validation.append(
                        {
                            "transaction": txn,
                            "suggested_category": result["category"],
                            "confidence": result["confidence"],
                        }
                    )

        # Phase 2: Batch uncategorized transactions (Case 1)
        if uncategorized:
            logger.info(
                f"Batch categorizing {len(uncategorized)} uncategorized "
                f"transactions (batch size: {batch_size})..."
            )

            for i in range(0, len(uncategorized), batch_size):
                batch = uncategorized[i : i + batch_size]
                logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} transactions)")

                # Execute batch categorization with orchestration
                llm_results = self._execute_batch_categorization(
                    transactions=batch,
                    categories=available_categories,
                )

                # Process LLM results and apply labels
                for txn in batch:
                    txn_id = txn["id"]

                    if txn_id in llm_results:
                        llm_result = llm_results[txn_id]

                        # Apply labels to LLM-categorized transaction
                        txn_with_category = txn.copy()
                        txn_with_category["category"] = {"title": llm_result["category"]}
                        label_result = self.rule_engine.categorize_and_label(txn_with_category)

                        results[txn_id] = {
                            "category": llm_result["category"],
                            "labels": label_result["labels"],
                            "confidence": llm_result["confidence"],
                            "source": "llm",
                            "llm_used": True,
                            "reasoning": llm_result.get("reasoning", ""),
                        }
                        stats["llm_categorized"] += 1
                    else:
                        # LLM returned no result
                        results[txn_id] = {
                            "category": None,
                            "labels": [],
                            "confidence": 0,
                            "source": "none",
                            "llm_used": True,
                        }
                        stats["skipped"] += 1

        # Phase 3: Batch medium-confidence validation (Case 2)
        if needs_validation:
            logger.info(
                f"Validating {len(needs_validation)} medium-confidence "
                f"categorizations (batch size: {batch_size})..."
            )

            for i in range(0, len(needs_validation), batch_size):
                batch = needs_validation[i : i + batch_size]
                logger.info(
                    f"Processing validation batch {i // batch_size + 1} ({len(batch)} validations)"
                )

                # Execute batch validation with orchestration
                validation_results = self._execute_batch_validation(
                    validations=batch, available_categories=available_categories
                )

                # Process validation results
                for val in batch:
                    txn = val["transaction"]
                    txn_id = txn["id"]

                    if txn_id in validation_results:
                        val_result = validation_results[txn_id]

                        # Check validation decision
                        if val_result["validation"] == "CONFIRM":
                            # LLM confirmed - upgrade confidence
                            results[txn_id]["confidence"] = val_result["confidence"]
                            stats["llm_validated"] += 1
                        elif val_result["validation"] == "REJECT":
                            # LLM rejected - update category and labels
                            new_category = val_result["category"]

                            # Apply labels to new category
                            txn_with_category = txn.copy()
                            txn_with_category["category"] = {"title": new_category}
                            label_result = self.rule_engine.categorize_and_label(txn_with_category)

                            results[txn_id] = {
                                "category": new_category,
                                "labels": label_result["labels"],
                                "confidence": val_result["confidence"],
                                "source": "rule+llm",
                                "llm_used": True,
                                "reasoning": val_result.get("reasoning", ""),
                            }
                            stats["llm_validated"] += 1

        return {
            "results": results,
            "stats": stats,
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

    def _should_validate_with_llm(self, confidence: Optional[int], mode: IntelligenceMode) -> bool:
        """Determine if rule-based categorization should be validated with LLM.

        Args:
            confidence: Confidence score from rule (0-100), may be None
            mode: Intelligence mode

        Returns:
            True if should validate with LLM (medium confidence range)
        """
        # Conservative mode: never validate with LLM (user reviews all)
        if mode == IntelligenceMode.CONSERVATIVE:
            return False

        # Handle None confidence (e.g., label-only rules)
        if confidence is None:
            return False

        # Medium confidence ranges by mode
        validation_ranges = {
            IntelligenceMode.SMART: (70, 89),  # 70-89% needs validation
            IntelligenceMode.AGGRESSIVE: (50, 79),  # 50-79% needs validation
        }

        if mode not in validation_ranges:
            return False

        min_conf, max_conf = validation_ranges[mode]
        return min_conf <= confidence <= max_conf

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
