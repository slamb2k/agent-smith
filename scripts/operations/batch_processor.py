"""Batch processing with operational modes and range filtering."""

import logging
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Tuple

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing mode enum."""

    DRY_RUN = "dry_run"  # Preview changes without applying
    VALIDATE = "validate"  # Identify what would change on existing values
    APPLY = "apply"  # Actually apply changes


class UpdateStrategy(Enum):
    """Strategy for handling existing categorizations."""

    SKIP_EXISTING = "skip_existing"  # Only process uncategorized
    REPLACE_ALL = "replace_all"  # Replace all, even existing
    UPGRADE_CONFIDENCE = "upgrade_confidence"  # Replace if new confidence higher
    REPLACE_IF_DIFFERENT = "replace_if_different"  # Replace if category differs


@dataclass
class DateRange:
    """Date range for filtering transactions."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BatchProcessor:
    """Batch processor with operational modes and filtering."""

    def __init__(
        self,
        mode: ProcessingMode = ProcessingMode.DRY_RUN,
        update_strategy: UpdateStrategy = UpdateStrategy.SKIP_EXISTING,
        date_range: Optional[DateRange] = None,
        accounts: Optional[List[str]] = None,
        limit: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int, int], None]] = None,
    ):
        """Initialize batch processor.

        Args:
            mode: Processing mode (dry_run/validate/apply)
            update_strategy: How to handle existing categorizations
            date_range: Optional date range filter
            accounts: Optional list of account names to process
            limit: Optional maximum number of transactions to process
            progress_callback: Optional callback function(current, total, transaction_id)
        """
        self.mode = mode
        self.update_strategy = update_strategy
        self.date_range = date_range
        self.accounts = accounts
        self.limit = limit
        self.progress_callback = progress_callback

    def filter_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter transactions by date range, accounts, and limit.

        Args:
            transactions: List of transaction dicts

        Returns:
            Filtered list of transactions
        """
        filtered = transactions

        # Filter by date range
        if self.date_range:
            filtered = self._filter_by_date(filtered)

        # Filter by accounts
        if self.accounts:
            filtered = self._filter_by_accounts(filtered)

        # Apply limit
        if self.limit:
            filtered = filtered[: self.limit]

        return filtered

    def _filter_by_date(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter transactions by date range."""
        if not self.date_range:
            return transactions

        filtered = []

        for txn in transactions:
            txn_date_str = txn.get("date")
            if not txn_date_str:
                continue

            try:
                txn_date = datetime.strptime(txn_date_str, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid date format: {txn_date_str}")
                continue

            # Check start date
            if self.date_range.start_date and txn_date < self.date_range.start_date:
                continue

            # Check end date
            if self.date_range.end_date and txn_date > self.date_range.end_date:
                continue

            filtered.append(txn)

        return filtered

    def _filter_by_accounts(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter transactions by accounts."""
        if not self.accounts:
            return transactions
        return [txn for txn in transactions if txn.get("_account_name") in self.accounts]

    def process_batch(
        self,
        transactions: List[Dict[str, Any]],
        categorization_fn: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Process a batch of transactions.

        Args:
            transactions: List of transaction dicts
            categorization_fn: Function to categorize transactions

        Returns:
            Results dict with counts and details
        """
        results: Dict[str, Any] = {
            "total": len(transactions),
            "processed": 0,
            "skipped": 0,
            "would_categorize": 0,
            "would_change": 0,
            "unchanged": 0,
            "upgraded": 0,
            "applied": 0,
            "dry_run": self.mode == ProcessingMode.DRY_RUN,
            "mode": self.mode.value,
            "update_strategy": self.update_strategy.value,
            "details": [],
        }

        for idx, txn in enumerate(transactions, start=1):
            # Report progress if callback provided
            if self.progress_callback:
                self.progress_callback(idx, len(transactions), txn["id"])

            # Categorize transaction (stub for now)
            if categorization_fn:
                categorization_result = categorization_fn(txn)
            else:
                categorization_result = self._stub_categorize(txn)

            # In VALIDATE mode, always process to check what would change
            # In other modes, check update strategy
            if self.mode != ProcessingMode.VALIDATE:
                should_process, skip_reason = self._should_process_transaction(
                    txn, categorization_result
                )

                if not should_process:
                    results["skipped"] += 1
                    continue

            # Handle based on mode
            if self.mode == ProcessingMode.DRY_RUN:
                results["would_categorize"] += 1
                results["details"].append(
                    {
                        "transaction_id": txn["id"],
                        "action": "would_categorize",
                        "category": categorization_result.get("category"),
                    }
                )

            elif self.mode == ProcessingMode.VALIDATE:
                if self._would_change(txn, categorization_result):
                    results["would_change"] += 1
                    results["details"].append(
                        {
                            "transaction_id": txn["id"],
                            "action": "would_change",
                            "from": txn.get("category", {}).get("title"),
                            "to": categorization_result.get("category"),
                        }
                    )
                else:
                    results["unchanged"] += 1

            elif self.mode == ProcessingMode.APPLY:
                # Actually apply the categorization
                results["processed"] += 1
                results["applied"] += 1

                if self.update_strategy == UpdateStrategy.UPGRADE_CONFIDENCE:
                    old_confidence = txn.get("_category_confidence", 0)
                    new_confidence = categorization_result.get("confidence", 0)
                    if new_confidence > old_confidence:
                        results["upgraded"] += 1

        return results

    def _should_process_transaction(
        self,
        transaction: Dict[str, Any],
        categorization_result: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Determine if transaction should be processed based on update strategy.

        Args:
            transaction: Transaction dict
            categorization_result: Result from categorization (if available)

        Returns:
            Tuple of (should_process, skip_reason)
        """
        has_category = transaction.get("category") is not None

        if self.update_strategy == UpdateStrategy.SKIP_EXISTING:
            if has_category:
                return False, "has_category"
            return True, None

        if self.update_strategy == UpdateStrategy.REPLACE_ALL:
            return True, None

        if self.update_strategy == UpdateStrategy.UPGRADE_CONFIDENCE:
            # Skip if no current category (nothing to upgrade from)
            if not has_category:
                return True, None

            # Skip if categorization result not available yet
            if categorization_result is None:
                return True, None

            # Check if new confidence is higher
            old_confidence = transaction.get("_category_confidence", 0)
            new_confidence = categorization_result.get("confidence", 0)

            if new_confidence > old_confidence:
                return True, None
            return False, "confidence_not_higher"

        if self.update_strategy == UpdateStrategy.REPLACE_IF_DIFFERENT:
            # If no current category, always process
            if not has_category:
                return True, None

            # Skip if categorization result not available yet
            if categorization_result is None:
                return True, None

            # Check if category would change
            current_category = transaction.get("category", {}).get("title")
            new_category = categorization_result.get("category")

            if current_category != new_category:
                return True, None
            return False, "category_same"

        # Fallback for any unknown strategy (should never happen)
        return True, None  # type: ignore[unreachable]

    def _would_change(self, transaction: Dict[str, Any], new_result: Dict[str, Any]) -> bool:
        """Check if applying categorization would change the transaction."""
        current_category = transaction.get("category", {}).get("title")
        new_category = new_result.get("category")

        # No current category means it would change
        if current_category is None:
            return True

        # Different category means it would change
        return bool(current_category != new_category)

    def _stub_categorize(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Stub categorization for testing.

        This is a simple stub that categorizes common merchants.
        In production, this would be replaced by actual categorization logic.
        """
        payee = transaction.get("payee", "").upper()

        # Simple rule-based categorization for testing
        if any(merchant in payee for merchant in ["WOOLWORTHS", "COLES"]):
            return {"category": "Groceries", "confidence": 95}
        elif "UBER" in payee:
            return {"category": "Transport", "confidence": 90}
        else:
            return {"category": "Uncategorized", "confidence": 50}
