# Migrating from Platform Rules to Local Rules

## Why Migrate?

**Platform rules** (created via PocketSmith API) have significant limitations:
- ✗ Cannot modify or delete via API
- ✗ Keyword-only matching (no regex patterns)
- ✗ No confidence scoring
- ✗ No performance tracking
- ✗ Cannot combine with labels
- ✗ No visibility into which rule applied
- ✗ No exclusion patterns

**Local rules** (YAML-based) provide full control:
- ✓ Full CRUD operations (create, read, update, delete)
- ✓ Regex patterns with exclusions
- ✓ Confidence scoring (0-100%)
- ✓ Performance tracking (accuracy metrics)
- ✓ Integrated with labeling system
- ✓ Complete audit trail
- ✓ Amount ranges and account filters
- ✓ Priority-based matching

## Migration Strategy

### Option 1: Automated Migration (Recommended)

Use the migration utility to automatically convert all platform rules:

```bash
# Dry run first to preview changes
uv run python scripts/migrations/migrate_platform_to_local.py --dry-run

# Run the actual migration
uv run python scripts/migrations/migrate_platform_to_local.py
```

**What this does:**
1. Fetches all platform rules from PocketSmith API
2. Converts each to YAML format with metadata
3. Creates a timestamped backup of existing `rules.yaml`
4. Appends converted rules to `rules.yaml`
5. Preserves original rule IDs in metadata for tracking

**Example conversion:**

Platform rule (via API):
```json
{
  "rule_id": 12345,
  "category_id": 67890,
  "payee_contains": "WOOLWORTHS"
}
```

Converts to YAML:
```yaml
- type: category
  name: WOOLWORTHS → Groceries
  patterns: [WOOLWORTHS]
  category: Groceries
  confidence: 95
  metadata:
    migrated_from_platform: true
    original_rule_id: 12345
    migrated_at: 2025-11-22T12:00:00
```

### Option 2: Manual Migration

For fine-tuned control, manually convert each rule:

#### Step 1: Export Platform Rules

```bash
uv run python -c "
from scripts.core.rule_engine import RuleEngine
from scripts.core.api_client import PocketSmithClient

client = PocketSmithClient()
engine = RuleEngine()
engine.sync_platform_rules(client)
print('Platform rules exported to data/platform_rules.json')
"
```

#### Step 2: Review Exported Rules

Open `data/platform_rules.json` and review your platform rules.

#### Step 3: Convert to YAML

For each platform rule, create a corresponding YAML entry in `data/rules.yaml`:

**Simple keyword rule:**
```yaml
- type: category
  name: UBER → Transport
  patterns: [UBER]
  category: Transport
  confidence: 90
```

**Enhanced with exclusions:**
```yaml
- type: category
  name: UBER → Transport (not UBER EATS)
  patterns: [UBER]
  exclude_patterns: [UBER EATS]
  category: Transport
  confidence: 90
```

**Enhanced with regex:**
```yaml
- type: category
  name: Coffee shops
  patterns: ['STARBUCKS.*', 'COSTA COFFEE.*', '.*CAFE.*']
  category: Dining Out
  confidence: 85
```

#### Step 4: Test Local Rules

Test with dry-run mode to verify matches:

```bash
uv run python scripts/operations/categorize_batch.py --dry-run --period=2025-11
```

Review output to ensure local rules match the same transactions.

### Step 5: Leave Platform Rules in Place

**Important:** You cannot delete platform rules via the API.

**Recommendation:** Leave platform rules active. They will continue to auto-categorize transactions when they sync from your bank. Agent Smith's local rules will supplement and enhance categorization without conflicts.

**Alternative:** Manually delete via PocketSmith web interface if you want to remove them entirely.

## Comparison Examples

### Before: Platform Rule

Created via API:
```python
api_client.create_category_rule(
    category_id=12345,
    payee_matches="UBER"
)
```

**Limitations:**
- Can't distinguish UBER from UBER EATS
- Can't track how often it's correct
- Can't add labels like "Business" or "Personal"
- Can't modify without manual web interface changes

### After: Local Rule with Labels

YAML rule:
```yaml
# Category rule with exclusion
- type: category
  name: UBER → Transport (exclude food delivery)
  patterns: [UBER]
  exclude_patterns: [UBER EATS]
  category: Transport
  confidence: 90

# Label rule for business transport
- type: label
  name: Business Transport
  payee_patterns: [UBER]
  category_patterns: [Transport]
  labels: [Business, Tax Deductible]
  confidence: 80

# Label rule for personal transport
- type: label
  name: Personal Transport (weekends)
  payee_patterns: [UBER]
  category_patterns: [Transport]
  day_of_week: [Saturday, Sunday]
  labels: [Personal]
  confidence: 85
```

**Benefits:**
- Precise matching with exclusions
- Combined with intelligent labeling
- Confidence-based application
- Full performance tracking
- Easy to modify and maintain

## Advanced Migration Scenarios

### Scenario 1: Split Single Platform Rule

If a platform rule is too broad, split it into multiple local rules:

**Platform rule:**
```json
{"payee_contains": "CAFE"}
```

**Split into targeted local rules:**
```yaml
- type: category
  name: Starbucks cafes
  patterns: [STARBUCKS]
  category: Dining Out
  confidence: 95

- type: category
  name: Costa Coffee
  patterns: [COSTA COFFEE]
  category: Dining Out
  confidence: 95

- type: category
  name: Generic cafes
  patterns: ['.*CAFE.*']
  category: Dining Out
  confidence: 75
```

### Scenario 2: Add Amount-Based Rules

Platform rules can't filter by amount. Local rules can:

```yaml
- type: category
  name: Large grocery shops
  patterns: [WOOLWORTHS, COLES]
  amount_min: 100
  category: Groceries
  confidence: 95

- type: label
  name: Weekly shop
  category_patterns: [Groceries]
  amount_min: 100
  labels: [Weekly Shop, Household]
  confidence: 90
```

### Scenario 3: Account-Specific Rules

Platform rules apply to all accounts. Local rules can target specific accounts:

```yaml
- type: category
  name: Business fuel (company card only)
  patterns: [SHELL, BP, CALTEX]
  account_ids: [12345]  # Company credit card
  category: Vehicle Expenses
  confidence: 95

- type: label
  name: Business expense
  account_ids: [12345]
  labels: [Business, Tax Deductible]
  confidence: 100
```

## Post-Migration Workflow

### 1. Monitor Rule Performance

Use the UnifiedRuleEngine to track rule accuracy:

```bash
uv run python scripts/operations/analyze_rule_performance.py
```

This shows:
- How often each rule matches
- User override rate (accuracy indicator)
- Suggested confidence adjustments

### 2. Refine Rules Based on Data

Review low-accuracy rules and refine:

```yaml
# Before: Low accuracy (75%)
- type: category
  name: Transport
  patterns: [UBER]
  confidence: 90

# After: Split with exclusions (95% accuracy)
- type: category
  name: UBER rides
  patterns: [UBER]
  exclude_patterns: [UBER EATS]
  confidence: 95

- type: category
  name: UBER food delivery
  patterns: [UBER EATS]
  category: Dining Out
  confidence: 95
```

### 3. Add Labels for Enhanced Analysis

Complement category rules with labels:

```yaml
# Tax-deductible transport
- type: label
  name: Tax deductible transport
  category_patterns: [Transport]
  payee_patterns: [UBER, TAXI]
  labels: [Tax Deductible, Business]
  confidence: 80
  metadata:
    tax_category: Work-related travel expenses
    ato_section: D9
```

## Troubleshooting

### Platform rules not appearing in export

**Cause:** Platform rules may not be accessible via API for all account types.

**Solution:** Manually note rules from PocketSmith web interface and create equivalent YAML rules.

### Duplicate categorizations

**Cause:** Both platform and local rules matching the same transaction.

**Solution:** This is expected behavior. PocketSmith applies platform rules on sync; Agent Smith applies local rules during batch operations. No conflicts occur.

### Migration script fails with API error

**Cause:** API rate limiting or network issues.

**Solution:** Retry after a few minutes. Use `--dry-run` mode to test without API calls.

### Converted rules have wrong category names

**Cause:** Category IDs may have changed or categories renamed.

**Solution:** Manually review `data/rules.yaml` after migration and update category names as needed.

## Best Practices

### 1. Start with High-Confidence Rules

Migrate platform rules that were working well first:

```yaml
- type: category
  name: Proven high-accuracy rule
  patterns: [WOOLWORTHS]
  category: Groceries
  confidence: 95  # High confidence for proven matches
```

### 2. Use Metadata for Tracking

Include metadata to track migration source:

```yaml
- type: category
  name: Migrated rule
  patterns: [UBER]
  category: Transport
  confidence: 90
  metadata:
    migrated_from_platform: true
    original_rule_id: 12345
    migration_date: 2025-11-22
    notes: Original platform rule was too broad
```

### 3. Combine with LLM Categorization

Use local rules for known patterns, LLM for new transactions:

```yaml
# Known merchants → high confidence rules
- type: category
  name: Known groceries
  patterns: [WOOLWORTHS, COLES, IGA]
  category: Groceries
  confidence: 95

# Unknown merchants fall through to LLM categorization
# LLM suggests category, user approves, new rule is created
```

### 4. Regular Performance Review

Schedule monthly reviews:

```bash
# Generate performance report
uv run python scripts/operations/analyze_rule_performance.py --output=report.md

# Review low-accuracy rules
uv run python scripts/operations/find_low_accuracy_rules.py --threshold=80
```

## Getting Help

If you encounter issues during migration:

1. Check migration logs for errors
2. Review `data/rules.yaml.backup_*` files to restore if needed
3. Test with `--dry-run` mode before committing changes
4. Use `/smith:categorize` command for interactive testing
5. See `docs/design/2025-11-20-agent-smith-design.md` for detailed rule engine documentation

## Summary

Platform rules served their purpose but have significant limitations. Migrating to local YAML rules unlocks:

- **Precision**: Regex patterns and exclusions for exact matching
- **Intelligence**: Confidence scoring and performance tracking
- **Flexibility**: Labels, amount ranges, account filters
- **Maintainability**: Full CRUD operations, version control
- **Integration**: Seamless combination with LLM categorization

Use the automated migration script for quick conversion, then enhance rules over time based on performance data.
