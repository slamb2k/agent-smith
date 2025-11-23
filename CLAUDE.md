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
- **Always backup before mutations** - Use timestamped backup directories
- **Tax advice disclaimer required** - All Level 3 tax outputs must include professional advice disclaimer
- **INDEX.md must be current** - Update whenever files are created/modified/deleted
- Complete design specification is the source of truth: `docs/design/2025-11-20-agent-smith-design.md`
- Always create a feature branch and use a PR to merge changes to main.