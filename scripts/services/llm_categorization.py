"""LLM-powered categorization service using subagent context.

This service provides LLM-based transaction categorization as a fallback
when rule-based categorization doesn't match or needs validation.

Key features:
- Prompt building with full category hierarchy and transaction details
- Response parsing supporting both text and JSON formats
- Intelligence mode integration (Conservative/Smart/Aggressive)
- Confidence threshold logic for auto-apply vs ask-user decisions
"""

import re
import json
import logging
from typing import List, Dict, Any

# Import from rule_engine to avoid duplication
from scripts.core.rule_engine import IntelligenceMode

logger = logging.getLogger(__name__)


class LLMCategorizationService:
    """Service for LLM-powered transaction categorization.

    Uses the subagent's own LLM context rather than external API calls.
    This is implemented via prompt instructions to the subagent.
    """

    def __init__(self) -> None:
        """Initialize LLM categorization service."""
        # Intelligence mode thresholds
        self.thresholds = {
            IntelligenceMode.CONSERVATIVE: {
                "auto_apply": 999,  # Never auto-apply (impossible threshold)
                "ask_user": 0,  # Always ask
            },
            IntelligenceMode.SMART: {
                "auto_apply": 90,  # ≥90% auto-apply
                "ask_user": 70,  # 70-89% ask
            },
            IntelligenceMode.AGGRESSIVE: {
                "auto_apply": 80,  # ≥80% auto-apply
                "ask_user": 50,  # 50-79% ask
            },
        }

    def build_categorization_prompt(
        self,
        transactions: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
        mode: IntelligenceMode = IntelligenceMode.SMART,
    ) -> str:
        """Build prompt for LLM to categorize transactions.

        Args:
            transactions: List of transaction dicts (id, payee, amount, date)
            categories: List of category dicts (title, parent hierarchy)
            mode: Intelligence mode affecting confidence expectations

        Returns:
            Formatted prompt string for LLM
        """
        # Build category hierarchy section
        category_lines = []
        for cat in categories:
            parent = cat.get("parent", "")
            if parent:
                category_lines.append(f"- {parent} > {cat['title']}")
            else:
                category_lines.append(f"- {cat['title']}")

        categories_text = "\n".join(category_lines)

        # Build transactions section with all relevant details
        transaction_lines = []
        for i, txn in enumerate(transactions, 1):
            payee = txn.get("payee", "Unknown")
            amount = txn.get("amount", 0)
            date = txn.get("date", "")
            date_str = f" on {date}" if date else ""

            transaction_lines.append(f"Transaction {i}: {payee} (${abs(amount):.2f}){date_str}")

        transactions_text = "\n".join(transaction_lines)

        # Mode-specific guidance
        mode_guidance = {
            IntelligenceMode.CONSERVATIVE: (
                "Use high confidence thresholds. Only suggest categories "
                "you're very certain about (90%+)."
            ),
            IntelligenceMode.SMART: (
                "Balance accuracy and coverage. Suggest categories with " "good confidence (70%+)."
            ),
            IntelligenceMode.AGGRESSIVE: (
                "Be more lenient with suggestions. Include reasonable "
                "matches even with moderate confidence (50%+)."
            ),
        }

        guidance = mode_guidance.get(mode, mode_guidance[IntelligenceMode.SMART])

        prompt = f"""Categorize these financial transactions.

INTELLIGENCE MODE: {mode.value}
GUIDANCE: {guidance}

Available Categories:
{categories_text}

IMPORTANT: Always use the MOST SPECIFIC subcategory available.
- For "Parent > Child" hierarchies, use the full "Parent > Child" format
- Example: Use "Food & Dining > Groceries" for supermarkets, NOT just "Food & Dining"
- Example: Use "Food & Dining > Restaurants" for dining out, NOT just "Food & Dining"
- Only use parent categories when no specific subcategory fits

Transactions to Categorize:
{transactions_text}

For each transaction provide:
- transaction_id: The transaction number (1, 2, 3, etc.)
- category: The MOST SPECIFIC category from the list above
  (use "Parent > Child" format when available)
- confidence: Integer 0-100 indicating certainty
- reasoning: Brief explanation for your choice
"""

        return prompt

    def parse_categorization_response(
        self, llm_response: str, transaction_ids: List[int]
    ) -> Dict[int, Dict[str, Any]]:
        """Parse LLM categorization response.

        Supports both text format and JSON format responses.

        Args:
            llm_response: Raw LLM response text
            transaction_ids: Original transaction IDs (in order)

        Returns:
            Dict mapping transaction_id to categorization result
            {
                transaction_id: {
                    "transaction_id": int,
                    "category": str,
                    "confidence": int,
                    "reasoning": str,
                    "source": "llm"
                }
            }
        """
        logger.debug(f"Parsing categorization response (length: {len(llm_response)})")
        logger.debug(f"Full response: {llm_response}")

        # Try JSON format first
        try:
            # Try array format first (legacy): [...]
            # Check for array BEFORE object to avoid matching first object in array
            json_match = re.search(r"\[[\s\S]*\]", llm_response)
            if json_match:
                parsed_json = json.loads(json_match.group(0))
                if isinstance(parsed_json, list):
                    results = {}
                    for item in parsed_json:
                        # Legacy array format uses sequential IDs (1, 2, 3...)
                        sequential_id = item.get("transaction_id")
                        if sequential_id is not None and 1 <= sequential_id <= len(transaction_ids):
                            # Map sequential ID to actual transaction ID
                            actual_txn_id = transaction_ids[sequential_id - 1]
                            results[actual_txn_id] = {
                                "transaction_id": actual_txn_id,
                                "category": item.get("category"),
                                "confidence": item.get("confidence", 50),
                                "reasoning": item.get("reasoning", ""),
                                "source": "llm",
                            }
                    return results

            # Try object format (structured output): {"transactions": [...]}
            json_match = re.search(r"\{[\s\S]*\}", llm_response)
            if json_match:
                parsed_json = json.loads(json_match.group(0))

                # Check for structured output format with "transactions" key (current schema)
                if isinstance(parsed_json, dict) and "transactions" in parsed_json:
                    transactions_list = parsed_json.get("transactions", [])
                    if isinstance(transactions_list, list):
                        results = {}
                        for item in transactions_list:
                            # LLM uses sequential IDs (1, 2, 3...), map to actual transaction IDs
                            sequential_id = item.get("transaction_id")
                            if sequential_id is not None and 1 <= sequential_id <= len(
                                transaction_ids
                            ):
                                # Map sequential ID to actual transaction ID
                                actual_txn_id = transaction_ids[sequential_id - 1]
                                results[actual_txn_id] = {
                                    "transaction_id": actual_txn_id,
                                    "category": item.get("category"),
                                    "confidence": item.get("confidence", 50),
                                    "reasoning": item.get("reasoning", ""),
                                    "source": "llm",
                                }
                        return results

                # Legacy: Check for "categorizations" key (old schema)
                if isinstance(parsed_json, dict) and "categorizations" in parsed_json:
                    categorizations = parsed_json.get("categorizations", [])
                    if isinstance(categorizations, list):
                        results = {}
                        for item in categorizations:
                            txn_id = item.get("transaction_id")
                            if txn_id is not None:
                                results[txn_id] = {
                                    "transaction_id": txn_id,
                                    "category": item.get("category"),
                                    "confidence": item.get("confidence", 50),
                                    "reasoning": item.get("reasoning", ""),
                                    "source": "llm",
                                }
                        return results

                # Check for single transaction object (legacy format)
                if isinstance(parsed_json, dict) and "transaction_id" in parsed_json:
                    txn_id = parsed_json.get("transaction_id")
                    results = {
                        txn_id: {
                            "transaction_id": txn_id,
                            "category": parsed_json.get("category"),
                            "confidence": parsed_json.get("confidence", 50),
                            "reasoning": parsed_json.get("reasoning", ""),
                            "source": "llm",
                        }
                    }
                    return results

        except (json.JSONDecodeError, ValueError):
            # Fall back to text parsing
            pass

        # Text format parsing
        results = {}

        # Split response into transaction blocks
        blocks = re.split(r"Transaction \d+:", llm_response)
        blocks = [b.strip() for b in blocks if b.strip()]

        for i, block in enumerate(blocks):
            if i >= len(transaction_ids):
                break

            txn_id = transaction_ids[i]

            # Extract category
            category_match = re.search(r"Category:\s*(.+?)(?:\n|$)", block)
            category = category_match.group(1).strip() if category_match else None

            # Extract confidence
            confidence_match = re.search(r"Confidence:\s*(\d+)", block)
            confidence = (
                int(confidence_match.group(1)) if confidence_match else 50
            )  # Default to 50% if missing

            # Extract reasoning (optional)
            reasoning_match = re.search(r"Reasoning:\s*(.+?)(?:\n\n|$)", block, re.DOTALL)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

            results[txn_id] = {
                "transaction_id": txn_id,
                "category": category,
                "confidence": confidence,
                "reasoning": reasoning,
                "source": "llm",
            }

        return results

    def categorize_batch(
        self,
        transactions: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
        mode: IntelligenceMode = IntelligenceMode.SMART,
    ) -> Dict[str, Any]:
        """Categorize a batch of transactions using Claude Code's LLM context.

        This method should be called from within a subagent context where
        Claude's LLM is available. It builds a prompt and returns the response
        for the parent to parse.

        Args:
            transactions: List of transaction dicts
            categories: Available categories for matching
            mode: Intelligence mode (Conservative/Smart/Aggressive)

        Returns:
            Dict mapping transaction IDs to categorization results
        """
        if not transactions:
            return {}

        # Build prompt for all transactions
        prompt = self.build_categorization_prompt(transactions, categories, mode)

        # CRITICAL: This method must be called from within a subagent context.
        # The parent workflow uses the Task tool to delegate here.
        # We return the prompt so parent can send to subagent.

        # For now, return the prompt as a special marker
        # The orchestration layer will detect this and delegate properly
        return {
            "_needs_llm": True,
            "_prompt": prompt,
            "_transaction_ids": [t["id"] for t in transactions],
        }

    def validate_batch(
        self,
        validations: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Validate a batch of rule-based categorizations using LLM.

        Args:
            validations: List of dicts with:
                - transaction: Transaction dict
                - suggested_category: Category from rule
                - confidence: Rule confidence score
            categories: Available categories for alternative suggestions

        Returns:
            Dict mapping transaction IDs to validation results:
                - validation: "CONFIRM" or "REJECT"
                - confidence: Adjusted confidence (0-100)
                - reasoning: Explanation
                - category: Original or new category (if REJECT)
        """
        if not validations:
            return {}

        # Build category hierarchy section (same as categorization prompt)
        category_lines = []
        for cat in categories:
            parent = cat.get("parent", "")
            if parent:
                category_lines.append(f"- {parent} > {cat['title']}")
            else:
                category_lines.append(f"- {cat['title']}")

        categories_text = "\n".join(category_lines)

        # Build combined validation prompt
        prompt_parts = [
            "Validate the following transaction categorizations.\n",
            "\nAvailable Categories:",
            categories_text,
            "\nIMPORTANT: If you REJECT a suggestion, provide the MOST",
            "SPECIFIC alternative category.",
            '- For "Parent > Child" hierarchies, use the full',
            '  "Parent > Child" format',
            '- Example: Use "Food & Dining > Groceries" for supermarkets,',
            '  NOT just "Food & Dining"',
            "- Only use parent categories when no specific subcategory fits\n",
        ]

        for i, val in enumerate(validations, 1):
            txn = val["transaction"]
            prompt_parts.append(
                f"\n{i}. "
                + self.build_validation_prompt(txn, val["suggested_category"], val["confidence"])
            )

        prompt_parts.append("\n\nProvide validation for each transaction in order (1, 2, 3...).")

        prompt = "\n".join(prompt_parts)

        # Return prompt for parent to delegate
        return {
            "_needs_llm": True,
            "_prompt": prompt,
            "_transaction_ids": [v["transaction"]["id"] for v in validations],
            "_validations": validations,  # Pass through for parsing
            "_type": "validation",
        }

    def _should_auto_apply(self, confidence: int, mode: IntelligenceMode) -> bool:
        """Determine if categorization should be auto-applied based on confidence and mode.

        Args:
            confidence: Confidence score (0-100)
            mode: Intelligence mode

        Returns:
            True if should auto-apply without asking user
        """
        threshold = self.thresholds[mode]["auto_apply"]
        return confidence >= threshold

    def _should_ask_user(self, confidence: int, mode: IntelligenceMode) -> bool:
        """Determine if categorization should prompt user for confirmation.

        Args:
            confidence: Confidence score (0-100)
            mode: Intelligence mode

        Returns:
            True if should ask user for confirmation
        """
        auto_threshold = self.thresholds[mode]["auto_apply"]
        ask_threshold = self.thresholds[mode]["ask_user"]

        # Ask if between ask_threshold and auto_threshold
        return ask_threshold <= confidence < auto_threshold

    def build_validation_prompt(
        self,
        transaction: Dict[str, Any],
        suggested_category: str,
        rule_confidence: int,
    ) -> str:
        """Build prompt for LLM to validate a rule-based categorization.

        Args:
            transaction: Transaction dict
            suggested_category: Category suggested by rule
            rule_confidence: Confidence of the rule match

        Returns:
            Formatted validation prompt
        """
        payee = transaction.get("payee", "Unknown")
        amount = transaction.get("amount", 0)
        date = transaction.get("date", "")
        date_str = f" on {date}" if date else ""

        prompt = f"""Validate this transaction categorization:

Transaction: {payee} (${abs(amount):.2f}){date_str}
Suggested Category: {suggested_category}
Rule Confidence: {rule_confidence}%

Does this categorization look correct? Provide:
1. Validation: CONFIRM or REJECT
2. Adjusted Confidence: 0-100%
3. Reasoning: Brief explanation

If you REJECT, suggest the MOST SPECIFIC better category from the available categories list.
"""

        return prompt

    def parse_validation_response(
        self,
        llm_response: str,
        original_category: str,
        original_confidence: int,
    ) -> Dict[str, Any]:
        """Parse LLM validation response.

        Args:
            llm_response: Raw LLM response
            original_category: Original suggested category
            original_confidence: Original confidence score

        Returns:
            Validation result dict with validation, category, confidence, reasoning
        """
        # Check validation status
        validation = "UNKNOWN"
        if "CONFIRM" in llm_response.upper():
            validation = "CONFIRM"
        elif "REJECT" in llm_response.upper():
            validation = "REJECT"

        # Extract adjusted confidence
        confidence_match = re.search(r"Adjusted Confidence:\s*(\d+)", llm_response)
        adjusted_confidence = (
            int(confidence_match.group(1)) if confidence_match else original_confidence
        )

        # Extract suggested category if rejected
        suggested_category = original_category
        if validation == "REJECT":
            category_match = re.search(r"Suggested Category:\s*(.+?)(?:\n|$)", llm_response)
            if category_match:
                suggested_category = category_match.group(1).strip()

        # Extract reasoning
        reasoning_match = re.search(r"Reasoning:\s*(.+?)(?:\n\n|$)", llm_response, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

        return {
            "validation": validation,
            "category": suggested_category,
            "confidence": adjusted_confidence,
            "reasoning": reasoning,
        }

    def parse_validation_batch_response(
        self,
        llm_response: str,
        validations: List[Dict[str, Any]],
    ) -> Dict[int, Dict[str, Any]]:
        """Parse batch validation response from LLM.

        Args:
            llm_response: Raw LLM response with multiple validations
            validations: Original validation request dicts with:
                - transaction: Transaction dict
                - suggested_category: Category from rule
                - confidence: Rule confidence score

        Returns:
            Dict mapping transaction IDs to validation results:
                - validation: "CONFIRM" or "REJECT"
                - confidence: Adjusted confidence (0-100)
                - reasoning: Explanation
                - category: Original or new category (if REJECT)
        """
        results = {}

        # Split response into validation blocks (numbered 1, 2, 3...)
        blocks = re.split(r"(?:^|\n)(\d+)\.", llm_response, flags=re.MULTILINE)
        blocks = [b.strip() for b in blocks if b.strip()]

        # Process each validation block
        for i, val_dict in enumerate(validations):
            txn = val_dict["transaction"]
            txn_id = txn["id"]
            original_category = val_dict["suggested_category"]
            original_confidence = val_dict["confidence"]

            # Try to find matching block (index i*2 because split includes numbers)
            if i * 2 + 1 < len(blocks):
                block_text = blocks[i * 2 + 1]

                # Parse this validation response
                val_result = self.parse_validation_response(
                    llm_response=block_text,
                    original_category=original_category,
                    original_confidence=original_confidence,
                )

                results[txn_id] = val_result
            else:
                # No response for this transaction - default to CONFIRM
                results[txn_id] = {
                    "validation": "CONFIRM",
                    "category": original_category,
                    "confidence": original_confidence,
                    "reasoning": "No validation response from LLM",
                }

        return results
