Categorize uncategorized transactions in PocketSmith with AI assistance.

## Usage

```
/agent-smith-categorize [options]
```

## Options

- `--mode=MODE` - Intelligence level (conservative|smart|aggressive) [default: smart]
- `--period=PERIOD` - Target period (YYYY-MM or YYYY) [default: all time]
- `--account=ID` - Limit to specific account [default: all accounts]
- `--dry-run` - Preview categorization without applying changes

## Intelligence Modes

**Conservative:**
- Only auto-categorize high-confidence matches (>90%)
- Require manual review for medium/low confidence
- Best for: First-time setup, important accounts

**Smart (default):**
- Auto-categorize high confidence (>90%)
- Auto-categorize medium confidence (>70%) with existing rules
- Review low confidence (<70%)
- Best for: Regular use, balanced automation

**Aggressive:**
- Auto-categorize all matches above 50% confidence
- Learn from patterns even with lower confidence
- Best for: High-volume accounts, established rule base

## Examples

```bash
# Categorize all uncategorized transactions (smart mode)
/agent-smith-categorize

# Aggressive mode for November 2025
/agent-smith-categorize --mode=aggressive --period=2025-11

# Preview changes without applying (dry-run)
/agent-smith-categorize --dry-run

# Conservative mode for specific account
/agent-smith-categorize --mode=conservative --account=12345
```

## How It Works

1. **Fetch uncategorized transactions** from PocketSmith
2. **Smart orchestration:**
   - < 100 transactions: Direct categorization in main context
   - > 100 transactions: Delegate to specialized subagent for speed
3. **Apply rules:** Match against existing platform and local rules
4. **Learn patterns:** Suggest new rules from categorization
5. **User review:** Present results and any manual review items
6. **Apply changes:** Update PocketSmith (unless --dry-run)

## What You'll See

**Progress:**
- Transaction count and date range
- Categorization status (applying rules, learning patterns)
- Real-time progress for large batches

**Results:**
- Categorized count and percentage
- Rules applied
- New rules suggested
- Manual review items (if any)

**Next Steps:**
- Review and approve new rules
- Handle manual review items
- Run again to catch any remaining uncategorized

---

**Starting categorization workflow...**
