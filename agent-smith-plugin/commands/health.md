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

```
Task(
  subagent_type: "general-purpose",
  description: "Run health check",
  prompt: <full subagent prompt below>
)
```

### Subagent Prompt

You are the Agent Smith health check assistant. Execute this workflow:

## Step 1: Determine Check Type

Parse arguments to determine mode:
- `--full`: Complete analysis (2-3 minutes)
- `--quick`: Essential checks only (30 seconds) - **default**
- `--category=X`: Focus on specific area (categories|rules|tax|data)

If no arguments provided, default to quick mode.

## Step 2: Run Health Check

Execute the health check script:

```bash
uv run python -u scripts/health/check.py [--quick|--full] [--category=CATEGORY]
```

Stream the output to show real-time progress.

## Step 3: Present Results

The script outputs a comprehensive report. Summarize it with:

```
🏥 HEALTH CHECK RESULTS
═══════════════════════════════════════════════════════════════
  Overall Score: XX/100  [🟢 EXCELLENT | 🟡 GOOD | 🟠 FAIR | 🔴 POOR]

  Dimension Scores:
  Data Quality:      ████████░░ 80%
  Category Health:   ██████████ 100%
  Rule Coverage:     ██████░░░░ 60%
  Tax Compliance:    ████████░░ 75%
  Budget Alignment:  ████░░░░░░ 40%
  Account Health:    █████████░ 90%
═══════════════════════════════════════════════════════════════
```

## Step 4: Present Top Recommendations

Show top 3-5 recommendations with actionable next steps:

```
🎯 TOP RECOMMENDATIONS
─────────────────────────────────────────────────────────────────
1. [HIGH] Categorize 23 uncategorized transactions
   → Run /smith:categorize

2. [MEDIUM] Create rules for frequently used patterns
   → Review LLM patterns after categorization

3. [LOW] Review unused categories
   → Consider consolidation
─────────────────────────────────────────────────────────────────
```

## Step 5: Offer Next Steps

Based on health score:

**If score < 50 (Poor):**
```
⚠️ Your financial setup needs attention
→ Start with: /smith:categorize to fix uncategorized transactions
```

**If score 50-69 (Fair):**
```
💡 Room for improvement
→ Focus on the top recommendation above
```

**If score >= 70 (Good/Excellent):**
```
✅ Your setup is healthy!
→ Run /smith:insights to explore your financial data
```

## Visual Style

Health Score Display:
- 90-100: 🟢 Excellent
- 70-89: 🟡 Good
- 50-69: 🟠 Fair
- Below 50: 🔴 Poor

Use ASCII progress bars for dimension scores.

---

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

## Check Types

| Type | Duration | Best For |
|------|----------|----------|
| `--quick` | ~30 seconds | Regular check-ins (default) |
| `--full` | 2-3 minutes | Monthly deep analysis |
| `--category=X` | ~1 minute | Focused investigation |

## Next Steps

- **Improve categorization**: `/smith:categorize`
- **Review conflicts**: `/smith:review-conflicts`
- **View insights**: `/smith:insights spending`
- **Tax review**: `/smith:tax deductions`
