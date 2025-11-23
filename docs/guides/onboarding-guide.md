# Agent Smith Onboarding Guide

Welcome to Agent Smith! This guide walks you through your first-time setup and helps you get the most out of your PocketSmith integration.

## Before You Begin

**Prerequisites:**
1. ✅ Agent Smith installed (see [INSTALL.md](../../INSTALL.md))
2. ✅ PocketSmith account with API access
3. ✅ API key configured in `.env` file
4. ✅ Python 3.9+ and `uv` installed

**Time Required:** 30-60 minutes (depending on transaction volume)

---

## The Onboarding Journey

Agent Smith's onboarding is an 8-stage interactive process that:
- Discovers your PocketSmith account structure
- Recommends and customizes rule templates
- Incrementally categorizes your transactions
- Shows measurable improvement with health scores

### Quick Start

```bash
# Launch the onboarding wizard
/smith:install
```

Claude will guide you through each stage interactively.

---

## Stage 1: Prerequisites Check

**What happens:**
- Verifies Agent Smith installation
- Checks API key configuration
- Tests PocketSmith connection

**If something is missing:**
- Follow the prompts to complete installation
- Refer to [INSTALL.md](../../INSTALL.md) for detailed setup

**Time:** 2 minutes

---

## Stage 2: Discovery

**What happens:**
- Analyzes your PocketSmith account structure
- Counts accounts, categories, and transactions
- Identifies uncategorized transactions
- Calculates baseline health score

**What you'll see:**
```
✓ Connected as: your@email.com
✓ Accounts: 3 (Checking, Savings, Credit Card)
✓ Categories: 47
✓ Transactions: 2,387
✓ Uncategorized: 1,245 (52%)
✓ Date Range: Jan 2023 - Nov 2025
✓ Baseline Health Score: 45/100 (Critical)
✓ Recommended Template: shared-household
```

**Time:** 5-10 minutes (depends on data volume)

---

## Stage 3: Template Selection

**What happens:**
- Shows 4 template options
- Recommends best fit based on discovery
- Applies selected template to `data/rules.yaml`

**Templates:**

| Template | Best For | Includes |
|----------|----------|----------|
| **Simple** | Single person, basic tracking | Common categories, essential rules |
| **Separated Families** | Child support, shared custody | Kids expenses, contributor tracking |
| **Shared Household** | Couples, roommates | Shared expense tracking, approval workflows |
| **Advanced** | Business owners, investors | Tax optimization, investment tracking, CGT |

**What you'll do:**
- Review the recommendation
- Choose a template (or browse all)
- Confirm application

**Time:** 3-5 minutes

---

## Stage 4: Template Customization

**What happens:**
- Guides you to customize the template for your needs

**Customizations needed:**

1. **Account Mapping**
   - Template uses generic names like "Shared Bills", "Personal"
   - Update to match your actual account names

2. **Category Validation**
   - Check if template categories exist in PocketSmith
   - Create missing categories or map to existing ones

3. **Merchant Localization**
   - Template has Australian merchants (WOOLWORTHS, COLES)
   - Update for your region (SAFEWAY, KROGER, etc.)

**How to customize:**
- Edit `data/rules.yaml` manually (for now)
- Future versions will have interactive customization tool

**Example:**
```yaml
# Before (template)
- type: category
  patterns: [WOOLWORTHS, COLES]
  category: Food & Dining > Groceries

# After (customized for US)
- type: category
  patterns: [SAFEWAY, KROGER, WHOLE FOODS]
  category: Food & Dining > Groceries
```

**Time:** 10-20 minutes

---

## Stage 5: Intelligence Mode Selection

**What happens:**
- Configure AI categorization behavior
- Set tax intelligence level

**Categorization Mode:**

| Mode | Auto-Apply Threshold | Best For |
|------|---------------------|----------|
| Conservative | 100% (manual approval all) | First-time setup, learning |
| **Smart** (default) | ≥90% confidence | Most users, balanced |
| Aggressive | ≥80% confidence | High volume, trust AI |

**Tax Intelligence Level:**

| Level | Capabilities | Best For |
|-------|-------------|----------|
| Reference | ATO category mapping, basic reports | Users with accountants |
| **Smart** (default) | Deduction detection, thresholds | Most taxpayers |
| Full | BAS prep, compliance checks | Business owners, power users |

**Time:** 2 minutes

---

## Stage 6: Incremental Categorization

**What happens:**
- Categorize transactions in manageable batches
- Start recent, expand to historical

**Recommended Strategy:**

1. **Current Month** (test rules on small dataset)
   ```bash
   uv run python scripts/operations/batch_categorize.py --mode=dry_run --period=2025-11
   uv run python scripts/operations/batch_categorize.py --mode=apply --period=2025-11
   ```

2. **Last 3 Months** (validate at scale)
   ```bash
   uv run python scripts/operations/batch_categorize.py --mode=apply --period=2025-09:2025-11
   ```

3. **Full Backfill** (complete the archive)
   ```bash
   uv run python scripts/operations/batch_categorize.py --mode=apply --period=2023-01:2025-11
   ```

**After Each Batch:**
- Review results (matched, auto-applied, needs review)
- Approve medium-confidence suggestions
- Agent Smith learns new rules from your corrections

**Time:** 20-60 minutes (depends on volume and mode)

---

## Stage 7: Health Check & Progress

**What happens:**
- Run post-categorization health check
- Show before/after improvement
- Identify remaining priorities

**What you'll see:**
```
═══════════════════════════════════════════════
AGENT SMITH HEALTH CHECK - PROGRESS REPORT
═══════════════════════════════════════════════

Baseline (before):    45/100 (Critical)
Current:              78/100 (Good) ⬆ +33 points

Improvements:
• Data Quality:        42 → 88 (+46) ✅
• Rule Engine:         15 → 72 (+57) ✅
• Category Structure:  58 → 81 (+23) ✅

Remaining priorities:
1. Review tax category mappings
2. Add 3 more rules for recurring merchants
3. Create budgets for top 5 categories
```

**Time:** 5 minutes

---

## Stage 8: Ongoing Usage

**What happens:**
- Receive guidance on regular Agent Smith usage
- Get quick reference for common operations

**Daily/Weekly:**
```bash
/smith:categorize --mode=smart --period=2025-11
```

**Monthly:**
```bash
/smith:analyze spending --period=2025-11
/smith:health --quick
```

**Quarterly:**
```bash
/smith:tax deductions --period=2024-25
```

**Annual (EOFY):**
```bash
/smith:tax eofy
```

**Time:** 2 minutes

---

## Troubleshooting

### Onboarding Interrupted

If onboarding is interrupted, your progress is saved in `data/onboarding_state.json`.

**Resume:**
```bash
/smith:install
```

Claude will detect saved state and offer to resume from where you left off.

**Start Over:**
```bash
uv run python -c "from scripts.onboarding.state import OnboardingState; OnboardingState().reset()"
/smith:install
```

### Discovery Fails

**Problem:** "Error during discovery: ..."

**Solutions:**
- Check `.env` has valid `POCKETSMITH_API_KEY`
- Verify PocketSmith account has API access enabled
- Check internet connection to api.pocketsmith.com

### Template Customization Unclear

**Problem:** Not sure how to customize `data/rules.yaml`

**Solutions:**
- Review [Unified Rules Guide](unified-rules-guide.md) for YAML syntax
- Check [Example Files](../examples/) for patterns
- Start with dry-run to test rules before applying

### Categorization Too Slow

**Problem:** Batch categorization taking too long

**Solutions:**
- Use smaller date ranges (1 month at a time)
- Switch to "Aggressive" mode for faster auto-apply
- Run in background with progress monitoring

---

## Next Steps

After completing onboarding:

1. **Set Up Alerts**
   - Weekly budget reviews
   - Monthly trend analysis
   - Tax deadline reminders

2. **Create Budgets**
   - Use health check recommendations
   - Focus on top spending categories
   - Track vs. budget monthly

3. **Optimize Rules**
   - Review rule performance metrics
   - Add rules for recurring merchants
   - Refine confidence scores

4. **Explore Advanced Features**
   - Scenario analysis
   - Tax optimization
   - Investment tracking

---

## Getting Help

- **Documentation:** [docs/](../INDEX.md)
- **API Reference:** [ai_docs/pocketsmith-api-documentation.md](../../ai_docs/pocketsmith-api-documentation.md)
- **Health Check Guide:** [health-check-guide.md](health-check-guide.md)
- **GitHub Issues:** [github.com/slamb2k/agent-smith/issues](https://github.com/slamb2k/agent-smith/issues)

---

**Welcome to Agent Smith! Let's transform your PocketSmith into an intelligent financial system.**
