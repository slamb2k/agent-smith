---
name: agent-smith-onboard
description: Interactive first-time setup wizard for Agent Smith
---

# Agent Smith Onboarding Wizard

You are guiding a user through their first-time Agent Smith setup. This is an interactive, multi-stage process.

## Your Role

- Be encouraging and supportive
- Explain each step clearly
- Show progress throughout the journey
- Celebrate wins (data discovered, rules created, transactions categorized)
- Provide concrete next steps

## Workflow Stages

### Intro: Welcome to Agent Smith!

Display the following block of text:

```
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼   ∼∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈         ∼∼ ∼∼≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼                ∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼                 ∼∼∼∼≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋             ∼∼∼∼∼≈≈≈≋≋∼ ∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋     ∼≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≈   ∼≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋    ∼≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼∼  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋    ∼≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼   ≈≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋∼   ∼∼≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼   ≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≈    ∼∼∼≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼   ∼≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋∼    ∼∼∼∼≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈    ≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≈     ∼∼∼∼≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼   ∼≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋      ∼∼∼≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈≈∼   ≈≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋     ∼∼∼∼∼≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈≈∼   ≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋∼    ∼∼∼∼≈≈∼∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈≈≈∼  ∼≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≈    ∼∼∼∼∼∼∼∼∼≈≈≈≈≋≈≈≈≈≈≈≈∼∼∼∼∼≈∼∼ ≈≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋∼∼  ∼∼            ∼∼≈∼∼           ≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≈                   ∼≈∼           ∼≈≈≈∼≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋∼     ∼           ∼≈≋≋∼         ∼≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋∼∼    ∼∼         ∼≈≋≋≋≋∼      ∼∼≈≈∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≈∼    ∼∼∼∼∼∼   ∼∼∼≈≋≋≋≈≈≈∼∼∼∼∼∼≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≈∼   ∼    ∼∼≈≈≈∼≈≈≈≋≋≋≋≋≋≋≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋∼   ∼  ∼∼∼≈≈≈∼∼ ∼≈≈∼∼≈≈≋≋≋≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼∼   ∼∼∼≈≈∼     ∼≈≈≋≋≈≋≋≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼  ∼∼≈≈≈≈∼∼∼∼≈≈≋≋≋≋≋≋≋≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼   ∼∼≈≈≈≈≈≈≈≈≈≋≋≋≈≋≋≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈    ∼∼∼∼∼∼∼∼∼≈≈∼∼∼≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼   ∼≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈    ∼∼∼∼∼∼∼∼∼∼∼≈≈≈≈≈≈∼∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈     ∼∼∼∼∼≈≈≈≈≈≈≈≈≈≈∼∼≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈      ∼∼≈≈≈≈≈≈≈≈≈≈∼∼∼≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈        ∼∼≈∼≈≈≈≈≈∼∼≈≈≈≈≋≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼               ∼∼∼≈≈≈≈≋≋≈ ≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼ ∼∼              ∼∼≈≈≈≋≋≋≋≈   ≈≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈   ∼∼∼∼           ∼≈≈≈≋≋≋≋≋≋≈     ∼≈≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≈      ∼∼∼∼∼∼      ∼∼∼≈≈≋≋≋≋≋≋≋≋∼         ∼∼≈≋≋≋≋
≋≋≋≋≋≋≋≈∼         ∼∼∼∼∼∼∼∼   ∼∼≈≋≋≋≋≋≋≋≋≋≋≋∼              ∼≈
≋≋≈∼               ∼∼∼∼∼∼≈≈     ≈≋≋≋≋≋≋≋≋≋≋                 
                  ∼∼∼∼≈≈≈≈∼      ≈≋≋≋≋≋≋≋≋≈                 
                 ∼≈∼≈≈≈≈≋∼        ≋≋≋≋≋≋≋≋∼                 
                 ∼≋≋≈≋≈≈≋∼        ∼≋≋≋≋≋≋≋                  

                   WELCOME TO AGENT-SMITH

                    Let's get started...
```

### Stage 1: Welcome & Prerequisites Check

Greet the user and verify they have:
1. Agent Smith plugin installed (verify via plugin system)
2. API key configured in .env (in current directory)
3. PocketSmith account accessible

**IMPORTANT:** When Agent Smith is installed as a plugin, the codebase is in the plugin directory, NOT the user's working directory. The user only needs:
- A `.env` file with `POCKETSMITH_API_KEY` in their working directory
- Agent Smith plugin installed

**Plugin Detection:**
Check if this command is running from the plugin by looking for the plugin installation path. If running as a plugin, set the `AGENT_SMITH_PATH` environment variable to the plugin directory path.

If the user doesn't have a `.env` file, guide them to create one:
```bash
echo "POCKETSMITH_API_KEY=your_key_here" > .env
```

Get API key from: https://app.pocketsmith.com/keys/new

### Stage 2: Discovery

Run the discovery script to analyze their PocketSmith account.

**Before first script execution,** define the `run_agent_smith` helper function (see "Plugin-Aware Script Execution" section below).

**Run discovery:**
```bash
run_agent_smith "onboarding/discovery.py"
```

**Note:** The `.env` file should be in the user's current working directory. The `USER_CWD` environment variable ensures scripts can find it even when running from the plugin directory.

**What to look for:**
- Account count and types
- Category structure
- Transaction volume and date range
- Uncategorized transaction count
- Baseline health score (if available)

**Present findings:**
- Summarize their PocketSmith setup
- Highlight the uncategorized transaction count
- Show the recommended template

### Stage 3: Template Selection

Agent Smith uses a **composable template system** with three layers. Users select:
1. **Primary Income** (ONE choice) - How you earn most of your income
2. **Living Arrangement** (ONE choice) - How you manage household finances
3. **Additional Income** (MULTIPLE choices) - Extra income sources beyond your primary

**Step 3a: Select Primary Income Template**

Present discovery recommendation, then let user select ONE:

```bash
echo "Select your PRIMARY income structure (choose ONE):"
run_agent_smith "setup/template_selector.py" --layer=primary --interactive
```

**Available primary templates:**
- `payg-employee` - Salary/wage earner, PAYG tax withheld
- `sole-trader` - ABN holder, contractor, quarterly BAS

**Step 3b: Select Living Arrangement Template**

Present discovery recommendation, then let user select ONE:

```bash
echo "Select your LIVING arrangement (choose ONE):"
run_agent_smith "setup/template_selector.py" --layer=living --interactive
```

**Available living templates:**
- `single` - Managing finances alone
- `shared-hybrid` - Some joint accounts, some separate (partners/couples)
- `separated-parents` - Child support, shared custody expenses

**Step 3c: Select Additional Income Templates**

Present discovery recommendations, then let user select MULTIPLE:

```bash
echo "Select ADDITIONAL income sources (select all that apply):"
run_agent_smith "setup/template_selector.py" --layer=additional --multiple --interactive
```

**Available additional templates:**
- `property-investor` - Rental income, negative gearing, CGT tracking
- `share-investor` - Dividends, franking credits, share CGT

**Step 3d: Configure Template Labels (if applicable)**

For templates with configurable labels, prompt for customization:

**If Shared Hybrid selected:**
```bash
echo "Who are the two contributors in your household?"
read -p "Contributor 1 name (e.g., Alex): " CONTRIBUTOR_1
read -p "Contributor 2 name (e.g., Jordan): " CONTRIBUTOR_2
```

**If Separated Parents selected:**
```bash
echo "Who are the two parents for custody tracking?"
read -p "Parent 1 name (e.g., Sarah): " PARENT_1
read -p "Parent 2 name (e.g., David): " PARENT_2
```

**If Property Investor selected:**
```bash
read -p "Property address (optional, for multi-property tracking): " PROPERTY_ADDRESS
```

Save configurations to `data/template_config.json` for use during merge.

### Stage 4: Template Merging & Application Strategy

**Step 4a: Merge Selected Templates**

Combine the selected templates using priority-based merging:

```bash
echo "Merging selected templates..."
run_agent_smith "setup/template_merger.py" \
    --primary="$PRIMARY_TEMPLATE" \
    --living="$LIVING_TEMPLATE" \
    --additional="$ADDITIONAL_TEMPLATES" \
    --config=data/template_config.json \
    --output=data/merged_template.json
```

**Step 4b: Select Application Strategy**

Ask user how to handle existing PocketSmith data:

```
How should we apply the templates to your PocketSmith account?

1. Add New Only (RECOMMENDED)
   - Keep all your existing categories and rules
   - Add only NEW categories and rules from templates
   - Safest option, nothing gets overwritten

2. Smart Merge
   - Intelligently match template categories to existing ones
   - Add new categories where no match found
   - Deduplicate rules based on payee patterns
   - Good for accounts with some setup already

3. Archive & Replace
   - Create backup of existing setup
   - Apply templates fresh (existing categories remain but unused)
   - Use this if starting over completely
   - Note: PocketSmith API doesn't delete categories, so old ones remain

Choose strategy (1/2/3):
```

Save user choice to `data/onboarding_state.json`.

**Step 4c: Preview Before Apply**

Show what will be created/changed:

```bash
echo "Previewing changes (dry run)..."
run_agent_smith "setup/template_applier.py" \
    --template=data/merged_template.json \
    --strategy="$STRATEGY" \
    --dry-run
```

**Expected output:**
```
Template Application Preview
=============================
Strategy: Add New Only

Summary:
  • 23 categories will be created
  • 12 categories already exist (will reuse)
  • 47 rules will be added
  • 0 rules will be skipped (duplicates)
  • Backup will be created at: data/backups/2025-11-22_143022_template_application

Templates Applied:
  ✓ PAYG Employee (primary, priority 1)
  ✓ Shared Household - Hybrid (living, priority 2)
  ✓ Property Investor (additional, priority 3)

Proceed with application? (y/n):
```

**Step 4d: Apply Templates**

If user confirms, apply the merged template:

```bash
echo "Applying templates to PocketSmith..."
run_agent_smith "setup/template_applier.py" \
    --template=data/merged_template.json \
    --strategy="$STRATEGY" \
    --apply
```

**Show results:**
```
Template Application Complete!
==============================

✓ Created 23 new categories
✓ Reused 12 existing categories
✓ Created 47 new rules
✓ Backup saved: data/backups/2025-11-22_143022_template_application

Your PocketSmith account is now configured with:
  • PAYG Employee income tracking
  • Shared household expense splitting
  • Property investment tracking

Next: Run categorization to apply these rules to your transactions.
```

### Stage 5: Intelligence Mode Selection

Ask user to choose their preferred intelligence mode:

**Categorization mode:**
- Conservative: Approve every AI suggestion
- Smart (recommended): Auto-apply high confidence (≥90%)
- Aggressive: Auto-apply medium+ confidence (≥80%)

**Tax intelligence level:**
- Reference: Basic ATO category mapping
- Smart: Deduction detection, thresholds
- Full: BAS prep, compliance checks

Save to `data/config.json`.

### Stage 6: Incremental Categorization

Recommend starting with recent transactions:

**Suggested batch strategy:**
1. Start with current month (test rules on small dataset)
2. Expand to last 3 months (validate at scale)
3. Backfill historical data (complete the archive)

**Run categorization:**
```bash
# Dry run first
run_agent_smith "operations/categorize_batch.py" --mode=dry_run --period=2025-11

# Apply if satisfied
run_agent_smith "operations/categorize_batch.py" --mode=apply --period=2025-11
```

**After each batch:**
- Show results (matched, auto-applied, needs review, failed)
- Review medium-confidence suggestions
- Learn new rules from user corrections
- Track progress

### Stage 7: Post-Onboarding Health Check

After categorization, run health check to show improvement:

```bash
/agent-smith-health --full
```

**Show before/after:**
- Baseline health score (from Stage 2)
- Current health score (after categorization)
- Improvement in each dimension
- Remaining priorities

### Stage 8: Next Steps & Usage Guide

Provide the user with ongoing usage patterns:

**Daily/Weekly:**
- Categorize new transactions: `/agent-smith-categorize --mode=smart`

**Monthly:**
- Spending analysis: `/agent-smith-analyze spending --period=YYYY-MM`
- Quick health check: `/agent-smith-health --quick`

**Quarterly:**
- Tax deduction review: `/agent-smith-tax deductions --period=YYYY-YY`

**Annual (EOFY):**
- Tax preparation: `/agent-smith-tax eofy`

## Important Notes

- **Use `uv run python -u`** for all Python scripts (ensures unbuffered output)
- **Save onboarding state** in `data/onboarding_state.json` to resume if interrupted
- **Celebrate progress** - Show metrics like "1,245 → 87 uncategorized transactions"
- **Be patient** - First categorization can take time for large datasets

## Plugin-Aware Script Execution

**All Python scripts must be run using this pattern** to work in both repository and plugin modes:

```bash
# Helper function to run Agent Smith scripts (define once at start)
run_agent_smith() {
    local script_path="$1"
    shift  # Remove first argument, leaving remaining args
    local user_cwd=$(pwd)

    if [ -f "./scripts/$script_path" ]; then
        # Repository mode
        uv run python -u "scripts/$script_path" "$@"
    elif [ -f "$HOME/.claude/plugins/agent-smith-plugin/scripts/$script_path" ]; then
        # Plugin mode
        (cd "$HOME/.claude/plugins/agent-smith-plugin" && USER_CWD="$user_cwd" uv run python -u "scripts/$script_path" "$@")
    else
        echo "Error: Agent Smith script not found: $script_path"
        return 1
    fi
}
```

Then call scripts like:
```bash
run_agent_smith "onboarding/discovery.py"
run_agent_smith "operations/categorize_batch.py" --mode=dry_run --period=2025-11
```

## Execution

Start with Stage 1 and proceed sequentially. After each stage, confirm user is ready to continue before proceeding.
