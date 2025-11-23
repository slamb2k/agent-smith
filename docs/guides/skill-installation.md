---
title: Agent Smith Claude Code Skill Installation Guide
category: guides
status: active
created: 2025-11-23
last_updated: 2025-11-23
tags: [installation, setup, skill, claude-code, onboarding]
---

# Agent Smith - Claude Code Skill Installation Guide

## What is Agent Smith?

Agent Smith is an intelligent financial management skill for Claude Code that provides comprehensive PocketSmith API integration with AI-powered analysis, transaction categorization, rule management, tax intelligence, and scenario planning.

**Version**: 1.3.6

## Installation

### Method 1: Direct Installation (Recommended)

1. **Install the skill file**:
   ```bash
   # In Claude Code, use the plugin command
   /plugin install path/to/agent-smith.skill
   ```

2. **Restart Claude Code** to load the skill.

3. **Configure the skill**:
   - Navigate to the installed skill directory (usually `~/.claude/skills/agent-smith/`)
   - Copy `.env.sample` to `.env`
   - Add your PocketSmith API key: `POCKETSMITH_API_KEY=<your_key>`
   - Configure other settings as needed

4. **Install dependencies**:
   ```bash
   cd ~/.claude/skills/agent-smith/
   uv sync
   ```

5. **Run the onboarding process**:
   ```bash
   /agent-smith:install
   ```

### Method 2: Manual Installation

1. **Extract the skill**:
   ```bash
   mkdir -p ~/.claude/skills/
   cd ~/.claude/skills/
   unzip path/to/agent-smith.skill
   ```

2. **Follow steps 2-5 from Method 1 above**.

## Quick Start

### First-Time Setup

After installation, launch the integrated onboarding process:

```bash
/agent-smith:install
```

This guided 8-stage process will:
1. Discover your PocketSmith account structure
2. Recommend and apply a rule template
3. Help you customize rules for your needs
4. Configure intelligence modes
5. Incrementally categorize your transactions
6. Show measurable improvement with health scores
7. Provide ongoing usage guidance
8. Generate intelligent suggestions

**Time required**: 30-60 minutes

### Daily Usage

Use the 8 specialized slash commands:

- `/agent-smith` - Main conversational entry point
- `/agent-smith-categorize [--mode] [--period]` - Transaction categorization
- `/agent-smith-analyze [type] [--period]` - Financial analysis
- `/agent-smith-scenario [type] [description]` - Scenario modeling
- `/agent-smith-report [format] [--period]` - Report generation
- `/agent-smith-optimize [target]` - Optimization operations
- `/agent-smith-tax [operation] [--period]` - Tax intelligence
- `/agent-smith-health [--full]` - Health check

## Configuration

### Required Configuration

Edit `~/.claude/skills/agent-smith/.env`:

```bash
# PocketSmith API (REQUIRED)
POCKETSMITH_API_KEY=<Your Developer API Key>

# Agent Smith Configuration
TAX_INTELLIGENCE_LEVEL=smart          # reference|smart|full
DEFAULT_INTELLIGENCE_MODE=smart       # conservative|smart|aggressive

# Tax Configuration (Australia)
TAX_JURISDICTION=AU
FINANCIAL_YEAR_END=06-30
```

### Optional Configuration

Additional settings in `.env`:

```bash
# Features
AUTO_BACKUP=true
AUTO_ARCHIVE=true
ALERT_NOTIFICATIONS=true
GST_REGISTERED=false

# Reporting
DEFAULT_REPORT_FORMAT=all            # markdown|csv|json|html|excel|all
CURRENCY=AUD

# Advanced
API_RATE_LIMIT_DELAY=100             # ms between calls
CACHE_TTL_DAYS=7
SUBAGENT_MAX_PARALLEL=5
```

## Core Features

### 1. Transaction Categorization
- Batch categorization with AI assistance
- Hybrid rule engine (platform + local)
- Three intelligence modes (Conservative/Smart/Aggressive)
- Merchant normalization and variation detection
- Dry-run mode for safe testing

### 2. Tax Intelligence (Australian ATO)
- **Level 1 (Reference)**: Basic tax reports, ATO mappings, GST tracking
- **Level 2 (Smart)**: Deduction detection, CGT tracking, substantiation requirements
- **Level 3 (Full)**: BAS preparation, compliance checks, audit-ready docs

### 3. Financial Analysis
- Spending analysis by category, merchant, period
- Trend detection (increasing/decreasing/stable)
- Multi-format reports (Markdown, CSV, JSON, HTML, Excel)
- Comparative analysis (YoY, QoQ, MoM)

### 4. Scenario Analysis
- Historical: What-if modeling ("What if I cut dining by 30%?")
- Projections: Spending forecasts, affordability analysis
- Optimization: Subscription detection, expense rationalization
- Tax Planning: Purchase timing, income deferral, CGT scenarios

### 5. Health Check System
- 6 health dimensions (Data Quality, Category Structure, Rule Engine, Tax Readiness, Automation, Budget Alignment)
- Automated monitoring (weekly/monthly/EOFY)
- Prioritized recommendations
- Impact projections

### 6. Advanced Features
- Smart alerts and notifications
- Document/receipt tracking (ATO $300 threshold)
- Multi-user shared expenses
- Audit trail with undo capability
- Automatic backups before mutations

## Using the Skill

### Example: Categorize Transactions

```bash
# Using slash command
/agent-smith-categorize --mode=smart --period=2025-11

# Or using Python directly
cd ~/.claude/skills/agent-smith/
uv run python -u scripts/operations/batch_categorize.py --mode=smart --period=2025-11
```

### Example: Run Health Check

```bash
# Using slash command
/agent-smith-health --full

# Or using Python directly
uv run python -u scripts/health/check.py --full
```

### Example: Generate Tax Report

```bash
# Using slash command
/agent-smith-report tax --period=2024-25 --tax-level=full

# Or using Python directly
uv run python -u scripts/tax/reporting.py --period=2024-25 --level=full
```

### Example: Scenario Analysis

```bash
# Using slash command
/agent-smith-scenario historical "What if I cut dining by 25% last year?"

# Or conversational
/agent-smith
> I'd like to analyze what would happen if I reduced my dining expenses by 25% over the last year
```

## Unified Rule System

Agent Smith uses a YAML-based rule system for categorization:

### Quick Start with Rules

```bash
# 1. Choose a template
uv run python scripts/setup/template_selector.py

# 2. Customize rules in data/rules.yaml

# 3. Test with dry run
uv run python scripts/operations/batch_categorize.py --mode=dry_run --period=2025-11

# 4. Apply to transactions
uv run python scripts/operations/batch_categorize.py --mode=apply --period=2025-11
```

### Example Rule

```yaml
rules:
  # Category rule
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS, COLES, ALDI]
    category: Food & Dining > Groceries
    confidence: 95

  # Label rule
  - type: label
    name: Shared Groceries
    when:
      categories: [Groceries]
      accounts: [Shared Bills]
    labels: [Shared Expense, Essential]
```

## Directory Structure

```
~/.claude/skills/agent-smith/
├── SKILL.md                    # Skill definition (loaded by Claude)
├── .env                        # Your configuration (create from .env.sample)
├── .env.sample                 # Configuration template
├── pyproject.toml              # Python dependencies
├── uv.lock                     # Dependency lock file
│
├── scripts/                    # Python code
│   ├── core/                   # API client, rule engine
│   ├── operations/             # Categorization, batch processing
│   ├── analysis/               # Spending analysis, trends
│   ├── reporting/              # Report generation
│   ├── tax/                    # Tax intelligence (3-tier)
│   ├── scenarios/              # Scenario analysis
│   ├── health/                 # Health check system
│   └── [other modules]
│
├── references/                 # Documentation
│   ├── pocketsmith-api.md      # PocketSmith API reference
│   ├── unified-rules-guide.md  # Rule system documentation
│   ├── onboarding-guide.md     # Setup walkthrough
│   ├── health-check-guide.md   # Health system details
│   └── design.md               # System architecture
│
├── assets/                     # Templates and samples
│   ├── templates/              # Pre-built rule templates
│   ├── .env.sample             # Configuration template
│   └── config.json.sample      # User preferences template
│
└── data/                       # Working data (created on first run)
    ├── config.json             # User preferences
    ├── rules.yaml              # Your categorization rules
    └── [other runtime data]
```

## Troubleshooting

### Skill Not Loading

1. Verify the skill is installed:
   ```bash
   ls -la ~/.claude/skills/agent-smith/
   ```

2. Check SKILL.md exists and has proper frontmatter:
   ```bash
   head -20 ~/.claude/skills/agent-smith/SKILL.md
   ```

3. Restart Claude Code.

### API Errors

1. Verify your API key is set:
   ```bash
   grep POCKETSMITH_API_KEY ~/.claude/skills/agent-smith/.env
   ```

2. Test API connectivity:
   ```bash
   cd ~/.claude/skills/agent-smith/
   uv run python -c "from scripts.core.api_client import PocketSmithClient; client = PocketSmithClient(); print(client.get_user())"
   ```

### Dependency Errors

1. Reinstall dependencies:
   ```bash
   cd ~/.claude/skills/agent-smith/
   uv sync --reinstall
   ```

2. Verify Python version (requires 3.9+):
   ```bash
   python --version
   ```

### Command Not Found

1. Verify slash commands are installed:
   ```bash
   ls ~/.claude/skills/agent-smith/.claude/commands/
   ```

2. Restart Claude Code to reload commands.

## Support & Documentation

- **Complete Documentation**: See `references/` directory
- **Design Specification**: `references/design.md`
- **API Reference**: `references/pocketsmith-api.md`
- **Rule System Guide**: `references/unified-rules-guide.md`
- **Onboarding Guide**: `references/onboarding-guide.md`
- **Health Check Guide**: `references/health-check-guide.md`

## Version History

- **1.3.6** - Complete implementation (all 8 phases)
- **1.0.0** - Initial release

## License

[To be determined]

---

**Note**: Agent Smith is designed for Australian tax compliance (ATO). Adapting for other jurisdictions requires updating tax intelligence modules and reference documentation.

**Get PocketSmith API Key**: https://www.pocketsmith.com/settings/security → Developer API Key
