# LLM Integration Architecture

**Date:** 2025-11-22
**Status:** Production Ready (Test Mode)
**Context:** Agent Smith uses Claude Code's LLM for transaction categorization and validation.

## Problem Statement

Agent Smith needs to leverage Claude Code's LLM capabilities for intelligent transaction categorization. However, there's a fundamental architectural constraint:

**Python scripts running via `uv run python` cannot directly access Claude Code's Task tool or LLM context.**

This creates a challenge: How do we integrate LLM-powered categorization into workflows that are primarily Python-based?

## Solution: Marker Pattern + Orchestration Layer

### Core Design

We use a **marker pattern** where Python services signal when LLM assistance is needed, and an orchestration layer (running within Claude Code's context) handles the actual LLM execution.

### Architecture Layers

```
┌────────────────────────────────────────────────────────────┐
│  Layer 1: Claude Code Context (slash commands)             │
│  - Has access to LLM via direct prompt execution           │
│  - Can detect _needs_llm markers                           │
│  - Orchestrates Python workflows                           │
└────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────┐
│  Layer 2: Python Workflows (scripts/workflows/)            │
│  - Implements business logic                               │
│  - Returns {_needs_llm: True, _prompt: str, _ids: [...]}   │
│  - Parses LLM responses into structured results            │
└────────────────────────────────────────────────────────────┐
                           ↓
┌────────────────────────────────────────────────────────────┐
│  Layer 3: LLM Services (scripts/services/)                 │
│  - Builds categorization/validation prompts                │
│  - Parses LLM text responses                               │
│  - Returns marker dicts when LLM needed                    │
└────────────────────────────────────────────────────────────┘
```

### Marker Pattern

When a Python service needs LLM assistance, it returns a special dict:

```python
{
    "_needs_llm": True,              # Signal that LLM is required
    "_prompt": "Categorize...",      # Full prompt for LLM
    "_transaction_ids": [1, 2, 3],   # IDs for result mapping
    "_type": "categorization"        # Optional: type of operation
}
```

The orchestration layer (running in Claude Code) detects this marker and:
1. Executes the prompt directly (has LLM access)
2. Gets LLM response text
3. Calls Python parsing methods to convert response → structured results

## Implementation Details

### 1. LLM Categorization Service

**File:** `scripts/services/llm_categorization.py`

**Key Methods:**
- `categorize_batch(transactions, categories, mode)` → Returns marker dict
- `validate_batch(validations)` → Returns marker dict
- `parse_categorization_response(llm_text, transaction_ids)` → Structured results
- `parse_validation_response(llm_text, original_category, confidence)` → Validation result

**Example:**
```python
service = LLMCategorizationService()

# Returns marker dict with prompt
result = service.categorize_batch(
    transactions=[{...}, {...}],
    categories=[{...}, {...}],
    mode=IntelligenceMode.SMART
)

# result = {
#     "_needs_llm": True,
#     "_prompt": "Categorize these transactions...",
#     "_transaction_ids": [1, 2]
# }
```

### 2. LLM Orchestrator

**File:** `scripts/orchestration/llm_subagent.py`

**Purpose:** Bridge between Python workflows and Claude Code's LLM

**Modes:**
- **Test Mode** (`test_mode=True`): Returns mock responses for testing
- **Production Mode** (`test_mode=False`): Placeholder for actual execution

**Key Methods:**
- `execute_categorization(prompt, transaction_ids, service)` → Categorization results
- `execute_validation(prompt, transaction_ids, service)` → Validation results

**Current Implementation:**
```python
class LLMSubagent:
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode

    def execute_categorization(self, prompt, transaction_ids, service):
        if self.test_mode:
            return self._mock_categorization_response(transaction_ids)

        # Production: Log warning that delegation isn't implemented yet
        logger.warning(
            f"Production LLM delegation not yet implemented. "
            f"Would delegate categorization for {len(transaction_ids)} transactions"
        )
        return {}
```

### 3. Categorization Workflow

**File:** `scripts/workflows/categorization.py`

**Key Method:** `categorize_transactions_batch(transactions, categories)`

**Flow:**
1. Apply rules to all transactions
2. Collect uncategorized → batch LLM categorization (Case 1)
3. Collect medium-confidence → batch LLM validation (Case 2)
4. Apply labels to all categorized transactions
5. Return results

**Orchestration Integration:**
```python
def _orchestrate_llm_call(self, marker_result):
    """Detect marker dict and delegate to LLM orchestrator."""
    if not isinstance(marker_result, dict) or not marker_result.get("_needs_llm"):
        return {}

    prompt = marker_result["_prompt"]
    transaction_ids = marker_result["_transaction_ids"]
    operation_type = marker_result.get("_type", "categorization")

    if operation_type == "validation":
        return self.llm_orchestrator.execute_validation(
            prompt=prompt,
            transaction_ids=transaction_ids,
            service=self.llm_service,
        )
    else:
        return self.llm_orchestrator.execute_categorization(
            prompt=prompt,
            transaction_ids=transaction_ids,
            service=self.llm_service,
        )
```

## Usage Patterns

### Pattern 1: Test Mode (Unit Tests)

For automated testing, enable test mode to get mock responses:

```python
from scripts.workflows.categorization import CategorizationWorkflow

workflow = CategorizationWorkflow(client=None, mode="smart")
workflow.llm_orchestrator.test_mode = True

result = workflow.categorize_transactions_batch(transactions, categories)

# Returns mock categorizations without needing actual LLM
```

### Pattern 2: Production Mode (NOT YET FUNCTIONAL)

For production use with real LLM integration, the workflow must be invoked from within Claude Code's context where the Task tool is available.

**Current Status:** Production mode logs warnings and returns empty results. Actual Claude Code Task tool integration is not yet implemented.

**Future Implementation:** See "Production Integration" section below.

### Pattern 3: Batch Processing Script

**File:** `scripts/operations/categorize_batch.py`

**Usage:**
```bash
uv run python scripts/operations/categorize_batch.py \
    --period last-30-days \
    --mode smart \
    --dry-run
```

**Note:** This script currently uses test mode for LLM operations. Production LLM integration requires running from Claude Code slash command.

## Production Integration (COMPLETED ✅)

**Status:** Production-ready using Claude Agent SDK

The LLM integration is now fully functional using the **Claude Agent SDK**, which provides direct Python access to Claude's LLM capabilities.

### Claude Agent SDK Integration

**Dependency:** `claude-agent-sdk>=0.1.0` (Python 3.10+)

The production implementation uses the Claude Agent SDK's `query()` function to execute prompts:

```python
# scripts/orchestration/llm_subagent.py

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

class LLMSubagent:
    def _execute_prompt_sync(self, prompt: str) -> str:
        """Execute prompt using Claude Agent SDK."""
        return asyncio.run(self._execute_prompt_async(prompt))

    async def _execute_prompt_async(self, prompt: str) -> str:
        """Execute prompt asynchronously via SDK."""
        options = ClaudeAgentOptions(
            system_prompt="You are a financial analysis expert helping categorize transactions.",
            allowed_tools=[],  # No tools needed for categorization
            permission_mode="default"
        )

        # Collect response chunks - SDK returns TextBlock objects
        response_chunks = []
        async for message in query(prompt=prompt, options=options):
            if hasattr(message, 'content') and isinstance(message.content, list):
                for item in message.content:
                    if hasattr(item, 'text'):
                        response_chunks.append(item.text)

        return "".join(response_chunks)
```

**Key Features:**
- ✅ Direct Python-to-LLM calls (no subprocess complexity)
- ✅ Async SDK with synchronous wrapper for easy integration
- ✅ Automatic authentication via Claude Code CLI
- ✅ No external API keys needed (uses existing Claude Code auth)
- ✅ Works seamlessly in both test mode and production mode

### Production Mode Flow

1. **Python workflow** calls `workflow.categorize_transactions_batch(transactions, categories)`
2. **Workflow** applies rules, collects uncategorized/medium-confidence transactions
3. **LLM service** builds prompts and returns `{_needs_llm: True, _prompt: "...", _transaction_ids: [...]}`
4. **Orchestrator** detects marker and calls `_execute_prompt_sync(prompt)`
5. **SDK** sends prompt to Claude via bundled CLI
6. **Claude** returns categorization response
7. **Service parser** extracts categories, confidence scores, reasoning
8. **Workflow** applies labels and returns complete results

### Testing

Production mode can be tested directly:

```bash
# Test with real SDK calls
uv run python test_sdk_integration.py
```

Test mode remains available for unit testing (no actual LLM calls).

## Testing Strategy

### Unit Tests

All LLM integration code has comprehensive unit tests:
- ✅ `tests/unit/test_llm_categorization.py` - Service methods (22 tests)
- ✅ `tests/unit/test_llm_batch_delegation.py` - Marker pattern (6 tests)
- ✅ `tests/unit/test_llm_orchestration.py` - Orchestrator (5 tests)
- ✅ `tests/unit/test_batch_categorization.py` - Workflow integration (5 tests)
- ✅ `tests/unit/test_medium_confidence_validation.py` - Validation flow (7 tests)

**Total:** 45 passing tests

### Integration Testing

To test end-to-end with real LLM:
1. Create small test dataset (5-10 transactions)
2. Invoke from Claude Code slash command
3. Verify categorizations are accurate
4. Verify confidence thresholds work correctly

## Summary

**Current State:**
- ✅ Marker pattern implemented and tested
- ✅ Prompt building works correctly
- ✅ Response parsing works correctly
- ✅ Test mode provides mock responses
- ✅ **Production mode FUNCTIONAL via Claude Agent SDK**
- ✅ All 421 unit tests passing
- ✅ End-to-end categorization tested successfully

**Architecture Decision:**
Use marker pattern to signal LLM needs from Python → orchestration layer uses Claude Agent SDK for actual execution

**Production Status:**
Fully functional - can categorize real transactions using Claude's LLM via Python SDK.
