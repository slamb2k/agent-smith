# Command Architecture Optimization Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign Agent Smith's user experience with two usage modes, eliminate redundancy, and ensure every interaction provides clear next steps.

**Architecture:**
1. **Guided Journey Mode** - SessionStart hook shows status dashboard with suggested actions
2. **Power User Mode** - Streamlined slash commands for direct access
3. All commands delegate to Python scripts and use subagent pattern
4. Every interaction ends with contextual next steps

**Tech Stack:** Python scripts (deterministic), Claude Code slash commands (UX), SessionStart hooks (guided entry), Task tool (subagent delegation)

---

## Part A: Redundancy & Discoverability Analysis

### Feature Overlap (Current State)

| Feature | Found In | Problem |
|---------|----------|---------|
| Tax analysis | `/smith:tax`, `/smith:analyze tax`, `/smith:scenario tax` | 3 entry points for same thing |
| Spending trends | `/smith:analyze trends`, `/smith:scenario historical`, `/smith:report` | Fragmented |
| Rule optimization | `/smith:optimize rules`, `/smith:categorize` (offers rule learning) | Duplicated |
| Category analysis | `/smith:health`, `/smith:analyze category`, `/smith:optimize categories` | 3 places |
| Subscription tracking | `/smith:optimize subscriptions`, `/smith:scenario optimization` | 2 places |

### Discoverability Issues

1. **No guided entry point** - Users don't know where to start after install
2. **No status dashboard** - Users can't see current state at a glance
3. **9 commands** - Too many for users to remember/choose between
4. **No "what can I do?"** - Features buried in documentation
5. **Missing next steps** - Commands end without guidance

### Proposed Command Consolidation

**BEFORE (9 commands):**
```
/smith:install        - Onboarding
/smith:categorize     - Categorization
/smith:review-conflicts - Conflict review
/smith:health         - Health check
/smith:analyze        - Analysis (spending, trends, category, tax, insights)
/smith:scenario       - Scenarios (historical, projection, optimization, tax)
/smith:report         - Reports (summary, detailed, tax, custom)
/smith:optimize       - Optimize (categories, rules, spending, subscriptions)
/smith:tax            - Tax (deductions, cgt, bas, eofy, scenario)
```

**AFTER (6 commands + guided skill):**
```
Agent Smith Skill     - 🆕 GUIDED JOURNEY (SessionStart dashboard + conversational)
/smith:install        - Onboarding (keep as-is)
/smith:categorize     - Categorization (keep, add next steps)
/smith:review-conflicts - Conflict review (keep, reference implementation)
/smith:health         - Health check (keep, add next steps)
/smith:insights       - 🔄 MERGED: analyze + scenario + report
/smith:tax            - Tax operations (keep, consolidate tax features here)
```

**Removed/Merged:**
- `/smith:analyze` → merged into `/smith:insights`
- `/smith:scenario` → merged into `/smith:insights`
- `/smith:report` → merged into `/smith:insights`
- `/smith:optimize` → split: rules→categorize, categories→health, spending→insights

---

## Part B: Two Usage Modes

### Mode 1: Guided Journey (Default)

**Trigger:** SessionStart hook OR invoking Agent Smith skill directly

**Experience:**
```
═══════════════════════════════════════════════════════════════
                    🤖 AGENT SMITH
              Your Financial Intelligence Assistant
═══════════════════════════════════════════════════════════════

📊 CURRENT STATUS
─────────────────────────────────────────────────────────────────
  Health Score: 🟢 87/100 (Good)
  Uncategorized: 12 transactions (last 7 days)
  Last Activity: Categorized 45 transactions (2 days ago)

🎯 SUGGESTED NEXT STEPS
─────────────────────────────────────────────────────────────────
  1. Categorize 12 new transactions
     → Say "categorize my transactions" or /smith:categorize

  2. Review 3 flagged conflicts
     → Say "review conflicts" or /smith:review-conflicts

  3. EOFY is in 6 months - start tax planning
     → Say "show my tax deductions" or /smith:tax deductions

💡 WHAT CAN I HELP WITH?
─────────────────────────────────────────────────────────────────
  • "Categorize my transactions"
  • "Show my spending this month"
  • "How's my financial health?"
  • "What are my tax deductions?"
  • "Show me insights"

  Power users: Type /smith: to see all commands
═══════════════════════════════════════════════════════════════
```

### Mode 2: Power User (Slash Commands)

**Trigger:** Direct `/smith:*` command invocation

**Experience:** Streamlined execution with:
- Clear argument hints
- Real-time progress feedback
- Results summary
- **ALWAYS** contextual next steps

---

## Part C: Principle Compliance Assessment

| Command | Principle Violations | Priority |
|---------|---------------------|----------|
| `/smith:categorize` | P1 (embeds Python), P2 (duplicates script), P6 (no subagent) | **CRITICAL** |
| `/smith:health` | P1 (no script call), P5 (no feedback), P6 (no subagent) | HIGH |
| `/smith:analyze` | Redundant - merge into insights | HIGH |
| `/smith:scenario` | Redundant - merge into insights | HIGH |
| `/smith:report` | Redundant - merge into insights | MEDIUM |
| `/smith:optimize` | Redundant - split into other commands | MEDIUM |
| `/smith:tax` | P1 (no script call), P5 (no feedback), P6 (no subagent) | MEDIUM |
| `/smith:install` | P6 (no subagent for heavy stages) | LOW |
| `/smith:review-conflicts` | None - **REFERENCE IMPLEMENTATION** | DONE |

---

## Task 0: Create Guided Journey (SessionStart Hook + Status Dashboard)

**Priority:** HIGH - This is the primary user experience improvement

**Files:**
- Create: `scripts/status/dashboard.py` - Generate status dashboard data
- Create: `agent-smith-plugin/hooks/session-start.md` - SessionStart hook
- Modify: `agent-smith-plugin/skills/agent-smith/SKILL.md` - Add guided journey instructions

**Step 1: Create the status dashboard script**

Create `scripts/status/dashboard.py`:

```python
#!/usr/bin/env python3
"""Generate Agent Smith status dashboard data."""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

def get_status_summary() -> Dict[str, Any]:
    """Gather current status from PocketSmith and local state."""
    from scripts.core.api_client import PocketSmithClient

    client = PocketSmithClient()
    user = client.get_user()

    # Get recent transactions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    transactions = client.get_transactions(
        user_id=user["id"],
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    )

    # Count uncategorized
    uncategorized = [t for t in transactions if not t.get("category")]

    # Count conflicts (transactions with review labels)
    conflicts = [t for t in transactions
                 if any("Review" in (l or "") for l in (t.get("labels") or []))]

    # Get health score (cached if available)
    health_score = _get_cached_health_score()

    # Check for tax deadlines
    tax_alerts = _check_tax_deadlines()

    return {
        "health_score": health_score,
        "uncategorized_count": len(uncategorized),
        "uncategorized_days": 7,
        "conflict_count": len(conflicts),
        "tax_alerts": tax_alerts,
        "last_activity": _get_last_activity(),
        "suggestions": _generate_suggestions(
            uncategorized_count=len(uncategorized),
            conflict_count=len(conflicts),
            health_score=health_score,
            tax_alerts=tax_alerts,
        ),
    }

def _get_cached_health_score() -> Dict[str, Any]:
    """Get cached health score or return unknown."""
    # Implementation reads from data/health_cache.json
    return {"score": None, "status": "unknown"}

def _check_tax_deadlines() -> list:
    """Check for upcoming tax deadlines."""
    alerts = []
    today = datetime.now()
    eofy = datetime(today.year if today.month <= 6 else today.year + 1, 6, 30)
    days_to_eofy = (eofy - today).days

    if days_to_eofy <= 180:
        alerts.append({
            "type": "eofy",
            "message": f"EOFY in {days_to_eofy} days - start tax planning",
            "priority": "medium" if days_to_eofy > 60 else "high"
        })
    return alerts

def _get_last_activity() -> Dict[str, Any]:
    """Get last Agent Smith activity."""
    # Read from data/activity_log.json
    return {"action": None, "date": None}

def _generate_suggestions(
    uncategorized_count: int,
    conflict_count: int,
    health_score: Dict,
    tax_alerts: list,
) -> list:
    """Generate prioritized suggestions based on current state."""
    suggestions = []

    if uncategorized_count > 0:
        suggestions.append({
            "priority": 1,
            "title": f"Categorize {uncategorized_count} new transactions",
            "natural": "categorize my transactions",
            "command": "/smith:categorize",
        })

    if conflict_count > 0:
        suggestions.append({
            "priority": 2,
            "title": f"Review {conflict_count} flagged conflicts",
            "natural": "review conflicts",
            "command": "/smith:review-conflicts",
        })

    if health_score.get("score") is None:
        suggestions.append({
            "priority": 3,
            "title": "Run health check to see your financial score",
            "natural": "check my financial health",
            "command": "/smith:health",
        })

    for alert in tax_alerts:
        suggestions.append({
            "priority": 4,
            "title": alert["message"],
            "natural": "show my tax deductions",
            "command": "/smith:tax deductions",
        })

    return sorted(suggestions, key=lambda x: x["priority"])[:3]

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", choices=["json", "formatted"], default="json")
    args = parser.parse_args()

    status = get_status_summary()

    if args.output == "json":
        print(json.dumps(status, indent=2, default=str))
    else:
        _print_formatted(status)

    return 0

def _print_formatted(status: Dict[str, Any]) -> None:
    """Print formatted dashboard."""
    print("═" * 63)
    print("                    🤖 AGENT SMITH")
    print("              Your Financial Intelligence Assistant")
    print("═" * 63)
    print()
    print("📊 CURRENT STATUS")
    print("─" * 63)

    hs = status.get("health_score", {})
    if hs.get("score"):
        emoji = "🟢" if hs["score"] >= 70 else "🟡" if hs["score"] >= 50 else "🔴"
        print(f"  Health Score: {emoji} {hs['score']}/100 ({hs.get('status', 'Unknown')})")
    else:
        print("  Health Score: ⚪ Not yet checked")

    uc = status.get("uncategorized_count", 0)
    if uc > 0:
        print(f"  Uncategorized: {uc} transactions (last {status.get('uncategorized_days', 7)} days)")
    else:
        print("  Uncategorized: ✅ All caught up!")

    la = status.get("last_activity", {})
    if la.get("action"):
        print(f"  Last Activity: {la['action']} ({la.get('date', 'recently')})")
    print()

    suggestions = status.get("suggestions", [])
    if suggestions:
        print("🎯 SUGGESTED NEXT STEPS")
        print("─" * 63)
        for i, s in enumerate(suggestions, 1):
            print(f"  {i}. {s['title']}")
            print(f"     → Say \"{s['natural']}\" or {s['command']}")
            print()

    print("💡 WHAT CAN I HELP WITH?")
    print("─" * 63)
    print('  • "Categorize my transactions"')
    print('  • "Show my spending this month"')
    print('  • "How\'s my financial health?"')
    print('  • "What are my tax deductions?"')
    print('  • "Show me insights"')
    print()
    print("  Power users: Type /smith: to see all commands")
    print("═" * 63)

if __name__ == "__main__":
    sys.exit(main())
```

**Step 2: Create SessionStart hook**

Create `agent-smith-plugin/hooks/session-start.md`:

```markdown
---
name: agent-smith-session-start
description: Display Agent Smith status dashboard on session start
event: session-start
---

# Agent Smith Session Start

When a new Claude Code session starts, provide a quick status overview.

## Execution

Run the status dashboard script to gather current state:

\`\`\`bash
uv run python -u scripts/status/dashboard.py --output formatted
\`\`\`

If the script fails (e.g., no API key configured), show a welcome message instead:

\`\`\`
═══════════════════════════════════════════════════════════════
                    🤖 AGENT SMITH
              Your Financial Intelligence Assistant
═══════════════════════════════════════════════════════════════

Welcome! To get started:
  → Run /smith:install to set up your PocketSmith connection

Need help? Ask me anything about your finances!
═══════════════════════════════════════════════════════════════
\`\`\`
```

**Step 3: Update SKILL.md with guided journey instructions**

Add section to SKILL.md explaining the two usage modes.

**Step 4: Create tests**

Run: `uv run pytest tests/unit/test_status_dashboard.py -v`

**Step 5: Commit**

```bash
git add scripts/status/dashboard.py agent-smith-plugin/hooks/session-start.md
git commit -m "feat: Add guided journey with SessionStart dashboard

- Create status dashboard script showing health, uncategorized, conflicts
- Add SessionStart hook for automatic status on session start
- Generate contextual suggestions based on current state
- Support both formatted and JSON output"
```

---

## Task 1: Fix Critical - Refactor `/smith:categorize`

**Files:**
- Modify: `agent-smith-plugin/commands/categorize.md`
- Reference: `scripts/operations/categorize_batch.py` (already exists)

**Step 1: Read the current categorize command**

Run: Read `agent-smith-plugin/commands/categorize.md`

**Step 2: Create the new command structure**

Replace the entire file with this content:

```markdown
---
name: smith:categorize
description: Categorize uncategorized transactions using the hybrid rule + LLM workflow
argument-hints:
  - "[--period=YYYY-MM|last-30-days] [--mode=conservative|smart|aggressive] [--dry-run]"
---

# Transaction Categorization

Categorize uncategorized transactions using Agent Smith's hybrid rule + LLM workflow.

## Goal

Automatically categorize transactions using rules first, then AI for unmatched items.

## Why This Matters

Uncategorized transactions reduce financial visibility, make reporting inaccurate, and lower your health score. Regular categorization keeps your finances organized.

## Execution

**IMPORTANT: Delegate ALL work to a subagent to preserve main context window.**

Use the Task tool with `subagent_type: "general-purpose"` to execute the categorization workflow:

### Subagent Prompt

```
You are the Agent Smith categorization assistant. Execute this workflow:

## Step 1: Gather Parameters

Ask the user (using AskUserQuestion) for:
1. **Period**: "2025-11" or "last-30-days" (default: current month)
2. **Mode**: conservative/smart/aggressive (default: smart)
3. **Dry-run**: Preview only or apply changes (default: dry-run first)

## Step 2: Run Categorization

Execute the Python script with user's parameters:

\`\`\`bash
uv run python -u scripts/operations/categorize_batch.py \
  --period [PERIOD] \
  --mode [MODE] \
  [--dry-run if selected]
\`\`\`

Stream the output to show real-time progress.

## Step 3: Present Results

Parse the script output and present:
- Total transactions processed
- Rule matches vs LLM fallbacks
- Auto-applied vs needs-review counts
- Any errors encountered

## Step 4: Offer Next Steps

Based on results, suggest:
- If conflicts found: "Review flagged transactions: /smith:review-conflicts"
- If many LLM matches: "These patterns could become rules - run /smith:optimize rules"
- Always: "Check your health score: /smith:health"

## Visual Style

Use emojis for status: ✅ success, ⏳ processing, ⚠️ warning, ❌ error
Show progress: [23/100] Processing...
Use tables for results summary
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--period` | Month (YYYY-MM) or "last-30-days" | Current month |
| `--mode` | Intelligence mode | smart |
| `--dry-run` | Preview without applying | false |

## Intelligence Modes

| Mode | Auto-Apply Threshold | Best For |
|------|---------------------|----------|
| **conservative** | Never (all manual) | First-time users, sensitive data |
| **smart** | 90%+ confidence | Regular use (recommended) |
| **aggressive** | 80%+ confidence | Trusted rules, bulk processing |

## Next Steps After Categorization

- **Review conflicts**: `/smith:review-conflicts`
- **Check health**: `/smith:health --quick`
- **Create rules from patterns**: `/smith:optimize rules --learn`
```

**Step 3: Verify the file was created correctly**

Run: `head -50 agent-smith-plugin/commands/categorize.md`

**Step 4: Run dev-sync to update plugin**

Run: `./scripts/dev-sync.sh`

**Step 5: Commit**

```bash
git add agent-smith-plugin/commands/categorize.md
git commit -m "refactor: Rewrite /smith:categorize to use scripts and subagent delegation

- Remove embedded Python code (was 90+ lines violating determinism principle)
- Delegate to existing categorize_batch.py script
- Add subagent delegation for context preservation
- Follow guided workflow pattern (Goal/Why/Steps/Next Steps)
- Add visual style guidelines"
```

---

## Task 2: Implement `/smith:health` Command

**Files:**
- Modify: `agent-smith-plugin/commands/health.md`
- Reference: `scripts/health/check.py` (already exists)

**Step 1: Read the current health command**

Run: Read `agent-smith-plugin/commands/health.md`

**Step 2: Create the new command with implementation**

Replace with this content:

```markdown
---
name: smith:health
description: Evaluate your PocketSmith setup and get optimization recommendations
argument-hints:
  - "[--full|--quick] [--category=categories|rules|tax|data]"
---

# PocketSmith Health Check

Evaluate your financial setup and get actionable optimization recommendations.

## Goal

Assess the health of your PocketSmith configuration across 6 dimensions and identify improvement opportunities.

## Why This Matters

A healthy financial setup means accurate reports, effective tax tracking, and reliable categorization. Regular health checks catch issues before they become problems.

## Execution

**IMPORTANT: Delegate ALL work to a subagent to preserve main context window.**

Use the Task tool with `subagent_type: "general-purpose"` to execute the health check:

### Subagent Prompt

```
You are the Agent Smith health check assistant. Execute this workflow:

## Step 1: Determine Check Type

Parse arguments to determine:
- `--full`: Complete analysis (default)
- `--quick`: Essential checks only
- `--category=X`: Focus on specific area

If no arguments, ask user using AskUserQuestion:
- Quick check (30 seconds) or Full analysis (2-3 minutes)?

## Step 2: Run Health Check

Execute the health check script:

\`\`\`bash
uv run python -u scripts/health/check.py [--quick|--full] [--category=CATEGORY]
\`\`\`

Stream the output to show real-time progress.

## Step 3: Present Results

The script outputs a comprehensive report. Present it with:
- Overall health score (0-100) with emoji indicator
- Individual dimension scores
- Top 3 priority recommendations
- Quick wins vs long-term improvements

## Step 4: Offer Next Steps

Based on results:
- Low data quality? → "/smith:categorize to fix uncategorized transactions"
- Low rule coverage? → "/smith:optimize rules to improve automation"
- Tax compliance issues? → "/smith:tax deductions to review"

## Visual Style

Health Score Display:
- 90-100: 🟢 Excellent
- 70-89: 🟡 Good
- 50-69: 🟠 Fair
- Below 50: 🔴 Poor

Use ASCII progress bars for dimension scores:
Data Quality: ████████░░ 80%
```

## Health Dimensions

| Dimension | Weight | Checks |
|-----------|--------|--------|
| **Data Quality** | 25% | Uncategorized %, duplicates, missing payees |
| **Rule Coverage** | 20% | Auto-categorization rate, rule accuracy |
| **Category Health** | 15% | Structure, hierarchy, unused categories |
| **Tax Compliance** | 15% | Deduction tracking, substantiation |
| **Budget Alignment** | 15% | Spending vs goals, trending |
| **Account Health** | 10% | Connections, reconciliation |

## Score Interpretation

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | Excellent | Maintain current practices |
| 70-89 | Good | Minor improvements available |
| 50-69 | Fair | Several issues to address |
| <50 | Poor | Significant work needed |

## Next Steps

- **Improve categorization**: `/smith:categorize`
- **Optimize rules**: `/smith:optimize rules`
- **Review tax setup**: `/smith:tax deductions`
```

**Step 3: Commit**

```bash
git add agent-smith-plugin/commands/health.md
git commit -m "feat: Implement /smith:health with script integration and subagent

- Add actual implementation calling scripts/health/check.py
- Add subagent delegation for context preservation
- Follow guided workflow pattern
- Add visual style guidelines for health scores"
```

---

## Task 3: Create Unified `/smith:insights` Command (Consolidation)

**Priority:** HIGH - Eliminates redundancy, improves discoverability

**Rationale:** `/smith:analyze`, `/smith:scenario`, `/smith:report`, and parts of `/smith:optimize` have significant overlap. Consolidating into `/smith:insights` provides a single entry point for all financial intelligence.

**Files:**
- Create: `agent-smith-plugin/commands/insights.md` - NEW unified command
- Delete: `agent-smith-plugin/commands/analyze.md` - Merged into insights
- Delete: `agent-smith-plugin/commands/scenario.md` - Merged into insights
- Delete: `agent-smith-plugin/commands/report.md` - Merged into insights
- Delete: `agent-smith-plugin/commands/optimize.md` - Split into other commands
- Reference: `scripts/analysis/`, `scripts/scenarios/`, `scripts/reporting/`

**Step 1: Create the unified insights command**

Create `agent-smith-plugin/commands/insights.md`:

```markdown
---
name: smith:insights
description: Financial insights - spending analysis, scenarios, trends, and reports
argument-hints:
  - "<spending|trends|scenario|report> [options]"
  - "spending [--period=YYYY-MM] [--category=NAME]"
  - "trends [--period=YYYY] [--compare=PERIOD]"
  - "scenario \"<what-if description>\""
  - "report [--format=summary|detailed|tax] [--output=markdown|csv|excel]"
---

# Financial Insights

Get comprehensive insights into your finances - spending analysis, trends, what-if scenarios, and reports.

## Goal

Understand your financial patterns and make informed decisions with data-driven insights.

## Why This Matters

Regular financial analysis reveals spending patterns, identifies optimization opportunities, and helps you plan for the future.

## Execution

**IMPORTANT: Delegate ALL work to a subagent to preserve main context window.**

Use the Task tool with `subagent_type: "general-purpose"` to execute the insights workflow:

### Subagent Prompt

\`\`\`
You are the Agent Smith insights assistant. Execute this workflow:

## Step 1: Determine Insight Type

Parse the command to determine which insight type:
- `spending` - Spending breakdown by category and merchant
- `trends` - Month-over-month and year-over-year trends
- `scenario` - What-if analysis (e.g., "What if I cut dining by 30%?")
- `report` - Generate formatted reports

If no type specified, ask using AskUserQuestion.

## Step 2: Run Analysis

Based on insight type, call the appropriate script:

**Spending Analysis:**
\`\`\`bash
uv run python -u scripts/analysis/spending.py --period [PERIOD] --category [CATEGORY]
\`\`\`

**Trend Analysis:**
\`\`\`bash
uv run python -u scripts/scenarios/historical.py --period [PERIOD] --compare [COMPARE]
\`\`\`

**Scenario Analysis:**
\`\`\`bash
uv run python -u scripts/scenarios/projections.py --scenario "[DESCRIPTION]"
\`\`\`

**Report Generation:**
\`\`\`bash
uv run python -u scripts/reporting/generate.py --format [FORMAT] --output [OUTPUT]
\`\`\`

## Step 3: Present Results

Present insights with:
- Key findings summary
- Visual charts/tables where appropriate
- Actionable recommendations

## Step 4: Offer Next Steps

Based on results:
- High spending category? → "Set a budget alert with /smith:health"
- Subscription costs? → "Review your subscriptions: /smith:insights spending --category=Subscriptions"
- Tax insights? → "Deep dive with /smith:tax deductions"
- Want to act? → "Categorize new transactions: /smith:categorize"

## Visual Style

Use tables for spending breakdowns.
Use ASCII bars for comparisons.
Use emojis for trends: 📈 up, 📉 down, ➡️ stable
\`\`\`

## Insight Types

| Type | Description | Example |
|------|-------------|---------|
| `spending` | Spending breakdown | `/smith:insights spending --period=2025-11` |
| `trends` | Historical trends | `/smith:insights trends --compare=2024` |
| `scenario` | What-if analysis | `/smith:insights scenario "cut dining 30%"` |
| `report` | Generate reports | `/smith:insights report --format=summary` |

## Options

| Option | Description | Applies To |
|--------|-------------|------------|
| `--period` | Time period (YYYY-MM, YYYY, YYYY-Q#) | spending, trends, report |
| `--category` | Focus on specific category | spending |
| `--compare` | Compare with another period | trends |
| `--format` | Report format (summary, detailed, tax) | report |
| `--output` | Output format (markdown, csv, excel) | report |

## Examples

\`\`\`bash
# This month's spending by category
/smith:insights spending

# Year-over-year comparison
/smith:insights trends --period=2025 --compare=2024

# What-if scenario
/smith:insights scenario "What if I reduced dining by 25%?"

# Generate tax report
/smith:insights report --format=tax --output=excel
\`\`\`

## Next Steps

After viewing insights:
- **Take action**: `/smith:categorize` to process new transactions
- **Deep dive tax**: `/smith:tax deductions` for tax-specific analysis
- **Check health**: `/smith:health` for overall financial health
```

**Step 2: Delete redundant commands**

```bash
rm agent-smith-plugin/commands/analyze.md
rm agent-smith-plugin/commands/scenario.md
rm agent-smith-plugin/commands/report.md
rm agent-smith-plugin/commands/optimize.md
```

**Step 3: Update command references**

Search and update any references to old commands in:
- SKILL.md
- install.md
- Other command files

**Step 4: Commit**

```bash
git add -A
git commit -m "feat: Consolidate analyze/scenario/report/optimize into /smith:insights

BREAKING: Removes 4 redundant commands, replaces with unified /smith:insights

Removed commands:
- /smith:analyze → use /smith:insights spending|trends
- /smith:scenario → use /smith:insights scenario
- /smith:report → use /smith:insights report
- /smith:optimize → split: rules→categorize, categories→health, spending→insights

Benefits:
- Single entry point for financial intelligence
- No more confusion about which command to use
- Cleaner, more discoverable feature set"
```

---

## Task 4: Update `/smith:categorize` with Rule Learning (from optimize)

**Priority:** MEDIUM - Absorbs rule optimization features from deleted /smith:optimize

**Files:**
- Modify: `agent-smith-plugin/commands/categorize.md`

**Step 1: Add rule learning capability**

After categorization completes, if LLM patterns were detected, offer to create rules:

Add to the categorize command's "Step 4" section:

```markdown
## Step 4: Offer Rule Learning

If LLM successfully categorized transactions with high confidence patterns:

"I noticed these patterns could become rules:
1. 'NETFLIX' → Entertainment (5 matches, 95% confidence)
2. 'UBER EATS' → Dining Out (3 matches, 92% confidence)

Would you like to create rules for any of these? This will auto-categorize similar transactions in the future."

If user agrees, call:
\`\`\`bash
uv run python -u scripts/operations/create_rule.py "[PATTERN]" --category "[CATEGORY]" --confidence [SCORE]
\`\`\`
```

**Step 2: Commit**

```bash
git add agent-smith-plugin/commands/categorize.md
git commit -m "feat: Add rule learning to /smith:categorize (from optimize)"
```

---

## Task 5: Update `/smith:health` with Category Optimization (from optimize)

**Priority:** MEDIUM - Absorbs category optimization features from deleted /smith:optimize

**Files:**
- Modify: `agent-smith-plugin/commands/health.md`

**Step 1: Add category optimization recommendations**

The health check already analyzes categories. Enhance the recommendations section to include:
- Unused category consolidation suggestions
- Category hierarchy improvements
- ATO alignment recommendations

These were previously in `/smith:optimize categories`.

**Step 2: Commit**

```bash
git add agent-smith-plugin/commands/health.md
git commit -m "feat: Add category optimization to /smith:health (from optimize)"
```

---

## Task 6: Implement `/smith:tax` Command

**Priority:** MEDIUM - Consolidate all tax features here (removed from other commands)

**Files:**
- Modify: `agent-smith-plugin/commands/tax.md`
- Reference: `scripts/tax/deduction_detector.py`, `scripts/tax/cgt_tracker.py`, `scripts/tax/bas_preparation.py`

**Step 1: Create the new command with full implementation**

Replace with content that:
- Delegates to subagent
- Routes to appropriate tax script based on operation
- Follows guided workflow pattern (Goal/Why/Steps/Next Steps)
- Includes required tax disclaimers for Level 3
- Consolidates all tax functionality (previously split across tax, analyze tax, scenario tax)

**Step 2: Commit**

```bash
git add agent-smith-plugin/commands/tax.md
git commit -m "feat: Implement /smith:tax with script integration and subagent

Consolidates all tax features:
- Deduction tracking
- CGT analysis
- BAS preparation
- EOFY checklist
- Tax scenarios"
```

---

## Task 7: Enhance `/smith:install` with Subagent Delegation

**Priority:** LOW - Already works, this is an optimization

**Files:**
- Modify: `agent-smith-plugin/commands/install.md`

**Step 1: Identify heavy stages that should delegate**

Review install.md and identify stages with:
- Multiple script calls
- Long-running operations
- Heavy data processing

Candidates: Stage 2 (Discovery), Stage 4 (Template Application), Stage 6 (Categorization)

**Step 2: Add subagent delegation for heavy stages**

Wrap heavy stages in subagent delegation pattern.

**Step 3: Commit**

```bash
git add agent-smith-plugin/commands/install.md
git commit -m "refactor: Add subagent delegation to heavy install stages"
```

---

## Task 8: Clean Up Unused Scripts

**Files:**
- Delete: `scripts/categorize.py` (superseded by `operations/categorize_batch.py`)
- Delete: `scripts/operations/review_conflicts.py` (superseded by current workflow)
- Delete: `scripts/operations/review_conflicts_v2.py` (superseded)
- Delete: `scripts/test_visualizer.py` (debug utility)
- Delete: `scripts/operations/setup_paypal_test.py` (test utility)

**Step 1: Verify scripts are truly unused**

Run: `grep -r "categorize.py" agent-smith-plugin/` (should find nothing referencing the old script)

**Step 2: Delete unused scripts**

```bash
rm scripts/categorize.py
rm scripts/operations/review_conflicts.py
rm scripts/operations/review_conflicts_v2.py
rm scripts/test_visualizer.py
rm scripts/operations/setup_paypal_test.py
```

**Step 3: Run tests to ensure nothing breaks**

Run: `uv run pytest tests/ -v`

**Step 4: Commit**

```bash
git add -A
git commit -m "chore: Remove deprecated and unused scripts

- scripts/categorize.py (use operations/categorize_batch.py)
- scripts/operations/review_conflicts.py (superseded by current workflow)
- scripts/operations/review_conflicts_v2.py (superseded)
- scripts/test_visualizer.py (debug utility)
- scripts/operations/setup_paypal_test.py (test utility)"
```

---

## Task 9: Update SKILL.md with New Patterns

**Files:**
- Modify: `agent-smith-plugin/skills/agent-smith/SKILL.md`

**Step 1: Review current SKILL.md**

Run: Read `agent-smith-plugin/skills/agent-smith/SKILL.md`

**Step 2: Add section on command patterns**

Add documentation explaining:
- How commands delegate to scripts
- When to use subagents
- Guided workflow pattern
- Visual style guidelines

**Step 3: Commit**

```bash
git add agent-smith-plugin/skills/agent-smith/SKILL.md
git commit -m "docs: Add command architecture patterns to SKILL.md"
```

---

## Task 10: Final Validation and Documentation

**Step 1: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All tests pass

**Step 2: Run dev-sync**

Run: `./scripts/dev-sync.sh`

**Step 3: Test each command manually**

Test: `/smith:health --quick`
Test: `/smith:categorize --dry-run`
Test: `/smith:analyze spending`

**Step 4: Update README if needed**

If any command signatures changed, update README.md

**Step 5: Final commit**

```bash
git add -A
git commit -m "docs: Complete command architecture optimization

All commands now:
- Use deterministic Python scripts for data operations
- Delegate to subagents for context preservation
- Follow guided workflow pattern (Goal/Why/Steps/Next Steps)
- Provide real-time feedback during execution
- Suggest appropriate next steps"
```

---

## Verification Checklist

### Principle Compliance

| Principle | Verification |
|-----------|--------------|
| P1: Determinism | No embedded Python in commands, all ops via scripts |
| P2: Code Reuse | Commands call existing scripts, no duplication |
| P3: TDD | All new scripts have tests |
| P4: Separation | Commands = UX, Scripts = Logic |
| P5: Real-Time Feedback | Scripts use `-u` flag, stream progress |
| P6: Context Management | Heavy ops delegate to subagents |

### UX Guidelines

| Guideline | Verification |
|-----------|--------------|
| Guided Workflow | Goal/Why/Steps/Summary/Next Steps present |
| Visual Elements | Emojis, progress bars, tables used appropriately |
| Frontmatter | description and argument-hints defined |
| Error Handling | Helpful messages with suggestions |
| **ALWAYS Next Steps** | Every command ends with contextual suggestions |

### Dual-Mode Experience

| Mode | Verification |
|------|--------------|
| **Guided Journey** | SessionStart hook shows status dashboard |
| | Dashboard includes: health score, uncategorized count, conflicts |
| | Dashboard shows: suggested next steps with natural language AND command |
| | Dashboard shows: "What can I help with?" examples |
| **Power User** | All commands have clear argument-hints |
| | Commands execute without prompts when args provided |
| | Commands still end with next steps |

### Command Consolidation

| Before | After | Verification |
|--------|-------|--------------|
| `/smith:analyze` | `/smith:insights spending\|trends` | Old command removed |
| `/smith:scenario` | `/smith:insights scenario` | Old command removed |
| `/smith:report` | `/smith:insights report` | Old command removed |
| `/smith:optimize categories` | `/smith:health` | Feature absorbed |
| `/smith:optimize rules` | `/smith:categorize` | Feature absorbed |
| `/smith:optimize spending` | `/smith:insights spending` | Feature absorbed |

### Final Command Set (6 commands)

| Command | Status |
|---------|--------|
| `/smith:install` | ✅ Onboarding wizard |
| `/smith:categorize` | ✅ Transaction categorization + rule learning |
| `/smith:review-conflicts` | ✅ Conflict review (reference implementation) |
| `/smith:health` | ✅ Health check + category optimization |
| `/smith:insights` | 🆕 Unified analysis/scenarios/reports |
| `/smith:tax` | ✅ Tax operations (consolidated) |

### Files to Delete

- [ ] `agent-smith-plugin/commands/analyze.md`
- [ ] `agent-smith-plugin/commands/scenario.md`
- [ ] `agent-smith-plugin/commands/report.md`
- [ ] `agent-smith-plugin/commands/optimize.md`
- [ ] `scripts/categorize.py`
- [ ] `scripts/operations/review_conflicts.py`
- [ ] `scripts/operations/review_conflicts_v2.py`
- [ ] `scripts/test_visualizer.py`
- [ ] `scripts/operations/setup_paypal_test.py`

### Files to Create

- [ ] `scripts/status/dashboard.py`
- [ ] `agent-smith-plugin/hooks/session-start.md`
- [ ] `agent-smith-plugin/commands/insights.md`
- [ ] `scripts/setup/schedule.py`
- [ ] `scripts/scheduled/auto_categorize.py`

---

## Appendix A: Automated Scheduling Feature

### Overview

Provide two ways to automate categorization:

1. **Smart SessionStart** - Auto-offer when Claude Code opens (if stale transactions)
2. **Scheduled Job** - System cron/launchd for truly automated processing

### Task A1: Create Standalone Auto-Categorize Script

**Files:**
- Create: `scripts/scheduled/auto_categorize.py`

This script runs WITHOUT Claude Code, suitable for cron jobs:

```python
#!/usr/bin/env python3
"""Automated categorization for scheduled execution.

Designed to run via cron/systemd/launchd without Claude Code.
Logs results for SessionStart dashboard to display.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["conservative", "smart", "aggressive"],
                        default="smart")
    parser.add_argument("--period", default="last-30-days")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-file", default="data/auto_categorize.log")
    args = parser.parse_args()

    from scripts.operations.categorize_batch import run_categorization

    print(f"[{datetime.now().isoformat()}] Starting auto-categorization...")
    print(f"  Mode: {args.mode}")
    print(f"  Period: {args.period}")
    print(f"  Dry-run: {args.dry_run}")

    result = run_categorization(
        mode=args.mode,
        period=args.period,
        dry_run=args.dry_run,
    )

    # Log results for SessionStart dashboard
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": args.mode,
        "period": args.period,
        "dry_run": args.dry_run,
        "results": {
            "processed": result.get("processed", 0),
            "auto_applied": result.get("auto_applied", 0),
            "flagged_for_review": result.get("flagged", 0),
            "errors": result.get("errors", 0),
        }
    }

    # Append to activity log
    log_path = Path(args.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"\n✅ Auto-categorization complete:")
    print(f"   Processed: {log_entry['results']['processed']}")
    print(f"   Auto-applied: {log_entry['results']['auto_applied']}")
    print(f"   Flagged for review: {log_entry['results']['flagged_for_review']}")

    return 0 if log_entry['results']['errors'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Task A2: Create Schedule Setup Script

**Files:**
- Create: `scripts/setup/schedule.py`

Interactive setup for scheduling:

```python
#!/usr/bin/env python3
"""Set up automated categorization scheduling."""

import argparse
import platform
import subprocess
import sys
from pathlib import Path

CRON_TEMPLATE = '''# Agent Smith Auto-Categorization
# Runs {frequency} at {time}
{schedule} cd {project_dir} && uv run python -u scripts/scheduled/auto_categorize.py --mode smart >> data/auto_categorize.log 2>&1
'''

LAUNCHD_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.agentsmith.autocategorize</string>
    <key>ProgramArguments</key>
    <array>
        <string>{uv_path}</string>
        <string>run</string>
        <string>python</string>
        <string>-u</string>
        <string>scripts/scheduled/auto_categorize.py</string>
        <string>--mode</string>
        <string>smart</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{project_dir}</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{project_dir}/data/auto_categorize.log</string>
    <key>StandardErrorPath</key>
    <string>{project_dir}/data/auto_categorize.log</string>
</dict>
</plist>
'''

def setup_cron(frequency: str, time: str, project_dir: Path) -> None:
    """Set up cron job for Linux."""
    hour, minute = time.split(":")

    if frequency == "daily":
        schedule = f"{minute} {hour} * * *"
    elif frequency == "weekly":
        schedule = f"{minute} {hour} * * 0"  # Sunday
    elif frequency == "hourly":
        schedule = f"{minute} * * * *"

    cron_entry = CRON_TEMPLATE.format(
        frequency=frequency,
        time=time,
        schedule=schedule,
        project_dir=project_dir,
    )

    print("Add this to your crontab (crontab -e):")
    print("-" * 50)
    print(cron_entry)
    print("-" * 50)

def setup_launchd(time: str, project_dir: Path) -> None:
    """Set up launchd for macOS."""
    hour, minute = map(int, time.split(":"))
    uv_path = subprocess.check_output(["which", "uv"]).decode().strip()

    plist_content = LAUNCHD_TEMPLATE.format(
        uv_path=uv_path,
        project_dir=project_dir,
        hour=hour,
        minute=minute,
    )

    plist_path = Path.home() / "Library/LaunchAgents/com.agentsmith.autocategorize.plist"

    print(f"Creating launchd plist at: {plist_path}")
    plist_path.write_text(plist_content)

    print("Loading launchd job...")
    subprocess.run(["launchctl", "load", str(plist_path)])
    print("✅ Scheduled! Will run daily at {time}")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frequency", choices=["hourly", "daily", "weekly"],
                        default="daily")
    parser.add_argument("--time", default="06:00", help="Time in HH:MM format")
    parser.add_argument("--remove", action="store_true", help="Remove scheduling")
    args = parser.parse_args()

    project_dir = Path(__file__).parent.parent.parent.absolute()
    system = platform.system()

    if args.remove:
        print("Removing scheduled job...")
        if system == "Darwin":
            plist = Path.home() / "Library/LaunchAgents/com.agentsmith.autocategorize.plist"
            if plist.exists():
                subprocess.run(["launchctl", "unload", str(plist)])
                plist.unlink()
        print("✅ Removed. Edit crontab manually if using cron.")
        return 0

    print(f"Setting up auto-categorization schedule...")
    print(f"  System: {system}")
    print(f"  Frequency: {args.frequency}")
    print(f"  Time: {args.time}")
    print(f"  Project: {project_dir}")
    print()

    if system == "Darwin":
        setup_launchd(args.time, project_dir)
    else:
        setup_cron(args.frequency, args.time, project_dir)

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Task A3: Enhance SessionStart with Auto-Categorize Offer

**Modify:** `agent-smith-plugin/hooks/session-start.md`

Add to the SessionStart dashboard logic:

```markdown
## Auto-Categorization Check

If uncategorized transactions exist for 3+ days AND no auto-categorize scheduled:

\`\`\`
🔔 AUTO-CATEGORIZATION AVAILABLE
─────────────────────────────────────────
{count} transactions uncategorized for 3+ days.

Would you like to:
  1. Auto-categorize now (uses smart mode)
  2. Set up scheduled auto-categorization
  3. Skip for now
\`\`\`

If auto-categorization is scheduled, show last run status instead:

\`\`\`
🤖 LAST AUTO-CATEGORIZATION: Today 6:00am
─────────────────────────────────────────
  Processed: 45
  Auto-applied: 40
  Flagged for review: 5

→ Review 5 flagged items with /smith:review-conflicts
\`\`\`
```

### Task A4: Add /smith:schedule Command

**Create:** `agent-smith-plugin/commands/schedule.md`

```markdown
---
name: smith:schedule
description: Configure automated categorization scheduling
argument-hints:
  - "[--setup|--status|--remove] [--frequency=daily|weekly] [--time=HH:MM]"
---

# Automated Categorization Scheduling

Set up automatic categorization to run on a schedule.

## Goal

Keep your transactions categorized automatically without manual intervention.

## Why This Matters

Regular categorization prevents backlogs and keeps your financial data current. Scheduled runs ensure you never fall behind.

## Execution

Use the Task tool with `subagent_type: "general-purpose"` to manage scheduling:

### Subagent Prompt

\`\`\`
You are the Agent Smith scheduling assistant.

## Check Current Status

First, check if scheduling is already configured:
\`\`\`bash
uv run python -u scripts/setup/schedule.py --status
\`\`\`

## Based on Arguments

**--setup (or no args):**
Ask user preferences using AskUserQuestion:
1. Frequency: Daily, Weekly, or Hourly?
2. Time: What time? (default: 6:00am)

Then run:
\`\`\`bash
uv run python -u scripts/setup/schedule.py --frequency [FREQ] --time [TIME]
\`\`\`

**--status:**
Show current schedule status and recent run history.

**--remove:**
\`\`\`bash
uv run python -u scripts/setup/schedule.py --remove
\`\`\`

## Present Results

Show confirmation with:
- Schedule details
- How to check logs: \`cat data/auto_categorize.log\`
- How to remove: \`/smith:schedule --remove\`
\`\`\`

## Scheduling Options

| Frequency | When | Best For |
|-----------|------|----------|
| **hourly** | Every hour | High-volume accounts |
| **daily** | Once per day (default: 6am) | Most users |
| **weekly** | Once per week (Sunday 6am) | Low-volume accounts |

## Next Steps

After scheduling:
- **Check logs**: `cat data/auto_categorize.log`
- **Review flagged**: `/smith:review-conflicts`
- **Modify schedule**: `/smith:schedule --setup`
- **Remove schedule**: `/smith:schedule --remove`
```

### Files to Create for Scheduling

- [ ] `scripts/scheduled/auto_categorize.py` - Standalone categorization
- [ ] `scripts/setup/schedule.py` - Schedule setup utility
- [ ] `agent-smith-plugin/commands/schedule.md` - Schedule command
