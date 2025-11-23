# Real LLM Integration - Implementation Plan

**Date:** 2025-11-22
**Status:** Ready for Implementation
**Prerequisite:** PR #7 (LLM Categorization & Labeling Foundation) must be merged

## Executive Summary

This plan implements "Real LLM Integration" by completing the two missing pieces from the original design:

1. **Case 1: Batch Uncategorized Transactions** - Collect transactions with no rule match and process in batches via Claude Code's LLM context
2. **Case 2: Batch Medium-Confidence Validation** - Validate rule matches with 70-89% confidence (Smart mode) or 50-79% (Aggressive mode) in batches

**Key Change:** Replace placeholder `categorize_batch()` and add validation workflow using Claude Code's Task tool for subagent delegation, NOT external Anthropic API calls.

## Current State Analysis

### What Exists (From PR #7)

✅ **LLM Service Methods** (`scripts/services/llm_categorization.py`):
- `build_categorization_prompt()` - Creates batch categorization prompts
- `parse_categorization_response()` - Parses LLM batch responses
- `build_validation_prompt()` - Creates validation prompts
- `parse_validation_response()` - Parses validation responses
- All methods have passing tests (22 tests total)

✅ **Workflow Structure** (`scripts/workflows/categorization.py`):
- `categorize_transaction()` - Main hybrid flow entry point
- `_get_intelligence_mode()` - Converts mode string to enum
- `suggest_rule_from_llm_result()` - Creates rules from LLM patterns
- Basic structure exists but missing validation logic

✅ **Unified Rule Engine** (`scripts/core/unified_rules.py`):
- `categorize_and_label()` - Returns confidence scores
- Two-phase execution (categories → labels)
- Full test coverage (445 tests)

### What's Missing

❌ **Case 1 (Uncategorized) - Batching**:
- Workflow calls `categorize_batch([transaction])` with single item (line 165)
- No collection of uncategorized transactions before LLM call
- No batch size optimization

❌ **Case 2 (Medium-Confidence Validation) - Completely Missing**:
- No confidence checking after rule match
- No `_should_validate_with_llm()` method
- Validation methods exist but never called
- No batch validation workflow

❌ **Subagent Integration - Placeholder Only**:
- `categorize_batch()` returns empty dict with warning log
- No actual Task tool delegation
- No prompt → subagent → response flow

## Architecture Overview

### Hybrid Categorization Flow (Updated)

```
Transaction Input
     ↓
┌────────────────────────────────────────────┐
│  Phase 1: Rule Engine                      │
│  - Try to match category rules             │
│  - Returns: {category, confidence, labels} │
└────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────┐
│  Decision Point: Check Confidence          │
│                                            │
│  High (90%+)    Medium (70-89%)   No Match │
│      ↓              ↓                ↓     │
│   Trust Rule    Validate (Case 2)  Case 1 │
└────────────────────────────────────────────┘
     ↓                ↓                ↓
┌─────────┐   ┌──────────────┐   ┌──────────┐
│ Return  │   │ Batch        │   │ Batch    │
│ Result  │   │ Validation   │   │ LLM      │
│         │   │ via Subagent │   │ via Sub  │
└─────────┘   └──────────────┘   └──────────┘
                    ↓                ↓
              ┌──────────────┐   ┌──────────┐
              │ CONFIRM:     │   │ Parse    │
              │ Upgrade conf │   │ Response │
              │ REJECT:      │   │          │
              │ Use LLM cat  │   │          │
              └──────────────┘   └──────────┘
                    ↓                ↓
              ┌──────────────────────────┐
              │ Phase 2: Label Rules     │
              │ - Apply to categorized   │
              │ - Return final result    │
              └──────────────────────────┘
```

### Batching Strategy

**Batch Size by Mode:**
- Conservative: 20 transactions (cautious, more review)
- Smart: 50 transactions (balanced)
- Aggressive: 100 transactions (maximize throughput)

**Two Separate Batch Types:**

1. **Categorization Batches** (Case 1):
   - Collect all uncategorized transactions
   - Group into batches by mode threshold
   - Single subagent call per batch
   - Parse all responses at once

2. **Validation Batches** (Case 2):
   - Collect all medium-confidence rule matches
   - Group into batches by mode threshold
   - Single subagent call per batch
   - Handle CONFIRM vs REJECT for each

**Progress Reporting:**
```
Processing 150 uncategorized transactions...
  Batch 1/3 (50 transactions): ████████████████████ 100%
  Batch 2/3 (50 transactions): ████████████████████ 100%
  Batch 3/3 (50 transactions): ████████████████████ 100%
✓ Categorized 142/150 (8 skipped - low confidence)

Validating 45 medium-confidence matches...
  Batch 1/1 (45 transactions): ████████████████████ 100%
✓ Confirmed 38, Upgraded 7 to higher confidence
```

## Implementation Tasks

### Task 1: Add Subagent Delegation Infrastructure

**Goal:** Implement actual Claude Code Task tool delegation for LLM calls.

**Files to Modify:**
- `scripts/services/llm_categorization.py`

**Changes:**

1. **Import Task delegation utilities:**
```python
from typing import TYPE_CHECKING, Any, Dict, List, Optional
import json

if TYPE_CHECKING:
    # Avoid circular import - subagent conductor handles Task tool
    pass
```

2. **Replace `categorize_batch()` placeholder:**
```python
def categorize_batch(
    self,
    transactions: List[Dict[str, Any]],
    categories: List[Dict[str, Any]],
    mode: IntelligenceMode = IntelligenceMode.SMART,
) -> Dict[int, Dict[str, Any]]:
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
```

3. **Add validation batch method:**
```python
def validate_batch(
    self,
    validations: List[Dict[str, Any]],
) -> Dict[int, Dict[str, Any]]:
    """Validate a batch of rule-based categorizations using LLM.

    Args:
        validations: List of dicts with:
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
    if not validations:
        return {}

    # Build combined validation prompt
    prompt_parts = [
        "Validate the following transaction categorizations:\n"
    ]

    for i, val in enumerate(validations, 1):
        txn = val["transaction"]
        prompt_parts.append(
            f"\n{i}. " + self.build_validation_prompt(
                txn,
                val["suggested_category"],
                val["confidence"]
            )
        )

    prompt_parts.append(
        "\n\nProvide validation for each transaction in order (1, 2, 3...)."
    )

    prompt = "\n".join(prompt_parts)

    # Return prompt for parent to delegate
    return {
        "_needs_llm": True,
        "_prompt": prompt,
        "_transaction_ids": [v["transaction"]["id"] for v in validations],
        "_type": "validation",
    }
```

**Testing:**
- Unit test: `test_categorize_batch_returns_prompt_marker()`
- Unit test: `test_validate_batch_builds_combined_prompt()`
- Verify prompt structure includes all transactions

**Acceptance Criteria:**
- `categorize_batch()` returns `_needs_llm` marker instead of empty dict
- `validate_batch()` combines multiple validation prompts
- Both methods return transaction IDs for response mapping

---

### Task 2: Add Subagent Orchestration Layer

**Goal:** Create orchestration methods that use Task tool to delegate to Claude Code's LLM.

**Files to Create:**
- `scripts/orchestration/llm_subagent.py`

**Implementation:**

```python
"""LLM subagent orchestration for Claude Code context."""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class LLMSubagent:
    """Handles delegation of LLM operations to Claude Code subagents.

    This class wraps the Task tool to send prompts to Claude's LLM
    context and parse responses.
    """

    def __init__(self):
        """Initialize LLM subagent orchestrator."""
        pass

    def execute_categorization(
        self,
        prompt: str,
        transaction_ids: List[int],
    ) -> str:
        """Execute categorization prompt via subagent.

        Args:
            prompt: Full categorization prompt for batch
            transaction_ids: Transaction IDs being categorized

        Returns:
            Raw LLM response text
        """
        # IMPLEMENTATION NOTE:
        # In Claude Code, we'll use the Task tool to spawn a subagent.
        # The subagent receives the prompt and has access to Claude's LLM.
        # For now, this is a placeholder that logs the intent.

        logger.info(
            f"Delegating categorization of {len(transaction_ids)} "
            f"transactions to LLM subagent"
        )

        # TODO: Actual Task tool invocation
        # result = task_tool.invoke(
        #     subagent_type="categorization-agent",
        #     prompt=prompt
        # )

        # For testing, return empty response
        # Real implementation will return actual LLM text
        return ""

    def execute_validation(
        self,
        prompt: str,
        transaction_ids: List[int],
    ) -> str:
        """Execute validation prompt via subagent.

        Args:
            prompt: Full validation prompt for batch
            transaction_ids: Transaction IDs being validated

        Returns:
            Raw LLM response text
        """
        logger.info(
            f"Delegating validation of {len(transaction_ids)} "
            f"transactions to LLM subagent"
        )

        # TODO: Actual Task tool invocation
        # result = task_tool.invoke(
        #     subagent_type="validation-agent",
        #     prompt=prompt
        # )

        return ""
```

**Files to Modify:**
- `scripts/workflows/categorization.py`

**Add method to workflow:**
```python
from scripts.orchestration.llm_subagent import LLMSubagent

class CategorizationWorkflow:
    def __init__(self, ...):
        # ... existing init ...
        self.llm_subagent = LLMSubagent()

    def _execute_llm_categorization(
        self,
        transactions: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
    ) -> Dict[int, Dict[str, Any]]:
        """Execute LLM categorization via subagent delegation.

        Args:
            transactions: Batch of transactions to categorize
            categories: Available categories

        Returns:
            Dict mapping transaction IDs to categorization results
        """
        # Get prompt from service
        batch_result = self.llm_service.categorize_batch(
            transactions,
            categories,
            self._get_intelligence_mode()
        )

        # Check if needs LLM delegation
        if not batch_result.get("_needs_llm"):
            # Direct result (shouldn't happen in production)
            return batch_result

        # Delegate to subagent
        prompt = batch_result["_prompt"]
        transaction_ids = batch_result["_transaction_ids"]

        llm_response = self.llm_subagent.execute_categorization(
            prompt,
            transaction_ids
        )

        # Parse response
        return self.llm_service.parse_categorization_response(
            llm_response,
            transaction_ids
        )

    def _execute_llm_validation(
        self,
        validations: List[Dict[str, Any]],
    ) -> Dict[int, Dict[str, Any]]:
        """Execute LLM validation via subagent delegation.

        Args:
            validations: Batch of validation requests

        Returns:
            Dict mapping transaction IDs to validation results
        """
        # Get prompt from service
        batch_result = self.llm_service.validate_batch(validations)

        if not batch_result.get("_needs_llm"):
            return batch_result

        # Delegate to subagent
        prompt = batch_result["_prompt"]
        transaction_ids = batch_result["_transaction_ids"]

        llm_response = self.llm_subagent.execute_validation(
            prompt,
            transaction_ids
        )

        # Parse each validation response
        results = {}
        validation_texts = llm_response.split("\n\n")  # Assume separated

        for i, val_text in enumerate(validation_texts):
            if i >= len(validations):
                break

            txn_id = validations[i]["transaction"]["id"]
            original_cat = validations[i]["suggested_category"]
            original_conf = validations[i]["confidence"]

            results[txn_id] = self.llm_service.parse_validation_response(
                val_text,
                original_cat,
                original_conf
            )

        return results
```

**Testing:**
- `tests/unit/test_llm_subagent.py` - Unit tests for orchestration
- `tests/integration/test_subagent_delegation.py` - Integration test (mock Task tool)

**Acceptance Criteria:**
- LLMSubagent class logs delegation intent
- Workflow methods call service → subagent → parse pipeline
- Tests verify prompt → response flow

---

### Task 3: Implement Case 1 - Batch Uncategorized Transactions

**Goal:** Modify workflow to collect uncategorized transactions and batch process them.

**Files to Modify:**
- `scripts/workflows/categorization.py`

**Changes:**

1. **Add batch size configuration:**
```python
class CategorizationWorkflow:
    def __init__(self, ...):
        # ... existing init ...
        self._batch_sizes = {
            IntelligenceMode.CONSERVATIVE: 20,
            IntelligenceMode.SMART: 50,
            IntelligenceMode.AGGRESSIVE: 100,
        }

    def get_batch_size(self) -> int:
        """Get batch size for current intelligence mode."""
        return self._batch_sizes[self._get_intelligence_mode()]
```

2. **Add batch processing method:**
```python
def categorize_transactions_batch(
    self,
    transactions: List[Dict[str, Any]],
    available_categories: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Categorize multiple transactions with batching and progress.

    Args:
        transactions: List of transaction dicts
        available_categories: Available categories for LLM

    Returns:
        Summary dict with:
            - categorized: Count of successfully categorized
            - skipped: Count skipped (low confidence)
            - results: Dict mapping transaction ID to result
            - validation_upgraded: Count of validations that upgraded confidence
    """
    results = {}
    stats = {
        "categorized": 0,
        "skipped": 0,
        "rule_matches": 0,
        "llm_fallbacks": 0,
        "validations": 0,
        "validation_upgraded": 0,
        "results": results,
    }

    # Phase 1: Apply rules to all transactions
    uncategorized = []
    medium_confidence = []

    for txn in transactions:
        rule_result = self.rule_engine.categorize_and_label(txn)

        if rule_result["category"] is None:
            # No match - collect for LLM categorization
            uncategorized.append(txn)
        else:
            confidence = rule_result["confidence"]
            mode = self._get_intelligence_mode()

            if self._should_validate_with_llm(confidence, mode):
                # Medium confidence - collect for validation
                medium_confidence.append({
                    "transaction": txn,
                    "suggested_category": rule_result["category"],
                    "confidence": confidence,
                    "labels": rule_result["labels"],
                })
            else:
                # High confidence - trust rule
                results[txn["id"]] = rule_result
                stats["categorized"] += 1
                stats["rule_matches"] += 1

    # Phase 2: Batch process uncategorized (Case 1)
    if uncategorized:
        batch_size = self.get_batch_size()
        batch_count = (len(uncategorized) + batch_size - 1) // batch_size

        print(f"\nProcessing {len(uncategorized)} uncategorized transactions...")

        for i in range(0, len(uncategorized), batch_size):
            batch = uncategorized[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            print(f"  Batch {batch_num}/{batch_count} ({len(batch)} transactions)...")

            # Delegate to LLM via subagent
            batch_results = self._execute_llm_categorization(batch, available_categories)

            # Apply labels to LLM-categorized transactions
            for txn in batch:
                if txn["id"] in batch_results:
                    llm_result = batch_results[txn["id"]]

                    if llm_result.get("category"):
                        # Update transaction with category for label matching
                        txn_with_cat = txn.copy()
                        txn_with_cat["category"] = {"title": llm_result["category"]}

                        # Apply label rules
                        label_result = self.rule_engine.categorize_and_label(txn_with_cat)

                        results[txn["id"]] = {
                            "category": llm_result["category"],
                            "labels": label_result["labels"],
                            "confidence": llm_result["confidence"],
                            "source": "llm",
                            "llm_used": True,
                            "reasoning": llm_result.get("reasoning", ""),
                        }
                        stats["categorized"] += 1
                        stats["llm_fallbacks"] += 1
                    else:
                        # LLM returned no category
                        stats["skipped"] += 1

    # Phase 3: Batch validate medium-confidence (Case 2)
    if medium_confidence:
        batch_size = self.get_batch_size()
        batch_count = (len(medium_confidence) + batch_size - 1) // batch_size

        print(f"\nValidating {len(medium_confidence)} medium-confidence matches...")

        for i in range(0, len(medium_confidence), batch_size):
            batch = medium_confidence[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            print(f"  Batch {batch_num}/{batch_count} ({len(batch)} validations)...")

            # Delegate to LLM via subagent
            validation_results = self._execute_llm_validation(batch)

            # Process validation results
            for val_req in batch:
                txn = val_req["transaction"]

                if txn["id"] in validation_results:
                    val_result = validation_results[txn["id"]]

                    if val_result["validation"] == "CONFIRM":
                        # LLM confirmed - use original with upgraded confidence
                        results[txn["id"]] = {
                            "category": val_req["suggested_category"],
                            "labels": val_req["labels"],
                            "confidence": val_result["confidence"],
                            "source": "rule",
                            "llm_used": True,
                            "llm_validated": True,
                            "reasoning": val_result["reasoning"],
                        }
                        stats["validation_upgraded"] += 1
                    else:
                        # LLM rejected - use LLM's category instead
                        new_category = val_result.get("category", val_req["suggested_category"])

                        # Apply labels to new category
                        txn_with_cat = txn.copy()
                        txn_with_cat["category"] = {"title": new_category}
                        label_result = self.rule_engine.categorize_and_label(txn_with_cat)

                        results[txn["id"]] = {
                            "category": new_category,
                            "labels": label_result["labels"],
                            "confidence": val_result["confidence"],
                            "source": "llm",
                            "llm_used": True,
                            "validation_rejected": True,
                            "reasoning": val_result["reasoning"],
                        }

                    stats["categorized"] += 1
                    stats["validations"] += 1

    print(f"\n✓ Categorized {stats['categorized']}/{len(transactions)}")
    print(f"  - Rule matches: {stats['rule_matches']}")
    print(f"  - LLM fallbacks: {stats['llm_fallbacks']}")
    print(f"  - Validations: {stats['validations']} ({stats['validation_upgraded']} upgraded)")
    print(f"  - Skipped: {stats['skipped']}")

    return stats
```

3. **Add helper method for validation check:**
```python
def _should_validate_with_llm(self, confidence: int, mode: IntelligenceMode) -> bool:
    """Determine if rule match needs LLM validation.

    Args:
        confidence: Rule confidence score (0-100)
        mode: Intelligence mode

    Returns:
        True if should validate with LLM
    """
    if mode == IntelligenceMode.CONSERVATIVE:
        # Conservative mode: never auto-apply, but also don't validate
        # Just ask user for everything
        return False

    validation_ranges = {
        IntelligenceMode.SMART: (70, 90),
        IntelligenceMode.AGGRESSIVE: (50, 80),
    }

    if mode in validation_ranges:
        min_conf, max_conf = validation_ranges[mode]
        return min_conf <= confidence < max_conf

    return False
```

**Testing:**
- `tests/integration/test_batch_categorization.py`
- Test with 0 uncategorized (all rules match)
- Test with 100 uncategorized (batching)
- Test with mixed (some rules, some uncategorized)
- Verify batch size respects mode

**Acceptance Criteria:**
- Workflow collects uncategorized before LLM call
- Batches respect mode thresholds (20/50/100)
- Progress reporting shows batch progress
- All uncategorized processed exactly once

---

### Task 4: Implement Case 2 - Medium-Confidence Validation

**Goal:** Add validation workflow for medium-confidence rule matches.

**Changes:** (Already included in Task 3's `categorize_transactions_batch()` method)

**Additional Testing:**
- `tests/unit/test_validation_workflow.py`
- Test validation with CONFIRM (upgrade confidence)
- Test validation with REJECT (use LLM category)
- Test confidence thresholds by mode:
  - Conservative: Never validate (always ask user)
  - Smart: Validate 70-89%
  - Aggressive: Validate 50-79%

**Test Cases:**

```python
def test_smart_mode_validates_medium_confidence():
    """Smart mode validates 70-89% confidence matches."""
    workflow = CategorizationWorkflow(None, mode="smart")

    # 75% confidence should validate
    assert workflow._should_validate_with_llm(75, IntelligenceMode.SMART)

    # 90% confidence should not validate (auto-apply)
    assert not workflow._should_validate_with_llm(90, IntelligenceMode.SMART)

    # 65% confidence should not validate (too low)
    assert not workflow._should_validate_with_llm(65, IntelligenceMode.SMART)

def test_aggressive_mode_validates_lower_confidence():
    """Aggressive mode validates 50-79% confidence."""
    workflow = CategorizationWorkflow(None, mode="aggressive")

    # 55% confidence should validate
    assert workflow._should_validate_with_llm(55, IntelligenceMode.AGGRESSIVE)

    # 80% confidence should not validate (auto-apply)
    assert not workflow._should_validate_with_llm(80, IntelligenceMode.AGGRESSIVE)

def test_conservative_never_validates():
    """Conservative mode never validates (asks user for all)."""
    workflow = CategorizationWorkflow(None, mode="conservative")

    # Even medium confidence doesn't validate
    assert not workflow._should_validate_with_llm(75, IntelligenceMode.CONSERVATIVE)
```

**Acceptance Criteria:**
- Medium-confidence matches collected for validation
- Validation batches sent to LLM subagent
- CONFIRM results upgrade confidence
- REJECT results use LLM category suggestion
- Stats track validation count and upgrade count

---

### Task 5: Update Batch Processing Script

**Goal:** Modify `scripts/operations/categorize_batch.py` to use new batch workflow.

**Files to Modify:**
- `scripts/operations/categorize_batch.py`

**Changes:**

```python
#!/usr/bin/env python3
"""Batch categorization script with real LLM integration."""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

from scripts.core.api_client import PocketSmithClient
from scripts.workflows.categorization import CategorizationWorkflow

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Categorize transactions in batch with LLM assistance"
    )
    parser.add_argument(
        "--period",
        help="Period to process (YYYY-MM or 'last-30-days')",
        default="last-30-days",
    )
    parser.add_argument(
        "--account",
        help="Account ID to filter (optional)",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--mode",
        help="Intelligence mode",
        choices=["conservative", "smart", "aggressive"],
        default="smart",
    )
    parser.add_argument(
        "--dry-run",
        help="Preview without applying changes",
        action="store_true",
    )

    return parser.parse_args()


def get_transactions(
    client: PocketSmithClient,
    period: str,
    account_id: int | None,
) -> List[Dict[str, Any]]:
    """Fetch transactions for period."""
    # Parse period
    if period == "last-30-days":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    else:
        # Parse YYYY-MM
        year, month = map(int, period.split("-"))
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

    # Fetch from API
    user = client.get_authorized_user()
    transactions = client.get_transactions(
        user_id=user["id"],
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    )

    # Filter by account if specified
    if account_id:
        transactions = [
            t for t in transactions
            if t.get("transaction_account", {}).get("id") == account_id
        ]

    # Filter to uncategorized or needs review
    needs_categorization = [
        t for t in transactions
        if not t.get("category") or t.get("needs_review")
    ]

    return needs_categorization


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        # Initialize client
        client = PocketSmithClient()

        # Fetch transactions
        print(f"Fetching transactions for {args.period}...")
        transactions = get_transactions(client, args.period, args.account)

        if not transactions:
            print("No transactions need categorization.")
            return 0

        print(f"Found {len(transactions)} transactions needing categorization.\n")

        # Get available categories
        user = client.get_authorized_user()
        categories = client.get_categories(user["id"])

        # Initialize workflow
        workflow = CategorizationWorkflow(
            client=client,
            mode=args.mode,
        )

        # Process batch
        if args.dry_run:
            print("DRY RUN MODE - No changes will be applied\n")

        results = workflow.categorize_transactions_batch(
            transactions=transactions,
            available_categories=categories,
        )

        # Apply results (if not dry run)
        if not args.dry_run:
            print("\nApplying categorizations...")
            applied = 0

            for txn_id, result in results["results"].items():
                if result.get("category"):
                    # Find category ID
                    cat = next(
                        (c for c in categories if c["title"] == result["category"]),
                        None
                    )

                    if cat:
                        client.update_transaction(
                            txn_id,
                            category_id=cat["id"],
                        )
                        applied += 1

            print(f"✓ Applied {applied} categorizations")

        return 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Testing:**
- Manual test: `uv run python scripts/operations/categorize_batch.py --dry-run`
- Verify batch progress output
- Verify stats summary

**Acceptance Criteria:**
- Script uses new `categorize_transactions_batch()` method
- Progress reporting shows batch processing
- Dry run mode works correctly
- Results applied to PocketSmith (when not dry run)

---

### Task 6: Add Slash Command Integration

**Goal:** Create `/smith:categorize` slash command that uses batch workflow.

**Files to Create:**
- `.claude/commands/smith:categorize.md`

**Implementation:**

```markdown
Categorize transactions using the hybrid rule + LLM workflow.

You are the Agent Smith categorization assistant. Your job is to:

1. Ask the user for:
   - Period to process (YYYY-MM or "last-30-days")
   - Intelligence mode (conservative/smart/aggressive)
   - Whether to apply changes or dry-run

2. Execute the categorization workflow:
   ```python
   from scripts.operations.categorize_batch import main as categorize_batch

   # Run with user-provided parameters
   # This will use the new batch processing workflow
   ```

3. After processing, show the user:
   - How many transactions were processed
   - Rule matches vs LLM fallbacks
   - Validation results (if any)
   - Any new rules suggested
   - Ask if they want to create rules from high-confidence LLM patterns

4. If user wants to create rules, collect:
   - Which LLM patterns to convert to rules
   - Confirmation before adding to rules.yaml

5. Remind user to restart Claude Code after any rule changes.

**Example interaction:**

```
User: /smith:categorize
Assistant: I'll help categorize your transactions. What period would you like to process?
  - "2025-11" for November 2025
  - "last-30-days" for recent transactions

User: last-30-daysAssistant: What intelligence mode would you like to use?
  - conservative: Manual review for all (safer)
  - smart: Auto-apply 90%+ confidence (recommended)
  - aggressive: Auto-apply 80%+ confidence (faster)

User: smart
Assistant: Would you like to apply changes or run in dry-run mode first?
  - dry-run: Preview only
  - apply: Make actual changes

User: dry-run
Assistant: Running categorization with smart mode in dry-run...

[Executes workflow, shows progress]

✓ Categorized 45/50 transactions
  - Rule matches: 30
  - LLM fallbacks: 12
  - Validations: 8 (6 upgraded)
  - Skipped: 5 (low confidence)

Found 3 high-confidence LLM patterns that could become rules:
1. "NETFLIX" → Entertainment (confidence: 95%)
2. "UBER EATS" → Dining Out (confidence: 92%)
3. "CHEMIST WAREHOUSE" → Health & Medical (confidence: 91%)

Would you like to create rules for any of these patterns?
```
```

**Testing:**
- Manual test: `/smith:categorize` in Claude Code
- Verify interactive prompts work
- Verify dry-run shows preview
- Verify apply mode updates transactions

**Acceptance Criteria:**
- Slash command prompts for period, mode, dry-run
- Executes batch workflow
- Shows progress and results
- Offers rule creation from LLM patterns
- Reminds user to restart after rule changes

---

## Summary

This plan implements Real LLM Integration by:

1. **Replacing placeholders** with actual subagent delegation infrastructure
2. **Implementing Case 1** - Batch uncategorized transactions (no rule match)
3. **Implementing Case 2** - Batch medium-confidence validation (70-89% Smart, 50-79% Aggressive)
4. **Creating orchestration layer** for Claude Code's Task tool integration
5. **Updating batch script** to use new workflow
6. **Adding slash command** for interactive categorization

**Total Tasks:** 6 tasks
**Estimated Effort:** Medium (building on existing foundation from PR #7)
**Testing Strategy:** Unit tests for each component, integration tests for workflow, manual testing for slash command

**Key Technical Decisions:**

- **No external API calls** - Use Claude Code's Task tool for subagent delegation
- **Marker pattern** - Service methods return `_needs_llm` marker for orchestration layer
- **Batch sizing** - Mode-dependent (20/50/100) for optimal throughput
- **Two-phase approach** - Categorization first, then label application
- **Validation thresholds** - Mode-specific confidence ranges (70-89% Smart, 50-79% Aggressive)

**Dependencies:**

- ✅ PR #7 merged (LLM Categorization & Labeling Foundation)
- ✅ Unified Rules System working
- ✅ Test infrastructure in place
- ✅ All 445 tests passing

**Next Steps After Completion:**

1. Test with real PocketSmith data
2. Tune confidence thresholds based on accuracy
3. Implement actual Task tool integration (currently placeholder)
4. Add rule learning workflow
5. Create monitoring/analytics for LLM accuracy
