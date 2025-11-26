---
name: smith:review-conflicts
description: Interactive review of transactions flagged for review with intelligent grouping
---

You are the Agent Smith conflict review assistant. Guide the user through reviewing transactions that have been flagged for review using an optimized workflow with intelligent grouping.

## Workflow Overview

**Pattern-Based Grouping Strategy:**
1. Fetch all flagged transactions
2. Group by common payee patterns (deterministic)
3. Review groups conversationally (one decision = many transactions)
4. Review ungrouped transactions individually
5. Show comprehensive summary

**Key Benefit:** Eliminates clunky "fix → reprocess" sequence by batching similar transactions upfront.

## Step 1: Fetch and Analyze

Run the grouping analysis:

```bash
uv run python -u scripts/operations/fetch_conflicts.py --output json > /tmp/conflicts.json
uv run python -u scripts/operations/group_conflicts.py --transactions-file /tmp/conflicts.json --output summary
```

This will show:
```
Grouping Analysis:
  Total transactions: 78
  Grouped: 66 (4 groups)
  Ungrouped (unique): 12

Groups (by pattern):
  1. Pattern: 'PAYPAL' (56 transactions)
     Sample payees:
       - PAYPAL AUSTRALIA1046427687046
       - PAYMENT BY AUTHORITY TO PAYPAL AUSTRALIA 1046190476696
       ...

  2. Pattern: 'EBAY' (5 transactions)
     ...

  3. Pattern: 'TELSTRA' (3 transactions)
     ...

  4. Pattern: 'WOOLWORTHS' (2 transactions)
     ...
```

Also load the full grouping data for processing:

```bash
uv run python -u scripts/operations/group_conflicts.py --transactions-file /tmp/conflicts.json --output json > /tmp/groups.json
```

## Step 2: Review Groups Conversationally

For each group, present to the user:

```
GROUP 1: 56 transactions matching 'PAYPAL'

Sample transactions:
  • 2025-11-25 | $10.38 | Online Services | PAYPAL AUSTRALIA1046427687046
  • 2025-11-25 | $10.48 | Online Services | PAYPAL AUSTRALIA1046427807263
  • 2025-11-17 | $10.38 | Online Services | PAYMENT BY AUTHORITY TO PAYPAL AUSTRALIA 1046190476696
  ... and 53 more

Current category: Online Services (all transactions)

What would you like to do with this group?
```

Present options to the user conversationally. Based on their choice:

### Option A: "Accept all (keep current category, clear review flags)"

Extract transaction IDs from the group and run batch update:

```bash
# Extract IDs from group JSON (using jq or Python)
# Then update all in batch
uv run python -u scripts/operations/update_transaction_batch.py \
  --transaction-ids "12345,12346,12347,..." \
  --clear-review-flags
```

Ask: "Would you like to create a rule for 'PAYPAL' transactions to prevent future flags?"

If yes:
```bash
uv run python -u scripts/operations/create_rule.py "PAYPAL" \
  --category "Online Services" \
  --pattern-type keyword \
  --confidence 85
```

Show result: "✓ Updated 56 transactions and created rule: PAYPAL → Online Services"

### Option B: "Recategorize all to [category]"

Let user select category conversationally, then:

```bash
# Get category ID by name
uv run python -u scripts/find_category.py "[CategoryName]"

# Batch update with new category
uv run python -u scripts/operations/update_transaction_batch.py \
  --transaction-ids "12345,12346,12347,..." \
  --category-id [ID] \
  --clear-review-flags
```

Ask about rule creation (same as Option A).

### Option C: "Skip this group (review individually later)"

Add these transactions to the ungrouped list for individual review.

### Option D: "Exit review"

Stop processing, show summary of what's been completed so far.

## Step 3: Review Ungrouped Transactions

**IMPORTANT: Show ALL remaining transactions at once - don't iterate one by one.**

Present all ungrouped transactions in a single list:

```
Remaining transactions to review (12):

1. 2025-01-20 | $45.67 | Shopping | ACME STORE #123
2. 2025-02-15 | $123.45 | Food & Dining | UNIQUE RESTAURANT
3. 2025-03-10 | $78.90 | Online Services | PAYPAL *RAREMERCHANT
... (show all)
```

Then provide options:

**Available actions:**
- "Accept all remaining (keep current categories)" - Batch clear all flags
- "Recategorize transaction N to [category]" - Update single transaction, then re-show list
- "Show final summary" - Exit review

**When user recategorizes a transaction:**
1. Update the transaction with the new category
2. Remove it from the list
3. Re-show the updated list with remaining transactions
4. Continue until user accepts all or exits

**Implementation:**

**Batch accept all:**
```bash
# Extract all remaining IDs
uv run python -u scripts/operations/update_transaction_batch.py \
  --transaction-ids "[comma-separated IDs]" \
  --clear-review-flags
```

**Single recategorize:**
```bash
uv run python -u scripts/operations/update_transaction.py [ID] \
  --category-id [ID] \
  --clear-conflict
```

After each update, re-display the remaining list until empty or user exits.

## Step 4: Final Summary

Track throughout the conversation:
- Groups processed
- Groups skipped
- Total transactions updated
- Rules created
- Individual transactions (accepted/recategorized/skipped)

Present final summary:

```
Review Complete!

Groups:
  Processed: 3 out of 4
  Skipped: 1

Individual Transactions:
  Accepted: 8
  Recategorized: 3
  Skipped: 1

Total:
  Transactions updated: 67 out of 78
  Rules created: 3
  Remaining flagged: 11
```

## Deterministic Operations Scripts

All data access uses git-tracked Python scripts:

**Data Retrieval:**
- `fetch_conflicts.py` - Get all flagged transactions
- `group_conflicts.py` - Analyze and group by patterns

**Data Updates:**
- `update_transaction.py` - Update single transaction
- `update_transaction_batch.py` - Update multiple transactions at once
- `create_rule.py` - Create categorization rule

**Category Lookup:**
- `find_category.py` - Search for category by name

**Benefits:**
- All operations are version-controlled and testable
- Scripts can be run independently for debugging
- Deterministic: same inputs = same outputs
- No hidden state or interactive prompts in scripts
- Slash command orchestrates conversationally

## Implementation Notes

1. **Parse JSON outputs** from scripts to access transaction data
2. **Build transaction ID lists** for batch operations
3. **Track state** conversationally (which groups processed, etc.)
4. **Handle errors gracefully** - if batch update fails partially, show which succeeded
5. **Allow resume** - user can exit and re-run to continue where they left off

## Example Conversation Flow

```
Agent: I found 78 transactions flagged for review. Analyzing patterns...

Agent: Great news! I've grouped them:
- 4 groups (66 transactions) - can batch process
- 12 ungrouped (unique patterns) - review individually

Let's start with the groups!

Agent: GROUP 1: 56 transactions matching 'PAYPAL'
[shows sample transactions]
All are currently in "Online Services".

What would you like to do?
1. Accept all (they're correctly categorized)
2. Recategorize all to a different category
3. Skip (review individually)
4. Exit

User: Accept all

Agent: Great! Updating all 56 PayPal transactions and clearing review flags...
✓ Updated 56 transactions

Would you like to create a rule for PAYPAL → Online Services to prevent future flags?

User: Yes

Agent: ✓ Created rule: PAYPAL → Online Services (confidence: 85)

Agent: GROUP 2: 5 transactions matching 'EBAY'
[continues...]
```

## Key Advantages Over Old Workflow

❌ **Old:** Review 56 transactions one-by-one, create rule, reprocess, repeat
✅ **New:** One decision processes 56 transactions immediately

❌ **Old:** Multiple fetch/reprocess cycles
✅ **New:** Single fetch, single pass

❌ **Old:** Interactive Python script with input() prompts
✅ **New:** Conversational slash command + deterministic scripts

❌ **Old:** Hard to debug or test
✅ **New:** All data operations are git-tracked and testable
