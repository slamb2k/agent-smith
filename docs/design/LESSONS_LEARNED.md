# Lessons Learned from PocketSmith Migration

**Date:** 2025-11-23
**Source:** build/ directory reference materials (now archived)

This document captures key insights from a previous PocketSmith category migration project that informed Agent Smith's design.

---

## Table of Contents

1. [API Quirks and Workarounds](#api-quirks-and-workarounds)
2. [Category Hierarchy Best Practices](#category-hierarchy-best-practices)
3. [Transaction Categorization Patterns](#transaction-categorization-patterns)
4. [Merchant Name Normalization](#merchant-name-normalization)
5. [User Experience Lessons](#user-experience-lessons)

---

## API Quirks and Workarounds

### Category Rules API Limitations

**Issue:** PocketSmith API does not support updating or deleting category rules.
- GET `/categories/{id}/category_rules` works
- POST works (create only)
- PUT/PATCH/DELETE return 404 errors

**Impact:** Rules created via API cannot be modified programmatically.

**Agent Smith Solution:** Hybrid rule engine with local rules for complex logic, platform rules for simple keywords only.

### Transaction Migration 500 Errors

**Issue:** Bulk transaction updates sometimes fail with 500 Internal Server Errors.

**Root Cause:** Likely API rate limiting or server-side stability issues.

**Agent Smith Solution:**
- Implement rate limiting (0.1-0.5s delay between requests)
- Batch processing with progress tracking
- Retry logic with exponential backoff
- Always backup before bulk operations

### Special Characters in Category Names

**Issue:** Using "&" in category names causes 422 Unprocessable Entity errors.

**Workaround:** Replace "&" with "and" in all category names.

**Example:**
- ❌ "Takeaway & Food Delivery" → 422 error
- ✅ "Takeaway and Food Delivery" → Success

### Use PUT instead of PATCH

**Issue:** PATCH for transaction updates is unreliable in PocketSmith API.

**Solution:** Always use PUT for transaction updates.

```python
# ✅ Correct
response = requests.put(
    f'https://api.pocketsmith.com/v2/transactions/{txn_id}',
    headers=headers,
    json={'category_id': category_id}
)

# ❌ Avoid (unreliable)
response = requests.patch(...)
```

---

## Category Hierarchy Best Practices

### Parent-Child Structure

**Recommendation:** Use 2-level hierarchy maximum.
- 12-15 parent categories for broad grouping
- 2-5 children per parent for specific tracking
- Avoid 3+ levels (PocketSmith UI gets cluttered)

**Example Structure:**
```
Food & Dining (parent)
├── Groceries
├── Restaurants
├── Takeaway and Food Delivery
└── Coffee Shops
```

### Duplicate Category Detection

**Problem:** Duplicate categories accumulate over time, causing confusion.

**Solution:** Before creating categories, check for existing matches:
1. Flatten nested category structure
2. Check both exact matches and case-insensitive matches
3. Check for variations (e.g., "Takeaway" vs "Takeaways")

**Agent Smith Implementation:** Category validation in health check system.

### Consolidation Strategy

**Insight:** Merging duplicate categories is risky:
- Requires migrating all associated transactions
- Transaction updates can fail (500 errors)
- Better to prevent duplicates than merge later

**Agent Smith Approach:** Template-based setup with validation prevents duplicates upfront.

---

## Transaction Categorization Patterns

### Pattern Matching Complexity

**Observation:** Transaction categorization evolved through multiple rounds:
- Round 1: Simple keyword matching (60% coverage)
- Round 2: Pattern matching with normalization (80% coverage)
- Round 3: User clarifications + edge cases (90% coverage)
- Round 4: Manual review of exceptions (95% coverage)

**Lesson:** Need both automated rules AND user override capability.

**Agent Smith Solution:** Tiered intelligence modes (Conservative/Smart/Aggressive) with confidence scoring.

### Confidence-Based Auto-Apply

**Insight:** Not all matches are equal:
- High confidence (95%+): Auto-apply safe (e.g., "WOOLWORTHS" → Groceries)
- Medium confidence (70-94%): Ask user (e.g., "LS DOLLI PL" → Coffee?)
- Low confidence (<70%): Always ask (e.g., "Purchase At Kac" → ???)

**Agent Smith Implementation:**
```python
if confidence >= 90:  # Smart mode threshold
    apply_automatically()
elif confidence >= 70:
    ask_user_for_approval()
else:
    skip_or_manual_review()
```

### Dry-Run Mode is Critical

**Lesson:** Always preview before bulk operations.

**Pattern from migration:**
```python
class BulkCategorizer:
    def __init__(self, dry_run=True):  # Default to dry-run!
        self.dry_run = dry_run

    def categorize_transactions(self):
        if self.dry_run:
            # Show what WOULD happen
            return preview
        else:
            # Actually execute
            return results
```

**Agent Smith Implementation:** All bulk operations support `--mode=dry_run` flag.

---

## Merchant Name Normalization

### Common Payee Patterns

**Observations from transaction data:**

1. **Location codes:** "WOOLWORTHS 1234" → "WOOLWORTHS"
2. **Legal suffixes:** "COLES PTY LTD" → "COLES"
3. **Country codes:** "UBER AU" → "UBER"
4. **Transaction codes:** "PURCHASE NSWxxx123" → "PURCHASE"
5. **Direct debit patterns:** "DIRECT DEBIT 12345" → "DIRECT DEBIT"

**Agent Smith Patterns:**
```python
LOCATION_CODE_PATTERN = r"\s+\d{4,}$"
SUFFIX_PATTERNS = [
    r"\s+PTY\s+LTD$",
    r"\s+LIMITED$",
    r"\s+LTD$",
    r"\s+AU$",
]
```

### Merchant Variation Grouping

**Problem:** Same merchant appears with multiple names:
- "woolworths"
- "WOOLWORTHS PTY LTD"
- "Woolworths 1234"
- "WOOLWORTHS SUPERMARKETS"

**Solution:** Learn canonical names from transaction history.

**Agent Smith Implementation:** `MerchantNormalizer.learn_from_transactions()` in scripts/utils/merchant_normalizer.py:101-130

---

## User Experience Lessons

### Backups are Non-Negotiable

**Critical Lesson:** ALWAYS backup before mutations.

**Migration practice:**
```python
def categorize_transactions(self):
    # Step 1: Always backup first
    self.backup_transactions()

    # Step 2: Then execute
    self.apply_changes()
```

**Agent Smith Policy:** Automatic backups before all mutation operations, tracked in backups/ directory.

### Progress Visibility Matters

**Problem:** Long-running operations feel broken without progress indicators.

**Solution:** Show progress every N iterations:
```python
for i, txn in enumerate(transactions, 1):
    # Process transaction

    if i % 100 == 0:
        print(f"Progress: {i}/{total} ({i/total*100:.1f}%)")
```

**Agent Smith Implementation:** All batch operations show real-time progress.

### Manual Cleanup is Inevitable

**Reality Check:** Even after 5+ rounds of automated categorization, ~5% of transactions needed manual review.

**Reasons:**
- Genuinely ambiguous merchants ("Purchase At Kac" = gambling)
- One-off transactions (unique payees)
- Data quality issues (missing/incorrect payee names)

**Agent Smith Approach:** Make manual review easy with health check reports showing uncategorized transactions.

### Weekly Review Habit

**Post-migration recommendation:** Review recent transactions weekly for first month.

**Why:** Helps catch:
- Miscategorized transactions
- New merchants needing rules
- Changes in spending patterns

**Agent Smith Feature:** Smart alerts with weekly budget reviews (Phase 7).

---

## Implementation Timelines

### Migration Timeline (Reality vs Plan)

**Planned:** 35 minutes total
**Actual:** 3+ hours over multiple days

**Breakdown:**
- Category structure migration: 10 minutes (as planned)
- Rule recreation: 20 minutes (10 minutes planned - API limitations doubled time)
- Transaction categorization Round 1: 30 minutes
- Transaction categorization Round 2: 45 minutes
- Transaction categorization Round 3: 60 minutes
- Manual cleanup and verification: 90 minutes

**Lesson:** Budget 3-5x estimated time for data migration projects.

**Agent Smith Design:** Incremental onboarding (30-60 minutes initial setup, ongoing refinement).

---

## Key Takeaways for Agent Smith

### What We Built Better

1. **Hybrid Rule Engine:** Local + Platform rules overcome API limitations
2. **Confidence Scoring:** Tiered auto-apply based on pattern strength
3. **Merchant Intelligence:** Learned normalization from transaction history
4. **Health Checks:** Proactive detection of category/rule issues
5. **Template System:** Pre-built rule sets prevent common mistakes

### What We Avoided

1. **Manual rule migration** - Templates and import/export instead
2. **Duplicate categories** - Validation and health checks
3. **Bulk update failures** - Rate limiting, retry logic, batching
4. **Lost context** - Comprehensive backups with metadata
5. **User fatigue** - Incremental categorization, not all-at-once

### Core Principles

✅ **Backup before mutations**
✅ **Dry-run before execute**
✅ **Progress visibility**
✅ **Confidence-based automation**
✅ **User choice over forced automation**
✅ **Learn from transaction history**
✅ **Graceful degradation** (LLM fallback when rules don't match)

---

## Reference

**Original Materials:** Archived from `build/` directory (removed 2025-11-23)

**Full backup available at:** `../budget-smith-backup-20251120_093733/`

**See Also:**
- [Agent Smith Design](2025-11-20-agent-smith-design.md) - Complete system design
- [Unified Rules Guide](../guides/unified-rules-guide.md) - Rule engine documentation
- [Health Check Guide](../guides/health-check-guide.md) - Health scoring system

---

**Last Updated:** 2025-11-23
