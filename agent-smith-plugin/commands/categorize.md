---
name: smith:categorize
description: Categorize uncategorized transactions using the hybrid rule + LLM workflow
argument-hints:
  - "[--period=YYYY-MM|last-30-days] [--mode=conservative|smart|aggressive] [--dry-run] [--reprocess]"
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

## Step 1: Gather Parameters & Confirm Scope

Parse any provided arguments from the command.

**Period** (default: none = all uncategorized):
- No period: Process ALL uncategorized transactions (any date)
- "YYYY-MM" format (e.g., "2025-11"): Specific month
- "last-30-days": Recent transactions only

**Mode** (default: smart):
- conservative: Manual review for all (safest)
- smart: Auto-apply 90%+ confidence (recommended)
- aggressive: Auto-apply 80%+ confidence (fastest)

**Reprocess** (default: false):
- false: Only uncategorized transactions
- true: ALL transactions (enables conflict detection)

**Dry-run** (default: false):
- true: Preview only, no changes
- false: Apply changes

### IMPORTANT: Confirm if No Period Filter

If `--period` is NOT provided in the arguments, you MUST confirm with the user before proceeding using AskUserQuestion:

```
⚠️ NO DATE FILTER SPECIFIED

You're about to process ALL uncategorized transactions across your entire history.
This may take a while depending on how many transactions you have.

Would you like to proceed?
```

Options:
1. "Yes, process all" - Continue without date filter
2. "Last 30 days only" - Add --period last-30-days
3. "Specific month" - Ask for YYYY-MM format

If `--reprocess` is also set, make it clear they're processing ALL transactions (not just uncategorized):

```
⚠️ REPROCESSING ALL TRANSACTIONS

You're about to reprocess ALL transactions (categorized and uncategorized)
across your entire history. This enables conflict detection but may take
significantly longer.

Would you like to proceed?
```

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

## Step 4: Offer Rule Learning

If LLM successfully categorized transactions with recurring patterns, offer to create rules:

```
💡 RULE LEARNING OPPORTUNITY
═══════════════════════════════════════════════════════════════
I noticed these patterns could become rules:

  1. 'NETFLIX' → Entertainment (5 matches, 95% confidence)
  2. 'UBER EATS' → Dining Out (3 matches, 92% confidence)
  3. 'SPOTIFY' → Subscriptions (2 matches, 90% confidence)

Would you like to create rules for any of these?
Rules auto-categorize similar transactions in the future.
═══════════════════════════════════════════════════════════════
```

If user agrees, use AskUserQuestion to confirm which patterns, then call:

```bash
uv run python -u scripts/operations/create_rule.py "[PATTERN]" --category "[CATEGORY]"
```

Show confirmation for each rule created.

## Step 5: Offer Next Steps

Based on results, suggest:

**If conflicts found:**
```
⚠️ {N} transactions flagged for review
→ Review them: /smith:review-conflicts
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
| `--period` | Month (YYYY-MM) or "last-30-days" | None (all uncategorized) |
| `--mode` | Intelligence mode | smart |
| `--dry-run` | Preview without applying | false |
| `--auto-confirm` | Auto-confirm transactions (clears needs_review) | false |
| `--reprocess` | Process ALL transactions (not just uncategorized) | false |

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
