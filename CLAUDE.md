# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Agent Smith** is an intelligent financial management skill for Claude Code that provides comprehensive PocketSmith API integration with advanced AI-powered analysis, rule management, tax intelligence, and scenario planning.

**Status:** Design phase complete, ready for implementation

## Architecture

### Three-Tier System

1. **API Integration Layer** - PocketSmith API communication with rate limiting, caching, error handling, automatic backups
2. **Intelligence Engine** - Hybrid rule engine (platform + local), 3-tier tax intelligence (Reference/Smart/Full), scenario analysis, AI categorization with tiered modes (Conservative/Smart/Aggressive)
3. **Orchestration Layer** - Smart subagent conductor for context preservation, parallel processing, and result aggregation

### Core Design Principles

- **Hybrid Approach:** Single-shot operations for simple tasks, conversational sessions for complex workflows
- **User Choice:** Always recommend a mode but allow user override
- **Context Preservation:** Use subagent orchestration to delegate heavy operations while preserving main context
- **Smart Archiving:** Automatic retention policies with INDEX.md files for LLM-efficient discovery
- **Backup-First:** Always backup before mutations
- **Deterministic Operations:** All data operations use git-tracked scripts for testability and reproducibility (see pattern below)

### Label Constants in Templates

**Template rules can reference label constants using `$CONSTANT_NAME` syntax:**

```json
{
  "name": "paypal-generic",
  "payee_pattern": "PAYPAL",
  "category": "Online Services",
  "labels": ["$LABEL_GENERIC_PAYPAL"]
}
```

When templates are applied, the `template_applier.py` resolves constants from `scripts/core/labels.py`:
- `$LABEL_GENERIC_PAYPAL` → `"⚠️ Review: Generic PayPal"`
- `$LABEL_CATEGORY_CONFLICT` → `"⚠️ Review: Category Conflict"`
- `$LABEL_TAX_DEDUCTIBLE` → `"Tax Deductible"`
- And all other constants defined in `scripts/core/labels.py`

**Benefits:**
- Ensures consistency between templates and code
- Single source of truth for label values
- Easy to update labels globally by changing constants
- Type-safe (constants are defined in Python with docstrings)

### Deterministic Operations Pattern

**CRITICAL: All data retrieval and mutation operations MUST use git-tracked Python scripts.**

**Pattern Structure:**
```
scripts/operations/
├── fetch_*.py      # Data retrieval (read-only)
├── update_*.py     # Single-record mutations
├── create_*.py     # Resource creation
└── reprocess_*.py  # Batch operations
```

**Why this pattern:**
- ✅ **Version Controlled:** All logic is git-tracked and auditable
- ✅ **Testable:** Each script can be tested independently
- ✅ **Deterministic:** Same inputs = same outputs, no hidden state
- ✅ **Reusable:** Scripts can be called from slash commands, skills, or terminal
- ✅ **Debuggable:** Easy to trace and reproduce issues

**Implementation Rules:**

1. **Never embed data operations in slash commands or conversational prompts**
   - ❌ BAD: Python code blocks in command markdown files
   - ✅ GOOD: Commands orchestrate git-tracked scripts via `uv run python -u`

2. **Scripts must be self-contained and CLI-friendly**
   - Accept arguments via argparse
   - Output to stdout (JSON, summary, or count)
   - Use exit codes (0 = success, non-zero = error)
   - Support `--dry-run` for safe testing

3. **Naming conventions:**
   - `fetch_*.py` - Read operations, no mutations
   - `update_*.py` - Update existing records
   - `create_*.py` - Create new records/resources
   - `reprocess_*.py` - Batch processing with multiple operations

4. **Example: Transaction conflict review workflow**
   ```bash
   # Fetch conflicts (deterministic read)
   uv run python -u scripts/operations/fetch_conflicts.py --output json > /tmp/conflicts.json

   # Update single transaction (deterministic write)
   uv run python -u scripts/operations/update_transaction.py 123456 --category-name "Food"

   # Create new rule (deterministic resource creation)
   uv run python -u scripts/operations/create_rule.py "Food" --payee "WOOLWORTHS" --pattern-type keyword

   # Reprocess with new rules (deterministic batch operation)
   uv run python -u scripts/operations/reprocess_conflicts.py --transactions-file /tmp/conflicts.json
   ```

5. **Orchestration layers (slash commands, skills) should:**
   - Call scripts via subprocess or uv run
   - Parse script output (JSON preferred)
   - Provide conversational UX around deterministic operations
   - Never duplicate logic that belongs in scripts

**Reference implementation:** See `/smith:review-conflicts` command and its associated scripts:
- `scripts/operations/fetch_conflicts.py`
- `scripts/operations/update_transaction.py`
- `scripts/operations/create_rule.py`
- `scripts/operations/reprocess_conflicts.py`

### Subagent Strategy

**When to delegate operations to subagents:**
- Transaction count > 100
- Estimated tokens > 5000
- Bulk processing, deep analysis, or multi-period operations
- Parallelization opportunities (e.g., analyze 12 months → 12 parallel agents)

**Subagent types (in future `scripts/subagents/`):**
- categorization-agent, analysis-agent, reporting-agent, tax-agent, optimization-agent, scenario-agent

## Repository Structure

**Key Directories:**

- `docs/design/` - Complete design specifications (start here for understanding)
- `ai_docs/` - Documentation for AI agents/subagents (PocketSmith API reference, future tax guidelines)
- `.env` - API configuration (**NEVER commit**, protected by .gitignore)

**Navigation:**
- Each major directory has an `INDEX.md` file for efficient discovery by both humans and LLMs
- `README.md` - Project overview and quick start
- `INDEX.md` (root) - Complete repository navigation guide

## Development Workflow

### **CRITICAL: Source Code Location**

**Agent Smith uses a dual-location architecture for scripts:**

```
agent-smith/
├── scripts/                    ← ✅ SOURCE (edit here, tracked in git)
│   ├── core/
│   ├── health/
│   └── ...
│
└── agent-smith-plugin/skills/agent-smith/
    └── scripts/                ← ❌ COPY (gitignored, synced from source)
```

**THE GOLDEN RULE: Always edit `/scripts/`, NEVER `agent-smith-plugin/.../scripts/`**

Files in `agent-smith-plugin/skills/agent-smith/scripts/` are:
- Gitignored (changes won't be committed)
- Overwritten by sync (changes will be lost)
- Build artifacts (not source code)

**When editing code:**
1. ✅ Edit files in `/scripts/` (source, tracked in git)
2. ✅ Run `./scripts/dev-sync.sh` to sync to plugin
3. ✅ Test using plugin copy
4. ✅ Commit source changes from `/scripts/`

**See DEVELOPMENT.md for complete dual-location architecture documentation.**

### Initial Setup

```bash
# Environment setup
cp .env.sample .env
# Add POCKETSMITH_API_KEY to .env

# For isolated development, use git worktrees
git worktree add ../agent-smith-dev -b feature/phase-1-foundation
```

### Running Python Scripts

**CRITICAL: Always use `uv run` when executing Python scripts in this repository.**

```bash
# ✅ CORRECT - Use uv run with unbuffered output
uv run python -u scripts/some_script.py

# ✅ For background tasks with real-time output
uv run python -u scripts/some_script.py &

# ✅ For one-liners
uv run python -u -c "from scripts.core.api_client import PocketSmithClient; ..."

# ❌ WRONG - Do not run Python directly (dependencies won't be found)
python scripts/some_script.py  # Will get ModuleNotFoundError
```

**Why use `uv run`:** Dependencies (`requests`, `python-dateutil`, `python-dotenv`) are installed in the `.venv` virtual environment. Using `uv run` ensures Python uses the venv automatically.

**Why use `-u` flag:** Python buffers output by default, hiding progress during long operations. The `-u` flag enables unbuffered output so you see results in real-time. This is especially important for:
- Long-running categorization tasks
- Health checks analyzing large datasets
- Multi-step workflows with progress indicators
- Background tasks where you need to monitor progress

**Alternative:** Activate the venv first, then run Python with `-u`:
```bash
source .venv/bin/activate  # Unix/macOS
python -u scripts/some_script.py
```

**Or set environment variable:**
```bash
export PYTHONUNBUFFERED=1  # Unix/macOS
uv run python scripts/some_script.py
```

### Implementation Phases

**Current Phase:** Foundation (Phase 1 of 8)

Refer to `docs/design/2025-11-20-agent-smith-design.md` Section 11 for complete 16-week roadmap:
1. Foundation (weeks 1-2) - Directory structure, core libraries
2. Rule Engine (weeks 3-4)
3. Analysis & Reporting (weeks 5-6)
4. Tax Intelligence (weeks 7-8)
5. Scenario Analysis (weeks 9-10)
6. Orchestration & UX (weeks 11-12)
7. Advanced Features (weeks 13-14)
8. Health Check & Polish (weeks 15-16)

### Reference Materials

Insights from previous PocketSmith migration work have been incorporated into Agent Smith's design.

**See:** `docs/design/LESSONS_LEARNED.md` for detailed patterns, API quirks, and best practices extracted from prior migration experience.

## Key Technical Decisions

### Hybrid Rule Engine

**Two-tier system:**
1. **Platform Rules** - Created via PocketSmith API (keyword-only), auto-apply server-side, tracked in `data/platform_rules.json`
2. **Local Rules** - Enhanced engine with regex, multi-condition logic, confidence scoring, stored in `data/local_rules.json`

**Decision logic:** Simple keyword patterns → Platform API. Complex patterns → Local engine.

### Tax Intelligence Levels

Configurable via `TAX_INTELLIGENCE_LEVEL` env var or runtime override:

- **Reference** - Basic reporting, ATO category mapping, links to resources
- **Smart** - Deduction flagging, expense splitting suggestions, CGT tracking, threshold monitoring
- **Full** - BAS preparation, compliance checks, scenario planning, audit-ready documentation

All Level 3 outputs must include disclaimer: "Consult a registered tax agent for advice"

### Smart Archiving & INDEX.md

**Retention policies:**
- Cache: 7 days auto-purge
- Logs: 14 days active → monthly .tar.gz archives
- Backups: 30 days recent → monthly archives
- Reports: 90 days → archive (tax reports: 7 years for ATO)

**Every file operation must update relevant INDEX.md** - Contains filename, date, size, description, tags. Enables LLM quick scanning without reading all files.

### Australian Tax Compliance

**ATO documentation caching strategy:**
- Cache ATO guidelines locally in `ai_docs/tax/`
- Track version/hash in `cache_metadata.json`
- Monthly refresh, force refresh pre-EOFY (May-June) and post-Budget (October)
- Before tax operations: verify cache freshness, alert on changes

## PocketSmith API Integration

**Authentication:** Developer key via `X-Developer-Key` header (from `.env`)

**Key endpoints used:**
- `/v2/me` - Get authorized user
- `/v2/users/{id}/transactions` - Transaction operations
- `/v2/users/{id}/categories` - Category management
- `/v2/categories/{id}/category-rules` - Rule creation (limited: keyword-only, no delete/modify)

**API constraints:**
- Rate limiting required (configurable delay via `API_RATE_LIMIT_DELAY`)
- Category rules API only supports simple keywords
- Rules cannot be modified/deleted via API (must track externally)

**Reference:** `ai_docs/pocketsmith-api-documentation.md`

### Category Hierarchy Handling

**CRITICAL: PocketSmith categories are hierarchical - parent categories contain child categories.**

**The Problem:**
The API returns categories with children nested in a `children` array:
```json
{
  "id": 26796189,
  "title": "Utilities",
  "children": [
    {"id": 26927667, "title": "Internet & Phone", "parent_id": 26796189},
    {"id": 17151799, "title": "Power", "parent_id": 26796189}
  ]
}
```

**Without flattening, child categories are invisible to search/matching operations!**

**The Solution:**
Always use `flatten=True` when retrieving categories for operations:

```python
from scripts.core.api_client import PocketSmithClient
from scripts.core.category_utils import find_category_by_name

client = PocketSmithClient()
user = client.get_user()

# ✅ CORRECT - Flatten to include all child categories
categories = client.get_categories(user["id"], flatten=True)

# Now child categories like "Internet & Phone" are searchable
cat = find_category_by_name(categories, "Internet & Phone")
print(cat["id"])  # 26927667

# ❌ WRONG - Hierarchical structure hides children
categories = client.get_categories(user["id"], flatten=False)
# Child categories are nested, won't be found by simple iteration!
```

**When to use each mode:**

| Mode | Use Case | Example |
|------|----------|---------|
| `flatten=True` | **Searching, matching, categorization** | Find category by name, update transactions, conflict resolution |
| `flatten=False` | **Display hierarchy, tree views** | Showing category structure to user, printing trees |

**Helper Functions in `scripts/core/category_utils.py`:**

*Basic Search & Lookup:*
- `find_category_by_name(categories, name)` - Search by name (case-insensitive)
- `find_category_by_id(categories, id)` - Search by ID
- `get_category_path(categories, category)` - Get full path (e.g., ["Utilities", "Internet & Phone"])
- `search_categories(categories, query)` - Partial match search
- `filter_categories(categories, parent_only=True)` - Filter by type

*Hierarchy & Specificity (uses `hierarchy_level` field added by flatten):*
- `sort_by_specificity(categories, prefer_specific=True)` - Sort by hierarchy level (child/parent)
- `find_most_specific_category(categories, query)` - Search and prioritize specific (child) categories
- `get_hierarchy_level(category)` - Get level (0=parent, 1=child, 2=grandchild)
- `is_child_category(category)` - Check if has parent
- `is_parent_category(category)` - Check if is root-level

**Hierarchy Level Metadata:**

When using `flatten=True`, each category gets a `hierarchy_level` field:
- **Level 0**: Parent categories (49 total) - e.g., "Utilities", "Food & Dining"
- **Level 1**: Child categories (127 total) - e.g., "Internet & Phone", "Groceries"
- **Level 2+**: Grandchildren (if any) - deeper nesting levels

**Use Cases for Hierarchy Awareness:**
```python
# Prioritize specific categories in AI categorization
specific_cats = sort_by_specificity(categories, prefer_specific=True)
# Result: ["Internet & Phone" (level 1), "Utilities" (level 0)]

# Find the most specific match
results = find_most_specific_category(categories, "utilities")
# Prefers child categories over parents when both match
```

**Mandatory Pattern for All Scripts:**
```python
# ✅ Use this pattern everywhere categories are used for operations
categories = client.get_categories(user_id, flatten=True)
cat = find_category_by_name(categories, "Internet & Phone")
```

**Scripts Updated to Use flatten=True:**
- ✅ `scripts/operations/update_transaction.py`
- ✅ `scripts/operations/categorize_batch.py`
- ✅ `scripts/setup/template_applier.py`
- ✅ `scripts/health/collector.py`
- ✅ `scripts/find_category.py`

**Real Impact:** Without flattening, 127 child categories (out of 176 total) are invisible to categorization, conflict resolution, and rule matching!

## Configuration

**Environment variables (`.env`):**
```bash
POCKETSMITH_API_KEY=<required>
TAX_INTELLIGENCE_LEVEL=smart|reference|full
DEFAULT_INTELLIGENCE_MODE=smart|conservative|aggressive
TAX_JURISDICTION=AU
FINANCIAL_YEAR_END=06-30
```

**User preferences:** `data/config.json` (household settings, alerts, report formats, benchmarking)

## Slash Commands

Agent Smith provides 8 slash commands in `agent-smith-plugin/commands/`:
- `/smith:install` - Installation and onboarding wizard
- `/smith:categorize` - Transaction categorization
- `/smith:analyze` - Financial analysis
- `/smith:scenario` - Scenario modeling
- `/smith:report` - Multi-format reports
- `/smith:optimize` - Category/rule/spending optimization
- `/smith:tax` - Tax intelligence operations
- `/smith:health` - PocketSmith setup health check

**Main conversational interface:** Use the Agent Smith skill directly for natural language
financial conversations and ad-hoc analysis.

**Note:** When creating slash commands, **immediately prompt user to restart Claude Code**.

## Important Notes

- **Never commit `.env`** - Contains sensitive API keys (protected by .gitignore)
- **Always edit `/scripts/`, never `agent-smith-plugin/.../scripts/`** - Plugin scripts are gitignored copies
- **Use Deterministic Operations Pattern** - All data operations MUST use git-tracked scripts in `scripts/operations/` (see pattern above)
- **Always backup before mutations** - Use timestamped backup directories
- **Tax advice disclaimer required** - All Level 3 tax outputs must include professional advice disclaimer
- **INDEX.md must be current** - Update whenever files are created/modified/deleted
- Complete design specification is the source of truth: `docs/design/2025-11-20-agent-smith-design.md`
- Always create a feature branch and use a PR to merge changes to main.

## Additional Documentation

- **DEVELOPMENT.md** - Complete development workflow guide, explains dual-location architecture for scripts
- **CONTRIBUTING.md** - Development setup and contribution guidelines
- **README.md** - Project overview, quick start, and repository structure