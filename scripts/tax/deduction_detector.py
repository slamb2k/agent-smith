"""Deduction detection for Australian tax compliance (Level 2 intelligence)."""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from scripts.tax.ato_categories import ATOCategoryMapper

logger = logging.getLogger(__name__)


class DeductionDetector:
    """Detects tax-deductible transactions using pattern matching and rules.

    Implements Level 2 tax intelligence:
    - Pattern-based deduction detection
    - Confidence scoring (high/medium/low)
    - Time-based commuting detection
    - Substantiation threshold checking
    - ATO category mapping integration
    """

    def __init__(self, patterns_file: Optional[Path] = None):
        """Initialize deduction detector.

        Args:
            patterns_file: Path to deduction patterns JSON file
        """
        if patterns_file is None:
            project_root = Path(__file__).parent.parent.parent
            patterns_file = project_root / "data" / "tax" / "deduction_patterns.json"

        self.patterns_file = Path(patterns_file)
        self.patterns: List[Dict[str, Any]] = []
        self.substantiation_thresholds: Dict[str, int] = {}
        self.commuting_hours: Dict[str, Any] = {}
        self.instant_asset_threshold: int = 20000
        self.ato_mapper = ATOCategoryMapper()

        if self.patterns_file.exists():
            self.load_patterns()

    def load_patterns(self) -> None:
        """Load deduction patterns from JSON file."""
        if not self.patterns_file.exists():
            logger.warning(f"Patterns file not found: {self.patterns_file}")
            return

        try:
            with open(self.patterns_file) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in patterns file {self.patterns_file}: {e}")
            raise ValueError(f"Failed to parse deduction patterns: {e}") from e
        except Exception as e:
            logger.error(f"Error reading patterns file {self.patterns_file}: {e}")
            raise

        self.patterns = data.get("patterns", [])
        self.substantiation_thresholds = data.get("substantiation_thresholds", {})
        self.commuting_hours = data.get("commuting_hours", {})

        instant_asset_data = data.get("instant_asset_write_off", {})
        self.instant_asset_threshold = instant_asset_data.get("threshold", 20000)

        logger.info(f"Loaded {len(self.patterns)} deduction patterns")

    def detect_deduction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Detect if a transaction is tax deductible.

        Args:
            transaction: Transaction dict with payee, amount, date, category, etc.

        Returns:
            Dict with:
                - is_deductible (bool)
                - confidence (str): high/medium/low
                - reason (str)
                - ato_category (str)
                - ato_code (str or None)
                - substantiation_required (bool)
                - threshold (int)
                - substantiation_notes (str)
                - suggestions (str, optional)
        """
        payee = transaction.get("payee", "").lower()
        amount = abs(float(transaction.get("amount", 0)))
        category_name = transaction.get("category", {}).get("title", "")
        date_str = transaction.get("date", "")
        time_str = transaction.get("time", "")
        notes = transaction.get("notes", "").lower()

        # Match against patterns
        matched_pattern = self._match_pattern(transaction, payee, category_name, notes)

        if matched_pattern:
            result = self._build_result_from_pattern(
                matched_pattern, transaction, amount, date_str, time_str
            )
        else:
            # No pattern match - use ATO category mapper
            result = self._build_result_from_ato_mapper(category_name, amount)

        return result

    def _match_pattern(
        self, transaction: Dict[str, Any], payee: str, category_name: str, notes: str
    ) -> Optional[Dict[str, Any]]:
        """Match transaction against deduction patterns.

        Args:
            transaction: Transaction dict
            payee: Lowercase payee name
            category_name: Category title
            notes: Lowercase transaction notes

        Returns:
            Matched pattern dict or None
        """
        for pattern in self.patterns:
            category_match = False
            payee_match = False

            # Check category patterns
            category_patterns = pattern.get("category_patterns", [])
            if category_patterns and category_name in category_patterns:
                # Check for keyword requirements
                keywords = pattern.get("keywords", [])
                if keywords:
                    # Must match at least one keyword if keywords are specified
                    if any(kw.lower() in notes or kw.lower() in payee for kw in keywords):
                        category_match = True
                else:
                    # No keywords required, category match is enough
                    category_match = True

            # Check payee patterns
            payee_patterns = pattern.get("payee_patterns", [])
            if payee_patterns:
                if any(pp.lower() in payee for pp in payee_patterns):
                    payee_match = True

            # Match if either category or payee matched
            if category_match or payee_match:
                return pattern

        return None

    def _build_result_from_pattern(
        self,
        pattern: Dict[str, Any],
        transaction: Dict[str, Any],
        amount: float,
        date_str: str,
        time_str: str,
    ) -> Dict[str, Any]:
        """Build deduction result from matched pattern.

        Args:
            pattern: Matched pattern dict
            transaction: Transaction dict
            amount: Absolute transaction amount
            date_str: Transaction date
            time_str: Transaction time

        Returns:
            Deduction detection result
        """
        is_deductible = pattern.get("deductible", False)
        confidence = pattern.get("confidence", "medium")

        # Special handling for commuting detection
        if pattern.get("commuting_detection") and time_str and date_str:
            is_commuting = self._is_commuting_time(date_str, time_str)
            if is_commuting:
                is_deductible = False
                confidence = "high"
                reason = "Commuting between home and regular workplace is not deductible"
            else:
                reason = f"Business travel - {pattern.get('reason', 'Unknown')}"
                # Lower confidence for business travel without more context
                confidence = "medium"
        else:
            reason = pattern.get("reason", "")

        # Determine substantiation requirements
        threshold = pattern.get(
            "special_threshold", self.substantiation_thresholds.get("default", 300)
        )
        substantiation_required = amount >= threshold
        substantiation_notes = pattern.get("substantiation_notes", "")

        # Build base result
        result = {
            "is_deductible": is_deductible,
            "confidence": confidence,
            "reason": reason,
            "ato_category": pattern.get("ato_category", "Unknown"),
            "ato_code": pattern.get("ato_code"),
            "substantiation_required": substantiation_required,
            "threshold": threshold,
            "substantiation_notes": substantiation_notes,
        }

        # Add suggestions for specific patterns
        suggestions = []

        if pattern.get("requires_apportionment"):
            suggestions.append("Consider apportioning costs between work and personal use.")

        if (
            pattern.get("instant_asset_write_off_eligible")
            and amount < self.instant_asset_threshold
        ):
            suggestions.append(
                f"May qualify for instant asset write-off "
                f"(under ${self.instant_asset_threshold:,.0f})."
            )

        if suggestions:
            result["suggestions"] = " ".join(suggestions)

        return result

    def _build_result_from_ato_mapper(self, category_name: str, amount: float) -> Dict[str, Any]:
        """Build deduction result using ATO category mapper fallback.

        Args:
            category_name: Category title
            amount: Absolute transaction amount

        Returns:
            Deduction detection result
        """
        ato_info = self.ato_mapper.get_ato_category(category_name)

        is_deductible = ato_info.get("deductible", False)
        threshold = ato_info.get("threshold", self.substantiation_thresholds.get("default", 300))
        substantiation_required = amount >= threshold if threshold else False

        return {
            "is_deductible": is_deductible,
            "confidence": "low",  # Low confidence for unmapped patterns
            "reason": ato_info.get("notes", "No specific pattern matched"),
            "ato_category": ato_info.get("ato_category", "Unknown"),
            "ato_code": ato_info.get("ato_code"),
            "substantiation_required": substantiation_required,
            "threshold": threshold or 300,
            "substantiation_notes": "Manual review recommended. Consult tax professional.",
        }

    def _is_commuting_time(self, date_str: str, time_str: str) -> bool:
        """Determine if transaction occurred during typical commuting hours.

        Args:
            date_str: Date string (YYYY-MM-DD)
            time_str: Time string (HH:MM:SS)

        Returns:
            True if transaction is during weekday commuting hours
        """
        try:
            # Parse date and time
            txn_date = datetime.strptime(date_str, "%Y-%m-%d")
            txn_time = datetime.strptime(time_str, "%H:%M:%S").time()

            # Check if weekday (Monday=0, Sunday=6)
            if txn_date.weekday() >= 5:  # Weekend
                return False

            # Check morning commute
            morning = self.commuting_hours.get("weekday_morning", {})
            if morning:
                morning_start = datetime.strptime(morning.get("start", "06:00"), "%H:%M").time()
                morning_end = datetime.strptime(morning.get("end", "09:30"), "%H:%M").time()
                if morning_start <= txn_time <= morning_end:
                    return True

            # Check evening commute
            evening = self.commuting_hours.get("weekday_evening", {})
            if evening:
                evening_start = datetime.strptime(evening.get("start", "16:30"), "%H:%M").time()
                evening_end = datetime.strptime(evening.get("end", "19:00"), "%H:%M").time()
                if evening_start <= txn_time <= evening_end:
                    return True

            return False

        except (ValueError, AttributeError) as e:
            logger.warning(f"Error parsing date/time for commuting detection: {e}")
            return False

    def detect_deductions_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect deductions for multiple transactions.

        Args:
            transactions: List of transaction dicts

        Returns:
            List of deduction detection results (same order as input)
        """
        results = []
        for txn in transactions:
            try:
                result = self.detect_deduction(txn)
                results.append(result)
            except Exception as e:
                logger.error(f"Error detecting deduction for transaction {txn.get('id')}: {e}")
                # Return error result
                results.append(
                    {
                        "is_deductible": False,
                        "confidence": "low",
                        "reason": f"Error during detection: {str(e)}",
                        "ato_category": "Unknown",
                        "ato_code": None,
                        "substantiation_required": False,
                        "threshold": 300,
                        "substantiation_notes": "Manual review required due to error.",
                    }
                )

        return results

    def get_deductible_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of deductible transactions.

        Args:
            transactions: List of transaction dicts

        Returns:
            Dict with summary statistics:
                - total_transactions (int)
                - deductible_count (int)
                - non_deductible_count (int)
                - total_deductible_amount (float)
                - high_confidence_count (int)
                - requires_substantiation_count (int)
        """
        results = self.detect_deductions_batch(transactions)

        deductible_count = sum(1 for r in results if r["is_deductible"])
        high_confidence = sum(1 for r in results if r["confidence"] == "high")
        substantiation = sum(1 for r in results if r["substantiation_required"])

        deductible_amount = sum(
            abs(float(txn.get("amount", 0)))
            for txn, result in zip(transactions, results)
            if result["is_deductible"]
        )

        return {
            "total_transactions": len(transactions),
            "deductible_count": deductible_count,
            "non_deductible_count": len(transactions) - deductible_count,
            "total_deductible_amount": deductible_amount,
            "high_confidence_count": high_confidence,
            "requires_substantiation_count": substantiation,
        }
