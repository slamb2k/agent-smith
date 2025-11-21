# Agent Smith Backup & Restore Guide

## Overview

Agent Smith provides a smart backup system based on PocketSmith best practices research. The system creates activity-specific backups before risky operations and clearly indicates what can and cannot be rolled back.

**Key Finding:** API access is available on ALL PocketSmith tiers (including Free), so Agent Smith works regardless of your subscription level.

## Backup Capabilities

### What CAN Be Backed Up & Restored

✅ **Transactions** (full CRUD support)
- Amounts, dates, payees, categories
- Labels, notes, splits
- Full rollback capability

✅ **Categories** (full CRUD support)
- Category hierarchies
- Metadata
- Can be restored from backup

✅ **Accounts** (full CRUD support)
- Account details, settings, balances
- Can be restored from backup

### What CANNOT Be Fully Restored

⚠️ **Category Rules** (API limitations)
- Can be backed up via API
- Can be created via API
- **CANNOT** be updated or deleted via API
- Must use PocketSmith web interface for modifications
- **Recommendation:** Use Agent Smith's local rule engine instead

❌ **Budgets**
- Not included in PocketSmith CSV backups
- Read-only via API
- Cannot be restored programmatically

❌ **Attachments**
- Not included in CSV backups
- Must download separately via API
- File restoration not automated

❌ **User Preferences**
- Dashboard settings
- Alert configurations
- Not accessible via API

## Activity-Specific Backups

Agent Smith automatically creates backups before these operations:

### Category Operations

**Category Optimization** (`category_optimization`)
- **Rollback:** ❌ No
- **Limitations:**
  - Structure changes cannot be undone
  - Merged categories cannot be unmerged
  - Transaction assignments CAN be restored

**Category Merge** (`category_merge`)
- **Rollback:** ❌ No
- **Limitations:**
  - Cannot unmerge once merged
  - Budgets/rules transfer to target (may duplicate)
  - Transaction assignments CAN be restored

**Category Delete** (`category_delete`)
- **Rollback:** ❌ No
- **Limitations:**
  - Deleted categories cannot be restored
  - Future imports won't auto-map
  - Transactions CAN be re-categorized

### Rule Operations

**Rule Batch Create** (`rule_batch_create`)
- **Rollback:** ❌ No (API limitation)
- **Limitations:**
  - Rules cannot be deleted via API
  - Must use web interface to remove
  - Use local rules for full control

### Transaction Operations

**Transaction Batch Update** (`transaction_batch_update`)
- **Rollback:** ✅ Yes (full support)
- **Limitations:** None
- Restores: amounts, dates, categories, labels, notes, splits

**Transaction Batch Delete** (`transaction_batch_delete`)
- **Rollback:** ✅ Yes
- **Limitations:**
  - Attachments must be restored separately

**Bulk Categorization** (`bulk_categorization`)
- **Rollback:** ✅ Yes (full support)
- **Limitations:** None
- Restores original category assignments

### Account Operations

**Account Delete** (`account_delete`)
- **Rollback:** ❌ No
- **Limitations:**
  - Cannot restore via API
  - Transactions can be restored but orphaned
  - Must manually recreate account first

### Import Operations

**Data Import** (`data_import`)
- **Rollback:** ✅ Yes
- **Limitations:**
  - Requires tracking import batch IDs
  - Can delete imported transactions

## Usage Examples

### Python API

```python
from scripts.utils.smart_backup import SmartBackupManager, ActivityType

manager = SmartBackupManager()

# Before bulk categorization
backup_path = manager.create_activity_backup(
    activity_type=ActivityType.BULK_CATEGORIZATION,
    description="Categorize 150 uncategorized transactions",
    affected_items={"transaction_count": 150}
)

# Perform operation...
# categorize_transactions(transactions)

# Check if rollback is possible
if manager.can_rollback(backup_path):
    print("✅ This operation can be rolled back")
else:
    limitations = manager.get_rollback_limitations(backup_path)
    print("⚠️ Rollback limitations:")
    for lim in limitations:
        print(f"  - {lim}")
```

### Backing Up Data

```python
# Backup transactions
manager.backup_transactions(backup_path, transactions)

# Backup categories
manager.backup_categories(backup_path, categories)

# Backup category rules (with API limitation warning)
manager.backup_category_rules(backup_path, rules)

# Backup accounts
manager.backup_accounts(backup_path, accounts)
```

### Checking Tier Requirements

```python
# Get tier information
tier_info = manager.get_tier_info()
print(tier_info["api_access"])  # "Available on ALL tiers (including Free)"

# Check feature requirements
tier = manager.check_feature_tier("unlimited_accounts")
if tier:
    print(f"Requires: {tier.value} tier or higher")
else:
    print("Available on all tiers")
```

## PocketSmith Subscription Tiers

| Feature | Free | Foundation | Flourish | Fortune |
|---------|------|------------|----------|---------|
| **Price (Annual)** | Free | $9.99/mo AUD | $16.66/mo AUD | $26.66/mo AUD |
| **Price (Monthly)** | Free | $14.95/mo AUD | $24.95/mo AUD | $39.95/mo AUD |
| **API Access** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Accounts** | 2 | Unlimited | Unlimited | Unlimited |
| **Bank Connections** | Manual only | 6 (1 country) | 18 (all countries) | Unlimited |
| **Budgets** | 12 | Unlimited | Unlimited | Unlimited |
| **Forecast** | 6 months | 10 years | 30 years | 60 years |

**Important:** Agent Smith works with ALL tiers. There are no API restrictions based on subscription level.

## Backup Storage & Retention

Agent Smith follows these retention policies:

- **Recent backups:** 30 days in `backups/`
- **Monthly archives:** Compressed backups older than 30 days
- **Tax backups:** 7 years (ATO requirement for Australian users)

## Reconciliation Note

**PocketSmith does NOT have traditional reconciliation** like QuickBooks or Xero.

Instead:
- **Transaction Confirmation Workflow** - Review and approve imported transactions
- **Balance Verification** - Compare PocketSmith balances to bank statements
- **No locking** - Transactions always editable (confirmation is workflow status only)

Agent Smith focuses on:
- Balance verification and gap detection
- Duplicate transaction detection
- Missing transaction identification
- De-emphasizes confirmation status (doesn't prevent edits)

## Best Practices

1. **Before Risky Operations:** Agent Smith automatically creates backups before:
   - Category structure changes
   - Bulk transaction updates
   - Rule batch creation
   - Account deletions

2. **Use Local Rules:** For category rules requiring updates/deletes, prefer Agent Smith's local rule engine over PocketSmith platform rules

3. **Verify Backups:** Check backup metadata before operations:
   ```python
   limitations = manager.get_rollback_limitations(backup_path)
   can_rollback = manager.can_rollback(backup_path)
   ```

4. **Keep Tax Backups:** Retain backups for 7 years for ATO compliance (Australian users)

5. **Test Restores:** Periodically verify backup integrity by testing restores on non-critical data

## Troubleshooting

### "Category rules cannot be restored"
- **Cause:** API limitation - rules can only be created, not updated/deleted
- **Solution:** Use Agent Smith's local rule engine (`data/local_rules.json`) instead
- **Workaround:** Manually delete rules via PocketSmith web interface

### "Deleted category cannot be restored"
- **Cause:** PocketSmith does not support category restoration via API
- **Solution:** Restore transaction category assignments from backup
- **Prevention:** Use category merge instead of delete when possible

### "Attachments missing after restore"
- **Cause:** Attachments not included in transaction data backups
- **Solution:** Download attachments separately before operations
- **Note:** Attachment download/upload supported via API but not automated

## See Also

- [PocketSmith Backup & Limitations Research](../research/pocketsmith-backup-and-limitations-research.md)
- [Health Check Guide](health-check-guide.md)
- [Installation Guide](../../INSTALL.md)
