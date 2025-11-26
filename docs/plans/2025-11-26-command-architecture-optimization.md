# Command Architecture Optimization Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor all Agent Smith slash commands to adhere to the 6 development principles and UX guidelines defined in CLAUDE.md.

**Architecture:** Commands delegate to Python scripts for all data operations, use subagents for heavy processing, and follow the guided workflow pattern (Goal/Why/Steps/Summary/Next Steps).

**Tech Stack:** Python scripts (deterministic), Claude Code slash commands (UX orchestration), Task tool (subagent delegation)

---

## Assessment Summary

| Command | Principle Violations | Priority |
|---------|---------------------|----------|
| `/smith:categorize` | P1 (embeds Python), P2 (duplicates script), P6 (no subagent) | **CRITICAL** |
| `/smith:health` | P1 (no script call), P5 (no feedback), P6 (no subagent) | HIGH |
| `/smith:analyze` | P1 (no script call), P5 (no feedback), P6 (no subagent) | HIGH |
| `/smith:scenario` | P1 (no script call), P5 (no feedback), P6 (no subagent) | MEDIUM |
| `/smith:tax` | P1 (no script call), P5 (no feedback), P6 (no subagent) | MEDIUM |
| `/smith:optimize` | P1 (no script call), P5 (no feedback), P6 (no subagent) | MEDIUM |
| `/smith:report` | P1 (no script call), P5 (no feedback), P6 (no subagent) | LOW |
| `/smith:install` | P6 (no subagent for heavy stages) | LOW |
| `/smith:review-conflicts` | None - **REFERENCE IMPLEMENTATION** | DONE |

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

## Task 3: Implement `/smith:analyze` Command

**Files:**
- Modify: `agent-smith-plugin/commands/analyze.md`
- Create: `scripts/analysis/spending.py` (if needed)
- Reference: `scripts/scenarios/historical.py`, `scripts/scenarios/projections.py`

**Step 1: Check existing analysis scripts**

Run: `ls -la scripts/analysis/ scripts/scenarios/`

**Step 2: Create the new command with implementation**

Replace `agent-smith-plugin/commands/analyze.md` with content that:
- Delegates to subagent
- Calls appropriate scripts based on analysis type
- Follows guided workflow pattern
- Streams real-time feedback
- Suggests next steps

**Step 3: Commit**

```bash
git add agent-smith-plugin/commands/analyze.md
git commit -m "feat: Implement /smith:analyze with script integration and subagent"
```

---

## Task 4: Implement `/smith:scenario` Command

**Files:**
- Modify: `agent-smith-plugin/commands/scenario.md`
- Reference: `scripts/scenarios/historical.py`, `scripts/scenarios/projections.py`, `scripts/scenarios/optimization.py`

**Step 1: Check existing scenario scripts**

Run: `ls -la scripts/scenarios/`

**Step 2: Create the new command with implementation**

Replace with content that:
- Delegates to subagent
- Routes to appropriate scenario script based on type
- Follows guided workflow pattern
- Provides visual scenario results

**Step 3: Commit**

```bash
git add agent-smith-plugin/commands/scenario.md
git commit -m "feat: Implement /smith:scenario with script integration and subagent"
```

---

## Task 5: Implement `/smith:tax` Command

**Files:**
- Modify: `agent-smith-plugin/commands/tax.md`
- Reference: `scripts/tax/deduction_detector.py`, `scripts/tax/cgt_tracker.py`, `scripts/tax/bas_preparation.py`

**Step 1: Check existing tax scripts**

Run: `ls -la scripts/tax/`

**Step 2: Create the new command with implementation**

Replace with content that:
- Delegates to subagent
- Routes to appropriate tax script based on operation
- Follows guided workflow pattern
- Includes required tax disclaimers for Level 3

**Step 3: Commit**

```bash
git add agent-smith-plugin/commands/tax.md
git commit -m "feat: Implement /smith:tax with script integration and subagent"
```

---

## Task 6: Implement `/smith:optimize` Command

**Files:**
- Modify: `agent-smith-plugin/commands/optimize.md`
- May need: New scripts for optimization operations

**Step 1: Read current optimize command**

Run: Read `agent-smith-plugin/commands/optimize.md`

**Step 2: Assess what scripts exist vs needed**

Run: `ls -la scripts/` and check for optimization-related scripts

**Step 3: Create/update command with implementation**

Follow same pattern as other commands.

**Step 4: Commit**

```bash
git add agent-smith-plugin/commands/optimize.md
git commit -m "feat: Implement /smith:optimize with script integration and subagent"
```

---

## Task 7: Implement `/smith:report` Command

**Files:**
- Modify: `agent-smith-plugin/commands/report.md`
- Reference: `scripts/reporting/` directory

**Step 1: Check existing reporting scripts**

Run: `ls -la scripts/reporting/`

**Step 2: Create/update command with implementation**

Follow same pattern as other commands.

**Step 3: Commit**

```bash
git add agent-smith-plugin/commands/report.md
git commit -m "feat: Implement /smith:report with script integration and subagent"
```

---

## Task 8: Enhance `/smith:install` with Subagent Delegation

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

## Task 9: Clean Up Unused Scripts

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

## Task 10: Update SKILL.md with New Patterns

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

## Task 11: Final Validation and Documentation

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

After completing all tasks, verify each command against principles:

| Principle | Verification |
|-----------|--------------|
| P1: Determinism | No embedded Python in commands, all ops via scripts |
| P2: Code Reuse | Commands call existing scripts, no duplication |
| P3: TDD | All new scripts have tests |
| P4: Separation | Commands = UX, Scripts = Logic |
| P5: Real-Time Feedback | Scripts use `-u` flag, stream progress |
| P6: Context Management | Heavy ops delegate to subagents |

| UX Guideline | Verification |
|--------------|--------------|
| Guided Workflow | Goal/Why/Steps/Summary/Next Steps present |
| Visual Elements | Emojis, progress bars, tables used appropriately |
| Frontmatter | description and argument-hints defined |
| Error Handling | Helpful messages with suggestions |
