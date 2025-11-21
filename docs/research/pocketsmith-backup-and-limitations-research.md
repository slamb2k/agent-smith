# PocketSmith Backup, Subscription Tiers, and API Limitations Research

**Research Date:** 2025-11-22
**Purpose:** Comprehensive analysis of PocketSmith backup capabilities, subscription tier features, category rules management, and reconciliation processes
**Sources:** PocketSmith official documentation, API reference, Learn Center articles

---

## Table of Contents

1. [Backup Best Practices](#1-backup-best-practices)
2. [Subscription Tiers](#2-subscription-tiers)
3. [Category Rules & Optimization](#3-category-rules--optimization)
4. [Reconciliation](#4-reconciliation)
5. [Key Takeaways for Agent Smith](#5-key-takeaways-for-agent-smith)

---

## 1. Backup Best Practices

### 1.1 What Can Be Backed Up via API

**Via API (Full CRUD Operations):**
- **Transactions** - Create, read, update, delete
  - Transaction details (amount, date, merchant, payee)
  - Transaction categorization
  - Transaction labels
  - Transaction notes
  - Split transactions
- **Categories** - Create, read, update, delete
  - Category hierarchies and nesting
  - Category metadata
- **Accounts** - Create, read, update, delete
  - Account details and settings
  - Account balances
- **Institutions** - Create, read, update, delete
- **Attachments** - Read attachments via API
  - Supported types: png, jpg, pdf, xls, xlsx, doc, docx
  - Requires `attachments.read` scope
- **Budgets** - Read and retrieve budget data
- **Events** - Manage financial events
- **Saved Searches** - Read saved search queries

**Via Web Interface (CSV Backup/Restore Feature - Released May 2024):**
- Categorized transaction history
- Account names
- Transaction labels and notes
- Account balances
- Bank and account number information

### 1.2 What CANNOT Be Backed Up or Restored

**Not Included in Backups:**
- **Category Rules** - Not included in CSV backup feature
  - Can only be listed (GET) and created (POST) via API
  - No update or delete operations via API
  - Must be managed through web interface
- **Filters** - Not included in backup
- **Saved Searches** - Not included in CSV backup (though accessible via API)
- **Budgets** - Explicitly excluded from CSV backup feature
- **Attachment Files** - Files attached to transactions not included in CSV backup
  - Must be downloaded separately via API if needed
- **User Preferences** - Dashboard settings, alert configurations, etc.

### 1.3 Rollback/Restore Capabilities

**Limited Undo Functionality:**
- **Auto-organize Categories** - Temporary undo available immediately after auto-organizing
  - Undo button appears on screen for limited time only
  - Can revert categories back to previous state
- **Transaction Restore** - CSV backup can restore transactions with categories, labels, notes, balances
- **Account Deletion** - Cannot be undone; account and all transactions permanently removed
- **Category Deletion** - No undo functionality; permanent deletion unless reassigned first
- **Category Rules** - No undo when deleting via web interface

**What CANNOT Be Rolled Back:**
- Category merges (unless done via auto-organize within the temporary undo window)
- Account deletions
- Category rule deletions
- Account resets (permanent and irreversible)

### 1.4 Community Recommendations

**Official Security & Data Protection Measures:**
- **Encryption:** All data encrypted in transit (TLS) and at rest (device-level encryption)
- **Two-Factor Authentication:** Available to all users (all tiers including free)
- **Login Monitoring:** All successful logins logged and viewable in Security settings
- **Data Deletion:** Complete permanent deletion from production databases and third-party providers on account closure
- **Privacy:** PocketSmith commits to never selling personal information

**Best Practices (Based on Official Documentation):**
- Use the Transaction Backup and Restore feature regularly (Manage > Transaction backup and restore)
- Do NOT edit backup CSV files in Excel (causes compatibility issues)
- Export data before performing account resets or major changes
- For historical data beyond bank feed limits, manually upload bank files
- Monitor login attempts for suspicious activity
- Enable two-factor authentication

### 1.5 Bank Feed Transaction History Limits

**Initial Import Limits by Provider:**
- **Yodlee:** 1 year or more (sometimes only 90 days)
- **Basiq (Australia):** 2 years (per CDR legislation)
- **Salt Edge (UK & EU):** Up to 1 year
- **Akahu (New Zealand):** Up to 1 year (occasionally only 90 days)
- **Plaid (Canada & US):** Up to 2 years

**Note:** These are guidelines only; actual results vary by bank and provider.

**Workaround for Older Data:**
- Upload bank files (OFX, QFX, QIF, CSV) directly to import historical transactions beyond feed limits

---

## 2. Subscription Tiers

### 2.1 Tier Comparison

| Feature | Free | Foundation | Flourish | Fortune |
|---------|------|------------|----------|---------|
| **Monthly Price** | Free | AUD $14.95 | AUD $24.95 | AUD $39.95 |
| **Annual Price** | Free | AUD $9.99/mo | AUD $16.66/mo | AUD $26.66/mo |
| **Savings (Annual)** | - | 33% | 33% | 33% |
| **Target User** | Casual budgeter | Financial tracker | Household CFO | Financial expert |
| **Accounts** | 2 | Unlimited | Unlimited | Unlimited |
| **Connected Banks** | - | 6 (1 country) | 18 (all countries) | Unlimited (all countries) |
| **Bank Feeds** | Manual imports only | Automatic | Automatic | Automatic |
| **Dashboards** | 2 | 6 | 18 | Unlimited |
| **Budgets** | 12 | Unlimited | Unlimited | Unlimited |
| **Forecast/Projection** | 6 months | 10 years | 30 years | 60 years |
| **Email Support** | - | ✓ | ✓ | ✓ |
| **Priority Support** | - | - | - | ✓ |

### 2.2 Features Available Across All Paid Tiers

**Core Features (Foundation, Flourish, Fortune):**
- Category rules
- Saved searches
- Transaction history (unlimited historical storage)
- Bank file uploads (OFX, QFX, QIF, CSV)
- Customizable budgets
- Rollover budgeting
- Safe balance calculations
- Visualization tools
- Reporting dashboards
- Multi-currency support
- Advisor access for account sharing
- Two-factor authentication
- Attachment support (files and photos on transactions)

### 2.3 API Access by Tier

**Critical Finding: API Access is Tier-Agnostic**

- **All tiers** (including Free) have full API access
- No restrictions based on subscription level
- API is "available for anyone to use without restriction and free of charge"
- Developer keys available to all users
- OAuth 2.0 available for multi-user applications (requires registration)

**API Authentication:**
- **Developer Keys:** Personal use, persistent access to your own account
  - Generated via Profile menu > Security & integrations
  - Key shown only once at creation
  - Can be revoked anytime
- **OAuth 2.0:** Multi-user applications
  - Requires email registration to [email protected]
  - Provides client_id and client_secret
  - Access tokens expire after 1 hour (3600 seconds)

**Rate Limiting:**
- No publicly documented rate limits
- API stated as "without restriction"
- Best practice: Implement conservative rate limiting in client applications
- Monitor response headers for any rate limit information (X-RateLimit-* headers)

### 2.4 Transaction History Limits

**Important Distinction:**
- **Projection/Forecast Limits:** Vary by tier (6 months to 60 years into future)
- **Historical Transaction Storage:** Unlimited for all tiers
  - No documented limits on how many past transactions can be stored
  - Limitations only on initial bank feed imports (90 days to 2 years depending on provider)
  - Manual file uploads allow importing unlimited historical data

**Free Tier Specific Limitations:**
- Only 2 accounts
- Manual imports only (no automatic bank feeds)
- 12 budgets maximum
- 6 months of future projections
- 2 dashboards

---

## 3. Category Rules & Optimization

### 3.1 Category Rules Management

**What Are Category Rules:**
- Automated rules that assign categories to transactions based on merchant keywords
- Only the first matching filter or category rule applies to each transaction
- Filters are checked before category rules
- Priority system: lowest number to highest number

**Creating Rules:**
- Via Web Interface: Manage > Category Rules, Saved Searches and Filters
- Via API: POST `/v2/categories/{id}/category_rules`
  - Can apply rule to all uncategorized transactions
  - Can apply rule to all transactions (regardless of current categorization)

**Editing Rules:**
- Via Web Interface: Select rule, click three-dot menu > Edit
  - Best practice: Make keywords as simple as possible for broader matching
  - Remove dates, times, account numbers for better pattern matching
- Via API: No PUT endpoint available (cannot update existing rules)

**Deleting Rules:**
- Via Web Interface: Three-dot menu > Delete
  - Can delete entire rule (removes all merchant keywords)
  - Can delete specific merchant keywords while keeping rule
  - Requires confirmation
- Via API: No DELETE endpoint available (cannot remove rules)

### 3.2 API Limitations for Category Rules

**Available Operations:**
- `GET /users/{id}/category_rules` - List all category rules for a user
- `POST /categories/{id}/category_rules` - Create new category rule

**Missing Operations:**
- No PUT endpoint (cannot update existing rules)
- No DELETE endpoint (cannot remove rules)
- No PATCH endpoint (cannot partially modify rules)

**Implications:**
- Category rules created via API cannot be modified or deleted via API
- Must use web interface to edit or delete rules
- External tracking required for rule management in applications
- Agent Smith must maintain local rule registry for rules created via platform API

### 3.3 Category Optimization & Merging

**Category Deletion Process:**
1. Navigate to Manage > Categories
2. Select category > three-dot menu > Delete
3. Choose whether to reassign transactions, budgets, and rules to another category

**If Reassigning to Another Category:**
- All transactions migrate to selected category
- Associated budgets transfer over (may create multiple budgets on target category - not recommended)
- Category rules and filters are reassigned

**If NOT Reassigning:**
- All transactions become uncategorized
- All budgets permanently deleted
- Category rules and filters permanently deleted

**Category Mapping:**
- PocketSmith tracks all category deletions and name changes
- Future bank feed imports automatically map to new category names
- Deleted category names result in uncategorized transactions

**Undo Capabilities:**
- **Auto-organize feature only:** Temporary undo button appears after auto-organizing
  - Available for limited time after operation
  - Can revert all changes made by auto-organize
- **Manual category merges:** No undo functionality
- **Category deletions:** No undo; permanent unless reassignment chosen

### 3.4 Backup Status of Category Rules

**Critical Finding: Category Rules Cannot Be Backed Up**

- Not included in CSV backup/restore feature (released May 2024)
- Can be listed via API but not exported in bulk
- When resetting account, separate option exists to "remove all saved searches and filters"
  - Treated as distinct from transaction data
- No documented way to backup category rule configurations

**Workaround for Agent Smith:**
- Maintain local copy of all category rules in `data/platform_rules.json`
- Track rule creation, modification, and deletion
- Implement rule export functionality via API listing
- Provide rule recreation capability from local backup

---

## 4. Reconciliation

### 4.1 What is PocketSmith Reconciliation?

**Important: PocketSmith Does NOT Have Traditional Reconciliation**

Unlike accounting software (e.g., QuickBooks, Xero), PocketSmith does not feature a formal reconciliation process. Instead, it provides:

**Transaction Confirmation Workflow:**
- **Awaiting Confirmation Page** - Review newly imported transactions
  - Compare with online banking statements
  - Approve transactions individually with OK ✓ button
  - Choose to confirm every transaction or only specific types
- Purpose: Verify accuracy of imported transactions

### 4.2 Balance Verification Approach

**PocketSmith's Method:**
- Calculates historical balances by adding/subtracting transactions from current balance
- If current balance is correct, historical balance discrepancies indicate:
  - Duplicate transactions
  - Missing transactions
  - Incorrect transaction amounts

**Recommended Process:**
1. Compare PocketSmith historical balances with bank statement balances
2. Identify date where deviation first occurs
3. Compare transactions around that date
4. Look for duplicates or missing entries
5. Verify current balance is accurate

**No Reconciliation Locking:**
- Transactions are not "locked" or "reconciled" to specific statements
- No formal period-end reconciliation process
- Continuous verification through balance comparison

### 4.3 What Changes During Transaction Confirmation?

**When Confirming Transactions:**
- Transactions move from "Awaiting Confirmation" to confirmed status
- No change to transaction data itself
- Simply marks user has reviewed and approved the transaction
- Does not lock or prevent future edits

**Transaction Status:**
- Unconfirmed: Newly imported, awaiting review
- Confirmed: User has reviewed and approved
- Transactions can still be edited, deleted, or recategorized after confirmation

### 4.4 Can Transaction Confirmation Be Undone?

**Findings:**
- No documented "undo confirmation" feature
- Transactions can be manually edited or deleted at any time (confirmed or not)
- No reconciliation lock prevents modifications
- No formal rollback of confirmation status

**Practical Implications:**
- Transaction confirmation is more of a workflow marker than a permanent state change
- Focus should be on transaction accuracy rather than confirmation status
- Balance verification is more important than confirmation workflow

---

## 5. Key Takeaways for Agent Smith

### 5.1 Backup Strategy Implementation

**Comprehensive Backup Approach:**

1. **Transaction Data:**
   - Use CSV backup feature via web interface (most complete for transactions)
   - Supplement with API exports for programmatic access
   - Backup frequency: Before any bulk operations or mutations

2. **Category Rules:**
   - Must maintain separate local tracking in `data/platform_rules.json`
   - Export via API listing: `GET /users/{id}/category_rules`
   - Track creation timestamp, source (platform vs local engine), and full rule definition

3. **Attachments:**
   - Not included in CSV backup
   - Download separately via API if needed: `GET /transactions/{id}/attachments`
   - Store with transaction ID reference for restoration

4. **Budgets:**
   - Not included in CSV backup
   - Must be tracked separately if restoration needed
   - API access available for reading budget data

5. **Categories:**
   - Included in transaction categorization in CSV backup
   - Category structure can be reconstructed from API
   - Track custom categories in local storage

**Recommended Backup Implementation:**
```bash
# Backup priority hierarchy:
1. CSV export via web interface (primary transaction backup)
2. API-based category rules listing (rules not in CSV)
3. API-based attachment downloads (files not in CSV)
4. API-based budget exports (budgets not in CSV)
5. Local rule engine data (local_rules.json - not in PocketSmith at all)
```

### 5.2 Hybrid Rule Engine Considerations

**Platform Rules (via PocketSmith API):**
- Simple keyword matching only
- Created via POST `/categories/{id}/category_rules`
- Cannot be updated or deleted via API
- Must track externally in `data/platform_rules.json`
- Included in CSV backup? **NO** - requires separate tracking
- Auto-apply server-side (always active)

**Local Rules (Agent Smith Engine):**
- Regex patterns, multi-condition logic, confidence scoring
- Stored in `data/local_rules.json`
- Full CRUD capabilities
- Not synchronized to PocketSmith
- Can be backed up completely under Agent Smith control

**Decision Tree for Rule Creation:**
```
Is pattern simple keyword-only?
├─ YES: Consider platform rule
│   ├─ Benefit: Auto-applies server-side to new transactions
│   ├─ Cost: Cannot modify/delete via API, must track externally
│   └─ Action: Create via API + store in platform_rules.json
└─ NO: Use local rule engine
    ├─ Benefit: Full control, complex patterns, confidence scores
    ├─ Cost: Must process transactions client-side
    └─ Action: Store in local_rules.json only
```

**Recommendation:**
- Prefer local rule engine for most use cases (full control, full backup)
- Use platform rules only when:
  1. User explicitly requests server-side automation
  2. Pattern is simple keyword match
  3. Willing to accept manual web interface edits if changes needed

### 5.3 API Integration Requirements

**API Access Tier Requirements:**
- **None** - All tiers including Free have full API access
- No rate limiting documented
- Implement conservative client-side rate limiting via `API_RATE_LIMIT_DELAY`

**Required Implementation:**
- Developer key authentication via `X-Developer-Key` header
- Error handling for HTTP status codes (401, 403, 404, 500)
- Pagination for list endpoints
- Token refresh for OAuth (if ever implemented for multi-user)

**Critical API Limitations to Handle:**
1. Category rules: Read and create only (no update/delete)
2. Attachments: Can read but not included in bulk backup
3. No bulk export endpoint (must paginate through resources)
4. No documented rate limits (implement conservative approach)

### 5.4 Subscription Tier Handling

**User Communication:**
- All API features available to all users (including Free tier)
- Limitations affect PocketSmith web interface usage:
  - Free: 2 accounts, manual imports only
  - Foundation: 6 accounts, automatic feeds
  - Flourish/Fortune: More accounts, longer projections

**Agent Smith Feature Availability:**
- Do NOT restrict features based on PocketSmith subscription tier
- API access is universal
- Only consider account limits when analyzing multiple accounts
- Inform user if they need to upgrade for more accounts, but Agent Smith functions work for all

### 5.5 Category Optimization Safety

**Before Category Operations:**
1. **Always backup first:**
   - CSV export via web interface
   - API export of category rules
   - Capture current category structure

2. **Warn user about irreversible operations:**
   - Category merges (except auto-organize within undo window)
   - Category deletions
   - Account deletions

3. **Provide rollback plan:**
   - "This operation cannot be undone via PocketSmith"
   - "Backup created at: [timestamp]"
   - "Restore requires manual recreation or CSV import"

4. **Test with reassignment:**
   - When deleting categories, always offer reassignment option
   - Prevent accidental uncategorization of transactions
   - Warn about multiple budget creation on target categories

### 5.6 Reconciliation Strategy

**Agent Smith Reconciliation Feature:**

Since PocketSmith has no formal reconciliation:

1. **Balance Verification Reports:**
   - Compare PocketSmith balances vs expected balances
   - Identify discrepancies by date
   - Flag potential duplicates or missing transactions

2. **Transaction Confirmation Workflow:**
   - Optional: Use PocketSmith's confirmation feature
   - Agent Smith guidance: "Review X unconfirmed transactions"
   - Low priority (confirmation doesn't lock transactions)

3. **Duplicate Detection:**
   - More valuable than confirmation workflow
   - Scan for duplicate merchant/amount/date combinations
   - Offer bulk duplicate resolution

4. **Missing Transaction Detection:**
   - Analyze balance gaps
   - Suggest date ranges to investigate
   - Recommend manual transaction creation or file import

**Reconciliation Priority:**
- Focus on balance accuracy and duplicate detection
- De-emphasize transaction confirmation status
- No "reconciliation lock" needed (PocketSmith doesn't support it)

### 5.7 Data Protection Recommendations

**For Agent Smith Users:**

1. **Regular Backups:**
   - Automatic backup before mutations (already in design)
   - Weekly scheduled backups (optional user configuration)
   - Pre-EOFY backup (June for Australian users)

2. **Retention Policy:**
   - Backups: 30 days recent → monthly archives
   - Align with existing Agent Smith retention policies
   - Tax-related backups: 7 years (ATO requirement)

3. **Security:**
   - Never commit `.env` (API keys)
   - Enable 2FA on PocketSmith account
   - Monitor login activity regularly
   - Encrypt local backup files if they contain sensitive data

4. **Validation:**
   - Verify backup integrity after creation
   - Test restore capability periodically
   - Check backup includes all expected data types

---

## 6. Sources

### Official Documentation
- **PocketSmith Backup & Restore:** https://learn.pocketsmith.com/article/1455-backup-and-restore-your-pocketsmith-data
- **PocketSmith API Documentation:** https://developers.pocketsmith.com/
- **Subscription Plans:** https://my.pocketsmith.com/plans
- **Category Rules Management:** https://learn.pocketsmith.com/article/649-editing-category-rules
- **Transaction Confirmation:** https://learn.pocketsmith.com/article/63-confirming-imported-transactions
- **Security Practices:** https://www.pocketsmith.com/security/

### API Reference
- **API Introduction:** https://developers.pocketsmith.com/docs/introduction
- **Category Rules Endpoint:** https://developers.pocketsmith.com/reference/get_users-id-category-rules-1
- **OpenAPI Specification:** https://github.com/pocketsmith/api/blob/master/openapi.json

### Additional Resources
- **Bank Feed Limits:** https://learn.pocketsmith.com/article/280-bank-feed-transaction-history-limits
- **Developer Keys:** https://learn.pocketsmith.com/article/1538-pocketsmith-api-developer-keys
- **Category Management:** https://learn.pocketsmith.com/article/675-editing-and-deleting-categories
- **Transaction Attachments:** https://learn.pocketsmith.com/article/1276-attaching-files-and-photos-to-transactions

---

**Research Completed:** 2025-11-22
**Document Version:** 1.0
**Next Update:** As needed when PocketSmith releases API updates or new features
