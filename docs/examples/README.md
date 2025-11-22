# Example YAML Files

This directory contains example YAML rule files demonstrating various patterns and use cases for the unified rules system.

## Available Examples

### [basic-rules.yaml](basic-rules.yaml)

**Level:** Beginner

**Description:** Simple category and label rules for getting started with the unified rules system.

**Includes:**
- Basic pattern matching (groceries, transport, utilities)
- Pattern exclusions (UBER vs UBER EATS)
- Simple labels (Essential, Discretionary)
- Large purchase flagging
- Uncategorized transaction flagging

**Use this when:** You're new to Agent Smith and want to understand the basics.

---

### [advanced-patterns.yaml](advanced-patterns.yaml)

**Level:** Intermediate/Advanced

**Description:** Complex rules demonstrating advanced features like account-specific routing, amount-based logic, and multi-condition labels.

**Includes:**
- Account-specific categorization (same merchant, different accounts)
- Amount-based rules (small coffee vs large coffee order)
- Complex exclusions (WOOLWORTHS groceries vs petrol)
- Multi-condition labels (category AND account AND amount)
- Cross-category patterns (tax deductible across multiple categories)
- High-priority uncategorized flagging

**Use this when:** You need sophisticated rules for complex financial situations.

---

### [household-workflow.yaml](household-workflow.yaml)

**Level:** Intermediate

**Description:** Complete shared household setup with approval workflows and reconciliation tracking.

**Includes:**
- Shared vs personal expense separation
- Contributor tracking (Alice, Bob)
- Approval workflows (large purchases, discretionary spending)
- Monthly and annual reconciliation items
- Error detection (personal expenses on shared account)
- Household maintenance tracking

**Use this when:** You're managing finances with a partner, roommate, or family.

---

### [tax-deductible.yaml](tax-deductible.yaml)

**Level:** Advanced

**Description:** Tax deduction tracking with Australian ATO codes and substantiation requirements.

**Includes:**
- Work-related expenses (ATO: D1)
- Home office deductions (ATO: D2)
- Work-related travel (ATO: D3)
- Self-education expenses (ATO: D4)
- Investment deductions
- Rental property deductions
- Substantiation requirements ($300 threshold, $75 for taxi/Uber)
- Instant asset write-off (<$20,000)
- CGT event tracking
- GST tracking for businesses

**Use this when:** You're optimizing for tax deductions and ATO compliance (Australian taxpayers).

---

## Using These Examples

### 1. View an Example

```bash
cat docs/examples/basic-rules.yaml
```

### 2. Copy to Your Rules File

```bash
# Copy entire example
cp docs/examples/basic-rules.yaml data/rules.yaml

# Or merge specific sections manually
```

### 3. Test Before Applying

```bash
# Dry run to preview results
uv run python scripts/operations/batch_categorize.py \
  --mode=dry_run \
  --period=2025-11
```

### 4. Customize for Your Needs

Edit `data/rules.yaml` to:
- Update merchant names for your region
- Adjust account names to match your PocketSmith
- Add your specific categories
- Fine-tune confidence scores

## Combining Examples

You can combine multiple examples into a single `data/rules.yaml`:

```yaml
# Start with basic rules
# (copy from basic-rules.yaml)

rules:
  # Basic groceries
  - type: category
    patterns: [WOOLWORTHS, COLES]
    category: Groceries
    confidence: 95

  # Add household-specific rules
  # (copy from household-workflow.yaml)

  - type: label
    name: Shared Expense
    when:
      accounts: [Shared Bills]
    labels: [Shared Expense]

  # Add tax tracking
  # (copy from tax-deductible.yaml)

  - type: label
    name: Tax Deductible
    when:
      categories: [Work]
    labels: [Tax Deductible, ATO: D1]
```

## Template vs Example Files

**Templates** (`data/templates/`) are complete, ready-to-use rule sets you can apply with the template selector.

**Examples** (`docs/examples/`) are educational files showing specific patterns and techniques.

Use templates to get started quickly, then refer to examples to learn advanced patterns.

## Further Reading

- **[Unified Rules Guide](../guides/unified-rules-guide.md)** - Complete reference documentation
- **[Template Selector](../../data/templates/)** - Pre-built rule sets for common households
- **[Design Document](../design/2025-11-20-agent-smith-design.md)** - Architecture and design decisions

## Contributing

If you've created useful rule patterns, consider sharing them:

1. Add a new example YAML file
2. Document the use case and patterns
3. Add to this README
4. Submit a pull request

---

**Last Updated:** 2025-11-22
