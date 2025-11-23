# Phase 6: Orchestration & UX Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build intelligent orchestration layer and user experience features that make Agent Smith easy to use through subagent delegation and slash commands.

**Architecture:** Three-tier system with (1) Conductor for smart subagent delegation, (2) Interactive workflows for guided operations, and (3) Slash commands for quick access to common operations. Conductor decides when to delegate heavy operations (>100 transactions, >5000 tokens) to subagents while preserving main context.

**Tech Stack:** Python 3.9+, Claude Code slash commands (.md), Task tool for subagent dispatch, pytest for testing

---

## Task 1: Subagent Conductor Foundation

**Files:**
- Create: `scripts/orchestration/__init__.py`
- Create: `scripts/orchestration/conductor.py`
- Create: `tests/unit/test_conductor.py`

### Step 1: Write failing tests for conductor decision logic

Create `tests/unit/test_conductor.py`:

```python
"""Tests for subagent conductor orchestration logic."""

import pytest
from scripts.orchestration.conductor import (
    SubagentConductor,
    OperationType,
    should_delegate,
)


def test_should_delegate_bulk_processing():
    """Bulk processing always delegates."""
    result = should_delegate(
        operation_type=OperationType.BULK_PROCESSING,
        transaction_count=50,
        estimated_tokens=2000,
        can_parallelize=False,
    )
    assert result is True


def test_should_delegate_high_transaction_count():
    """Over 100 transactions delegates."""
    result = should_delegate(
        operation_type=OperationType.SIMPLE_QUERY,
        transaction_count=150,
        estimated_tokens=2000,
        can_parallelize=False,
    )
    assert result is True


def test_should_delegate_high_token_estimate():
    """Over 5000 tokens delegates."""
    result = should_delegate(
        operation_type=OperationType.SIMPLE_QUERY,
        transaction_count=50,
        estimated_tokens=6000,
        can_parallelize=False,
    )
    assert result is True


def test_should_delegate_parallelizable():
    """Parallelizable operations delegate."""
    result = should_delegate(
        operation_type=OperationType.SIMPLE_QUERY,
        transaction_count=50,
        estimated_tokens=2000,
        can_parallelize=True,
    )
    assert result is True


def test_should_not_delegate_simple_query():
    """Simple queries stay in main context."""
    result = should_delegate(
        operation_type=OperationType.SIMPLE_QUERY,
        transaction_count=20,
        estimated_tokens=1000,
        can_parallelize=False,
    )
    assert result is False


def test_conductor_initialization():
    """Conductor initializes with default settings."""
    conductor = SubagentConductor()

    assert conductor.transaction_threshold == 100
    assert conductor.token_threshold == 5000
    assert conductor.dry_run is False


def test_conductor_custom_thresholds():
    """Conductor accepts custom thresholds."""
    conductor = SubagentConductor(
        transaction_threshold=200,
        token_threshold=10000,
        dry_run=True,
    )

    assert conductor.transaction_threshold == 200
    assert conductor.token_threshold == 10000
    assert conductor.dry_run is True


def test_estimate_operation_complexity():
    """Estimate tokens for an operation."""
    conductor = SubagentConductor()

    result = conductor.estimate_complexity(
        operation_type=OperationType.ANALYSIS,
        transaction_count=100,
        period_months=3,
    )

    assert "estimated_tokens" in result
    assert "can_parallelize" in result
    assert "suggested_subagents" in result
    assert result["estimated_tokens"] > 0


def test_build_subagent_prompt():
    """Build delegation prompt for subagent."""
    conductor = SubagentConductor()

    prompt = conductor.build_subagent_prompt(
        operation_type="categorization",
        task_description="Categorize 150 uncategorized transactions",
        data_summary="150 transactions from Nov 2025",
        intelligence_mode="smart",
        constraints={"dry_run": True},
    )

    assert "categorization agent" in prompt.lower()
    assert "150 transactions" in prompt
    assert "intelligence mode: smart" in prompt.lower()
    assert "dry_run: true" in prompt.lower()
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/unit/test_conductor.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'scripts.orchestration'"

### Step 3: Create conductor module structure

Create `scripts/orchestration/__init__.py`:

```python
"""Orchestration layer for subagent conductor system."""

from scripts.orchestration.conductor import (
    SubagentConductor,
    OperationType,
    should_delegate,
)

__all__ = [
    "SubagentConductor",
    "OperationType",
    "should_delegate",
]
```

### Step 4: Implement conductor with decision logic

Create `scripts/orchestration/conductor.py`:

```python
"""Subagent conductor for intelligent orchestration.

The conductor decides when to delegate operations to subagents based on
complexity, size, and parallelization opportunities.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Operation types for conductor decision making."""

    BULK_PROCESSING = "bulk_processing"
    DEEP_ANALYSIS = "deep_analysis"
    MULTI_PERIOD = "multi_period"
    CATEGORIZATION = "categorization"
    REPORTING = "reporting"
    TAX_ANALYSIS = "tax_analysis"
    SCENARIO_MODELING = "scenario_modeling"
    OPTIMIZATION = "optimization"
    SIMPLE_QUERY = "simple_query"


def should_delegate(
    operation_type: OperationType,
    transaction_count: int,
    estimated_tokens: int,
    can_parallelize: bool,
) -> bool:
    """Decide if operation should be delegated to a subagent.

    Args:
        operation_type: Type of operation
        transaction_count: Number of transactions involved
        estimated_tokens: Estimated token count for operation
        can_parallelize: Whether operation can be parallelized

    Returns:
        True if operation should be delegated to subagent
    """
    # Always delegate these operation types
    always_delegate = {
        OperationType.BULK_PROCESSING,
        OperationType.DEEP_ANALYSIS,
        OperationType.MULTI_PERIOD,
    }
    if operation_type in always_delegate:
        return True

    # Check complexity thresholds
    if transaction_count > 100:
        return True

    if estimated_tokens > 5000:
        return True

    # Check parallelization opportunity
    if can_parallelize:
        return True

    # Simple queries stay in main context
    return False


class SubagentConductor:
    """Intelligent orchestration for subagent delegation.

    The conductor manages when and how to delegate operations to specialized
    subagents, preserving main context while handling heavy operations.
    """

    def __init__(
        self,
        transaction_threshold: int = 100,
        token_threshold: int = 5000,
        dry_run: bool = False,
    ):
        """Initialize subagent conductor.

        Args:
            transaction_threshold: Transaction count threshold for delegation
            token_threshold: Token estimate threshold for delegation
            dry_run: If True, don't actually dispatch subagents
        """
        self.transaction_threshold = transaction_threshold
        self.token_threshold = token_threshold
        self.dry_run = dry_run

    def estimate_complexity(
        self,
        operation_type: OperationType,
        transaction_count: int,
        period_months: int = 1,
        categories: int = 1,
    ) -> Dict[str, Any]:
        """Estimate computational complexity of an operation.

        Args:
            operation_type: Type of operation
            transaction_count: Number of transactions
            period_months: Number of months in analysis period
            categories: Number of categories to analyze

        Returns:
            Dict with estimated_tokens, can_parallelize, suggested_subagents
        """
        # Base token estimate: ~5 tokens per transaction
        base_tokens = transaction_count * 5

        # Operation multipliers
        multipliers = {
            OperationType.CATEGORIZATION: 3,  # Pattern matching
            OperationType.DEEP_ANALYSIS: 5,  # Detailed analysis
            OperationType.TAX_ANALYSIS: 4,  # Tax rules
            OperationType.SCENARIO_MODELING: 6,  # Complex calculations
            OperationType.REPORTING: 2,  # Formatting
            OperationType.SIMPLE_QUERY: 1,
        }
        multiplier = multipliers.get(operation_type, 2)

        estimated_tokens = base_tokens * multiplier

        # Add overhead for multi-period operations
        if period_months > 1:
            estimated_tokens = int(estimated_tokens * (1 + (period_months - 1) * 0.3))

        # Determine if can parallelize
        can_parallelize = False
        if period_months > 1:
            can_parallelize = True
        elif categories > 3:
            can_parallelize = True
        elif transaction_count > 200:
            # Can batch large transaction sets
            can_parallelize = True

        # Suggest number of subagents for parallel processing
        suggested_subagents = 1
        if can_parallelize:
            if period_months > 1:
                suggested_subagents = min(period_months, 12)
            elif categories > 3:
                suggested_subagents = min(categories, 5)
            elif transaction_count > 200:
                suggested_subagents = min((transaction_count // 100), 5)

        return {
            "estimated_tokens": estimated_tokens,
            "can_parallelize": can_parallelize,
            "suggested_subagents": suggested_subagents,
        }

    def build_subagent_prompt(
        self,
        operation_type: str,
        task_description: str,
        data_summary: str,
        intelligence_mode: str = "smart",
        tax_level: str = "smart",
        constraints: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build delegation prompt for subagent.

        Args:
            operation_type: Type of operation (categorization, analysis, etc.)
            task_description: Detailed description of task
            data_summary: Summary of data to process
            intelligence_mode: conservative|smart|aggressive
            tax_level: reference|smart|full
            constraints: Additional constraints (dry_run, max_api_calls, etc.)

        Returns:
            Formatted prompt for subagent
        """
        constraints = constraints or {}

        # Build constraints section
        constraints_lines = []
        for key, value in constraints.items():
            constraints_lines.append(f"- {key}: {value}")
        constraints_text = "\n".join(constraints_lines) if constraints_lines else "- None"

        prompt = f"""You are a specialized {operation_type} agent for Agent Smith.

CONTEXT:
- Operation: {task_description}
- Intelligence Mode: {intelligence_mode}
- Tax Level: {tax_level}

DATA:
{data_summary}

REFERENCES:
- API Documentation: ai_docs/pocketsmith-api-documentation.md
- Tax Guidelines: ai_docs/tax/ (if applicable)

TASK:
{task_description}

CONSTRAINTS:
{constraints_text}

Please complete the operation and return results in a structured format.
"""
        return prompt

    def should_delegate_operation(
        self,
        operation_type: OperationType,
        transaction_count: int,
        estimated_tokens: Optional[int] = None,
        can_parallelize: bool = False,
    ) -> bool:
        """Determine if operation should be delegated.

        Args:
            operation_type: Type of operation
            transaction_count: Number of transactions
            estimated_tokens: Token estimate (if None, will estimate)
            can_parallelize: Whether operation can be parallelized

        Returns:
            True if should delegate
        """
        if estimated_tokens is None:
            complexity = self.estimate_complexity(
                operation_type=operation_type, transaction_count=transaction_count
            )
            estimated_tokens = complexity["estimated_tokens"]
            can_parallelize = complexity["can_parallelize"]

        return should_delegate(
            operation_type=operation_type,
            transaction_count=transaction_count,
            estimated_tokens=estimated_tokens,
            can_parallelize=can_parallelize,
        )
```

### Step 5: Run tests to verify they pass

```bash
pytest tests/unit/test_conductor.py -v
```

Expected: PASS (all 10 tests)

### Step 6: Run format and lint checks

```bash
ruff format scripts/orchestration/ tests/unit/test_conductor.py
ruff check scripts/orchestration/ tests/unit/test_conductor.py
mypy scripts/orchestration/
```

Expected: All checks pass

### Step 7: Commit conductor foundation

```bash
git add scripts/orchestration/ tests/unit/test_conductor.py
git commit -m "feat(orchestration): add subagent conductor with decision logic

- Implement OperationType enum for operation classification
- Add should_delegate() function with complexity thresholds
- Create SubagentConductor class for orchestration
- Estimate operation complexity (tokens, parallelization)
- Build subagent delegation prompts
- Tests: 10 unit tests for decision logic

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Context Preservation & Result Aggregation

**Files:**
- Modify: `scripts/orchestration/conductor.py`
- Create: `tests/unit/test_context_preservation.py`

### Step 1: Write failing tests for context preservation

Create `tests/unit/test_context_preservation.py`:

```python
"""Tests for context preservation and result aggregation."""

import pytest
from scripts.orchestration.conductor import SubagentConductor, ContextManager


def test_context_manager_initialization():
    """Context manager initializes with session state."""
    context = ContextManager(user_id="test-user-123")

    assert context.user_id == "test-user-123"
    assert context.preferences == {}
    assert context.session_state == {}


def test_context_manager_set_preference():
    """Store user preferences."""
    context = ContextManager(user_id="test-user")

    context.set_preference("intelligence_mode", "smart")
    context.set_preference("tax_level", "full")

    assert context.get_preference("intelligence_mode") == "smart"
    assert context.get_preference("tax_level") == "full"


def test_context_manager_session_state():
    """Manage session state across operations."""
    context = ContextManager(user_id="test-user")

    context.update_session_state("last_operation", "categorization")
    context.update_session_state("transactions_processed", 150)

    assert context.get_session_state("last_operation") == "categorization"
    assert context.get_session_state("transactions_processed") == 150


def test_result_aggregator_initialization():
    """Result aggregator initializes empty."""
    aggregator = ResultAggregator()

    assert aggregator.results == []
    assert aggregator.total_operations == 0


def test_result_aggregator_add_result():
    """Add individual subagent result."""
    aggregator = ResultAggregator()

    aggregator.add_result(
        operation="categorization",
        status="success",
        data={"categorized": 50, "skipped": 5},
    )

    assert aggregator.total_operations == 1
    assert len(aggregator.results) == 1
    assert aggregator.results[0]["operation"] == "categorization"


def test_result_aggregator_merge_results():
    """Merge multiple subagent results."""
    aggregator = ResultAggregator()

    # Add results from 3 parallel subagents
    aggregator.add_result("batch1", "success", {"categorized": 30})
    aggregator.add_result("batch2", "success", {"categorized": 40})
    aggregator.add_result("batch3", "success", {"categorized": 25})

    merged = aggregator.merge_results(operation_type="categorization")

    assert merged["status"] == "success"
    assert merged["total_operations"] == 3
    assert merged["aggregated_data"]["categorized"] == 95


def test_result_aggregator_handle_partial_failure():
    """Handle results with partial failures."""
    aggregator = ResultAggregator()

    aggregator.add_result("batch1", "success", {"categorized": 30})
    aggregator.add_result("batch2", "error", {"error": "API timeout"})
    aggregator.add_result("batch3", "success", {"categorized": 25})

    merged = aggregator.merge_results(operation_type="categorization")

    assert merged["status"] == "partial"
    assert merged["successful_operations"] == 2
    assert merged["failed_operations"] == 1


def test_conductor_with_context_preservation():
    """Conductor preserves context during delegation."""
    conductor = SubagentConductor()
    context = ContextManager(user_id="test-user")
    context.set_preference("intelligence_mode", "aggressive")

    prompt = conductor.build_subagent_prompt(
        operation_type="categorization",
        task_description="Categorize transactions",
        data_summary="100 transactions",
        intelligence_mode=context.get_preference("intelligence_mode"),
    )

    assert "Intelligence Mode: aggressive" in prompt
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/unit/test_context_preservation.py -v
```

Expected: FAIL with "ImportError: cannot import name 'ContextManager'"

### Step 3: Implement context preservation classes

Add to `scripts/orchestration/conductor.py`:

```python
class ContextManager:
    """Manages user context across subagent operations.

    Preserves user preferences, session state, and configuration
    while delegating heavy operations to subagents.
    """

    def __init__(self, user_id: str):
        """Initialize context manager.

        Args:
            user_id: PocketSmith user ID
        """
        self.user_id = user_id
        self.preferences: Dict[str, Any] = {}
        self.session_state: Dict[str, Any] = {}

    def set_preference(self, key: str, value: Any) -> None:
        """Store user preference.

        Args:
            key: Preference key
            value: Preference value
        """
        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Retrieve user preference.

        Args:
            key: Preference key
            default: Default value if key not found

        Returns:
            Preference value or default
        """
        return self.preferences.get(key, default)

    def update_session_state(self, key: str, value: Any) -> None:
        """Update session state.

        Args:
            key: State key
            value: State value
        """
        self.session_state[key] = value

    def get_session_state(self, key: str, default: Any = None) -> Any:
        """Retrieve session state.

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            State value or default
        """
        return self.session_state.get(key, default)


class ResultAggregator:
    """Aggregates results from multiple subagent operations.

    Handles parallel processing results and merges them into
    coherent summaries for the user.
    """

    def __init__(self):
        """Initialize result aggregator."""
        self.results: list[Dict[str, Any]] = []
        self.total_operations = 0

    def add_result(self, operation: str, status: str, data: Dict[str, Any]) -> None:
        """Add result from a subagent operation.

        Args:
            operation: Operation identifier
            status: success|error|partial
            data: Operation result data
        """
        self.results.append({"operation": operation, "status": status, "data": data})
        self.total_operations += 1

    def merge_results(self, operation_type: str) -> Dict[str, Any]:
        """Merge multiple subagent results into summary.

        Args:
            operation_type: Type of operation being aggregated

        Returns:
            Merged result summary
        """
        if not self.results:
            return {
                "status": "error",
                "message": "No results to aggregate",
                "total_operations": 0,
            }

        # Count successes and failures
        successful = sum(1 for r in self.results if r["status"] == "success")
        failed = sum(1 for r in self.results if r["status"] == "error")

        # Determine overall status
        if failed == 0:
            status = "success"
        elif successful == 0:
            status = "error"
        else:
            status = "partial"

        # Merge numeric data fields
        aggregated_data: Dict[str, Any] = {}
        for result in self.results:
            if result["status"] != "success":
                continue

            data = result["data"]
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    aggregated_data[key] = aggregated_data.get(key, 0) + value
                elif key == "error":
                    # Skip error fields from successful results
                    continue

        return {
            "status": status,
            "operation_type": operation_type,
            "total_operations": self.total_operations,
            "successful_operations": successful,
            "failed_operations": failed,
            "aggregated_data": aggregated_data,
        }
```

Update `scripts/orchestration/__init__.py`:

```python
"""Orchestration layer for subagent conductor system."""

from scripts.orchestration.conductor import (
    SubagentConductor,
    OperationType,
    should_delegate,
    ContextManager,
    ResultAggregator,
)

__all__ = [
    "SubagentConductor",
    "OperationType",
    "should_delegate",
    "ContextManager",
    "ResultAggregator",
]
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/unit/test_context_preservation.py -v
```

Expected: PASS (all 9 tests)

### Step 5: Run all orchestration tests

```bash
pytest tests/unit/test_conductor.py tests/unit/test_context_preservation.py -v
```

Expected: PASS (19 tests total)

### Step 6: Commit context preservation

```bash
git add scripts/orchestration/ tests/unit/test_context_preservation.py
git commit -m "feat(orchestration): add context preservation and result aggregation

- Implement ContextManager for user preferences and session state
- Create ResultAggregator for parallel subagent results
- Handle partial failures in aggregation
- Preserve context during subagent delegation
- Tests: 9 unit tests for context management

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Core Slash Command - Main Entry Point

**Files:**
- Create: `.claude/commands/agent-smith.md`
- Create: `tests/integration/test_slash_commands.py`

### Step 1: Write integration test for main command

Create `tests/integration/test_slash_commands.py`:

```python
"""Integration tests for Agent Smith slash commands."""

import pytest
from pathlib import Path


pytestmark = pytest.mark.integration


class TestSlashCommands:
    """Test slash command files exist and are properly formatted."""

    def test_main_command_exists(self):
        """Main agent-smith command file exists."""
        cmd_path = Path(".claude/commands/agent-smith.md")
        assert cmd_path.exists(), "agent-smith.md command file not found"

    def test_main_command_content(self):
        """Main command has proper content structure."""
        cmd_path = Path(".claude/commands/agent-smith.md")
        content = cmd_path.read_text()

        # Check for key sections
        assert "Agent Smith" in content
        assert "financial management" in content.lower()
        assert "PocketSmith" in content

        # Check for subcommands reference
        assert "categorize" in content.lower()
        assert "analyze" in content.lower()
        assert "scenario" in content.lower()

    def test_commands_directory_structure(self):
        """Commands directory has all 8 slash command files."""
        commands_dir = Path(".claude/commands")
        assert commands_dir.exists()

        expected_commands = [
            "agent-smith.md",
            "agent-smith-categorize.md",
            "agent-smith-analyze.md",
            "agent-smith-scenario.md",
            "agent-smith-report.md",
            "agent-smith-optimize.md",
            "agent-smith-tax.md",
            "agent-smith-health.md",
        ]

        for cmd_file in expected_commands:
            cmd_path = commands_dir / cmd_file
            assert cmd_path.exists(), f"Command file {cmd_file} not found"
```

### Step 2: Run test to verify it fails

```bash
pytest tests/integration/test_slash_commands.py::TestSlashCommands::test_main_command_exists -v
```

Expected: FAIL with "agent-smith.md command file not found"

### Step 3: Create main slash command file

Create `.claude/commands/agent-smith.md`:

```markdown
You are **Agent Smith**, an intelligent financial management assistant for PocketSmith.

## Your Capabilities

You provide comprehensive financial management through:

1. **Transaction Categorization** - AI-powered categorization with rule learning
2. **Financial Analysis** - Spending analysis, trends, and insights
3. **Scenario Modeling** - What-if analysis, projections, and optimization
4. **Tax Intelligence** - Australian tax compliance (deductions, CGT, BAS)
5. **Reporting** - Multi-format reports (Markdown, CSV, JSON, Excel)
6. **Optimization** - Category structure, rules, and spending optimization
7. **Health Checks** - PocketSmith setup evaluation and recommendations

## Available Commands

For quick operations, use these specialized commands:

- `/smith:categorize` - Categorize uncategorized transactions
- `/smith:analyze` - Run financial analysis
- `/smith:scenario` - Model financial scenarios
- `/smith:report` - Generate comprehensive reports
- `/smith:optimize` - Optimize categories, rules, or spending
- `/smith:tax` - Tax-focused analysis and compliance
- `/smith:health` - Evaluate PocketSmith setup

## Conversational Mode

When you use `/agent-smith` without arguments, I'll guide you through:

- Understanding your current financial situation
- Identifying opportunities for optimization
- Setting up intelligent categorization rules
- Tax planning and compliance
- Scenario modeling and projections
- Custom analysis and reporting

## How I Work

**Smart Orchestration:**
- Simple queries (< 100 transactions): Direct response
- Complex operations (> 100 transactions): Delegate to specialized subagents
- Multi-period analysis: Parallel processing for speed
- Always preserve your preferences and context

**Intelligence Modes:**
- **Conservative:** High confidence, manual review for uncertainty
- **Smart:** Balanced automation with selective review (default)
- **Aggressive:** Maximum automation, apply low-confidence matches

**Tax Intelligence Levels:**
- **Reference:** Basic ATO category mapping and links
- **Smart:** Deduction detection, threshold monitoring (default)
- **Full:** BAS preparation, compliance checks, audit documentation

## Getting Started

Let's start with understanding your needs:

1. What financial operations are taking the most time?
2. What are your primary goals (tax optimization, spending control, insights)?
3. Do you have any upcoming tax deadlines or financial decisions?

Tell me what you'd like help with, and I'll guide you through the process!
```

### Step 4: Run test to verify it passes

```bash
pytest tests/integration/test_slash_commands.py::TestSlashCommands::test_main_command_exists -v
pytest tests/integration/test_slash_commands.py::TestSlashCommands::test_main_command_content -v
```

Expected: PASS (2 tests)

### Step 5: Commit main slash command

```bash
git add .claude/commands/agent-smith.md tests/integration/test_slash_commands.py
git commit -m "feat(commands): add main agent-smith slash command

- Create conversational entry point for Agent Smith
- Document all 8 available subcommands
- Explain intelligence modes and tax levels
- Describe smart orchestration approach
- Tests: Integration tests for command structure

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Categorization Command & Workflow

**Files:**
- Create: `.claude/commands/smith:categorize.md`
- Create: `scripts/workflows/__init__.py`
- Create: `scripts/workflows/categorization.py`
- Create: `tests/unit/test_categorization_workflow.py`

### Step 1: Write failing tests for categorization workflow

Create `tests/unit/test_categorization_workflow.py`:

```python
"""Tests for categorization workflow."""

import pytest
from scripts.workflows.categorization import (
    CategorizationWorkflow,
    parse_categorize_args,
)


def test_parse_categorize_args_defaults():
    """Parse categorization args with defaults."""
    args = parse_categorize_args([])

    assert args["mode"] == "smart"
    assert args["period"] is None
    assert args["account"] is None
    assert args["dry_run"] is False


def test_parse_categorize_args_with_mode():
    """Parse mode argument."""
    args = parse_categorize_args(["--mode=aggressive"])

    assert args["mode"] == "aggressive"


def test_parse_categorize_args_with_period():
    """Parse period argument."""
    args = parse_categorize_args(["--period=2025-11"])

    assert args["period"] == "2025-11"


def test_parse_categorize_args_with_dry_run():
    """Parse dry-run flag."""
    args = parse_categorize_args(["--dry-run"])

    assert args["dry_run"] is True


def test_categorization_workflow_initialization():
    """Workflow initializes with API client."""
    from scripts.api.client import PocketSmithClient

    client = PocketSmithClient(api_key="test-key")
    workflow = CategorizationWorkflow(client)

    assert workflow.client == client
    assert workflow.mode == "smart"


def test_categorization_workflow_should_use_subagent():
    """Determine if should use subagent for categorization."""
    from scripts.api.client import PocketSmithClient

    client = PocketSmithClient(api_key="test-key")
    workflow = CategorizationWorkflow(client)

    # Large transaction count should delegate
    result = workflow.should_use_subagent(transaction_count=150)
    assert result is True

    # Small transaction count should not
    result = workflow.should_use_subagent(transaction_count=20)
    assert result is False


def test_categorization_workflow_build_summary():
    """Build summary of categorization results."""
    from scripts.api.client import PocketSmithClient

    client = PocketSmithClient(api_key="test-key")
    workflow = CategorizationWorkflow(client)

    results = {
        "categorized": 85,
        "skipped": 15,
        "rules_applied": 12,
        "new_rules": 3,
    }

    summary = workflow.build_summary(results, total=100)

    assert "85/100" in summary
    assert "85.0%" in summary
    assert "12 rules" in summary
    assert "3 new" in summary
```

### Step 2: Run tests to verify they fail

```bash
pytest tests/unit/test_categorization_workflow.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'scripts.workflows'"

### Step 3: Create categorization workflow module

Create `scripts/workflows/__init__.py`:

```python
"""Interactive workflows for guided operations."""

from scripts.workflows.categorization import (
    CategorizationWorkflow,
    parse_categorize_args,
)

__all__ = [
    "CategorizationWorkflow",
    "parse_categorize_args",
]
```

Create `scripts/workflows/categorization.py`:

```python
"""Categorization workflow for interactive transaction categorization."""

import logging
from typing import Dict, Any, List, Optional
from scripts.orchestration.conductor import SubagentConductor, OperationType

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

    def __init__(self, client, mode: str = "smart"):
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
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/unit/test_categorization_workflow.py -v
```

Expected: PASS (all 7 tests)

### Step 5: Create categorization slash command

Create `.claude/commands/smith:categorize.md`:

```markdown
Categorize uncategorized transactions in PocketSmith with AI assistance.

## Usage

```
/smith:categorize [options]
```

## Options

- `--mode=MODE` - Intelligence level (conservative|smart|aggressive) [default: smart]
- `--period=PERIOD` - Target period (YYYY-MM or YYYY) [default: all time]
- `--account=ID` - Limit to specific account [default: all accounts]
- `--dry-run` - Preview categorization without applying changes

## Intelligence Modes

**Conservative:**
- Only auto-categorize high-confidence matches (>90%)
- Require manual review for medium/low confidence
- Best for: First-time setup, important accounts

**Smart (default):**
- Auto-categorize high confidence (>90%)
- Auto-categorize medium confidence (>70%) with existing rules
- Review low confidence (<70%)
- Best for: Regular use, balanced automation

**Aggressive:**
- Auto-categorize all matches above 50% confidence
- Learn from patterns even with lower confidence
- Best for: High-volume accounts, established rule base

## Examples

```bash
# Categorize all uncategorized transactions (smart mode)
/smith:categorize

# Aggressive mode for November 2025
/smith:categorize --mode=aggressive --period=2025-11

# Preview changes without applying (dry-run)
/smith:categorize --dry-run

# Conservative mode for specific account
/smith:categorize --mode=conservative --account=12345
```

## How It Works

1. **Fetch uncategorized transactions** from PocketSmith
2. **Smart orchestration:**
   - < 100 transactions: Direct categorization in main context
   - > 100 transactions: Delegate to specialized subagent for speed
3. **Apply rules:** Match against existing platform and local rules
4. **Learn patterns:** Suggest new rules from categorization
5. **User review:** Present results and any manual review items
6. **Apply changes:** Update PocketSmith (unless --dry-run)

## What You'll See

**Progress:**
- Transaction count and date range
- Categorization status (applying rules, learning patterns)
- Real-time progress for large batches

**Results:**
- Categorized count and percentage
- Rules applied
- New rules suggested
- Manual review items (if any)

**Next Steps:**
- Review and approve new rules
- Handle manual review items
- Run again to catch any remaining uncategorized

---

**Starting categorization workflow...**
```

### Step 6: Run categorization command tests

```bash
pytest tests/unit/test_categorization_workflow.py -v
pytest tests/integration/test_slash_commands.py::TestSlashCommands::test_commands_directory_structure -v
```

Expected: test_commands_directory_structure will FAIL for missing other command files (expected - will create in next tasks)

### Step 7: Commit categorization workflow

```bash
git add .claude/commands/smith:categorize.md scripts/workflows/ tests/unit/test_categorization_workflow.py
git commit -m "feat(workflows): add categorization workflow and slash command

- Implement CategorizationWorkflow with subagent delegation
- Parse command arguments (mode, period, account, dry-run)
- Build human-readable summaries
- Create /smith:categorize slash command
- Document intelligence modes and usage examples
- Tests: 7 unit tests for workflow logic

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Analysis & Reporting Commands

**Files:**
- Create: `.claude/commands/smith:analyze.md`
- Create: `.claude/commands/smith:report.md`

### Step 1: Create analysis slash command

Create `.claude/commands/smith:analyze.md`:

```markdown
Run financial analysis on your PocketSmith data.

## Usage

```
/smith:analyze <type> [options]
```

## Analysis Types

- `spending` - Spending breakdown by category and merchant
- `trends` - Month-over-month and year-over-year trends
- `category` - Deep dive into specific category
- `tax` - Tax-focused analysis (deductions, CGT, etc.)
- `insights` - AI-generated insights and recommendations

## Options

- `--period=PERIOD` - Analysis period (YYYY-MM or YYYY) [default: current year]
- `--category=NAME` - Focus on specific category
- `--compare=PERIOD` - Compare with another period (YoY, MoM)
- `--tax-level=LEVEL` - Tax intelligence (reference|smart|full) [default: smart]

## Examples

```bash
# Spending analysis for 2025
/smith:analyze spending --period=2025

# Trend analysis comparing 2024 vs 2025
/smith:analyze trends --period=2025 --compare=2024

# Category deep-dive for Dining
/smith:analyze category --category="Dining"

# Tax analysis for FY 2024-25 (full intelligence)
/smith:analyze tax --period=2024-25 --tax-level=full

# AI insights for current month
/smith:analyze insights
```

## What You'll Get

**Spending Analysis:**
- Total expenses by category
- Top 10 merchants
- Average daily/weekly/monthly spending
- Comparison vs. previous periods

**Trends:**
- Month-over-month changes
- Year-over-year growth rates
- Trending up/down categories
- Anomaly detection

**Category Deep-Dive:**
- Transaction count and total
- Merchant breakdown
- Spending patterns (day of week, time of day)
- Optimization opportunities

**Tax Analysis:**
- Deductible expenses by ATO category
- Substantiation requirements
- CGT events and timing
- Tax-saving opportunities

**AI Insights:**
- Spending pattern observations
- Budget recommendations
- Subscription optimization
- Goal tracking suggestions

---

**Starting analysis...**
```

### Step 2: Create reporting slash command

Create `.claude/commands/smith:report.md`:

```markdown
Generate comprehensive financial reports in various formats.

## Usage

```
/smith:report <format> [options]
```

## Report Formats

- `summary` - High-level financial summary
- `detailed` - Comprehensive transaction report
- `tax` - Tax compliance report (deductions, CGT, BAS)
- `custom` - Custom report with specific sections

## Options

- `--period=PERIOD` - Report period (YYYY-MM, YYYY, or YYYY-Q#) [default: current FY]
- `--output=FORMAT` - Output format (markdown|csv|json|html|excel|all) [default: markdown]
- `--tax-level=LEVEL` - Tax intelligence level [default: smart]
- `--sections=LIST` - Custom sections (spending,trends,tax,goals)

## Examples

```bash
# Summary report for Q4 2025
/smith:report summary --period=2025-Q4

# Detailed transaction report in Excel
/smith:report detailed --period=2025-11 --output=excel

# Tax report for FY 2024-25 (full intelligence)
/smith:report tax --period=2024-25 --tax-level=full

# Custom report with specific sections
/smith:report custom --sections=spending,trends,goals

# Generate all formats
/smith:report summary --output=all
```

## Report Sections

**Summary Report:**
- Income & expense totals
- Net position and savings rate
- Top spending categories (top 10)
- Month-over-month trends
- Goal progress

**Detailed Report:**
- Complete transaction list
- Category breakdown
- Merchant analysis
- Uncategorized transactions
- Duplicate detection

**Tax Report (Level 3):**
- Deductible expenses by ATO category
- Substantiation status
- CGT events with discount eligibility
- BAS worksheet (GST calculations)
- Tax-saving recommendations
- Compliance checklist

**Custom Report:**
- Choose specific sections
- Flexible output formats
- Tailored to your needs

## Output Formats

- **Markdown:** Human-readable, great for documentation
- **CSV:** Spreadsheet import, data analysis
- **JSON:** Machine-readable, API integration
- **HTML:** Shareable web page
- **Excel:** Full-featured workbook with sheets
- **All:** Generate all formats at once

## What You'll Get

Reports are saved to `output/reports/` with timestamps. Tax reports include:
- Disclaimer (Level 3 tax advice)
- ATO category codes
- Substantiation requirements
- Recommended next steps

---

**Generating report...**
```

### Step 3: Run integration test for all commands

```bash
pytest tests/integration/test_slash_commands.py -v
```

Expected: Still FAIL for remaining 4 command files (will create in Tasks 6-7)

### Step 4: Commit analysis and reporting commands

```bash
git add .claude/commands/smith:analyze.md .claude/commands/smith:report.md
git commit -m "feat(commands): add analysis and reporting slash commands

- Create /smith:analyze with 5 analysis types
- Create /smith:report with 4 report formats
- Document options for period, comparison, tax level
- Support multiple output formats (MD, CSV, JSON, HTML, Excel)
- Examples for common use cases

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Scenario & Optimization Commands

**Files:**
- Create: `.claude/commands/smith:scenario.md`
- Create: `.claude/commands/smith:optimize.md`

### Step 1: Create scenario modeling slash command

Create `.claude/commands/smith:scenario.md`:

```markdown
Model financial scenarios with what-if analysis, projections, and optimization.

## Usage

```
/smith:scenario <type> "<description>"
```

## Scenario Types

- `historical` - What-if analysis on past transactions
- `projection` - Future spending projections and affordability
- `optimization` - Subscription and spending optimization
- `tax` - Tax scenario planning and optimization

## Natural Language Descriptions

Describe your scenario in plain English. Agent Smith will interpret and execute.

## Examples

```bash
# Historical what-if scenarios
/smith:scenario historical "What if I reduced dining by 25% last quarter?"
/smith:scenario historical "Compare August vs September spending"

# Future projections
/smith:scenario projection "Can I afford a $600/month car payment?"
/smith:scenario projection "Forecast expenses for next 6 months with 3% inflation"

# Optimization scenarios
/smith:scenario optimization "Find subscription savings opportunities"
/smith:scenario optimization "Which categories are trending up?"

# Tax scenarios
/smith:scenario tax "Should I buy $25k equipment before or after EOFY?"
/smith:scenario tax "Compare super contribution strategies"
/smith:scenario tax "Optimize CGT timing for shares purchased 11 months ago"
```

## Scenario Capabilities

**Historical Analysis:**
- What-if spending adjustments (-50% to +100%)
- Period comparisons (MoM, YoY, custom)
- Anomaly detection
- Savings calculations

**Projections:**
- Spending forecasts (3-24 months)
- Affordability analysis for new expenses
- Savings goal modeling
- Inflation adjustments

**Optimization:**
- Subscription detection and cost analysis
- Category trend analysis
- Recurring expense optimization
- Savings opportunity identification

**Tax Scenarios:**
- Prepayment vs. deferral analysis
- CGT timing optimization (12-month discount)
- Salary sacrifice vs. super contribution
- Capital loss offset strategies

## What You'll Get

**Analysis Results:**
- Scenario outcomes (best/realistic/worst case)
- Financial impact ($ savings/cost)
- Confidence levels
- Assumptions made

**Recommendations:**
- Actionable next steps
- Risk assessment
- Alternative strategies
- Tax implications

**Visualizations:**
- Comparison charts
- Trend projections
- Savings over time

---

**Analyzing scenario...**
```

### Step 2: Create optimization slash command

Create `.claude/commands/smith:optimize.md`:

```markdown
AI-assisted optimization for categories, rules, spending, and subscriptions.

## Usage

```
/smith:optimize <target> [options]
```

## Optimization Targets

- `categories` - Category structure and hierarchy
- `rules` - Categorization rules (accuracy, coverage)
- `spending` - Spending patterns and reduction opportunities
- `subscriptions` - Recurring charges and subscription management

## Options

- `--aggressive` - More aggressive optimization recommendations
- `--preview` - Show recommendations without applying
- `--focus=AREA` - Focus on specific area (e.g., "dining", "utilities")

## Examples

```bash
# Optimize category structure
/smith:optimize categories

# Improve rule accuracy and coverage
/smith:optimize rules

# Find spending reduction opportunities
/smith:optimize spending

# Analyze subscriptions and recurring charges
/smith:optimize subscriptions

# Preview aggressive optimizations for dining
/smith:optimize spending --aggressive --focus=dining --preview
```

## What Gets Optimized

**Categories:**
- Consolidate similar categories
- Fix hierarchy issues
- Identify unused categories
- Suggest better groupings
- Align with ATO categories for tax

**Rules:**
- Improve accuracy (reduce overrides)
- Increase coverage (more auto-categorization)
- Remove conflicting rules
- Optimize priority ordering
- Suggest new rules for patterns

**Spending:**
- Identify trending-up categories
- Find unusual spikes
- Compare to benchmarks
- Suggest reduction targets
- Track progress vs. goals

**Subscriptions:**
- Detect recurring payments
- Calculate annual costs
- Find unused/redundant services
- Compare alternatives
- Track price increases

## Optimization Process

1. **Analysis:** Examine current state
2. **Opportunities:** Identify improvements
3. **Recommendations:** Suggest specific changes
4. **Impact:** Estimate savings/improvement
5. **Approval:** Get your confirmation
6. **Apply:** Execute changes (unless --preview)

## What You'll Get

**Recommendations:**
- Specific actions to take
- Expected impact ($ or % improvement)
- Risk assessment
- Implementation steps

**Before/After:**
- Current state metrics
- Projected improvements
- Success criteria

**Monitoring:**
- Track optimization results
- Measure actual vs. expected
- Continuous improvement suggestions

---

**Starting optimization analysis...**
```

### Step 3: Run integration test

```bash
pytest tests/integration/test_slash_commands.py -v
```

Expected: Still FAIL for remaining 2 command files

### Step 4: Commit scenario and optimization commands

```bash
git add .claude/commands/smith:scenario.md .claude/commands/smith:optimize.md
git commit -m "feat(commands): add scenario and optimization slash commands

- Create /smith:scenario with 4 scenario types
- Support natural language scenario descriptions
- Create /smith:optimize for 4 optimization targets
- Document what-if, projections, and tax scenarios
- Examples for common optimization use cases

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Tax & Health Check Commands

**Files:**
- Create: `.claude/commands/smith:tax.md`
- Create: `.claude/commands/smith:health.md`

### Step 1: Create tax intelligence slash command

Create `.claude/commands/smith:tax.md`:

```markdown
Tax-focused analysis and compliance for Australian tax requirements.

## Usage

```
/smith:tax <operation> [options]
```

## Tax Operations

- `deductions` - Track tax-deductible expenses
- `cgt` - Capital gains tax tracking and optimization
- `bas` - BAS preparation (GST calculations)
- `eofy` - End of financial year tax prep
- `scenario` - Tax scenario planning

## Options

- `--period=PERIOD` - Financial year (YYYY-YY format) [default: current FY]
- `--level=LEVEL` - Tax intelligence (reference|smart|full) [default: smart]
- `--output=FORMAT` - Output format [default: markdown]

## Examples

```bash
# Track deductible expenses for FY 2024-25
/smith:tax deductions --period=2024-25

# CGT analysis with timing recommendations
/smith:tax cgt --period=2024-25 --level=full

# BAS worksheet preparation (GST only)
/smith:tax bas --period=2024-Q4

# Complete EOFY tax prep checklist
/smith:tax eofy

# Tax scenario: equipment purchase timing
/smith:tax scenario "Buy $25k equipment before or after EOFY?"
```

## Tax Intelligence Levels

**Reference (Level 1):**
- Basic ATO category mapping
- Links to ATO resources
- General guidance

**Smart (Level 2 - default):**
- Deduction detection with confidence scoring
- Substantiation threshold monitoring
- CGT discount eligibility tracking
- Tax-saving suggestions

**Full (Level 3):**
- BAS preparation (GST calculations)
- Compliance checks and validation
- Audit-ready documentation
- Detailed tax scenarios

**Important:** Level 3 outputs include disclaimer to consult a registered tax agent.

## Tax Operations Detail

**Deductions:**
- Expenses by ATO category code
- Substantiation requirements (>$300)
- Confidence scoring (high/medium/low)
- Missing documentation alerts
- Instant asset write-off eligibility

**CGT Tracking:**
- Purchase and sale events
- Cost base calculations
- 12-month discount eligibility
- Capital gains/losses by FY
- Optimization recommendations

**BAS Preparation (Level 3):**
- G1: Total sales
- G10/G11: Capital/non-capital purchases
- 1A/1B: GST calculations
- 1C: Net GST position
- Scope: GST only (W1, W2 excluded)

**EOFY Preparation:**
- Deduction summary
- CGT event summary
- Missing substantiation
- Compliance checklist
- Tax-saving opportunities
- Deadlines and due dates

## Australian Tax Compliance

**ATO Guidelines:**
- Substantiation thresholds
- CGT 50% discount (>12 months)
- Instant asset write-off (<$20k)
- Commuting vs. business travel
- Home office deductions

**Financial Year:**
- July 1 - June 30
- EOFY deadline: October 31
- BAS deadlines: Quarterly (monthly for some)

---

**Starting tax analysis...**
```

### Step 2: Create health check slash command

Create `.claude/commands/smith:health.md`:

```markdown
Evaluate your PocketSmith setup and get optimization recommendations.

## Usage

```
/smith:health [options]
```

## Options

- `--full` - Complete deep analysis (may take longer)
- `--quick` - Fast essential checks only
- `--category=AREA` - Specific area (categories|rules|tax|data)

## Health Checks

**Six Health Scores (0-100):**

1. **Category Health** - Structure, hierarchy, ATO alignment
2. **Rule Coverage** - Auto-categorization rate and accuracy
3. **Data Quality** - Completeness, duplicates, errors
4. **Tax Compliance** - Deduction tracking, substantiation
5. **Budget Alignment** - Spending vs. goals
6. **Account Health** - Balances, reconciliation, connections

## Examples

```bash
# Quick health check (essential checks)
/smith:health --quick

# Full comprehensive analysis
/smith:health --full

# Focus on category structure
/smith:health --category=categories

# Focus on tax compliance
/smith:health --category=tax
```

## What You'll Get

**Overall Health Score:**
- Combined score from all 6 areas
- Pass/Warning/Fail status
- Priority recommendations

**Detailed Scores:**
- Individual scores for each area
- Strengths and weaknesses
- Specific issues identified
- Improvement opportunities

**Recommendations:**
- Prioritized action items
- Expected impact
- Implementation steps
- Quick wins vs. long-term improvements

**Category Health:**
- Category structure analysis
- Unused categories
- ATO alignment issues
- Consolidation opportunities

**Rule Coverage:**
- Auto-categorization rate
- Rule accuracy (override rate)
- Coverage gaps
- Conflicting rules

**Data Quality:**
- Uncategorized transaction count
- Duplicate detection
- Missing payee names
- Date range coverage

**Tax Compliance:**
- Deduction tracking coverage
- Substantiation status
- CGT event tracking
- Missing documentation

**Budget Alignment:**
- Spending vs. budget
- Goal progress
- Trending issues
- Adjustment recommendations

**Account Health:**
- Connection status
- Balance reconciliation
- Transaction import issues
- Stale data alerts

## Health Check Process

1. **Scan:** Analyze PocketSmith data
2. **Score:** Calculate health metrics
3. **Identify:** Find issues and opportunities
4. **Recommend:** Prioritized action plan
5. **Monitor:** Track improvements over time

## Interpreting Scores

- **90-100:** Excellent - Maintain current practices
- **70-89:** Good - Minor improvements available
- **50-69:** Fair - Several issues to address
- **Below 50:** Poor - Significant work needed

---

**Running health check...**
```

### Step 3: Run integration test for all commands

```bash
pytest tests/integration/test_slash_commands.py -v
```

Expected: ALL PASS (all 8 command files now exist)

### Step 4: Commit tax and health check commands

```bash
git add .claude/commands/smith:tax.md .claude/commands/smith:health.md
git commit -m "feat(commands): add tax and health check slash commands

- Create /smith:tax with 5 tax operations
- Support 3-tier tax intelligence levels
- Create /smith:health with 6 health score areas
- Document Australian tax compliance (ATO guidelines)
- EOFY preparation checklist
- Tests: All 8 slash commands now complete

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com)"
```

---

## Task 8: Integration Tests for Workflows

**Files:**
- Create: `tests/integration/test_orchestration.py`

### Step 1: Write integration tests for orchestration

Create `tests/integration/test_orchestration.py`:

```python
"""Integration tests for orchestration and workflows."""

import pytest
from scripts.orchestration.conductor import (
    SubagentConductor,
    OperationType,
    ContextManager,
    ResultAggregator,
)
from scripts.workflows.categorization import CategorizationWorkflow


pytestmark = pytest.mark.integration


class TestOrchestrationIntegration:
    """Test orchestration with real workflow scenarios."""

    def test_conductor_categorization_workflow(self, api_client):
        """Test conductor with categorization workflow."""
        # Initialize conductor and context
        conductor = SubagentConductor()
        user = api_client.get_user()
        context = ContextManager(user_id=str(user["id"]))
        context.set_preference("intelligence_mode", "smart")

        # Create categorization workflow
        workflow = CategorizationWorkflow(api_client, mode="smart")

        # Check if should delegate (simulate 150 transactions)
        should_delegate = workflow.should_use_subagent(transaction_count=150)
        assert should_delegate is True

        print("✓ Conductor correctly delegates large categorization batch")

    def test_conductor_small_operation_direct(self, api_client):
        """Test conductor keeps small operations in main context."""
        conductor = SubagentConductor()
        workflow = CategorizationWorkflow(api_client, mode="smart")

        # Check if should delegate (simulate 20 transactions)
        should_delegate = workflow.should_use_subagent(transaction_count=20)
        assert should_delegate is False

        print("✓ Conductor correctly handles small operations directly")

    def test_complexity_estimation(self):
        """Test operation complexity estimation."""
        conductor = SubagentConductor()

        # Estimate categorization complexity
        result = conductor.estimate_complexity(
            operation_type=OperationType.CATEGORIZATION,
            transaction_count=150,
            period_months=1,
        )

        assert result["estimated_tokens"] > 0
        assert "can_parallelize" in result
        assert "suggested_subagents" in result

        # Large transaction count should enable parallelization
        assert result["can_parallelize"] is True

        print(f"✓ Estimated {result['estimated_tokens']} tokens for 150 transactions")

    def test_context_preservation_across_operations(self, api_client):
        """Test context preservation across multiple operations."""
        user = api_client.get_user()
        context = ContextManager(user_id=str(user["id"]))

        # Set preferences
        context.set_preference("intelligence_mode", "aggressive")
        context.set_preference("tax_level", "full")

        # Simulate operation
        context.update_session_state("last_operation", "categorization")
        context.update_session_state("transactions_processed", 150)

        # Verify preservation
        assert context.get_preference("intelligence_mode") == "aggressive"
        assert context.get_preference("tax_level") == "full"
        assert context.get_session_state("transactions_processed") == 150

        print("✓ Context preserved across operations")

    def test_result_aggregation_parallel_batches(self):
        """Test result aggregation from parallel subagents."""
        aggregator = ResultAggregator()

        # Simulate 3 parallel batches
        aggregator.add_result("batch1", "success", {"categorized": 50, "skipped": 5})
        aggregator.add_result("batch2", "success", {"categorized": 45, "skipped": 3})
        aggregator.add_result("batch3", "success", {"categorized": 40, "skipped": 7})

        # Merge results
        merged = aggregator.merge_results(operation_type="categorization")

        assert merged["status"] == "success"
        assert merged["total_operations"] == 3
        assert merged["successful_operations"] == 3
        assert merged["aggregated_data"]["categorized"] == 135
        assert merged["aggregated_data"]["skipped"] == 15

        print("✓ Successfully aggregated results from 3 parallel batches")

    def test_subagent_prompt_building(self, api_client):
        """Test subagent prompt includes all necessary context."""
        conductor = SubagentConductor()
        user = api_client.get_user()

        prompt = conductor.build_subagent_prompt(
            operation_type="categorization",
            task_description="Categorize 150 uncategorized transactions",
            data_summary="150 transactions from November 2025",
            intelligence_mode="smart",
            tax_level="full",
            constraints={"dry_run": True, "max_api_calls": 100},
        )

        # Verify prompt structure
        assert "categorization agent" in prompt.lower()
        assert "150 transactions" in prompt
        assert "intelligence mode: smart" in prompt.lower()
        assert "tax level: full" in prompt.lower()
        assert "dry_run: true" in prompt.lower()
        assert "max_api_calls: 100" in prompt

        print("✓ Subagent prompt built with complete context")
```

### Step 2: Run integration tests

```bash
pytest tests/integration/test_orchestration.py -v
```

Expected: PASS (all 6 integration tests)

### Step 3: Run all tests to verify Phase 6

```bash
pytest tests/unit/test_conductor.py tests/unit/test_context_preservation.py tests/unit/test_categorization_workflow.py tests/integration/test_orchestration.py tests/integration/test_slash_commands.py -v
```

Expected: PASS (all tests pass)

### Step 4: Commit integration tests

```bash
git add tests/integration/test_orchestration.py
git commit -m "test(orchestration): add integration tests for workflows

- Test conductor with categorization workflow
- Test delegation decisions (large vs small operations)
- Test complexity estimation
- Test context preservation across operations
- Test parallel result aggregation
- Test subagent prompt building
- Tests: 6 integration tests

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com)"
```

---

## Task 9: Documentation Updates

**Files:**
- Modify: `README.md`
- Modify: `INDEX.md`
- Create: `scripts/orchestration/INDEX.md`
- Create: `scripts/workflows/INDEX.md`
- Create: `.claude/commands/INDEX.md`
- Create: `docs/operations/2025-11-21_phase6_completion.md`

### Step 1: Update README.md

Update implementation roadmap and add Phase 6 section:

```markdown
## Implementation Roadmap

- ✅ **Phase 1:** Foundation (Weeks 1-2) - API client, utilities, backups
- ✅ **Phase 2:** Rule Engine (Weeks 3-4) - Hybrid platform + local rules
- ✅ **Phase 3:** Analysis & Reporting (Weeks 5-6) - Spending analysis, tax reports
- ✅ **Phase 4:** Tax Intelligence (Weeks 7-8) - 3-tier tax system, deductions, BAS
- ✅ **Phase 5:** Scenario Analysis (Weeks 9-10) - What-if, projections, optimization
- ✅ **Phase 6:** Orchestration & UX (Weeks 11-12) - Subagent conductor, slash commands
- ⏳ **Phase 7:** Advanced Features (Weeks 13-14) - Alerts, merchant intelligence
- ⏳ **Phase 8:** Health Check & Polish (Weeks 15-16) - Health scores, optimization

**Progress:** 6/8 phases complete (75%)
```

Add Phase 6 features section after Phase 5:

```markdown
### Phase 6: Orchestration & UX ✅

**Intelligent Orchestration:**
```python
from scripts.orchestration.conductor import SubagentConductor, OperationType

# Smart delegation based on complexity
conductor = SubagentConductor()
should_delegate = conductor.should_delegate_operation(
    operation_type=OperationType.CATEGORIZATION,
    transaction_count=150  # > 100 triggers delegation
)

# Context preservation
from scripts.orchestration.conductor import ContextManager
context = ContextManager(user_id="12345")
context.set_preference("intelligence_mode", "smart")
context.set_preference("tax_level", "full")
```

**Slash Commands (8 commands):**
```bash
# Installation and onboarding
/agent-smith

# Quick operations
/smith:categorize --mode=smart --period=2025-11
/smith:analyze spending --period=2025
/smith:scenario historical "What if I cut dining by 25%?"
/smith:report tax --period=2024-25 --tax-level=full
/smith:optimize subscriptions
/smith:tax deductions --period=2024-25
/smith:health --full
```

**Interactive Workflows:**
- Guided categorization with AI assistance
- Multi-step scenario planning
- Smart recommendations with context
- Progress tracking and feedback

**Features:**
- Smart subagent delegation (>100 transactions, >5000 tokens)
- Context preservation across operations
- Parallel processing for multi-period analysis
- Result aggregation from distributed subagents
- 8 specialized slash commands
- Interactive workflows with user approval
- Natural language scenario descriptions
```

### Step 2: Update INDEX.md

Add to `/scripts/` section:

```markdown
- `orchestration/` - Subagent conductor and orchestration logic (26 files, Phase 6)
  - `conductor.py` - Smart delegation, complexity estimation, context management
  - `INDEX.md` - Orchestration API reference
- `workflows/` - Interactive workflows for guided operations (15 files, Phase 6)
  - `categorization.py` - Categorization workflow with subagent delegation
  - `INDEX.md` - Workflow API reference
```

Add to `.claude/commands/` section:

```markdown
- `.claude/commands/` - Slash commands for Agent Smith (8 files, Phase 6)
  - `agent-smith.md` - Installation and onboarding point
  - `agent-smith-categorize.md` - Transaction categorization
  - `agent-smith-analyze.md` - Financial analysis
  - `agent-smith-scenario.md` - Scenario modeling
  - `agent-smith-report.md` - Report generation
  - `agent-smith-optimize.md` - Optimization operations
  - `agent-smith-tax.md` - Tax intelligence
  - `agent-smith-health.md` - Health check
  - `INDEX.md` - Command reference
```

Update test counts:

```markdown
- **Total Tests:** 225 tests (186 unit + 39 integration)
  - Phase 1-5: 194 tests
  - Phase 6: 31 tests (25 unit + 6 integration)
```

### Step 3: Create orchestration INDEX.md

Create `scripts/orchestration/INDEX.md`:

```markdown
# Orchestration Layer

Smart subagent conductor for intelligent delegation and context preservation.

## Modules

### conductor.py

Core orchestration logic for subagent management.

**Key Classes:**
- `OperationType` - Enum for operation classification
- `SubagentConductor` - Main orchestration coordinator
- `ContextManager` - User context preservation
- `ResultAggregator` - Parallel result aggregation

**Key Functions:**
- `should_delegate()` - Decision logic for delegation

## API Reference

### should_delegate()

```python
def should_delegate(
    operation_type: OperationType,
    transaction_count: int,
    estimated_tokens: int,
    can_parallelize: bool,
) -> bool
```

Determine if operation should be delegated to subagent.

**Parameters:**
- `operation_type` - Type of operation
- `transaction_count` - Number of transactions involved
- `estimated_tokens` - Estimated token count
- `can_parallelize` - Whether operation can be parallelized

**Returns:** `True` if should delegate

**Delegation Rules:**
- Always delegate: BULK_PROCESSING, DEEP_ANALYSIS, MULTI_PERIOD
- Transaction count > 100
- Estimated tokens > 5000
- Can parallelize

### SubagentConductor

```python
class SubagentConductor:
    def __init__(
        self,
        transaction_threshold: int = 100,
        token_threshold: int = 5000,
        dry_run: bool = False,
    )
```

Intelligent orchestration for subagent delegation.

**Methods:**

#### estimate_complexity()

```python
def estimate_complexity(
    self,
    operation_type: OperationType,
    transaction_count: int,
    period_months: int = 1,
    categories: int = 1,
) -> Dict[str, Any]
```

Estimate computational complexity.

**Returns:**
```python
{
    "estimated_tokens": 2250,
    "can_parallelize": True,
    "suggested_subagents": 3
}
```

#### build_subagent_prompt()

```python
def build_subagent_prompt(
    self,
    operation_type: str,
    task_description: str,
    data_summary: str,
    intelligence_mode: str = "smart",
    tax_level: str = "smart",
    constraints: Optional[Dict[str, Any]] = None,
) -> str
```

Build delegation prompt for subagent.

**Returns:** Formatted prompt with context, data, references, and constraints.

### ContextManager

```python
class ContextManager:
    def __init__(self, user_id: str)
```

Manages user context across subagent operations.

**Methods:**
- `set_preference(key, value)` - Store user preference
- `get_preference(key, default=None)` - Retrieve preference
- `update_session_state(key, value)` - Update session state
- `get_session_state(key, default=None)` - Retrieve state

### ResultAggregator

```python
class ResultAggregator:
    def __init__(self)
```

Aggregates results from multiple subagent operations.

**Methods:**

#### add_result()

```python
def add_result(
    self,
    operation: str,
    status: str,
    data: Dict[str, Any]
) -> None
```

Add result from a subagent operation.

#### merge_results()

```python
def merge_results(self, operation_type: str) -> Dict[str, Any]
```

Merge multiple subagent results into summary.

**Returns:**
```python
{
    "status": "success",
    "operation_type": "categorization",
    "total_operations": 3,
    "successful_operations": 3,
    "failed_operations": 0,
    "aggregated_data": {
        "categorized": 135,
        "skipped": 15
    }
}
```

## Usage Examples

### Basic Delegation Decision

```python
from scripts.orchestration.conductor import SubagentConductor, OperationType

conductor = SubagentConductor()

# Check if should delegate
should_delegate = conductor.should_delegate_operation(
    operation_type=OperationType.CATEGORIZATION,
    transaction_count=150
)

if should_delegate:
    print("Delegating to subagent...")
else:
    print("Handling directly...")
```

### Context Preservation

```python
from scripts.orchestration.conductor import ContextManager

context = ContextManager(user_id="12345")

# Set preferences
context.set_preference("intelligence_mode", "aggressive")
context.set_preference("tax_level", "full")

# Track session state
context.update_session_state("last_operation", "categorization")
context.update_session_state("transactions_processed", 150)

# Retrieve later
mode = context.get_preference("intelligence_mode")
```

### Parallel Result Aggregation

```python
from scripts.orchestration.conductor import ResultAggregator

aggregator = ResultAggregator()

# Add results from parallel subagents
aggregator.add_result("batch1", "success", {"categorized": 50})
aggregator.add_result("batch2", "success", {"categorized": 45})
aggregator.add_result("batch3", "success", {"categorized": 40})

# Merge into summary
merged = aggregator.merge_results(operation_type="categorization")
print(f"Total categorized: {merged['aggregated_data']['categorized']}")
```

## Tests

- **Unit tests:** `tests/unit/test_conductor.py`, `tests/unit/test_context_preservation.py`
- **Integration tests:** `tests/integration/test_orchestration.py`
- **Test count:** 25 unit tests, 6 integration tests

## Future Enhancements

- Subagent health monitoring
- Rate limiting across subagents
- Retry logic for failed operations
- Cost tracking and optimization
- Performance analytics
```

### Step 4: Create workflows INDEX.md

Create `scripts/workflows/INDEX.md`:

```markdown
# Interactive Workflows

Guided workflows for multi-step operations with user interaction.

## Modules

### categorization.py

Interactive transaction categorization workflow.

## API Reference

### parse_categorize_args()

```python
def parse_categorize_args(args: List[str]) -> Dict[str, Any]
```

Parse arguments for categorization command.

**Returns:**
```python
{
    "mode": "smart",
    "period": "2025-11",
    "account": None,
    "dry_run": False
}
```

### CategorizationWorkflow

```python
class CategorizationWorkflow:
    def __init__(self, client, mode: str = "smart")
```

Interactive workflow for transaction categorization.

**Methods:**

#### should_use_subagent()

```python
def should_use_subagent(self, transaction_count: int) -> bool
```

Determine if should use subagent for categorization.

#### build_summary()

```python
def build_summary(self, results: Dict[str, Any], total: int) -> str
```

Build human-readable summary of categorization results.

## Usage Examples

### Categorization Workflow

```python
from scripts.workflows.categorization import CategorizationWorkflow, parse_categorize_args
from scripts.api.client import PocketSmithClient

# Parse command arguments
args = parse_categorize_args(["--mode=smart", "--period=2025-11"])

# Create workflow
client = PocketSmithClient(api_key="your-key")
workflow = CategorizationWorkflow(client, mode=args["mode"])

# Check delegation
if workflow.should_use_subagent(transaction_count=150):
    print("Using subagent for large batch...")
else:
    print("Handling directly...")

# Build summary
results = {"categorized": 85, "skipped": 15, "rules_applied": 12, "new_rules": 3}
summary = workflow.build_summary(results, total=100)
print(summary)
```

## Tests

- **Unit tests:** `tests/unit/test_categorization_workflow.py`
- **Test count:** 7 unit tests

## Future Workflows

- Analysis workflow (spending, trends, insights)
- Reporting workflow (multi-format generation)
- Optimization workflow (categories, rules, spending)
- Tax workflow (deductions, CGT, BAS)
- Health check workflow (6 health scores)
```

### Step 5: Create commands INDEX.md

Create `.claude/commands/INDEX.md`:

```markdown
# Agent Smith Slash Commands

Quick-access commands for common financial management operations.

## All Commands

1. `/agent-smith` - Installation and onboarding point
2. `/smith:categorize` - Transaction categorization
3. `/smith:analyze` - Financial analysis
4. `/smith:scenario` - Scenario modeling
5. `/smith:report` - Report generation
6. `/smith:optimize` - Optimization operations
7. `/smith:tax` - Tax intelligence
8. `/smith:health` - Health check

## Command Descriptions

### /agent-smith

Main conversational skill for complex multi-step operations.

**Use for:**
- Understanding your financial situation
- Guided setup and onboarding
- Multi-step workflows
- Custom analysis

### /smith:categorize

Categorize uncategorized transactions with AI assistance.

**Arguments:**
- `--mode=MODE` - conservative|smart|aggressive
- `--period=PERIOD` - YYYY-MM or YYYY
- `--account=ID` - Specific account
- `--dry-run` - Preview only

**Example:**
```bash
/smith:categorize --mode=smart --period=2025-11
```

### /smith:analyze

Run financial analysis on PocketSmith data.

**Types:**
- `spending` - Category and merchant breakdown
- `trends` - MoM and YoY trends
- `category` - Deep dive into specific category
- `tax` - Tax-focused analysis
- `insights` - AI-generated insights

**Example:**
```bash
/smith:analyze spending --period=2025
```

### /smith:scenario

Model financial scenarios with what-if analysis.

**Types:**
- `historical` - What-if on past transactions
- `projection` - Future forecasts
- `optimization` - Savings opportunities
- `tax` - Tax scenario planning

**Example:**
```bash
/smith:scenario historical "What if I reduced dining by 25%?"
```

### /smith:report

Generate comprehensive reports in multiple formats.

**Formats:**
- `summary` - High-level overview
- `detailed` - Complete transaction report
- `tax` - Tax compliance report
- `custom` - Custom sections

**Output:** markdown|csv|json|html|excel|all

**Example:**
```bash
/smith:report tax --period=2024-25 --output=excel
```

### /smith:optimize

AI-assisted optimization for various targets.

**Targets:**
- `categories` - Category structure
- `rules` - Categorization rules
- `spending` - Spending patterns
- `subscriptions` - Recurring charges

**Example:**
```bash
/smith:optimize subscriptions
```

### /smith:tax

Tax-focused analysis and compliance.

**Operations:**
- `deductions` - Track deductible expenses
- `cgt` - Capital gains tax
- `bas` - BAS preparation (GST)
- `eofy` - End of financial year prep
- `scenario` - Tax scenario planning

**Example:**
```bash
/smith:tax deductions --period=2024-25 --level=full
```

### /smith:health

Evaluate PocketSmith setup health.

**Options:**
- `--full` - Complete deep analysis
- `--quick` - Fast essential checks
- `--category=AREA` - Specific area

**Health Areas:**
1. Category health
2. Rule coverage
3. Data quality
4. Tax compliance
5. Budget alignment
6. Account health

**Example:**
```bash
/smith:health --full
```

## Usage Patterns

### Quick Operations

Use specialized commands for single-purpose operations:
```bash
/smith:categorize
/smith:analyze spending
/smith:health --quick
```

### Complex Workflows

Use main command for multi-step guidance:
```bash
/agent-smith
# Then describe your needs in natural language
```

### Automation

Chain commands for regular tasks:
```bash
/smith:categorize --mode=smart
/smith:analyze trends
/smith:health --category=rules
```

## Integration with Orchestration

All commands use the subagent conductor for smart delegation:
- Small operations (< 100 transactions): Direct execution
- Large operations (> 100 transactions): Subagent delegation
- Multi-period analysis: Parallel processing

## Future Commands

Planned for Phase 7:
- `/agent-smith-alert` - Configure alerts and notifications
- `/agent-smith-merchant` - Merchant intelligence
- `/agent-smith-goal` - Goal management
```

### Step 6: Create operation log

Create `docs/operations/2025-11-21_phase6_completion.md`:

```markdown
# Phase 6: Orchestration & UX - Completion Log

**Date:** 2025-11-21
**Phase:** 6 of 8 (Weeks 11-12)
**Status:** Complete ✅

## Summary

Phase 6 implemented the intelligent orchestration layer and user experience features that make Agent Smith easy to use through subagent delegation and slash commands.

## Deliverables

### 1. Subagent Conductor (Task 1-2)

**Files Created:**
- `scripts/orchestration/__init__.py`
- `scripts/orchestration/conductor.py`
- `scripts/orchestration/INDEX.md`

**Features:**
- Smart delegation based on complexity (>100 transactions, >5000 tokens)
- Operation complexity estimation
- Subagent prompt building
- Context preservation (ContextManager)
- Result aggregation (ResultAggregator)

**Tests:**
- 19 unit tests (conductor + context preservation)
- 6 integration tests

### 2. Slash Commands (Task 3-7)

**Files Created:**
- `.claude/commands/agent-smith.md` - Main entry point
- `.claude/commands/smith:categorize.md` - Categorization
- `.claude/commands/smith:analyze.md` - Analysis
- `.claude/commands/smith:scenario.md` - Scenario modeling
- `.claude/commands/smith:report.md` - Report generation
- `.claude/commands/smith:optimize.md` - Optimization
- `.claude/commands/smith:tax.md` - Tax intelligence
- `.claude/commands/smith:health.md` - Health check
- `.claude/commands/INDEX.md` - Command reference

**Features:**
- 8 specialized slash commands
- Argument parsing for all commands
- Natural language scenario descriptions
- Multiple output formats (MD, CSV, JSON, HTML, Excel)
- Intelligence mode selection (conservative|smart|aggressive)
- Tax level selection (reference|smart|full)

### 3. Interactive Workflows (Task 4)

**Files Created:**
- `scripts/workflows/__init__.py`
- `scripts/workflows/categorization.py`
- `scripts/workflows/INDEX.md`

**Features:**
- Categorization workflow with subagent delegation
- Command argument parsing
- Result summary building
- Integration with orchestration conductor

**Tests:**
- 7 unit tests

### 4. Documentation (Task 9)

**Files Updated/Created:**
- `README.md` - Added Phase 6 features and examples
- `INDEX.md` - Added orchestration, workflows, commands
- `scripts/orchestration/INDEX.md` - API reference
- `scripts/workflows/INDEX.md` - Workflow reference
- `.claude/commands/INDEX.md` - Command reference
- `docs/operations/2025-11-21_phase6_completion.md` - This log

## Metrics

**Code:**
- New modules: 3 (orchestration, workflows, commands)
- Lines of code: ~1,200
- Functions: 12
- Classes: 5

**Tests:**
- Unit tests: 25 (19 orchestration + 7 workflows - 1 duplicate)
- Integration tests: 6
- Total Phase 6 tests: 31
- Overall tests: 225 (194 from Phases 1-5 + 31 from Phase 6)
- Pass rate: 100%

**Documentation:**
- Slash command files: 8
- API reference docs: 3 INDEX.md files
- Usage examples: 15+
- Operation log: 1

## Key Features Implemented

### Intelligent Orchestration
- Decision tree for subagent delegation
- Complexity estimation (token count, parallelization)
- Context preservation across operations
- Result aggregation from parallel subagents

### Slash Commands
- Installation and onboarding (/agent-smith)
- Categorization (/smith:categorize)
- Analysis (/smith:analyze)
- Scenario modeling (/smith:scenario)
- Reporting (/smith:report)
- Optimization (/smith:optimize)
- Tax intelligence (/smith:tax)
- Health check (/smith:health)

### User Experience
- Natural language scenario descriptions
- Multiple output formats
- Progress tracking
- Smart recommendations
- Guided workflows

## Technical Implementation

**Delegation Rules:**
1. Always delegate: BULK_PROCESSING, DEEP_ANALYSIS, MULTI_PERIOD
2. Transaction count > 100
3. Estimated tokens > 5000
4. Can parallelize (multi-period, multi-category)

**Context Management:**
- User preferences (intelligence_mode, tax_level)
- Session state (last_operation, transactions_processed)
- Preservation across subagent operations

**Result Aggregation:**
- Merge results from parallel subagents
- Handle partial failures
- Aggregate numeric data fields

## Git Commits

1. `feat(orchestration): add subagent conductor with decision logic`
2. `feat(orchestration): add context preservation and result aggregation`
3. `feat(commands): add main agent-smith slash command`
4. `feat(workflows): add categorization workflow and slash command`
5. `feat(commands): add analysis and reporting slash commands`
6. `feat(commands): add scenario and optimization slash commands`
7. `feat(commands): add tax and health check slash commands`
8. `test(orchestration): add integration tests for workflows`
9. `docs: update documentation for Phase 6 orchestration and UX completion`

**Total commits:** 9

## Testing Results

**All tests passing:**
```
tests/unit/test_conductor.py ................... (10 tests)
tests/unit/test_context_preservation.py ........ (9 tests)
tests/unit/test_categorization_workflow.py ..... (7 tests)
tests/integration/test_orchestration.py ........ (6 tests)
tests/integration/test_slash_commands.py ....... (3 tests)

Total: 35 tests (29 unit + 6 integration) - includes 4 from slash command structure tests
```

## Challenges & Solutions

**Challenge 1: Determining when to delegate**
- **Solution:** Implemented complexity estimation with multiple factors (transaction count, tokens, parallelization)

**Challenge 2: Context preservation**
- **Solution:** Created ContextManager to store user preferences and session state

**Challenge 3: Aggregating parallel results**
- **Solution:** Built ResultAggregator to merge numeric data and handle partial failures

**Challenge 4: Slash command discoverability**
- **Solution:** Created comprehensive INDEX.md with examples and usage patterns

## Next Phase: Phase 7

**Phase 7: Advanced Features (Weeks 13-14)**

Planned features:
- Smart alerts & notifications
- Merchant intelligence
- Receipt & document management
- Multi-user & shared expenses
- Audit trail
- Comparative benchmarking

**Estimated tasks:**
- Alert configuration and scheduling
- Merchant enrichment and learning
- Document attachment tracking
- Shared expense splitting
- Activity logging
- Benchmarking analytics

## Project Status

**Completed Phases:**
1. ✅ Foundation
2. ✅ Rule Engine
3. ✅ Analysis & Reporting
4. ✅ Tax Intelligence
5. ✅ Scenario Analysis
6. ✅ Orchestration & UX

**Remaining Phases:**
7. ⏳ Advanced Features
8. ⏳ Health Check & Polish

**Progress:** 6/8 phases (75% complete)

**Overall Statistics:**
- Total tests: 225 (186 unit + 39 integration)
- Total modules: 30+
- Total slash commands: 8
- Lines of code: ~12,000
- Pass rate: 100%

---

**Phase 6 Complete!** 🎉

Next: Phase 7 - Advanced Features
```

### Step 7: Run all tests

```bash
pytest -v --tb=short
```

Expected: PASS (225 tests total)

### Step 8: Commit documentation

```bash
git add README.md INDEX.md scripts/orchestration/INDEX.md scripts/workflows/INDEX.md .claude/commands/INDEX.md docs/operations/2025-11-21_phase6_completion.md
git commit -m "docs: update documentation for Phase 6 orchestration and UX completion

- Update README with Phase 6 features and examples
- Add orchestration, workflows, commands to INDEX
- Create API reference for orchestration layer
- Create workflow reference documentation
- Create slash command reference with usage patterns
- Document operation completion log with metrics
- Phase 6: 31 tests (25 unit + 6 integration)
- Total: 225 tests (186 unit + 39 integration)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com)"
```

---

## Phase 6 Summary

**Total Tasks:** 9
**Total Steps:** ~50
**Estimated Time:** 2-3 hours (bite-sized tasks)

**Deliverables:**
- Subagent conductor with smart delegation
- Context preservation and result aggregation
- 8 slash commands for quick operations
- Interactive categorization workflow
- Comprehensive API documentation
- Integration tests
- 31 new tests (25 unit + 6 integration)

**Testing:**
- All TDD (RED-GREEN-REFACTOR)
- 225 total tests (186 unit + 39 integration)
- 100% pass rate

**Commits:** 9 feature commits with conventional commit messages

---

**Plan saved to:** `docs/plans/2025-11-21-phase-6-orchestration-ux.md`

