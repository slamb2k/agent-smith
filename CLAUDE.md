# CLAUDE.md

This file provides **mandatory operating instructions** for AI coding assistants working on Agent Smith. These rules ensure consistency, quality, and a great user experience.

> **Audience:** AI coding assistants (Claude Code, etc.)
> **For human developers:** See [DEVELOPMENT.md](DEVELOPMENT.md) and [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Project Identity

**Agent Smith** is an intelligent financial management skill for Claude Code providing PocketSmith API integration with AI-powered analysis, rule management, tax intelligence, and scenario planning.

**Design Specification:** `docs/design/2025-11-20-agent-smith-design.md` (source of truth)

---

## Critical Operating Rules

These rules are **non-negotiable**. Violating them causes bugs, data loss, or poor user experience.

### 1. Source Code Location

```
agent-smith/
├── scripts/                    ← ✅ EDIT HERE (tracked in git)
└── agent-smith-plugin/.../scripts/  ← ❌ NEVER EDIT (gitignored, overwritten)
```

- **ALWAYS** edit files in `/scripts/`
- **NEVER** edit files in `agent-smith-plugin/skills/agent-smith/scripts/`
- Run `./scripts/dev-sync.sh` after editing to sync to plugin

### 2. Python Execution

```bash
# ✅ CORRECT - Always use uv run with unbuffered output
uv run python -u scripts/some_script.py

# ❌ WRONG - Dependencies won't be found
python scripts/some_script.py
```

The `-u` flag is **mandatory** for real-time output streaming.

### 3. Deterministic Operations

**All PocketSmith API operations MUST use git-tracked Python scripts.**

```
scripts/operations/
├── fetch_*.py      # Read operations (no mutations)
├── update_*.py     # Single-record mutations
├── create_*.py     # Resource creation
└── reprocess_*.py  # Batch operations
```

- ❌ **NEVER** embed Python code in slash commands or prompts
- ❌ **NEVER** write ad-hoc scripts for one-time operations
- ✅ **ALWAYS** use existing scripts in `scripts/operations/`
- ✅ **ALWAYS** create new scripts if functionality doesn't exist

### 4. Category Hierarchy

**ALWAYS** use `flatten=True` when retrieving categories:

```python
# ✅ CORRECT - Child categories are searchable
categories = client.get_categories(user_id, flatten=True)

# ❌ WRONG - 127 child categories are invisible!
categories = client.get_categories(user_id, flatten=False)
```

### 5. Backup Before Mutations

**ALWAYS** backup data before any write operation to PocketSmith.

### 6. Restart Notifications

**ALWAYS** prompt user to restart Claude Code when creating/modifying:
- Slash commands
- Skills
- Hooks
- MCP servers

---

## Development Principles

These principles guide **how** we build Agent Smith. Follow them in order of priority.

### Principle 1: Determinism & Consistency

> **Python provides consistency. Prompts provide interactivity.**

- Use **typed Python interfaces** for all PocketSmith operations
- Same inputs MUST produce same outputs
- No hidden state or side effects
- All logic is testable and auditable

```python
# ✅ Typed, deterministic function
def update_transaction(
    transaction_id: int,
    category_id: Optional[int] = None,
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Update a transaction with explicit parameters."""
    ...
```

### Principle 2: Code Reuse Over Creation

> **Before writing new code, search for existing code that does what you need.**

1. **Check existing scripts first:**
   - `scripts/operations/` - Data operations
   - `scripts/workflows/` - Multi-step processes
   - `scripts/services/` - Business logic
   - `scripts/core/` - Shared utilities

2. **Look for similar patterns:**
   - If `fetch_conflicts.py` exists, don't create `get_conflicts.py`
   - If `update_transaction.py` handles labels, don't duplicate label logic

3. **Extend, don't duplicate:**
   - Add parameters to existing scripts
   - Create shared utilities in `scripts/core/`
   - Refactor common patterns into reusable functions

### Principle 3: Test-Driven Development

> **Write tests first. Watch them fail. Then implement.**

- **Unit tests** for all new functions
- **Integration tests** for API interactions
- Tests live in `tests/unit/` and `tests/integration/`
- Run tests: `uv run pytest tests/ -v`

```bash
# TDD workflow
1. Write failing test
2. Run test, confirm failure
3. Implement minimal code to pass
4. Refactor if needed
5. Repeat
```

### Principle 4: Separation of Concerns

| Layer | Purpose | Tools |
|-------|---------|-------|
| **Python Scripts** | Data operations, business logic | Typed functions, argparse CLI |
| **Skills/Commands** | User interaction, orchestration | Markdown prompts, Claude Code |
| **Prompts** | Conversational UX, guidance | Natural language |

```
User → Slash Command → Python Script → PocketSmith API
         (UX)           (Logic)         (Data)
```

### Principle 5: Real-Time Feedback

> **Stream information to the user during long operations.**

- Use `print()` with flush for progress updates
- Use `-u` flag for unbuffered Python output
- Provide progress indicators: `[23/100] Processing...`
- Never leave user waiting without feedback

```python
# ✅ Stream progress to user
for i, txn in enumerate(transactions):
    print(f"[{i+1}/{len(transactions)}] Processing {txn['payee']}...")
    process(txn)
print(f"✅ Completed {len(transactions)} transactions")
```

---

## User Experience Guidelines

Agent Smith should feel like a **guided, intuitive assistant**. Follow these UX patterns.

### Guided Workflows

Every command/skill interaction should include:

1. **Goal** - What will this accomplish?
2. **Why** - Why is this important?
3. **Steps** - What steps will be taken?
4. **Progress** - Real-time feedback during execution
5. **Summary** - What was accomplished?
6. **Next Steps** - What should the user do next?

```markdown
## Goal
Categorize uncategorized transactions using rules and AI.

## Why This Matters
Uncategorized transactions reduce your financial visibility and health score.

## Steps
1. Fetch uncategorized transactions
2. Apply rule engine matching
3. Use AI for unmatched transactions
4. Update PocketSmith

## Next Steps
- Review flagged conflicts: `/smith:review-conflicts`
- Check your health score: `/smith:health`
```

### Visual Elements

Leverage Claude Code's UI capabilities:

| Element | Use Case | Example |
|---------|----------|---------|
| **Emojis** | Status indicators | ✅ ❌ ⚠️ 🔄 📊 💰 |
| **Progress** | Long operations | `[23/100] Processing...` |
| **Tables** | Data summaries | Markdown tables |
| **ASCII Charts** | Visual data | Bar charts, sparklines |
| **Colors** | Emphasis (in prompts) | Status highlighting |
| **Selection Menus** | User choices | `AskUserQuestion` tool |

### Command Frontmatter

Define helpful metadata in slash commands:

```yaml
---
description: Categorize uncategorized transactions
argument-hint: [period] [--mode smart|conservative|aggressive] [--dry-run]
---
```

### Error Handling UX

- **Explain** what went wrong in plain language
- **Suggest** how to fix it
- **Offer** next steps or alternatives

```markdown
❌ **Error:** Could not find category "Grocereis"

**Did you mean:** "Groceries" (Food & Dining > Groceries)?

**To fix:** Run the command again with the correct category name.
```

---

## Code Patterns

### Script CLI Pattern

All scripts should follow this pattern:

```python
#!/usr/bin/env python3
"""Brief description of what this script does."""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--output", choices=["json", "summary"], default="summary")
    args = parser.parse_args()

    # Implementation here
    result = do_work(dry_run=args.dry_run)

    # Output
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"✅ Processed {result['count']} items")

    return 0 if result["success"] else 1

if __name__ == "__main__":
    sys.exit(main())
```

### API Client Usage

```python
from scripts.core.api_client import PocketSmithClient
from scripts.core.category_utils import find_category_by_name

client = PocketSmithClient()
user = client.get_user()

# Always flatten categories for operations
categories = client.get_categories(user["id"], flatten=True)
category = find_category_by_name(categories, "Groceries")

# Update with explicit parameters
client.update_transaction(
    transaction_id=12345,
    category_id=category["id"],
    labels=["processed"]
)
```

### Label Constants

Use constants from `scripts/core/labels.py`:

```python
from scripts.core.labels import (
    LABEL_CATEGORY_CONFLICT,
    LABEL_NEEDS_REVIEW,
    LABEL_TAX_DEDUCTIBLE,
)

# In templates, use $CONSTANT_NAME syntax
# $LABEL_CATEGORY_CONFLICT → "⚠️ Review: Category Conflict"
```

---

## Quick Reference

### Common Commands

```bash
# Run tests
uv run pytest tests/ -v

# Sync scripts to plugin
./scripts/dev-sync.sh

# Health check
uv run python -u scripts/health/check.py

# Categorize transactions
uv run python -u scripts/operations/categorize_batch.py --period 2025-11
```

### Directory Structure

| Directory | Purpose |
|-----------|---------|
| `scripts/core/` | Shared libraries (API client, rules, utils) |
| `scripts/operations/` | Data operations (fetch, update, create) |
| `scripts/workflows/` | Multi-step processes |
| `scripts/services/` | Business logic (LLM categorization) |
| `scripts/health/` | Health check system |
| `scripts/tax/` | Tax intelligence |
| `scripts/scenarios/` | Scenario analysis |
| `scripts/setup/` | Onboarding and templates |

### Key Files

| File | Purpose |
|------|---------|
| `scripts/core/api_client.py` | PocketSmith API client |
| `scripts/core/rule_engine.py` | Transaction rule matching |
| `scripts/core/labels.py` | Label constants |
| `scripts/core/category_utils.py` | Category helpers |
| `data/rules.yaml` | User-defined rules |

---

## Technical Reference

### PocketSmith API

- **Auth:** `X-Developer-Key` header from `.env`
- **Rate Limit:** Configurable via `API_RATE_LIMIT_DELAY`
- **Docs:** `ai_docs/pocketsmith-api-documentation.md`

### Environment Variables

```bash
POCKETSMITH_API_KEY=<required>
TAX_INTELLIGENCE_LEVEL=smart|reference|full
DEFAULT_INTELLIGENCE_MODE=smart|conservative|aggressive
TAX_JURISDICTION=AU
FINANCIAL_YEAR_END=06-30
```

### Tax Intelligence Levels

| Level | Features |
|-------|----------|
| **Reference** | Basic reporting, ATO category mapping |
| **Smart** | Deduction flagging, CGT tracking, thresholds |
| **Full** | BAS preparation, compliance checks (requires disclaimer) |

---

## Additional Documentation

| Document | Audience | Purpose |
|----------|----------|---------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Humans | Development workflow, dual-location architecture |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Humans | Setup, testing, PR process |
| [README.md](README.md) | Everyone | Project overview, quick start |
| `docs/design/*.md` | Everyone | Architecture and design specs |
| `ai_docs/` | AI Agents | API reference, tax guidelines |
