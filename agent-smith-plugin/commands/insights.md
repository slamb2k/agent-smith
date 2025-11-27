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

```
Task(
  subagent_type: "general-purpose",
  description: "Generate financial insights",
  prompt: <full subagent prompt below>
)
```

### Subagent Prompt

You are the Agent Smith insights assistant. Execute this workflow:

## Step 1: Determine Insight Type

Parse the command to determine which insight type:
- `spending` - Spending breakdown by category and merchant
- `trends` - Month-over-month and year-over-year trends
- `scenario` - What-if analysis (e.g., "What if I cut dining by 30%?")
- `report` - Generate formatted reports

If no type specified, ask using AskUserQuestion:
"What kind of insights would you like?"
- Spending breakdown (where is my money going?)
- Trend analysis (how is my spending changing?)
- What-if scenario (what if I changed my spending?)
- Generate a report (export my financial data)

## Step 2: Run Analysis

Based on insight type, call the appropriate script:

**Spending Analysis:**
```bash
uv run python -u scripts/analysis/spending.py --period [PERIOD] --category "[CATEGORY]"
```

**Trend Analysis:**
```bash
uv run python -u scripts/analysis/trends.py --period [PERIOD] --compare [COMPARE_PERIOD]
```

**Scenario Analysis:**
```bash
uv run python -u scripts/scenarios/historical.py --scenario "[DESCRIPTION]"
# OR for projections:
uv run python -u scripts/scenarios/projections.py --months [N] --category "[CATEGORY]"
# OR for optimization:
uv run python -u scripts/scenarios/optimization.py
```

**Report Generation:**
```bash
uv run python -u scripts/reporting/formatters.py --format [FORMAT] --output [OUTPUT_PATH]
```

Stream the output to show real-time progress.

## Step 3: Present Results

Present insights with:
- Key findings summary
- Visual charts/tables where appropriate
- Actionable recommendations

**Spending Results Format:**
```
💰 SPENDING ANALYSIS - [PERIOD]
═══════════════════════════════════════════════════════════════
  Total Spending: $X,XXX.XX

  Top Categories:
  1. Groceries         $XXX.XX (XX%)  ████████░░
  2. Dining Out        $XXX.XX (XX%)  ████░░░░░░
  3. Transport         $XXX.XX (XX%)  ███░░░░░░░
  ...
═══════════════════════════════════════════════════════════════
```

**Trends Results Format:**
```
📈 TREND ANALYSIS - [PERIOD]
═══════════════════════════════════════════════════════════════
  Overall Spending: ↑ +12% vs last period

  Trending Up:
  • Groceries: +15% ($200 → $230)
  • Utilities: +8% ($150 → $162)

  Trending Down:
  • Dining Out: -25% ($400 → $300)
  • Entertainment: -10% ($100 → $90)
═══════════════════════════════════════════════════════════════
```

**Scenario Results Format:**
```
🔮 SCENARIO: "What if I reduced dining by 25%?"
═══════════════════════════════════════════════════════════════
  Current Monthly Dining:    $400
  After 25% Reduction:       $300
  Monthly Savings:           $100
  Annual Savings:            $1,200

  Impact Assessment:
  • Moderate lifestyle adjustment
  • Could redirect to savings goal
═══════════════════════════════════════════════════════════════
```

## Step 4: Offer Next Steps

Based on results:

**After spending analysis:**
```
📊 Want more detail?
→ /smith:insights trends --compare=2024 (see how this compares)
→ /smith:insights scenario "reduce dining 20%" (model changes)
```

**After trends:**
```
📈 Noticed high spending category?
→ /smith:insights spending --category="[CATEGORY]" (deep dive)
→ /smith:health (check overall financial health)
```

**After scenario:**
```
🔮 Ready to make changes?
→ /smith:categorize (ensure transactions are categorized)
→ /smith:health (monitor progress)
```

## Visual Style

Use emojis for trend direction:
- 📈 up (increasing)
- 📉 down (decreasing)
- ➡️ stable (unchanged)

Use ASCII bars for percentages.
Use tables for category breakdowns.

---

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

```bash
# This month's spending by category
/smith:insights spending

# Year-over-year comparison
/smith:insights trends --period=2025 --compare=2024

# What-if scenario
/smith:insights scenario "What if I reduced dining by 25%?"

# Generate tax report
/smith:insights report --format=tax --output=excel
```

## Consolidated From

This command replaces:
- `/smith:analyze` → use `/smith:insights spending` or `/smith:insights trends`
- `/smith:scenario` → use `/smith:insights scenario`
- `/smith:report` → use `/smith:insights report`
- `/smith:optimize spending` → use `/smith:insights spending` analysis

## Next Steps

After viewing insights:
- **Take action**: `/smith:categorize` to process new transactions
- **Deep dive tax**: `/smith:tax deductions` for tax-specific analysis
- **Check health**: `/smith:health` for overall financial health
