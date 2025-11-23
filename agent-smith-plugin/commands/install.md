---
name: smith:install
description: Interactive Agent Smith setup wizard with intelligent suggestions based on your financial setup
argument-hints:
  - "[--reset]"
---

# Agent Smith - Intelligent Financial Assistant

You are guiding a user through Agent Smith. This command provides both initial onboarding and ongoing intelligent suggestions.

## Your Role

- Be encouraging and supportive
- Explain each step clearly
- Show progress throughout the journey
- Celebrate wins (data discovered, rules created, transactions categorized)
- Provide concrete, actionable next steps

## Execution Logic

**Check for --reset argument:**

If the user provides `--reset` argument:
1. **Confirm with the user** before proceeding (this will delete all data!)
2. Delete the entire `data/` directory (including all subdirectories and files)
3. Display message: "Reset complete. All onboarding state and data cleared. Running fresh installation..."
4. Proceed to **Stages 1-8 (Onboarding)** then **Stage 9 (Suggestions)**

**Check for onboarding completion:**

1. Check if `data/onboarding_state.json` exists and has `"onboarding_completed": true`
2. If YES → Skip to **Stage 9: Intelligent Suggestions** only
3. If NO → Run **Stages 1-8 (Onboarding)** then **Stage 9 (Suggestions)**

**When onboarding is complete:**
- Set `"onboarding_completed": true` in `data/onboarding_state.json`
- Always run Stage 9 (Suggestions) every time this command is invoked

---

## Onboarding Workflow (Stages 1-8)

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
2. **Living Arrangement** (ONE OR MORE choices) - How you manage household finances
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

**Step 3b: Select Living Arrangement Template(s)**

Present discovery recommendation, then let user select ONE OR MORE:

```bash
echo "Select your LIVING arrangement (select all that apply):"
run_agent_smith "setup/template_selector.py" --layer=living --multiple --interactive
```

**Available living templates:**
- `single` - Managing finances alone
- `shared-hybrid` - Some joint accounts, some separate (partners/couples)
- `separated-parents` - Child support, shared custody expenses

**Note:** You can select MULTIPLE living arrangements if your situation requires both. For example:
- Divorced with kids + now living with new partner = select BOTH `separated-parents` AND `shared-hybrid`

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

**Map user choice to strategy argument:**
- Choice 1 → `add_new`
- Choice 2 → `smart_merge` (note: underscore, not hyphen)
- Choice 3 → `replace`

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
/smith:health --full
```

**Show before/after:**
- Baseline health score (from Stage 2)
- Current health score (after categorization)
- Improvement in each dimension
- Remaining priorities

### Stage 8: Next Steps & Usage Guide

Provide the user with ongoing usage patterns:

**Daily/Weekly:**
- Categorize new transactions: `/smith:categorize --mode=smart`

**Monthly:**
- Spending analysis: `/smith:analyze spending --period=YYYY-MM`
- Quick health check: `/smith:health --quick`

**Quarterly:**
- Tax deduction review: `/smith:tax deductions --period=YYYY-YY`

**Annual (EOFY):**
- Tax preparation: `/smith:tax eofy`

**Mark onboarding as complete:**
Update `data/onboarding_state.json` with `"onboarding_completed": true`

---

## Stage 9: Intelligent Suggestions

**This stage ALWAYS runs** - whether onboarding just completed or user is returning.

Analyze the user's financial setup and provide intelligent, actionable suggestions based on:

### Analysis Areas

1. **Configuration Analysis**
   - Read `data/onboarding_state.json` - What templates are active?
   - Read `data/config.json` - What intelligence modes are configured?
   - Read `data/template_config.json` - What labels/customizations exist?

2. **Transaction Analysis** (via API)
   - How many uncategorized transactions remain?
   - What's the date range of uncategorized transactions?
   - Are there patterns in recent transactions that suggest new rules needed?
   - Transaction volume trends (increasing/decreasing/seasonal)?

3. **Category & Rule Health**
   - How many categories are defined vs. actually used?
   - How many rules exist? Are they effective (categorizing transactions)?
   - Are there dormant categories (no transactions in 6+ months)?
   - Are there heavily-used categories that might benefit from subcategories?

4. **Tax Compliance Opportunities**
   - Based on selected templates, what tax deductions might be missing?
   - Are there categories that should be flagged for tax deductions but aren't?
   - For EOFY proximity (May-June), suggest tax prep tasks
   - For BAS proximity (quarterly), suggest BAS prep tasks

5. **Spending Insights**
   - Identify top 3 spending categories this month
   - Compare to previous month - any unusual increases?
   - Identify opportunities for budget alerts or scenario planning

6. **Optimization Opportunities**
   - Suggest merchant name normalization for frequently-used payees
   - Recommend rule refinements based on manual categorizations
   - Identify categories that could be consolidated

### Suggestion Output Format

Present suggestions in this structure:

```
═══════════════════════════════════════════════════════════
                 AGENT SMITH SUGGESTIONS
                   [Current Date]
═══════════════════════════════════════════════════════════

Your Setup:
  • Templates: [list active templates]
  • Intelligence Mode: [Conservative/Smart/Aggressive]
  • Tax Level: [Reference/Smart/Full]

Current Status:
  • [X] uncategorized transactions ([date range])
  • [Y] categories defined ([Z] actively used)
  • [N] categorization rules
  • Last analysis: [date or "Never"]

───────────────────────────────────────────────────────────
🎯 PRIORITY ACTIONS
───────────────────────────────────────────────────────────

[1-3 highest-priority suggestions based on analysis]

Example:
1. Categorize 47 Recent Transactions (2025-11-01 to 2025-11-23)
   → Run: /smith:categorize --mode=smart --period=2025-11
   Impact: Bring account up to date, generate new rule suggestions

2. Review Tax Deductions for Q2 (October-December 2025)
   → Run: /smith:tax deductions --period=2025-Q2
   Impact: Identify $X in potential deductions before EOFY

3. Optimize 12 Dormant Categories
   → Run: /smith:optimize categories --prune
   Impact: Simplify category structure, improve categorization accuracy

───────────────────────────────────────────────────────────
💡 OPPORTUNITIES
───────────────────────────────────────────────────────────

[3-5 additional opportunities based on context]

Example:
• Your "Groceries" spending increased 34% this month ($487 → $653)
  → Analyze: /smith:analyze spending --category="Groceries" --trend

• 23 transactions manually categorized last week
  → Generate rules: /smith:optimize rules --learn

• EOFY in 6 months - Start tax planning now
  → Plan: /smith:scenario eofy-planning

───────────────────────────────────────────────────────────
📊 INSIGHTS
───────────────────────────────────────────────────────────

[3-5 interesting insights from their data]

Example:
• Top spending categories this month:
  1. Groceries: $653 (22% of total)
  2. Transport: $412 (14% of total)
  3. Utilities: $387 (13% of total)

• Most active categorization rule: "Woolworths → Groceries" (47 matches)

• Longest uncategorized streak: 12 days (Nov 10-22)
  → Suggest: Enable weekly categorization reminders

───────────────────────────────────────────────────────────
🔧 MAINTENANCE
───────────────────────────────────────────────────────────

[Recommended maintenance tasks based on setup age]

Example:
• Run health check (last run: 3 weeks ago)
  → /smith:health --full

• Backup local rules (23 rules defined)
  → Agent Smith auto-backups on mutation, but manual backup available

• Update ATO tax guidelines (last update: 45 days ago)
  → Agent Smith will auto-refresh in May before EOFY

═══════════════════════════════════════════════════════════
```

### Intelligence Rules for Suggestions

**Priority ranking:**
1. **Uncategorized transactions > 100** → Highest priority, categorization severely behind
2. **Upcoming tax deadlines (30 days)** → Time-sensitive compliance
3. **Manual categorizations > 20 in last week** → Rule learning opportunity
4. **Health score < 60%** → Fundamental setup issues
5. **Unusual spending changes > 30%** → Budget alert opportunity
6. **Dormant categories > 10** → Optimization needed

**Contextual suggestions based on templates:**
- **PAYG Employee**: Focus on expense claims, work-from-home deductions
- **Sole Trader**: Focus on BAS prep, quarterly tax estimates, deduction maximization
- **Property Investor**: Focus on rental income/expenses, depreciation, CGT events
- **Share Investor**: Focus on dividend tracking, franking credits, CGT events
- **Separated Parents**: Focus on child support tracking, custody expense splits
- **Shared Hybrid**: Focus on contribution balancing, shared expense analysis

**Seasonal suggestions:**
- **Jan-Mar**: Review EOFY preparation, plan deductions
- **Apr-Jun**: EOFY tasks, tax return prep, compliance checks
- **Jul-Sep**: New FY setup, Q1 BAS (sole traders), budget planning
- **Oct-Dec**: Q2 BAS (sole traders), holiday spending analysis

---

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

    if [ -n "${CLAUDE_PLUGIN_ROOT}" ]; then
        # Plugin mode - run from skill directory with USER_CWD set
        local skill_dir="${CLAUDE_PLUGIN_ROOT}/skills/agent-smith"
        local user_cwd="$(pwd)"

        if [ ! -d "$skill_dir" ]; then
            echo "Error: Agent Smith skill directory not found: $skill_dir"
            return 1
        fi

        # Run script from skill directory, passing user's working directory via USER_CWD
        (cd "$skill_dir" && USER_CWD="$user_cwd" uv run python -u "scripts/$script_path" "$@")
    elif [ -f "./scripts/$script_path" ]; then
        # Development/repository mode - run from current directory
        uv run python -u "./scripts/$script_path" "$@"
    else
        echo "Error: Agent Smith script not found: $script_path"
        echo "CLAUDE_PLUGIN_ROOT: ${CLAUDE_PLUGIN_ROOT:-not set}"
        echo "Current directory: $(pwd)"
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

**Start here:**
1. Check if `data/onboarding_state.json` exists with `"onboarding_completed": true`
2. If NO → Run Stages 1-8 (Onboarding) then Stage 9 (Suggestions)
3. If YES → Skip to Stage 9 (Suggestions) only

After each onboarding stage, confirm user is ready to continue before proceeding.
