Evaluate your PocketSmith setup and get optimization recommendations.

## Usage

```
/agent-smith-health [options]
```

## Options

- `--full` - Complete deep analysis (may take longer)
- `--quick` - Fast essential checks only
- `--category=AREA` - Specific area (categories|rules|tax|data)

## Health Checks

**Six Health Scores (0-100):**

1. **Category Health** - Structure, hierarchy, ATO alignment
2. **Rule Coverage** - Auto-categorization rate and accuracy
3. **Data Quality** - Completeness, duplicates, errors
4. **Tax Compliance** - Deduction tracking, substantiation
5. **Budget Alignment** - Spending vs. goals
6. **Account Health** - Balances, reconciliation, connections

## Examples

```bash
# Quick health check (essential checks)
/agent-smith-health --quick

# Full comprehensive analysis
/agent-smith-health --full

# Focus on category structure
/agent-smith-health --category=categories

# Focus on tax compliance
/agent-smith-health --category=tax
```

## What You'll Get

**Overall Health Score:**
- Combined score from all 6 areas
- Pass/Warning/Fail status
- Priority recommendations

**Detailed Scores:**
- Individual scores for each area
- Strengths and weaknesses
- Specific issues identified
- Improvement opportunities

**Recommendations:**
- Prioritized action items
- Expected impact
- Implementation steps
- Quick wins vs. long-term improvements

**Category Health:**
- Category structure analysis
- Unused categories
- ATO alignment issues
- Consolidation opportunities

**Rule Coverage:**
- Auto-categorization rate
- Rule accuracy (override rate)
- Coverage gaps
- Conflicting rules

**Data Quality:**
- Uncategorized transaction count
- Duplicate detection
- Missing payee names
- Date range coverage

**Tax Compliance:**
- Deduction tracking coverage
- Substantiation status
- CGT event tracking
- Missing documentation

**Budget Alignment:**
- Spending vs. budget
- Goal progress
- Trending issues
- Adjustment recommendations

**Account Health:**
- Connection status
- Balance reconciliation
- Transaction import issues
- Stale data alerts

## Health Check Process

1. **Scan:** Analyze PocketSmith data
2. **Score:** Calculate health metrics
3. **Identify:** Find issues and opportunities
4. **Recommend:** Prioritized action plan
5. **Monitor:** Track improvements over time

## Interpreting Scores

- **90-100:** Excellent - Maintain current practices
- **70-89:** Good - Minor improvements available
- **50-69:** Fair - Several issues to address
- **Below 50:** Poor - Significant work needed

---

**Running health check...**
