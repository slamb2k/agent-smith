# Unified Rules Guide - Categories & Labels

## Overview

Agent Smith uses a **unified YAML rule system** that handles both transaction categorization and labeling in a single, easy-to-read file.

**Key Features:**
- YAML format - Easy to read and edit
- Two-phase execution - Categories first, then labels
- Pattern matching - Regex patterns with exclusions
- Confidence scoring - 0-100% confidence for auto-apply logic
- Smart labeling - Context-aware labels (account, category, amount)
- LLM fallback - AI categorization when rules don't match
- Template system - Pre-built rule sets for common household types

## Table of Contents

1. [Quick Start](#quick-start)
2. [Rule Types](#rule-types)
3. [Execution Flow](#execution-flow)
4. [Intelligence Modes](#intelligence-modes)
5. [LLM Integration](#llm-integration)
6. [Advanced Patterns](#advanced-patterns)
7. [Best Practices](#best-practices)
8. [Operational Modes](#operational-modes)
9. [Update Strategies](#update-strategies)
10. [Template System](#template-system)
11. [Migration Guide](#migration-guide)
12. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Choose a Template

Start with a pre-built template that matches your household type:

```bash
uv run python scripts/setup/template_selector.py
```

Available templates:
- **Simple** - Single person, no shared expenses
- **Separated Families** - Divorced/separated parents with shared custody
- **Shared Household** - Couples, roommates, or families
- **Advanced** - Business owners, investors, complex finances

### 2. Customize Your Rules

Edit `data/rules.yaml` to match your specific needs:

```yaml
rules:
  # Add your first category rule
  - type: category
    name: Coffee → Dining Out
    patterns: [STARBUCKS, COSTA, CAFE]
    category: Food & Dining > Dining Out
    confidence: 95

  # Add your first label rule
  - type: label
    name: Personal Coffee
    when:
      categories: [Dining Out]
      accounts: [Personal]
    labels: [Discretionary, Personal]
```

### 3. Test Your Rules

Always test before applying to real transactions:

```bash
# Dry run - preview what would happen
uv run python scripts/operations/batch_categorize.py --mode=dry_run --period=2025-11

# Validate - see what would change on existing categorizations
uv run python scripts/operations/batch_categorize.py --mode=validate --period=2025-11

# Apply - actually categorize transactions
uv run python scripts/operations/batch_categorize.py --mode=apply --period=2025-11
```

### 4. Review and Refine

Check the results and refine your rules:

```bash
# See categorization summary
/smith:analyze spending --period=2025-11

# Check uncategorized transactions
/smith:categorize --mode=smart --show-uncategorized
```

## Rule Types

### Category Rules

Categorize transactions based on payee patterns, amounts, and accounts.

**Full Syntax:**

```yaml
- type: category
  name: Rule Name (for logging/display)
  patterns: [PATTERN1, PATTERN2, PATTERN3]  # OR logic
  exclude_patterns: [EXCLUDE1, EXCLUDE2]    # Optional
  category: Category > Subcategory
  confidence: 95                             # 0-100%
  accounts: [Account1, Account2]             # Optional filter
  amount_operator: ">"                       # Optional: >, <, >=, <=, ==, !=
  amount_value: 100.00                       # Required if amount_operator set
```

**Field Descriptions:**

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `type` | Yes | String | Must be "category" |
| `name` | Yes | String | Descriptive name for logs (e.g., "WOOLWORTHS → Groceries") |
| `patterns` | Yes | List[String] | Payee keywords to match (case-insensitive, OR logic) |
| `category` | Yes | String | Category to assign (can include parent: "Parent > Child") |
| `confidence` | No | Integer | Confidence score 0-100% (default: 90) |
| `exclude_patterns` | No | List[String] | Patterns to exclude from match |
| `accounts` | No | List[String] | Only match transactions in these accounts |
| `amount_operator` | No | String | Amount comparison: >, <, >=, <=, ==, != |
| `amount_value` | No | Number | Amount threshold (required if operator set) |

**Examples:**

```yaml
# Basic pattern matching
- type: category
  name: WOOLWORTHS → Groceries
  patterns: [WOOLWORTHS, COLES, ALDI]
  category: Food & Dining > Groceries
  confidence: 95

# With exclusions (exclude UBER EATS from UBER)
- type: category
  name: UBER → Transport
  patterns: [UBER]
  exclude_patterns: [UBER EATS]
  category: Transport
  confidence: 90

# Account-specific rule
- type: category
  name: Work Laptop Purchase
  patterns: [APPLE STORE, MICROSOFT STORE]
  accounts: [Work Credit Card]
  category: Work > Equipment
  confidence: 90

# Amount-based rule (large purchases)
- type: category
  name: Large Electronics
  patterns: [JB HI-FI, HARVEY NORMAN]
  category: Shopping > Electronics
  confidence: 85
  amount_operator: ">"
  amount_value: 500
```

### Label Rules

Apply labels to transactions based on their category, account, amount, or categorization status.

**Full Syntax:**

```yaml
- type: label
  name: Label Rule Name
  when:
    categories: [Category1, Category2]       # Optional (OR logic)
    accounts: [Account1, Account2]           # Optional (OR logic)
    amount_operator: ">"                     # Optional
    amount_value: 100.00                     # Required if operator set
    uncategorized: true                      # Optional (true to match uncategorized)
  labels: [Label1, Label2, Label3]
```

**Important:** All `when` conditions must match (AND logic), but values within each list use OR logic.

**Field Descriptions:**

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `type` | Yes | String | Must be "label" |
| `name` | Yes | String | Descriptive name for logs |
| `when` | Yes | Object | Conditions that must ALL match |
| `when.categories` | No | List[String] | Match if category contains any of these (OR) |
| `when.accounts` | No | List[String] | Match if account name contains any of these (OR) |
| `when.amount_operator` | No | String | Amount comparison: >, <, >=, <=, ==, != |
| `when.amount_value` | No | Number | Amount threshold |
| `when.uncategorized` | No | Boolean | Match uncategorized transactions (true/false) |
| `labels` | Yes | List[String] | Labels to apply when conditions match |

**Examples:**

```yaml
# Category-based labeling
- type: label
  name: Tax Deductible Work Expenses
  when:
    categories: [Work, Professional Development, Home Office]
  labels: [Tax Deductible, ATO: D1]

# Account-based labeling
- type: label
  name: Shared Household Expense
  when:
    accounts: [Shared Bills, Joint Account]
  labels: [Shared Expense, Needs Reconciliation]

# Combined conditions (category AND account)
- type: label
  name: Personal Coffee Spending
  when:
    categories: [Dining Out]
    accounts: [Personal]
  labels: [Discretionary, Personal]

# Amount-based labeling
- type: label
  name: Large Purchase Flag
  when:
    amount_operator: ">"
    amount_value: 500
  labels: [Large Purchase, Review Required]

# Flag uncategorized transactions
- type: label
  name: Needs Categorization
  when:
    uncategorized: true
  labels: [Uncategorized, Needs Review]

# Multi-condition (category AND account AND amount)
- type: label
  name: Large Shared Grocery Trip
  when:
    categories: [Groceries]
    accounts: [Shared Bills]
    amount_operator: ">"
    amount_value: 200
  labels: [Shared Expense, Large Purchase, Needs Approval]
```

## Execution Flow

The unified rule engine uses **two-phase execution** to ensure labels can depend on categories assigned in the same run.

### Phase 1: Categorization

1. Iterate through all category rules in order
2. For each transaction, find the FIRST matching rule
3. Apply the category and confidence score
4. **Short-circuit:** Stop at first match (no further category rules evaluated)
5. Update transaction with matched category for Phase 2

**Rule Order Matters!** Specific rules should come before general rules.

### Phase 2: Labeling

1. Using the transaction (now with category from Phase 1)
2. Check ALL label rules
3. Apply labels from EVERY matching rule (additive)
4. Deduplicate and sort labels

**All Matches Applied!** Unlike categories, ALL matching label rules are applied.

### Example Execution

Transaction: `WOOLWORTHS` in `Shared Bills` account, amount `-$127.50`

**Phase 1 - Category Rules:**

```yaml
# Rule 1 matches!
- type: category
  name: WOOLWORTHS → Groceries
  patterns: [WOOLWORTHS]
  category: Food & Dining > Groceries
  confidence: 95

# Rule 2 would also match but is NOT evaluated (short-circuit)
- type: category
  name: All Food Purchases
  patterns: [WOOLWORTHS, COLES, RESTAURANT]
  category: Food
  confidence: 80
```

**Result after Phase 1:** Category = "Food & Dining > Groceries", Confidence = 95

**Phase 2 - Label Rules:**

```yaml
# Rule 1 matches (category: Groceries, account: Shared Bills)
- type: label
  name: Shared Grocery Expense
  when:
    categories: [Groceries]
    accounts: [Shared Bills]
  labels: [Shared Expense, Essential]

# Rule 2 matches (amount > 100)
- type: label
  name: Large Purchase
  when:
    amount_operator: ">"
    amount_value: 100
  labels: [Large Purchase, Review]

# Rule 3 does NOT match (category doesn't contain "Dining Out")
- type: label
  name: Discretionary Dining
  when:
    categories: [Dining Out]
  labels: [Discretionary]
```

**Final Result:**
- Category: Food & Dining > Groceries
- Confidence: 95
- Labels: Essential, Large Purchase, Review, Shared Expense (sorted, deduplicated)

## Intelligence Modes

Agent Smith has three intelligence modes that control auto-apply behavior based on confidence scores.

### Conservative Mode

**Never auto-applies** - always asks user for confirmation.

```yaml
Confidence Level: ANY
Action: Ask user for approval
Use when: Learning the system, want full control
```

Example:
```
Transaction: STARBUCKS -$6.50
Rule match: "Dining Out" (95% confidence)
→ [Ask User] Apply category "Dining Out"?
  [Yes] [No] [Edit]
```

### Smart Mode (Default)

**Balanced approach** - auto-applies high confidence, asks for medium, skips low.

```yaml
Confidence ≥ 90%:  Auto-apply without asking
Confidence 70-89%: Ask user for approval (LLM validates first)
Confidence < 70%:  Skip (don't categorize)
```

Example:
```
Transaction: UBER -$25.00
Rule match: "Transport" (95% confidence)
→ [Auto-applied] Category: Transport

Transaction: UBER MEDICAL CENTRE -$80
Rule match: "UBER → Transport" (75% confidence)
→ [LLM Validates] This looks like medical, not transport
→ [Suggests] Medical & Healthcare (90% confidence)
→ [Auto-applied] Category: Medical & Healthcare
```

### Aggressive Mode

**More permissive** - auto-applies medium-high confidence, asks for medium-low.

```yaml
Confidence ≥ 80%: Auto-apply without asking
Confidence 50-79%: Ask user for approval
Confidence < 50%: Skip (don't categorize)
```

Example:
```
Transaction: ACME WIDGETS -$245.00
Rule match: "Business Supplies" (82% confidence)
→ [Auto-applied] Category: Business Supplies
```

### Setting the Mode

**In command:**
```bash
/smith:categorize --mode=smart
```

**In environment (.env):**
```bash
DEFAULT_INTELLIGENCE_MODE=smart
```

**In code:**
```python
from scripts.workflows.categorization import CategorizationWorkflow

workflow = CategorizationWorkflow(
    client=client,
    mode="smart"  # conservative, smart, or aggressive
)
```

## LLM Integration

When rule-based categorization fails, Agent Smith falls back to AI-powered categorization using Claude.

### Fallback Categorization

When no rule matches, Agent Smith asks the LLM to suggest a category.

**Flow:**

1. No category rule matches transaction
2. Build LLM prompt with:
   - Full category hierarchy
   - Transaction details (payee, amount, date)
   - Intelligence mode guidance
3. LLM suggests category with confidence and reasoning
4. Apply intelligence mode thresholds:
   - High confidence → Auto-apply (or ask in conservative mode)
   - Medium confidence → Ask user
   - Low confidence → Skip

**Example:**

```
Transaction: ACME WIDGETS LTD -$245.00
No rule match
→ [LLM] Analyzing transaction...
→ [LLM] Suggests: Business Supplies (85% confidence)
   Reasoning: "ACME WIDGETS appears to be a business supplier based on
   naming convention and typical transaction amount."
→ [Smart Mode] 85% is above ask threshold (70%) but below auto (90%)
→ [Ask User] Apply category "Business Supplies"?
   [Yes] [No] [Create Rule]
```

### Validation

Medium-confidence rule matches (70-89% in smart mode) are validated by the LLM to catch edge cases.

**Flow:**

1. Rule matches with medium confidence
2. Build validation prompt with:
   - Transaction details
   - Suggested category
   - Rule confidence
3. LLM responds: CONFIRM or REJECT
   - CONFIRM: Can upgrade confidence → auto-apply
   - REJECT: Suggests alternative category
4. Apply validated result

**Example:**

```
Transaction: UBER MEDICAL CENTRE -$80
Rule match: "UBER → Transport" (75% confidence)
→ [LLM] Validating categorization...
→ [LLM] REJECT - This appears to be a medical facility, not transport
   Suggests: Medical & Healthcare (90% confidence)
→ [Smart Mode] 90% ≥ auto-apply threshold
→ [Auto-applied] Category: Medical & Healthcare
```

### Learning from LLM Results

After the LLM categorizes transactions, Agent Smith offers to create rules for future use.

**Flow:**

1. LLM categorizes N transactions with same merchant
2. Detect pattern: Same payee → Same category
3. Suggest rule creation
4. User approves, edits, or declines
5. If approved: Add rule to `data/rules.yaml`

**Example:**

```
LLM categorized 12 "ACME WIDGETS" transactions as "Business Supplies"

Suggested rule:
  - type: category
    name: ACME WIDGETS → Business Supplies
    patterns: [ACME WIDGETS]
    category: Business Supplies
    confidence: 90

[Create Rule] [Edit Rule] [Decline]

→ User selects [Create Rule]
→ Rule added to data/rules.yaml
→ Future ACME WIDGETS transactions auto-categorized (90% confidence)
```

## Advanced Patterns

### Cross-Category Labels

Apply the same label to multiple categories:

```yaml
# Tax deductible categories
- type: label
  name: ATO Tax Deductible
  when:
    categories: [Work, Professional Development, Home Office, Software]
  labels: [Tax Deductible, ATO: D1]

# Large purchases across all categories
- type: label
  name: Large Purchase Alert
  when:
    amount_operator: ">"
    amount_value: 500
  labels: [Large Purchase, Review Required]
```

### Account-Based Workflows

Different labels for same category in different accounts:

```yaml
# Same category rule for all accounts
- type: category
  name: Transport
  patterns: [UBER, LYFT, TAXI]
  category: Transport
  confidence: 90

# Personal transport
- type: label
  name: Personal Transport
  when:
    categories: [Transport]
    accounts: [Personal]
  labels: [Personal, Discretionary]

# Work transport (reimbursable)
- type: label
  name: Work Transport
  when:
    categories: [Transport]
    accounts: [Work, Personal]  # Can be from either account
    amount_operator: ">"
    amount_value: 20            # But large amounts suggest work trips
  labels: [Work Related, Reimbursable]
```

### Shared Household Expense Tracking

Track who paid for shared expenses:

```yaml
# Shared groceries
- type: category
  name: Shared Groceries
  patterns: [WOOLWORTHS, COLES]
  accounts: [Shared Bills, Joint Account]
  category: Food & Dining > Groceries
  confidence: 95

- type: label
  name: Shared Essential
  when:
    categories: [Groceries]
    accounts: [Shared Bills, Joint Account]
  labels: [Shared Expense, Essential, Needs Reconciliation]

# Large shared purchases need approval
- type: label
  name: Needs Approval
  when:
    accounts: [Shared Bills, Joint Account]
    amount_operator: ">"
    amount_value: 150
  labels: [Needs Approval, Review Required]
```

### Tax Deductible Tracking

Flag potential tax deductions with ATO codes:

```yaml
# Work-related expenses
- type: label
  name: Work Deduction - D1
  when:
    categories: [Work, Office Supplies, Professional Development]
  labels: [Tax Deductible, ATO: D1, Work-related other expenses]

# Home office expenses
- type: label
  name: Home Office Deduction - D2
  when:
    categories: [Home Office, Internet, Phone]
  labels: [Tax Deductible, ATO: D2, Home office expenses]

# Large deductions requiring substantiation
- type: label
  name: Requires Receipt (>$300)
  when:
    labels: [Tax Deductible]  # Note: This won't work! Labels can't check labels
    amount_operator: ">"
    amount_value: 300
  labels: [Substantiation Required, Keep Receipt]
```

**Important:** Label rules cannot check for other labels. Use categories or accounts instead.

### Uncategorized Transaction Management

Flag and prioritize uncategorized transactions:

```yaml
# Flag all uncategorized
- type: label
  name: Needs Categorization
  when:
    uncategorized: true
  labels: [Uncategorized, Needs Review]

# High-priority uncategorized (large amounts)
- type: label
  name: High Priority Uncategorized
  when:
    uncategorized: true
    amount_operator: ">"
    amount_value: 100
  labels: [Uncategorized, High Priority, Urgent Review]

# Uncategorized in shared account
- type: label
  name: Uncategorized Shared Expense
  when:
    uncategorized: true
    accounts: [Shared Bills, Joint Account]
  labels: [Uncategorized, Shared Account, Needs Approval]
```

## Best Practices

### 1. Order Rules Specific → General

Rules are evaluated in order. Put specific rules first:

```yaml
# ✓ GOOD: Specific first
- type: category
  name: UBER EATS → Dining Out
  patterns: [UBER EATS]
  category: Food & Dining > Dining Out
  confidence: 95

- type: category
  name: UBER → Transport
  patterns: [UBER]
  category: Transport
  confidence: 90

# ✗ BAD: General first (UBER catches UBER EATS)
- type: category
  name: UBER → Transport
  patterns: [UBER]
  category: Transport
  confidence: 90

- type: category
  name: UBER EATS → Dining Out  # Never reached!
  patterns: [UBER EATS]
  category: Food & Dining > Dining Out
  confidence: 95
```

**Fix with exclusions:**

```yaml
- type: category
  name: UBER → Transport
  patterns: [UBER]
  exclude_patterns: [UBER EATS]
  category: Transport
  confidence: 90
```

### 2. Use Visual Grouping

Group related rules with comments for easy scanning:

```yaml
# ═══════════════════════════════════════════════════════════
# GROCERIES WORKFLOW
# ═══════════════════════════════════════════════════════════

- type: category
  name: Groceries
  patterns: [WOOLWORTHS, COLES, ALDI]
  category: Food & Dining > Groceries
  confidence: 95

- type: label
  name: Essential Spending
  when:
    categories: [Groceries]
  labels: [Essential, Needs]

- type: label
  name: Shared Groceries
  when:
    categories: [Groceries]
    accounts: [Shared Bills]
  labels: [Shared Expense, Reconciliation]

# ═══════════════════════════════════════════════════════════
# TRANSPORT WORKFLOW
# ═══════════════════════════════════════════════════════════

- type: category
  name: Rideshare
  patterns: [UBER, LYFT]
  exclude_patterns: [UBER EATS]
  category: Transport
  confidence: 90
```

### 3. Start with High Confidence

Begin with rules you're certain about (95%+):

```yaml
# High confidence - very specific merchants
- type: category
  name: WOOLWORTHS → Groceries
  patterns: [WOOLWORTHS]
  category: Food & Dining > Groceries
  confidence: 95

- type: category
  name: AGL → Utilities
  patterns: [AGL]
  category: Bills > Utilities
  confidence: 95
```

Add medium-confidence rules (80-90%) later as you verify:

```yaml
# Medium confidence - could be ambiguous
- type: category
  name: Amazon Purchases
  patterns: [AMAZON]
  category: Shopping
  confidence: 80  # Could be books, electronics, groceries, etc.
```

### 4. Test with Dry Run

Always test before applying to real transactions:

```bash
# Preview what would happen without making changes
uv run python scripts/operations/batch_categorize.py \
  --mode=dry_run \
  --period=2025-11 \
  --limit=50

# See what would change on existing categorizations
uv run python scripts/operations/batch_categorize.py \
  --mode=validate \
  --period=2025-11
```

Review the output carefully before running with `--mode=apply`.

### 5. Version Control Your Rules

Commit `data/rules.yaml` to git to track evolution:

```bash
# After adding/modifying rules
git add data/rules.yaml
git commit -m "rules: add coffee shop categorization with personal label"

# View history
git log --oneline data/rules.yaml

# Compare versions
git diff HEAD~1 data/rules.yaml
```

### 6. Review Rule Performance Regularly

Check rule accuracy monthly:

```bash
# Analyze categorization coverage
/smith:analyze rules --period=last-month

# See which rules are matching most often
/smith:analyze rules --sort=matches

# Find low-accuracy rules
/smith:analyze rules --min-accuracy=80
```

Refine rules that have low accuracy or aren't matching as expected.

### 7. Use Templates as Starting Points

Don't start from scratch - use a template:

```bash
uv run python scripts/setup/template_selector.py
```

Then customize by:
1. Updating merchant names for your region (e.g., WOOLWORTHS → KROGER)
2. Adjusting account names to match your PocketSmith setup
3. Adding your specific categories
4. Fine-tuning confidence scores based on your data

### 8. Document Complex Rules

Add comments explaining non-obvious rules:

```yaml
# Complex rule: UBER is transport UNLESS it's UBER EATS or during work hours
# Work hours trips from Personal account are likely work-related (reimbursable)
- type: category
  name: UBER Transport (Excluding Food Delivery)
  patterns: [UBER]
  exclude_patterns: [UBER EATS, UBER EATS MARKETPLACE]
  category: Transport
  confidence: 90

# Note: Work-related UBER trips need manual review for reimbursement
# They'll get the "Reimbursable" label from the account-based rule below
```

## Operational Modes

The batch processor supports three operational modes for safe rule testing and application.

### DRY_RUN Mode

**Purpose:** Preview what would happen without making any changes.

**Use when:**
- Testing new rules
- Checking rule coverage
- Seeing potential categorizations before committing

**Example:**

```bash
uv run python scripts/operations/batch_categorize.py \
  --mode=dry_run \
  --period=2025-11
```

**Output:**

```
DRY RUN MODE - No changes will be made

Transaction #12345: WOOLWORTHS -$127.50
  → Would categorize as: Food & Dining > Groceries (95% confidence)
  → Would apply labels: [Essential, Shared Expense]

Transaction #12346: STARBUCKS -$6.50
  → Would categorize as: Food & Dining > Dining Out (90% confidence)
  → Would apply labels: [Discretionary, Personal]

Transaction #12347: ACME WIDGETS -$245.00
  → No rule match
  → Would request LLM categorization

Summary:
  Would categorize: 2/3 transactions (66.7%)
  LLM fallback needed: 1 transaction
  No changes made (DRY RUN)
```

### VALIDATE Mode

**Purpose:** Show what would CHANGE on transactions that already have categories.

**Use when:**
- Checking if new rules conflict with existing categorizations
- Planning to update categories with better rules
- Auditing categorization accuracy

**Example:**

```bash
uv run python scripts/operations/batch_categorize.py \
  --mode=validate \
  --period=2025-11
```

**Output:**

```
VALIDATE MODE - Showing potential changes

Transaction #12345: WOOLWORTHS -$127.50
  Current: Food (80% confidence)
  New: Food & Dining > Groceries (95% confidence)
  Change: Category would be updated ✓

Transaction #12346: STARBUCKS -$6.50
  Current: Food & Dining > Dining Out (90% confidence)
  New: Food & Dining > Dining Out (90% confidence)
  Change: No change (same category)

Transaction #12347: UBER -$25.00
  Current: Dining Out (user-assigned)
  New: Transport (90% confidence from rule)
  Change: Category would be REPLACED (was user-assigned!)

Summary:
  Would update: 2 transactions
  Already correct: 1 transaction
  Would replace user assignments: 1 transaction ⚠️
  No changes made (VALIDATE)
```

### APPLY Mode

**Purpose:** Actually apply categorizations and labels to transactions.

**Use when:**
- Ready to commit changes after testing with DRY_RUN/VALIDATE
- Processing new uncategorized transactions
- Updating categorizations with improved rules

**Example:**

```bash
uv run python scripts/operations/batch_categorize.py \
  --mode=apply \
  --period=2025-11 \
  --update-strategy=skip_existing
```

**Output:**

```
APPLY MODE - Making changes to PocketSmith

Transaction #12345: WOOLWORTHS -$127.50
  ✓ Categorized as: Food & Dining > Groceries (95%)
  ✓ Labels applied: [Essential, Shared Expense]

Transaction #12346: STARBUCKS -$6.50
  ⊘ Skipped (already categorized)

Transaction #12347: ACME WIDGETS -$245.00
  → Requesting LLM categorization...
  ? Suggested: Business Supplies (85% confidence)
    [A]ccept  [E]dit  [S]kip  [C]reate Rule
```

## Update Strategies

Control how the batch processor handles transactions that already have categories.

### SKIP_EXISTING (Default)

Only process uncategorized transactions. Leave existing categorizations unchanged.

**Use when:**
- Processing new transactions
- Don't want to override user-assigned categories
- Preserving manual categorization work

```bash
uv run python scripts/operations/batch_categorize.py \
  --mode=apply \
  --update-strategy=skip_existing
```

**Behavior:**
- Uncategorized → Apply rules
- Already categorized → Skip
- User-assigned → Skip

### REPLACE_ALL

Replace ALL categorizations, even if they were user-assigned.

**Use when:**
- Rebuilding all categorizations from scratch
- Confident new rules are better than old assignments
- Fixing systemic categorization errors

**⚠️ Warning:** This will override user-assigned categories!

```bash
uv run python scripts/operations/batch_categorize.py \
  --mode=apply \
  --update-strategy=replace_all
```

**Behavior:**
- Uncategorized → Apply rules
- Already categorized → Replace with rule result
- User-assigned → Replace with rule result (loses user intent!)

### UPGRADE_CONFIDENCE

Replace categorization ONLY if new rule has higher confidence.

**Use when:**
- Improving categorizations with better rules
- Keeping high-confidence assignments
- Upgrading low-confidence auto-categorizations

```bash
uv run python scripts/operations/batch_categorize.py \
  --mode=apply \
  --update-strategy=upgrade_confidence
```

**Behavior:**
- Uncategorized → Apply rules
- Lower confidence → Replace with higher confidence rule
- Higher confidence → Keep existing
- User-assigned (confidence: 100%) → Never replaced

**Example:**

```
Transaction: WOOLWORTHS -$50
Current: Food (80% confidence from old rule)
New: Food & Dining > Groceries (95% confidence from new rule)
→ REPLACED (95% > 80%)

Transaction: STARBUCKS -$6
Current: Dining Out (95% confidence)
New: Dining Out (90% confidence from new rule)
→ KEPT (95% > 90%)
```

### REPLACE_IF_DIFFERENT

Replace categorization if the category NAME differs.

**Use when:**
- Fixing miscategorized transactions
- Migrating to a new category structure
- Correcting category hierarchies

```bash
uv run python scripts/operations/batch_categorize.py \
  --mode=apply \
  --update-strategy=replace_if_different
```

**Behavior:**
- Uncategorized → Apply rules
- Same category → Keep existing
- Different category → Replace with rule result
- User-assigned → Still replaced if different!

**Example:**

```
Transaction: WOOLWORTHS -$50
Current: Food
New: Food & Dining > Groceries
→ REPLACED (different category name)

Transaction: STARBUCKS -$6
Current: Dining Out
New: Dining Out
→ KEPT (same category)
```

## Template System

Agent Smith provides pre-built rule templates for common household types. Templates are stored in `data/templates/` and can be applied to create your `data/rules.yaml`.

### Available Templates

#### 1. Simple - Single Person

**File:** `data/templates/simple.yaml`

**Best for:**
- Single person households
- No shared expenses
- Basic income and expense tracking

**Includes:**
- Income categorization (salary, wages)
- Essential expenses (groceries, utilities, rent)
- Discretionary spending (dining out, entertainment)
- Transport categories
- Basic labels (Essential, Discretionary, Large Purchase)
- Uncategorized flagging

**Example rules:**

```yaml
# Income
- type: category
  patterns: [SALARY, WAGES, EMPLOYER]
  category: Income > Salary
  confidence: 95

# Essential groceries
- type: category
  patterns: [WOOLWORTHS, COLES, ALDI]
  category: Food & Dining > Groceries
  confidence: 95

- type: label
  when:
    categories: [Groceries, Utilities, Rent]
  labels: [Essential]
```

#### 2. Separated Families

**File:** `data/templates/separated-families.yaml`

**Best for:**
- Divorced or separated parents
- Shared custody arrangements
- Child support tracking
- Kids' expense management

**Includes:**
- Kids' expense categories (school, activities, clothing, medical)
- Child support tracking
- Contributor labels (Parent A, Parent B)
- Reimbursement workflows
- School term and vacation labels
- Medical and education receipts flagging

**Example rules:**

```yaml
# Child expenses
- type: category
  patterns: [SCHOOL, UNIFORM, SCHOOL FEES]
  category: Kids > Education
  confidence: 90

- type: label
  when:
    categories: [Kids]
  labels: [Child Expense, Needs Documentation]

# Child support tracking
- type: label
  when:
    patterns: [CHILD SUPPORT]
  labels: [Child Support, Parent B Contribution]

# Shared kid expenses requiring reimbursement
- type: label
  when:
    categories: [Kids]
    amount_operator: ">"
    amount_value: 50
  labels: [Needs Reimbursement, Split 50/50]
```

#### 3. Shared Household

**File:** `data/templates/shared-household.yaml`

**Best for:**
- Couples living together
- Roommates sharing expenses
- Families with joint accounts

**Includes:**
- Shared vs personal expense separation
- Contributor tracking (Person A, Person B)
- Approval workflows (large purchases, discretionary spending)
- Reconciliation labels
- Essential vs discretionary labeling
- Account-based routing (Shared Bills, Personal accounts)

**Example rules:**

```yaml
# Shared essential expenses
- type: category
  patterns: [WOOLWORTHS, COLES]
  accounts: [Shared Bills, Joint Account]
  category: Food & Dining > Groceries
  confidence: 95

- type: label
  when:
    categories: [Groceries]
    accounts: [Shared Bills]
  labels: [Shared Expense, Essential, Monthly Reconciliation]

# Approval workflow for large shared purchases
- type: label
  when:
    accounts: [Shared Bills]
    amount_operator: ">"
    amount_value: 150
  labels: [Needs Approval, Review Required]

# Personal vs shared distinction
- type: label
  when:
    accounts: [Personal, PersonA Account, PersonB Account]
  labels: [Personal, Individual]
```

#### 4. Advanced

**File:** `data/templates/advanced.yaml`

**Best for:**
- Business owners
- Investors and traders
- Complex financial situations
- Tax optimization focus

**Includes:**
- Business expense categories (with ATO codes)
- Investment tracking (shares, crypto, property)
- Tax deductible flagging (work, home office, professional development)
- Capital gains tracking
- Substantiation requirements ($300 threshold)
- Instant asset write-off flagging
- GST tracking
- Business vs personal separation

**Example rules:**

```yaml
# Business expenses
- type: category
  patterns: [OFFICE, STATIONERY, SUPPLIES]
  accounts: [Business, Work]
  category: Work > Office Supplies
  confidence: 90

- type: label
  when:
    categories: [Work, Home Office, Professional Development]
  labels: [Tax Deductible, ATO: D1, Business Expense]

# Investment purchases
- type: category
  patterns: [COMMSEC, SELFWEALTH, STAKE]
  category: Investments > Share Purchase
  confidence: 90

- type: label
  when:
    categories: [Investments]
  labels: [CGT Event, Track Cost Base]

# Substantiation requirements
- type: label
  when:
    labels: [Tax Deductible]
    amount_operator: ">"
    amount_value: 300
  labels: [Receipt Required, ATO Substantiation]
```

### Applying a Template

**Interactive selection:**

```bash
uv run python scripts/setup/template_selector.py
```

**Output:**

```
══════════════════════════════════════════════════════════════════
Agent Smith - Rule Template Setup
══════════════════════════════════════════════════════════════════

Available templates:

1. Simple - Single Person
   Basic categories for individual financial tracking
   Best for: Single person, no shared expenses

2. Separated Families
   Kids expenses, child support, contributor tracking
   Best for: Divorced/separated parents with shared custody

3. Shared Household
   Shared expense tracking with approval workflows
   Best for: Couples, roommates, or families

4. Advanced
   Tax optimization and investment management
   Best for: Business owners, investors, complex finances

Select template (1-4): 3

Applying template: Shared Household
Backed up existing rules to data/rules.yaml.backup
✓ Template applied successfully!

Next steps:
1. Review data/rules.yaml and customize for your needs
2. Update merchant patterns for your region
3. Adjust account names to match your PocketSmith setup
4. Run: /smith:categorize --mode=dry-run to test
```

**Programmatic usage:**

```python
from scripts.setup.template_selector import TemplateSelector

selector = TemplateSelector()

# List templates
templates = selector.list_templates()
for key, info in templates.items():
    print(f"{info['name']}: {info['description']}")

# Apply template
selector.apply_template("shared-household", backup=True)
```

### Customizing Templates

After applying a template:

1. **Update merchant patterns** for your region:
   ```yaml
   # Template (Australian)
   patterns: [WOOLWORTHS, COLES, ALDI]

   # Customize (US)
   patterns: [KROGER, SAFEWAY, WHOLE FOODS]
   ```

2. **Adjust account names** to match your PocketSmith:
   ```yaml
   # Template
   accounts: [Shared Bills, Joint Account]

   # Your setup
   accounts: [Joint Checking, Household Card]
   ```

3. **Add your specific categories**:
   ```yaml
   # Add new rules
   - type: category
     name: Pet Expenses
     patterns: [VET, PET STORE, PETBARN]
     category: Pets > Veterinary
     confidence: 90
   ```

4. **Fine-tune confidence scores** based on your data:
   ```yaml
   # Start conservative
   confidence: 70

   # After validation, increase
   confidence: 90
   ```

## Migration Guide

### From Platform Rules to Unified YAML

If you have existing platform rules created via the PocketSmith API, you can migrate them to the unified YAML format.

**See:** [Platform to Local Rules Migration Guide](platform-to-local-migration.md)

**Quick summary:**

1. Export platform rules to JSON
2. Convert to unified YAML format
3. Test with dry run
4. Disable platform rules (keep for backup)
5. Enable unified rules

**Migration script:**

```bash
uv run python scripts/migrations/migrate_platform_to_local.py \
  --output=data/rules.yaml \
  --backup
```

### Adding Labels to Existing Rules

If you have category rules and want to add labels:

1. Keep all existing category rules as-is
2. Add label rules at the bottom
3. Test with dry run to see labels applied
4. Apply with `--update-strategy=skip_existing` to avoid re-categorizing

**Example:**

```yaml
# Existing category rules (don't change)
- type: category
  name: WOOLWORTHS → Groceries
  patterns: [WOOLWORTHS]
  category: Groceries
  confidence: 95

# NEW: Add label rules
- type: label
  name: Essential Spending
  when:
    categories: [Groceries]
  labels: [Essential, Needs]

- type: label
  name: Large Grocery Trip
  when:
    categories: [Groceries]
    amount_operator: ">"
    amount_value: 150
  labels: [Large Purchase]
```

Run with:
```bash
uv run python scripts/operations/batch_categorize.py \
  --mode=apply \
  --update-strategy=skip_existing \
  --period=2025-11
```

This will:
- Skip already categorized transactions (no re-categorization)
- Apply new labels to all transactions (even already categorized ones)

## Troubleshooting

### Rule Not Matching

**Symptom:** Rule should match but doesn't.

**Check:**

1. **Pattern case sensitivity** - Patterns are case-insensitive, but spacing matters:
   ```yaml
   # Won't match "UBEREATS" (no space)
   patterns: [UBER EATS]

   # Better: account for variations
   patterns: [UBER EATS, UBEREATS]
   ```

2. **Exclusion patterns blocking** - Check if an exclusion is preventing the match:
   ```yaml
   - type: category
     patterns: [UBER]
     exclude_patterns: [UBER EATS, MEDICAL]  # Blocks "UBER MEDICAL"
     category: Transport
   ```

3. **Account filter too restrictive** - Transaction might be in a different account:
   ```yaml
   # Only matches transactions in "Personal" account
   accounts: [Personal]

   # Check transaction's actual account name
   ```

4. **Amount condition incorrect** - Verify the amount operator and value:
   ```yaml
   amount_operator: ">"
   amount_value: 100
   # Won't match transactions ≤ $100
   ```

5. **Rule order** - A previous rule might have matched first (short-circuit):
   ```yaml
   # General rule matches first!
   - patterns: [UBER]
     category: Transport

   # Specific rule never reached
   - patterns: [UBER EATS]
     category: Dining Out  # Dead code!
   ```

**Debug with test script:**

```bash
# Test specific payee
uv run python scripts/operations/test_rules.py \
  --payee="EXACT PAYEE NAME" \
  --account="Account Name" \
  --amount=127.50 \
  --debug
```

**Output:**

```
Testing transaction:
  Payee: EXACT PAYEE NAME
  Account: Account Name
  Amount: $127.50

Checking category rules...
  ✗ Rule 1 "WOOLWORTHS → Groceries": Pattern mismatch
  ✗ Rule 2 "UBER → Transport": Pattern mismatch
  ✗ Rule 3 "CAFE → Dining Out": Pattern mismatch

No category match found.

Checking label rules...
  (skipped - no category assigned)

Result: No categorization
```

### Multiple Rules Matching

**Symptom:** Worried about multiple rules matching the same transaction.

**This is expected!** Category rules use short-circuit (first match wins), label rules accumulate all matches.

**For category rules:**

```yaml
# Only the FIRST matching rule applies
- patterns: [UBER EATS]
  category: Dining Out
  # ✓ This matches UBER EATS

- patterns: [UBER]
  category: Transport
  # ✗ Never reached for UBER EATS (already matched above)
```

**For label rules:**

```yaml
# ALL matching rules apply (additive)
- type: label
  when:
    categories: [Groceries]
  labels: [Essential]
  # ✓ Matches

- type: label
  when:
    amount_operator: ">"
    amount_value: 100
  labels: [Large Purchase]
  # ✓ Also matches

# Result: [Essential, Large Purchase]
```

**Fix unwanted category matches** by adjusting rule order or using exclusions.

**Control label accumulation** by making conditions more specific:

```yaml
# Too broad - applies to ALL transactions
- type: label
  when:
    amount_operator: ">"
    amount_value: 0
  labels: [Has Amount]  # Not useful!

# Better - specific categories only
- type: label
  when:
    categories: [Groceries, Dining Out]
    amount_operator: ">"
    amount_value: 100
  labels: [Large Food Purchase]
```

### Labels Not Applying

**Symptom:** Label rule should match but labels aren't applied.

**Check:**

1. **Category must be assigned first** - Labels depend on Phase 1 categorization:
   ```yaml
   # Label requires category "Groceries"
   - type: label
     when:
       categories: [Groceries]
     labels: [Essential]

   # But transaction wasn't categorized in Phase 1
   # → Label rule won't match
   ```

   **Fix:** Ensure a category rule matches the transaction first.

2. **When conditions too restrictive** - All conditions must match (AND logic):
   ```yaml
   - type: label
     when:
       categories: [Groceries]  # Must match
       accounts: [Shared Bills]  # AND must match
       amount_operator: ">"       # AND must match
       amount_value: 100
     labels: [Large Shared Grocery]

   # Won't match if ANY condition fails
   ```

3. **Uncategorized flag incorrect** - Can't combine with other conditions:
   ```yaml
   # This won't work as expected
   - type: label
     when:
       uncategorized: true
       categories: [Groceries]  # Contradiction! Can't be both uncategorized and have a category
     labels: [Invalid]
   ```

   **Fix:** Use `uncategorized: true` alone or with accounts/amount only.

4. **Labels can't check labels** - You can't reference other labels in conditions:
   ```yaml
   # This WON'T work - no way to check existing labels
   - type: label
     when:
       labels: [Tax Deductible]  # Not supported!
       amount_operator: ">"
       amount_value: 300
     labels: [Substantiation Required]
   ```

   **Fix:** Use categories or accounts as conditions instead.

**Debug:**

```bash
uv run python scripts/operations/test_rules.py \
  --payee="WOOLWORTHS" \
  --account="Shared Bills" \
  --amount=127.50 \
  --category="Groceries" \
  --debug
```

### Confidence Scores Unclear

**Symptom:** Not sure what confidence score to use.

**Guidelines:**

| Confidence | When to Use | Example |
|------------|-------------|---------|
| 95-100% | Exact merchant match, no ambiguity | WOOLWORTHS → Groceries |
| 85-94% | Very likely but minor ambiguity | AMAZON → Shopping (could be many subcategories) |
| 75-84% | Likely but context-dependent | UBER → Transport (unless UBER EATS) |
| 70-74% | Moderate confidence, needs validation | Generic patterns like "MARKET" |
| < 70% | Low confidence, probably shouldn't auto-apply | Broad patterns |

**Smart mode thresholds:**
- ≥ 90%: Auto-apply
- 70-89%: Ask user (with LLM validation)
- < 70%: Skip

**Start high (95%), reduce if:**
- LLM frequently suggests different category
- User frequently overrides
- Pattern matches too broadly

### LLM Not Being Used

**Symptom:** Expected LLM fallback but it's not happening.

**Possible causes:**

1. **Rule matched** - LLM only used when NO rule matches:
   ```
   Transaction: ACME WIDGETS
   Rule match: "Generic Business" pattern [WIDGETS] (75%)
   → Rule applied, LLM not needed
   ```

   **Fix:** Remove overly broad rules if you want LLM to handle edge cases.

2. **Categories not provided** - LLM needs category list:
   ```python
   workflow.categorize_transaction(
       transaction=txn,
       available_categories=None  # ← LLM can't suggest without categories!
   )
   ```

   **Fix:** Pass `available_categories` from PocketSmith API.

3. **Conservative mode + low confidence** - Conservative never auto-applies:
   ```
   Mode: Conservative
   LLM suggests: Business Supplies (85%)
   → Asks user (doesn't auto-apply)
   ```

   This is expected! Conservative always asks.

### Performance Issues

**Symptom:** Batch categorization is slow with many rules.

**Optimizations:**

1. **Reduce rule count** - Consolidate similar patterns:
   ```yaml
   # Before: 3 rules
   - patterns: [WOOLWORTHS]
     category: Groceries
   - patterns: [COLES]
     category: Groceries
   - patterns: [ALDI]
     category: Groceries

   # After: 1 rule
   - patterns: [WOOLWORTHS, COLES, ALDI]
     category: Groceries
   ```

2. **Use account filters** - Skip irrelevant transactions early:
   ```yaml
   # Check account BEFORE pattern matching
   - patterns: [WORK PATTERN]
     accounts: [Work Credit Card]  # Skips 90% of transactions
     category: Work Expenses
   ```

3. **Order by frequency** - Put most common rules first:
   ```yaml
   # Most frequent transaction (groceries) - check first
   - patterns: [WOOLWORTHS, COLES]
     category: Groceries

   # Less frequent - check later
   - patterns: [RARE MERCHANT]
     category: Rare Category
   ```

4. **Limit batch size** - Process in smaller chunks:
   ```bash
   # Instead of processing all at once
   uv run python scripts/operations/batch_categorize.py --period=2025

   # Process month by month
   uv run python scripts/operations/batch_categorize.py --period=2025-01
   uv run python scripts/operations/batch_categorize.py --period=2025-02
   # etc.
   ```

## Examples

See `docs/examples/` for complete example YAML files:

- **basic-rules.yaml** - Simple category and label rules
- **advanced-patterns.yaml** - Complex rules with exclusions, amounts, accounts
- **household-workflow.yaml** - Complete shared household setup
- **tax-deductible.yaml** - Tax optimization rules with ATO codes
- **migration-example.yaml** - Migrated from platform rules

## Further Reading

- **[Platform to Local Migration Guide](platform-to-local-migration.md)** - Migrate existing platform rules to unified YAML
- **[Backup and Restore Guide](backup-and-restore-guide.md)** - Smart backup system with activity-specific rollbacks
- **[Health Check Guide](health-check-guide.md)** - PocketSmith setup health evaluation
- **[Design Document](../design/2025-11-20-agent-smith-design.md)** - Complete Agent Smith architecture

## Support

For questions or issues:
1. Check this guide's troubleshooting section
2. Review example files in `docs/examples/`
3. Check template files in `data/templates/`
4. Refer to design documentation
5. Create an issue in the repository

---

**Last Updated:** 2025-11-22
**Version:** 1.0.0
