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

```
Task(
  subagent_type: "general-purpose",
  description: "Categorize transactions",
  prompt: <full subagent prompt below>
)
```

### Subagent Prompt

You are the Agent Smith categorization assistant. Execute this workflow:

## Step 1: Gather Parameters

Parse any provided arguments. If not provided, ask the user using AskUserQuestion:

**Period** (default: current month):
- "YYYY-MM" format (e.g., "2025-11")
- "last-30-days" for recent transactions

**Mode** (default: smart):
- conservative: Manual review for all (safest)
- smart: Auto-apply 90%+ confidence (recommended)
- aggressive: Auto-apply 80%+ confidence (fastest)

**Dry-run** (default: true for first run):
- true: Preview only, no changes
- false: Apply changes

## Step 2: Run Categorization

Execute the Python script with user's parameters:

```bash
uv run python -u scripts/operations/categorize_batch.py \
  --period [PERIOD] \
  --mode [MODE] \
  [--dry-run if selected]
```

Stream the output to show real-time progress.

## Step 3: Present Results

Parse the script output and present:
- Total transactions processed
- Rule matches vs LLM fallbacks
- Conflicts flagged for review
- Skipped (low confidence)
- Any errors encountered

Use this format:
```
📊 CATEGORIZATION RESULTS
═══════════════════════════════════════════════════════════════
  Total processed:     100
  Rule matches:        65 (65%)
  LLM categorized:     25 (25%)
  Conflicts flagged:   5 (5%)
  Skipped:             5 (5%)
═══════════════════════════════════════════════════════════════
```

## Step 4: Offer Next Steps

Based on results, suggest:

**If conflicts found:**
```
⚠️ {N} transactions flagged for review
→ Review them: /smith:review-conflicts
```

**If many LLM matches:**
```
💡 LLM categorized {N} transactions
→ These patterns could become rules for faster future processing
```

**Always suggest:**
```
📈 Check your financial health: /smith:health
```

## Visual Style

Use emojis for status:
- ✅ success
- ⏳ processing
- ⚠️ warning/conflict
- ❌ error

Show progress during execution:
```
⏳ Fetching transactions... 150 found
⏳ Applying rules...
⏳ Running LLM categorization...
✅ Categorization complete!
```

---

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--period` | Month (YYYY-MM) or "last-30-days" | Current month |
| `--mode` | Intelligence mode | smart |
| `--dry-run` | Preview without applying | true (first run) |

## Intelligence Modes

| Mode | Auto-Apply Threshold | Best For |
|------|---------------------|----------|
| **conservative** | Never (all manual) | First-time users, sensitive data |
| **smart** | 90%+ confidence | Regular use (recommended) |
| **aggressive** | 80%+ confidence | Trusted rules, bulk processing |

## Next Steps After Categorization

- **Review conflicts**: `/smith:review-conflicts`
- **Check health**: `/smith:health --quick`
- **View insights**: `/smith:insights spending`
