"""Transaction categorization operations."""

import logging
from typing import List, Dict, Any, Optional
from scripts.core.rule_engine import RuleEngine
from scripts.core.api_client import PocketSmithClient


logger = logging.getLogger(__name__)


def categorize_transaction(
    transaction: Dict[str, Any],
    engine: RuleEngine,
    api_client: Optional[PocketSmithClient] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Categorize a single transaction using rule engine.

    Args:
        transaction: Transaction dict with id, payee, amount, etc.
        engine: RuleEngine instance
        api_client: PocketSmith API client (required if not dry_run)
        dry_run: If True, don't actually update transaction

    Returns:
        Result dict with matched, rule_name, category_id, auto_applied, etc.
    """
    result = {
        "transaction_id": transaction.get("id"),
        "payee": transaction.get("payee"),
        "matched": False,
        "rule_name": None,
        "category_id": None,
        "confidence": None,
        "auto_applied": False,
        "requires_approval": False,
    }

    # Find best matching rule
    best_match = engine.find_best_match(transaction)

    if not best_match:
        return result

    # Rule matched
    result["matched"] = True
    result["rule_name"] = best_match.name
    result["category_id"] = best_match.category_id
    result["confidence"] = best_match.confidence

    # Determine if should auto-apply or ask for approval
    if engine.should_auto_apply(best_match):
        result["auto_applied"] = True

        if not dry_run:
            if api_client is None:
                raise ValueError("api_client required when dry_run=False")

            # Apply categorization via API
            api_client.update_transaction(
                transaction_id=transaction["id"],
                category_id=best_match.category_id,
            )

            # Record performance
            best_match.record_application()
            logger.info(f"Auto-applied rule '{best_match.name}' to transaction {transaction['id']}")

    elif engine.should_ask_approval(best_match):
        result["requires_approval"] = True
        best_match.record_match()

    else:
        # Below threshold, skip
        best_match.record_match()

    return result


def categorize_batch(
    transactions: List[Dict[str, Any]],
    engine: RuleEngine,
    api_client: Optional[PocketSmithClient] = None,
    dry_run: bool = True,
) -> List[Dict[str, Any]]:
    """Categorize a batch of transactions.

    Args:
        transactions: List of transaction dicts
        engine: RuleEngine instance
        api_client: PocketSmith API client (required if not dry_run)
        dry_run: If True, don't actually update transactions

    Returns:
        List of result dicts
    """
    results = []

    for txn in transactions:
        result = categorize_transaction(txn, engine, api_client, dry_run)
        results.append(result)

    # Summary logging
    matched = sum(1 for r in results if r["matched"])
    auto_applied = sum(1 for r in results if r["auto_applied"])
    requires_approval = sum(1 for r in results if r["requires_approval"])

    logger.info(
        f"Batch categorization: {len(transactions)} transactions, "
        f"{matched} matched, {auto_applied} auto-applied, "
        f"{requires_approval} require approval"
    )

    return results
