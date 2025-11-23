# Agent Smith - Complete Design Specification

**Design Date:** 2025-11-20
**Status:** Approved
**Version:** 1.0

---

## Executive Summary

**Agent Smith** is an intelligent financial management skill for Claude Code that provides comprehensive PocketSmith API integration with advanced AI-powered analysis, rule management, tax intelligence, and scenario planning.

**Name Origin:** "Agent Smith" combines the PocketSmith platform reference with the Matrix's AI agent - a fitting metaphor for an intelligent assistant managing your financial matrix.

**Key Value Proposition:**
- Transform PocketSmith from a passive tracking tool into an active financial intelligence system
- Reduce manual financial admin time by 60-80% through intelligent automation
- Provide proactive insights, alerts, and optimization recommendations
- Ensure Australian tax compliance with ATO-aligned intelligence
- Enable sophisticated financial scenario modeling and forecasting

---

## Table of Contents

1. [Core Architecture](#core-architecture)
2. [Directory Structure](#directory-structure)
3. [Hybrid Rule Engine](#hybrid-rule-engine)
4. [Tax Intelligence Module](#tax-intelligence-module)
5. [Scenario Analysis Engine](#scenario-analysis-engine)
6. [Subagent Orchestration](#subagent-orchestration)
7. [Slash Commands](#slash-commands)
8. [Additional Features](#additional-features)
9. [Health Check System](#health-check-system)
10. [Configuration](#configuration)
11. [Implementation Roadmap](#implementation-roadmap)

---

## Core Architecture

### Three-Tier System

**1. API Integration Layer**
- Handles all PocketSmith API communication
- Rate limiting and retry logic
- Response caching (7-day TTL)
- Error handling and fallback strategies
- Automatic backup before mutations

**2. Intelligence Engine**
- **Hybrid Rule Engine:** Platform-native + enhanced local rules
- **Tax Intelligence:** 3-tier system (Reference, Smart, Full)
- **Scenario Analysis:** Historical, projections, optimization, tax planning
- **AI Categorization:** Tiered intelligence modes (Conservative, Smart, Aggressive)
- **Pattern Learning:** Performance tracking and rule evolution

**3. Orchestration Layer**
- Smart subagent conductor
- Decision tree for delegation vs. direct handling
- Parallel processing for bulk operations
- Context preservation in main skill
- Result aggregation and synthesis

### Philosophy

**Hybrid Approach:**
- Quick single-shot operations for simple tasks
- Deep conversational sessions for complex workflows
- User choice: always provide recommended mode but allow override
- Context preservation through intelligent subagent orchestration

**AI Intelligence Levels:**
- **Conservative:** User approval required for all actions
- **Smart:** Auto-apply high-confidence (≥90%), ask for medium (70-89%)
- **Aggressive:** Auto-apply ≥80% confidence, ask for 50-79%
- User can override per operation

---

## Directory Structure

```
~/.claude/skills/agent-smith/
├── agent-smith.md               # Main skill file (invocation point)
├── .env.sample                  # API key configuration template
├── .gitignore                   # Protect sensitive data
├── README.md                    # Skill documentation
├── INDEX.md                     # Master directory index
│
├── ai_docs/                     # Documentation for Claude subagents
│   ├── INDEX.md                 # Document catalog with descriptions
│   ├── pocketsmith-api-documentation.md
│   ├── category-optimization-guide.md
│   ├── ato-tax-guidelines.md
│   ├── rule-engine-architecture.md
│   └── subagent-protocols.md
│
├── backups/                     # Recent backups (30-day retention)
│   ├── INDEX.md                 # Latest backups with descriptions
│   ├── YYYY-MM-DD_HHMMSS/       # Timestamped backup sets
│   └── archive/                 # Older backups (compressed)
│       ├── INDEX.md             # Archived backup catalog
│       └── YYYY-MM/             # Monthly archives (.tar.gz)
│
├── data/                        # Working data & persistent state
│   ├── INDEX.md                 # Current state files & purpose
│   ├── config.json              # User preferences, modes, tax level
│   ├── rule_metadata.json       # Rule tracking & performance metrics
│   ├── platform_rules.json      # PocketSmith native rules created
│   ├── local_rules.json         # Enhanced local rule engine
│   ├── session_state.json       # Current session context
│   ├── alerts/
│   │   ├── alert_rules.json
│   │   ├── alert_history.json
│   │   └── alert_templates.json
│   ├── tax/
│   │   ├── INDEX.md
│   │   ├── ato_category_mappings.json
│   │   ├── deduction_rules.json
│   │   ├── thresholds.json
│   │   ├── cgt_register.json
│   │   └── substantiation_tracking.json
│   ├── scenarios/
│   │   ├── INDEX.md
│   │   ├── saved_scenarios.json
│   │   ├── scenario_templates.json
│   │   └── scenario_results/
│   ├── merchants/
│   │   ├── INDEX.md
│   │   └── merchant_intelligence.json
│   ├── investments/
│   │   ├── INDEX.md
│   │   ├── portfolio.json
│   │   ├── transactions.json
│   │   └── performance.json
│   ├── goals/
│   │   ├── INDEX.md
│   │   └── financial_goals.json
│   ├── health/
│   │   ├── INDEX.md
│   │   ├── health_scores.json
│   │   ├── recommendations.json
│   │   └── health_history/
│   ├── audit/
│   │   ├── INDEX.md
│   │   ├── transaction_changes.log
│   │   ├── category_changes.log
│   │   ├── rule_changes.log
│   │   └── api_activity.log
│   └── cache/                   # API response cache (7-day TTL)
│       ├── INDEX.md             # Cache inventory & freshness
│       └── *.json               # Cached responses
│
├── docs/                        # Generated documentation
│   ├── INDEX.md                 # Recent docs & analyses
│   ├── operations/              # Recent operation logs (30 days)
│   │   ├── INDEX.md             # Operation summaries
│   │   └── YYYY-MM-DD_*.md
│   ├── analyses/                # Recent analysis reports (90 days)
│   │   ├── INDEX.md             # Analysis catalog
│   │   └── *.md
│   ├── guides/                  # User guides (persistent)
│   │   └── INDEX.md
│   └── archive/                 # Older docs (compressed)
│       ├── INDEX.md
│       └── YYYY-MM/
│
├── logs/                        # Execution logs (14 days active)
│   ├── INDEX.md                 # Recent log summary
│   ├── api_calls.log            # API interaction log
│   ├── operations.log           # High-level operations
│   ├── errors.log               # Error tracking
│   └── archive/                 # Compressed historical logs
│       ├── INDEX.md
│       └── YYYY-MM.tar.gz
│
├── reports/                     # Multi-format output (90 days)
│   ├── INDEX.md                 # Recent reports catalog
│   ├── markdown/
│   │   ├── INDEX.md
│   │   └── *.md
│   ├── data/                    # CSV/JSON exports
│   │   ├── INDEX.md
│   │   └── *.{csv,json}
│   ├── interactive/             # HTML dashboards
│   │   ├── INDEX.md
│   │   └── *.html
│   ├── tax/                     # Tax-ready formats (7-year retention)
│   │   ├── INDEX.md
│   │   └── YYYY-*.{pdf,xlsx}
│   └── archive/                 # Older reports
│       ├── INDEX.md
│       └── YYYY-MM/
│
└── scripts/                     # Python utilities & subagent tools
    ├── INDEX.md                 # Script catalog & usage
    ├── core/                    # Core libraries (reusable)
    │   ├── api_client.py        # PocketSmith API wrapper
    │   ├── rule_engine.py       # Hybrid rule system
    │   ├── tax_intelligence.py  # Tax analysis module
    │   ├── scenario_engine.py   # Financial scenarios
    │   └── archiver.py          # Smart archiving engine
    ├── operations/              # Specific operation scripts
    │   ├── INDEX.md
    │   ├── categorize.py
    │   ├── analyze.py
    │   ├── optimize_categories.py
    │   └── generate_reports.py
    ├── subagents/               # Subagent definitions
    │   ├── categorization-agent.md
    │   ├── analysis-agent.md
    │   ├── reporting-agent.md
    │   ├── tax-agent.md
    │   ├── optimization-agent.md
    │   └── scenario-agent.md
    └── utils/                   # Helper utilities
        ├── INDEX.md
        ├── backup.py
        ├── validation.py
        ├── formatters.py
        └── index_updater.py     # Auto-update INDEX.md files
```

### Smart Archiving Strategy

**Retention Policies:**
- **Cache:** 7 days, auto-purge
- **Logs:** 14 days active, then compress to monthly archives
- **Backups:** 30 days recent, then monthly compressed archives
- **Operations docs:** 30 days, then archive
- **Analyses/Reports:** 90 days, then archive
- **Tax reports:** 7 years (ATO requirement)

**Archiving Process:**
- Automatic after operations
- Compresses old files into monthly `.tar.gz` archives
- Updates INDEX.md in archive directories
- Manual archive/restore commands available

**INDEX.md Auto-Update:**
- Every file creation/modification triggers index update
- Contains: filename, creation date, size, description, tags
- Enables LLM to quickly scan without reading all files
- Sorted by relevance (newest first, or by type)

---

## Hybrid Rule Engine

### Architecture

**Two-Tier System:**
1. **Platform Rules** - PocketSmith native (via API)
2. **Local Rules** - Enhanced engine with advanced features

**Platform Rules (PocketSmith Native):**
- Created via API for simple keyword patterns
- **Advantages:** Auto-apply to future transactions server-side
- **Limitations:** Keyword-only matching, no modification/deletion via API
- **Tracking:** Metadata stored in `data/platform_rules.json`

**Local Rules (Enhanced Engine):**
- Stored in `data/local_rules.json`
- **Capabilities:**
  - Regex pattern matching
  - Multi-condition logic (amount ranges, date patterns, account filters)
  - Confidence scoring (0-100%)
  - Priority/precedence management
  - Rule chaining (conditional rules)
  - Negative patterns (exclusions)
  - Statistical learning (accuracy tracking)

### Rule Schema (Local)

```json
{
  "rule_id": "uuid",
  "name": "Woolworths Groceries",
  "type": "local|platform|session",
  "pattern": {
    "payee_regex": "WOOLWORTHS.*",
    "amount_range": {"min": null, "max": null},
    "account_ids": [],
    "date_range": null,
    "excludes": ["WOOLWORTHS PETROL"]
  },
  "action": {
    "category_id": 12345,
    "confidence": 95,
    "requires_approval": false
  },
  "metadata": {
    "created": "2025-11-20",
    "created_by": "user|ai",
    "last_modified": "2025-11-20",
    "priority": 100,
    "tags": ["groceries", "auto-categorize"]
  },
  "performance": {
    "matches": 150,
    "applied": 148,
    "user_overrides": 2,
    "accuracy": 98.67,
    "last_used": "2025-11-19"
  }
}
```

### Intelligence Modes

**1. Conservative Mode:**
- All rules require user approval before applying
- Best for: Initial setup, learning phase, high-stakes categorization

**2. Smart Mode (Default):**
- Auto-apply rules with confidence ≥ 90%
- Ask for approval: 70-89% confidence
- Skip: < 70% confidence
- Best for: Most users, balanced automation

**3. Aggressive Mode:**
- Auto-apply confidence ≥ 80%
- Ask for approval: 50-79% confidence
- Skip: < 50% confidence
- Best for: Experienced users, trusted rule sets

### Session Rules

- Temporary rules for one-off bulk operations
- Stored in `session_state.json`, not persisted by default
- User prompted: "Keep this rule for future use?"
- Useful for: Bulk categorization, experimentation

### Rule Lifecycle

1. **Creation:** AI suggests or user defines
2. **Validation:** Test against historical transactions (dry-run)
3. **Application:** Apply with chosen intelligence mode
4. **Tracking:** Record performance metrics
5. **Evolution:** Suggest refinements based on override patterns
6. **Archival:** Move low-performing rules to review queue

### Platform Sync Strategy

**Decision Logic:**
```python
if rule.is_simple_keyword() and not rule.has_exclusions():
    # Create via PocketSmith API
    create_platform_rule(rule)
    track_in_platform_rules_json(rule)
else:
    # Keep local-only
    store_in_local_rules_json(rule)
```

**Migration Tool:**
- Convert proven local rules to platform rules when possible
- Audit which rules are platform vs. local
- Bulk migration capability

---

## Tax Intelligence Module

### Three-Tier System

**Configuration:**
- Environment variable: `TAX_INTELLIGENCE_LEVEL=reference|smart|full`
- Runtime override: `--tax-level=full`
- Interactive prompt when ambiguous

---

### Level 1: Reference & Reporting

**Capabilities:**
- Generate tax-ready expense summaries by category
- Map PocketSmith categories to ATO expense categories
- Basic GST tracking (GST paid on business purchases)
- Flag potential deductible expenses based on category
- Link to relevant ATO resources and guides
- Simple reports: "You spent $X on deductible categories"

**Output:**
- Factual reporting with resource links
- No advice given
- CSV exports mapped to ATO tax return categories

**Use Case:** Users who have accountants, just need organized data

---

### Level 2: Smart Categorization Assistant

**Everything from Level 1, PLUS:**

**Advanced Detection:**
- Flag transactions likely deductible based on payee patterns
- Suggest expense splitting (mixed personal/business)
- Identify missing documentation requirements
- Track capital gains/losses events (asset purchases/sales)
- Calculate vehicle logbook percentages from fuel/service patterns
- Monitor common deduction thresholds ($300 receipt rule, etc.)
- Detect home office expense patterns
- Flag estimated tax obligations based on income patterns

**Intelligent Suggestions:**
- "This $850 laptop purchase may be instantly deductible"
- "Detected 15 Uber rides to/from work - likely NOT deductible"
- "Mobile phone bill: consider 50/50 split for business deduction"

**Capital Gains Tracking:**
- Detect asset purchase/sale pairs
- Calculate holding periods
- Flag CGT discount eligibility (> 12 months)
- Track cost base adjustments

**Output:** Actionable insights with "consult your accountant" disclaimers

**Use Case:** Most users, proactive tax optimization

---

### Level 3: Full Compliance Suite

**Everything from Levels 1 & 2, PLUS:**

**Comprehensive Tax Management:**

**Deduction Optimization:**
- Track deductions against ATO category limits and guidelines
- Suggest timing optimizations (prepay expenses before EOFY)
- Identify bundling opportunities
- Compare deduction methods (actual vs. standard rates)
- Monitor substantiation requirements by category

**BAS & GST Management:**
- BAS-ready reports (quarterly/monthly)
- GST paid vs. collected tracking
- Input tax credit calculations
- PAYG installment tracking
- BAS reconciliation reports

**Threshold Monitoring:**
- $300 substantiation threshold
- $75 taxi/Uber receipt requirements
- FBT thresholds
- Small business entity thresholds ($10M turnover)
- Instant asset write-off limits (currently $20,000)

**Investment & CGT Intelligence:**
- Comprehensive CGT register
- Cost base tracking (purchase price + incidental costs)
- Dividend tracking (franked/unfranked)
- Foreign income detection
- Cryptocurrency transaction tracking
- Wash sale detection

**Scenario Planning:**
- "Sell investment now vs. after 12 months - tax impact?"
- "Prepay insurance before EOFY - savings?"
- "You're approaching threshold X - implications"

**Compliance Checks:**
- Cross-reference expenses against ATO audit triggers
- Identify unusual patterns
- Verify substantiation completeness
- Generate audit-ready documentation

**Reports Generated:**
- Tax return schedule summaries (D1-D15)
- BAS worksheets
- CGT schedule
- Depreciation schedules
- Home office calculation worksheets
- Vehicle logbook summaries

**Disclaimers:**
- All Level 3 outputs include: "This analysis is for informational purposes. Consult a registered tax agent for advice."
- Flags complex situations requiring professional review

**Use Case:** Power users, small business owners, serious tax optimization

---

### ATO Documentation Caching

**Smart Documentation Strategy:**

**Local Cache Structure:**
```
ai_docs/tax/
├── INDEX.md
├── cache_metadata.json
├── ato_guidelines/
│   ├── motor_vehicle_expenses_2025.md
│   ├── home_office_deductions_2025.md
│   ├── capital_gains_tax_2025.md
│   └── instant_asset_writeoff_2025.md
├── legislation/
│   ├── income_tax_rates_2024-25.json
│   ├── gst_rules.md
│   └── substantiation_requirements.md
└── archived/
    └── YYYY/
```

**Cache Metadata:**
```json
{
  "document_id": "motor_vehicle_expenses_2025",
  "source_url": "https://www.ato.gov.au/...",
  "cached_date": "2025-11-01",
  "last_verified": "2025-11-20",
  "content_hash": "abc123...",
  "refresh_policy": "monthly",
  "expiry_date": "2025-12-01",
  "version": "v2.1",
  "change_log": [
    {
      "date": "2025-11-15",
      "change": "Updated instant asset write-off threshold to $20,000"
    }
  ]
}
```

**Smart Refresh Strategy:**

1. **Automatic Checks:**
   - Monthly refresh of all cached docs
   - Pre-EOFY force refresh (May-June)
   - Post-Budget alert (October)

2. **On-Demand Verification:**
   - Before generating tax reports: check for doc updates
   - Compare cached vs. online versions
   - Highlight changes to user

3. **Integration with Tax Levels:**
   - Level 1: Use cached docs, verify monthly
   - Level 2: Verify before recommendations
   - Level 3: Always verify freshness before compliance operations

**Commands:**
- `refresh-tax-cache` - Force refresh
- `verify-tax-cache` - Check for updates
- `diff-tax-changes` - Show changes since last cache

---

## Scenario Analysis Engine

### Four Scenario Types

**1. Historical Analysis**

**What-If Replays:**
- "What if I had cut dining out by 30% in 2024?"
- "Show impact of eliminating subscription X"
- "What if I had sold investment Y in June vs. December?"

**Trend Analysis:**
- Compare spending across periods (YoY, QoQ, MoM)
- Identify trending categories
- Seasonal pattern detection
- Anomaly detection

**Comparative Scenarios:**
- Actual vs. Budget variance
- Category spending comparisons
- Account-level analysis

---

**2. Future Projections**

**Spending Forecasts:**
- Project based on historical patterns
- Seasonal adjustments
- Account for known upcoming changes
- Confidence intervals (optimistic/pessimistic/realistic)

**Affordability Analysis:**
- "Can I afford a $500/month car payment?"
- "Impact of $15k annual expense on cash flow?"
- Cash flow projections (monthly surplus/deficit)

**Goal Modeling:**
- "Save $20k by Dec 2026 - required monthly savings?"
- "Retire at 60 - monthly savings needed?"
- Investment growth projections

**Algorithm:**
1. Analyze historical patterns (12-24 months)
2. Detect trends (increasing/decreasing categories)
3. Apply seasonal adjustments
4. Factor in inflation (configurable %)
5. Account for known future changes
6. Generate 3 scenarios: conservative/realistic/optimistic
7. Project forward 3/6/12/24 months

---

**3. Optimization Engine**

**AI-Suggested Opportunities:**

**Subscription Analysis:**
- Detect recurring payments
- Identify unused/underutilized subscriptions
- Calculate consolidation savings
- Suggest alternatives

**Category Trend Alerts:**
- Flag categories trending up >10%
- Identify unusual spending patterns
- Compare to peer benchmarks (optional)
- Suggest budget adjustments

**Expense Rationalization:**
- Duplicate service detection
- Identify optimization opportunities
- Bundle opportunities

**Tax Optimization:**
- Prepayment opportunities before EOFY
- Timing of asset sales (CGT optimization)
- Salary sacrifice recommendations
- Deduction maximization strategies

---

**4. Tax Scenario Planning**

**Pre-Purchase Analysis:**
- "Buy $25k equipment now vs. next FY - tax impact?"
- "Instant asset write-off vs. depreciation?"
- "Salary sacrifice $10k to super - net benefit?"

**Income Timing:**
- "Defer $20k invoice to next FY - tax savings?"
- "Bonus timing optimization"
- "Capital gain timing (< or > 12 months)"

**Deduction Optimization:**
- "Prepay 12 months insurance before EOFY - deductible?"
- "Extra super contribution - tax benefit?"
- "Bring forward expenses - impact?"

**CGT Scenarios:**
- "Sell now (8 months held) vs. wait 4 months (CGT discount)"
- "Offset gains with losses - which assets?"
- "Distribute gains across financial years"

---

## Subagent Orchestration

### Orchestration Decision Tree

```python
def should_delegate(operation):
    """Decide if operation should use subagent"""

    # Always delegate
    if operation.type in ['bulk_processing', 'deep_analysis', 'multi_period']:
        return True

    # Check complexity
    if operation.transaction_count > 100:
        return True

    if operation.estimated_tokens > 5000:
        return True

    # Check parallelization opportunity
    if operation.can_parallelize:
        return True

    # Simple queries stay in main context
    return False
```

### Subagent Types

**Specialized Workers:**
- `categorization-agent.md` - Transaction categorization
- `analysis-agent.md` - Financial analysis
- `reporting-agent.md` - Report generation
- `tax-agent.md` - Tax intelligence operations
- `optimization-agent.md` - Category/rule optimization
- `scenario-agent.md` - Scenario modeling

### Processing Patterns

**1. Parallel Processing:**
- Multi-period analysis (12 months → 12 parallel agents)
- Category-wise deep dives (top 5 categories → 5 agents)
- Bulk categorization (500 transactions → 5 batches → 5 agents)

**2. Sequential Delegation:**
- Complex workflows requiring user approval between steps
- Each step's output feeds next step
- Main skill orchestrates and presents results

**3. Smart Context Management:**

**Main Skill Handles:**
- User preferences and configuration
- Session state
- High-level decision making
- User interaction and approvals
- Result aggregation

**Subagents Handle:**
- Large data processing
- API-intensive operations
- Detailed analysis
- Report generation
- Rule application
- Complex calculations

### Communication Protocol

**Delegation Message Format:**
```markdown
You are a specialized {operation_type} agent for Agent Smith.

CONTEXT:
- User: {user_id}
- Operation: {operation_description}
- Intelligence Mode: {conservative|smart|aggressive}
- Tax Level: {reference|smart|full}

DATA:
{relevant_data_subset}

REFERENCES:
- API Documentation: ai_docs/pocketsmith-api-documentation.md
- {operation_specific_docs}

TASK:
{specific_instructions}

OUTPUT FORMAT:
{expected_output_schema}

CONSTRAINTS:
- Dry-run mode: {true|false}
- Maximum API calls: {limit}
- Backup before mutations: {true|false}
```

**Response Format:**
```json
{
  "status": "success|error|partial",
  "operation": "categorization",
  "summary": "Categorized 95/100 transactions",
  "results": {
    "categorized": 95,
    "skipped": 5,
    "rules_applied": 12,
    "new_rules_suggested": 3
  },
  "details": {},
  "errors": [],
  "recommendations": [],
  "next_steps": []
}
```

---

## Slash Commands

### Command Structure

```
.claude/commands/
├── agent-smith.md                      # Installation and onboarding
├── agent-smith-categorize.md           # Transaction categorization
├── agent-smith-analyze.md              # Financial analysis
├── agent-smith-report.md               # Report generation
├── agent-smith-scenario.md             # Scenario modeling
├── agent-smith-optimize.md             # Optimization operations
├── agent-smith-tax.md                  # Tax intelligence
└── agent-smith-health.md               # Health check
```

### Command Definitions

**1. `/agent-smith` - Main Conversational Skill**
```markdown
Start a conversational Agent Smith session for complex multi-step operations.
Use for workflows involving multiple operations or guided assistance.
```

**2. `/agent-smith-categorize [--mode] [--period]`**
```markdown
Categorize uncategorized transactions with AI assistance.

Arguments:
  --mode=conservative|smart|aggressive  Intelligence level (default: smart)
  --period=YYYY-MM                      Target specific month/year
  --account=ID                          Limit to specific account
  --dry-run                             Preview without applying

Examples:
  /agent-smith-categorize
  /agent-smith-categorize --mode=aggressive --period=2025-11
```

**3. `/agent-smith-analyze [type] [--period]`**
```markdown
Run financial analysis on PocketSmith data.

Arguments:
  type: spending|trends|category|tax|insights
  --period=YYYY-MM or YYYY
  --category=ID
  --compare=YYYY-MM
  --tax-level=reference|smart|full

Examples:
  /agent-smith-analyze spending --period=2025
  /agent-smith-analyze trends --compare=2024
```

**4. `/agent-smith-scenario [type] [description]`**
```markdown
Model financial scenarios: what-if, projections, optimization, tax planning.

Arguments:
  type: historical|projection|optimization|tax
  description: Natural language scenario description

Examples:
  /agent-smith-scenario historical "What if I cut dining by 25% last year?"
  /agent-smith-scenario projection "Can I afford $600/month car payment?"
  /agent-smith-scenario tax "Buy $25k equipment before or after EOFY?"
```

**5. `/agent-smith-report [format] [--period]`**
```markdown
Generate comprehensive reports in various formats.

Arguments:
  format: summary|detailed|tax|custom
  --period=YYYY-MM or YYYY
  --output=markdown|csv|json|html|excel|all
  --tax-level=reference|smart|full

Examples:
  /agent-smith-report summary --period=2025-Q4
  /agent-smith-report tax --period=2024-25 --tax-level=full
```

**6. `/agent-smith-optimize [target]`**
```markdown
AI-assisted optimization for categories, rules, or spending.

Arguments:
  target: categories|rules|spending|subscriptions

Examples:
  /agent-smith-optimize categories
  /agent-smith-optimize rules
```

**7. `/agent-smith-tax [operation] [--period]`**
```markdown
Tax-focused analysis, deduction tracking, compliance reporting.

Arguments:
  operation: deductions|cgt|bas|eofy|scenario
  --period=YYYY-YY
  --level=reference|smart|full

Examples:
  /agent-smith-tax deductions --period=2024-25
  /agent-smith-tax eofy
```

**8. `/agent-smith-health [--full]`**
```markdown
Evaluate PocketSmith setup and get optimization recommendations.

Arguments:
  --full                    Complete deep analysis
  --quick                   Fast essential checks
  --category=area           Specific area: categories|rules|tax|data

Examples:
  /agent-smith-health
  /agent-smith-health --full
```

---

## Additional Features

### 1. Smart Alerts & Notifications

**Alert Types:**
- Budget alerts (overspending, trending)
- Tax alerts (thresholds, EOFY deadlines, CGT timing)
- Pattern alerts (new recurring charges, duplicates, unusual transactions)
- Optimization alerts (unused subscriptions, fee increases)

**Scheduling:**
- Weekly spending summary
- Monthly budget review
- Quarterly trend analysis
- EOFY tax prep reminder (May)
- Post-budget cache refresh (October)

### 2. Merchant Intelligence

**Automated Payee Enrichment:**
- Detect payee variations automatically
- Group similar transactions
- Learn from user corrections
- Suggest canonical names

**Merchant Insights:**
- Spending patterns by merchant
- Price trend tracking
- Optimization suggestions

### 3. Receipt & Document Management

**Integration with PocketSmith Attachments:**
- Flag transactions requiring receipts (>$300)
- Track missing documentation
- Generate substantiation reports
- OCR receipt data
- Auto-link receipts to transactions

### 4. Multi-User & Shared Expense Tracking

**Household Finance:**
- Track shared expenses
- Calculate settlement amounts
- Split transactions by custom ratios
- Generate "who owes whom" reports

### 5. Investment Tracking

**Portfolio Integration:**
- Link transactions to investment events
- Track cost basis
- Calculate unrealized gains/losses
- CGT optimization
- Dividend tracking
- Performance vs. benchmarks

### 6. Cash Flow Forecasting

**Intelligent Liquidity Management:**
- Predict future account balances
- Identify potential shortfalls
- Optimize payment timing
- Track recurring payments
- Model major purchase impact

### 7. Goal Tracking

**Financial Goals:**
- Emergency fund
- House deposit
- Debt payoff
- Investment targets
- Retirement savings

**Progress Tracking:**
- Automatic updates
- On-track vs. behind alerts
- Required contribution adjustments
- Milestone celebrations

### 8. Comparative Benchmarking

**Anonymous Peer Comparison (Opt-In):**
- Compare spending to similar households
- Privacy-first (aggregated, anonymized)
- Configurable peer criteria

### 9. Audit Trail

**Complete Activity Log:**
- Every transaction modification
- Category structure changes
- Rule creation/updates
- Bulk operations
- Report generation

**Benefits:**
- "Undo" capability
- Compliance tracking
- Troubleshooting
- Accountability

### 10. Smart Backup & Recovery

**Automated Protection:**
- Before every bulk operation
- Daily automatic backups (if changes made)
- Pre-migration snapshots
- Configurable retention

**Recovery Tools:**
- List backups
- Preview backup contents
- Selective restore
- Full restore
- Diff between backup and current

---

## Health Check System

### Six Health Scores

**1. Data Quality (0-100)**
- Categorization coverage
- Data completeness
- Data consistency

**2. Category Structure (0-100)**
- Hierarchy optimization
- Category usage
- Tax alignment

**3. Rule Engine (0-100)**
- Rule coverage
- Rule quality
- Rule completeness

**4. Tax Readiness (0-100)**
- ATO compliance
- Tax category mapping
- EOFY preparation

**5. Automation & Efficiency (0-100)**
- Agent Smith utilization
- PocketSmith feature usage
- Data entry efficiency

**6. Overall Health**
- Composite of all scores
- Top 3 priorities identified
- Impact projections

### Health Check Output

```
🏥 AGENT SMITH HEALTH CHECK - OVERALL
════════════════════════════════════════

Overall Score: 59/100 (Fair)

Individual Scores:
├─ Data Quality:        72/100  ✅ Good
├─ Category Structure:  58/100  ⚠️ Needs Work
├─ Rule Engine:         45/100  ⚠️ Needs Improvement
├─ Tax Readiness:       68/100  ⚠️ Fair
└─ Automation:          52/100  ⚠️ Moderate

🎯 TOP 3 PRIORITIES:
1. CREATE CATEGORY HIERARCHY (Highest Impact)
2. EXPAND RULE COVERAGE (Quick Win)
3. TAX COMPLIANCE FIXES (Risk Reduction)

After completing: Projected score 96/100
```

### Automated Health Monitoring

**Periodic Checks:**
- Weekly quick health check
- Monthly full health analysis
- Pre-EOFY comprehensive check
- Post-major-operation validation

**Proactive Alerts:**
- Health score changes
- New recommendations
- Declining tax readiness

---

## Configuration

### .env.sample

```bash
# PocketSmith API Authentication
POCKETSMITH_API_KEY=<Your Developer API Key>

# Agent Smith Configuration
TAX_INTELLIGENCE_LEVEL=smart          # reference|smart|full
DEFAULT_INTELLIGENCE_MODE=smart       # conservative|smart|aggressive
AUTO_BACKUP=true
AUTO_ARCHIVE=true
ALERT_NOTIFICATIONS=true

# Tax Configuration (Australia)
TAX_JURISDICTION=AU
FINANCIAL_YEAR_END=06-30             # June 30
GST_REGISTERED=false

# Reporting Preferences
DEFAULT_REPORT_FORMAT=all            # markdown|csv|json|html|excel|all
CURRENCY=AUD

# Advanced
API_RATE_LIMIT_DELAY=100             # ms between calls
CACHE_TTL_DAYS=7
SUBAGENT_MAX_PARALLEL=5
```

### User Preferences (data/config.json)

```json
{
  "user_id": 217031,
  "tax_level": "smart",
  "intelligence_mode": "smart",
  "alerts_enabled": true,
  "alert_preferences": {
    "budget": true,
    "tax": true,
    "patterns": true,
    "optimization": true,
    "frequency": "weekly"
  },
  "backup_before_mutations": true,
  "auto_archive": true,
  "default_report_formats": ["markdown", "csv", "html"],
  "household": {
    "enabled": false,
    "members": [],
    "split_method": "proportional"
  },
  "benchmarking": {
    "enabled": false,
    "criteria": {}
  }
}
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Core Infrastructure:**
- ✅ Directory structure creation
- ✅ .env.sample and configuration files
- ✅ INDEX.md templates for all directories
- ✅ Python core libraries:
  - api_client.py (PocketSmith API wrapper)
  - archiver.py (smart archiving engine)
  - index_updater.py (INDEX.md automation)
  - backup.py (backup/restore utilities)
  - validation.py (data validation)

**Basic Functionality:**
- ✅ API authentication and basic queries
- ✅ Backup/restore system
- ✅ Archiving automation
- ✅ Logging infrastructure

### Phase 2: Rule Engine (Weeks 3-4)

**Hybrid Rule System:**
- ✅ Local rule engine implementation
- ✅ Platform rule tracking
- ✅ Rule performance metrics
- ✅ Intelligence mode implementation
- ✅ Session rules
- ✅ Rule validation and testing

**Categorization:**
- ✅ Basic categorization workflow
- ✅ Batch categorization
- ✅ Rule suggestion engine
- ✅ Merchant normalization

### Phase 3: Analysis & Reporting (Weeks 5-6)

**Analysis Engine:**
- ✅ Spending analysis
- ✅ Trend detection
- ✅ Category analysis
- ✅ Pattern recognition

**Multi-Format Reporting:**
- ✅ Markdown reports
- ✅ CSV/JSON exports
- ✅ HTML dashboards (interactive)
- ✅ Excel generation

### Phase 4: Tax Intelligence (Weeks 7-8)

**3-Tier Tax System:**
- ✅ Level 1: Reference & Reporting
- ✅ Level 2: Smart Categorization Assistant
- ✅ Level 3: Full Compliance Suite

**ATO Integration:**
- ✅ Documentation caching
- ✅ Category mappings
- ✅ Deduction rules
- ✅ CGT register
- ✅ BAS preparation

### Phase 5: Scenario Analysis (Weeks 9-10)

**Scenario Engine:**
- ✅ Historical analysis
- ✅ Future projections
- ✅ Optimization engine
- ✅ Tax scenario planning

**Advanced Analytics:**
- ✅ Cash flow forecasting
- ✅ Goal tracking
- ✅ Investment tracking

### Phase 6: Orchestration & UX (Weeks 11-12)

**Subagent System:**
- ✅ Subagent definitions
- ✅ Orchestration logic
- ✅ Parallel processing
- ✅ Result aggregation

**Slash Commands:**
- ✅ All 8 slash commands
- ✅ Argument parsing
- ✅ Natural language integration
- ✅ Interactive workflows

### Phase 7: Advanced Features (Weeks 13-14)

**Additional Capabilities:**
- ✅ Smart alerts & notifications
- ✅ Merchant intelligence
- ✅ Document management
- ✅ Multi-user support
- ✅ Comparative benchmarking
- ✅ Audit trail

### Phase 8: Health Check & Polish (Weeks 15-16)

**Health Check System:**
- ✅ 6 health scores
- ✅ Recommendation engine
- ✅ Automated monitoring
- ✅ Guided setup workflow

**Polish & Testing:**
- ✅ End-to-end testing
- ✅ Documentation completion
- ✅ Performance optimization
- ✅ User guides

---

## Success Metrics

**Efficiency Gains:**
- Reduce manual categorization time by 60-80%
- Auto-categorization rate: 70%+ (from ~5%)
- Financial admin time: 45 min/week → 10 min/week

**Quality Improvements:**
- Health score: 95/100 average
- Categorization accuracy: 95%+
- Tax compliance score: 90%+

**User Satisfaction:**
- All essential tax documents generated automatically
- Proactive optimization suggestions implemented
- Financial insights delivered weekly
- Zero missed tax deadlines/thresholds

---

## Future Enhancements

**v2.0 Potential Features:**
- Machine learning for transaction categorization
- Integration with other financial platforms
- Mobile app companion
- Real-time alerts via notifications
- Advanced visualizations and dashboards
- Multi-currency support enhancements
- Business expense separation automation
- Integration with accounting software (Xero, MYOB)
- Predictive budget adjustments
- AI financial advisor capabilities

---

**End of Design Document**

**Status:** Ready for implementation
**Next Steps:**
1. Review and approve design
2. Set up git worktree for isolated development
3. Create detailed implementation plan
4. Begin Phase 1: Foundation

---

**Document Version:** 1.0
**Last Updated:** 2025-11-20
**Approved By:** [Pending]
