# Agent Smith Health Check Guide

## Introduction

The Agent Smith health check system provides a comprehensive assessment of your PocketSmith financial setup. It analyzes six key dimensions of your financial data management, identifies issues, and provides prioritized recommendations for improvement.

**Why use health checks?**

- **Proactive Issue Detection**: Catch problems before they affect your financial tracking
- **Continuous Improvement**: Track your setup quality over time with actionable metrics
- **Tax Readiness**: Ensure your categorization and data quality meet compliance requirements
- **Optimization Guidance**: Get specific recommendations to improve automation and accuracy

---

## The Six Health Dimensions

Agent Smith evaluates your PocketSmith setup across six weighted dimensions:

### 1. Data Quality (25% weight)

The foundation of accurate financial tracking. This dimension measures:

| Metric | Description | Target |
|--------|-------------|--------|
| Uncategorized Rate | Percentage of transactions without categories | < 5% |
| Duplicate Detection | Potential duplicate transactions identified | 0 |
| Data Gaps | Missing transaction periods | None |
| Description Quality | Transactions with meaningful descriptions | > 90% |

**Why it matters**: Poor data quality cascades into inaccurate reports, missed deductions, and unreliable budgets.

### 2. Category Structure (20% weight)

How well your category hierarchy is organized:

| Metric | Description | Target |
|--------|-------------|--------|
| Category Depth | Optimal nesting (2-4 levels) | Balanced |
| Unused Categories | Categories with no transactions | < 10% |
| Unclassified Amounts | Money in catch-all categories | < 3% |
| Category Distribution | Even spread across categories | No outliers |

**Why it matters**: A well-structured category system makes analysis meaningful and tax preparation straightforward.

### 3. Rule Engine (15% weight)

Effectiveness of your categorization rules:

| Metric | Description | Target |
|--------|-------------|--------|
| Rule Coverage | Transactions matched by rules | > 80% |
| Rule Efficiency | Rules that actively match transactions | > 70% |
| Conflict Detection | Rules with overlapping patterns | 0 |
| Pattern Quality | Specificity of rule patterns | High |

**Why it matters**: Strong rules reduce manual categorization work and ensure consistency.

### 4. Tax Readiness (15% weight)

Preparedness for tax reporting and compliance:

| Metric | Description | Target |
|--------|-------------|--------|
| Tax Category Coverage | Deductible expenses properly categorized | > 95% |
| Business/Personal Split | Clear separation where required | Complete |
| Receipt Documentation | Transactions over $82.50 with receipts | 100% |
| GST Tracking | GST amounts recorded where applicable | Complete |

**Why it matters**: Poor tax categorization means missed deductions and compliance risks.

### 5. Automation (10% weight)

Level of automated financial management:

| Metric | Description | Target |
|--------|-------------|--------|
| Savings Automation | Automated transfers to savings | Active |
| Bill Scheduling | Recurring bills tracked | > 90% |
| Account Sync Freshness | Time since last sync | < 24 hours |
| Auto-categorization Rate | Transactions auto-categorized | > 85% |

**Why it matters**: Automation reduces manual effort and prevents missed payments.

### 6. Budget Alignment (15% weight)

How well actual spending matches budgets:

| Metric | Description | Target |
|--------|-------------|--------|
| Budget Variance | Difference from planned amounts | < 10% |
| Overspending Categories | Categories over budget | < 20% |
| Budget Coverage | Expenses covered by budgets | > 80% |
| Forecast Accuracy | Predicted vs actual spending | > 85% |

**Why it matters**: Budget alignment indicates financial discipline and planning accuracy.

---

## How to Run Health Checks

### Using the Slash Command

Run a health check using the Agent Smith command:

```
/agent-smith-health
```

### Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `full` | Complete analysis of all dimensions | `/agent-smith-health full` |
| `quick` | Fast check of critical metrics only | `/agent-smith-health quick` |
| `dimension` | Check specific dimension | `/agent-smith-health data-quality` |
| `compare` | Compare to previous check | `/agent-smith-health compare` |

### What Happens During a Health Check

1. **Data Collection**: Agent Smith queries your PocketSmith account
2. **Analysis**: Each dimension is evaluated against benchmarks
3. **Scoring**: Individual and overall scores are calculated
4. **Recommendations**: Prioritized action items are generated
5. **Report**: Results are displayed and optionally saved

---

## Interpreting Scores

### Score Ranges

| Range | Rating | Meaning |
|-------|--------|---------|
| 90-100 | Excellent | Your setup is optimized and well-maintained |
| 70-89 | Good | Solid foundation with minor improvements possible |
| 50-69 | Needs Attention | Several areas require improvement |
| 0-49 | Critical | Significant issues affecting financial tracking |

### Status Indicators

Throughout health check results, you will see these status indicators:

| Indicator | Meaning |
|-----------|---------|
| `[PASS]` | Metric meets or exceeds target |
| `[WARN]` | Metric is below target but not critical |
| `[FAIL]` | Metric requires immediate attention |

### Dimension Breakdown

Each dimension shows:
- **Score**: 0-100 for that dimension
- **Weight**: How much it contributes to overall score
- **Contribution**: Weighted points added to total
- **Status**: Overall health of that dimension

---

## Understanding Recommendations

Health checks generate prioritized recommendations to improve your score.

### Priority Levels

| Priority | Description | Action Timeframe |
|----------|-------------|------------------|
| **Critical** | Issues affecting data integrity or compliance | Immediate (today) |
| **High** | Significant impact on accuracy or efficiency | This week |
| **Medium** | Improvements for better organization | This month |
| **Low** | Nice-to-have optimizations | When convenient |

### Effort Estimates

Each recommendation includes an effort estimate:

| Effort | Typical Time | Examples |
|--------|--------------|----------|
| **Quick Win** | < 15 minutes | Enable a setting, create one rule |
| **Moderate** | 15-60 minutes | Reorganize categories, review duplicates |
| **Significant** | 1-4 hours | Major category restructure, bulk updates |

### Acting on Recommendations

Recommendations follow this format:

```
[PRIORITY] Recommendation Title
  Issue: What the problem is
  Impact: Why it matters
  Action: Specific steps to fix it
  Effort: Time estimate
```

**Best practice**: Start with critical/quick-win items for maximum impact with minimum effort.

---

## Automated Monitoring

### Weekly Health Checks

Agent Smith can run automated weekly health checks:

- **Schedule**: Every Sunday at midnight (configurable)
- **Storage**: Results saved to `data/health/weekly/`
- **Comparison**: Automatic comparison to previous week

### Score Drop Alerts

Get notified when your health score changes significantly:

| Alert Type | Trigger | Priority |
|------------|---------|----------|
| Critical Drop | Score falls below 50 | High |
| Significant Drop | Score drops > 15 points | Medium |
| Dimension Alert | Any dimension falls to Critical | High |
| Improvement | Score increases > 10 points | Info |

### Configuring Alerts

Set alert preferences in your environment or config:

```bash
# .env
HEALTH_CHECK_ALERTS=true
HEALTH_CHECK_THRESHOLD=15
```

Or in `data/config.json`:

```json
{
  "healthCheck": {
    "weeklyEnabled": true,
    "alertOnDrop": true,
    "dropThreshold": 15,
    "notificationMethod": "summary"
  }
}
```

---

## Example Output

Here is a sample health check result:

```
================================================================================
                        AGENT SMITH HEALTH CHECK
                           2025-01-15 09:30 AM
================================================================================

OVERALL SCORE: 74/100 [GOOD]

--------------------------------------------------------------------------------
DIMENSION BREAKDOWN
--------------------------------------------------------------------------------

  Data Quality          [################----]  80/100  (25%)  = 20.0 pts
  Category Structure    [###############-----]  75/100  (20%)  = 15.0 pts
  Rule Engine           [############--------]  60/100  (15%)  =  9.0 pts  [WARN]
  Tax Readiness         [################----]  82/100  (15%)  = 12.3 pts
  Automation            [##############------]  70/100  (10%)  =  7.0 pts
  Budget Alignment      [##############------]  72/100  (15%)  = 10.8 pts

--------------------------------------------------------------------------------
KEY METRICS
--------------------------------------------------------------------------------

  [PASS] Uncategorized transactions: 3.2% (target: <5%)
  [PASS] Duplicate transactions: 0 found
  [WARN] Rule coverage: 68% (target: >80%)
  [PASS] Tax categories mapped: 94%
  [WARN] Budget variance: 12% (target: <10%)

--------------------------------------------------------------------------------
RECOMMENDATIONS (5)
--------------------------------------------------------------------------------

  [CRITICAL] Quick Win
    Create rules for top 10 uncategorized merchants
    Issue: 15 merchants account for 60% of uncategorized transactions
    Impact: Could improve rule coverage by 12%
    Action: Run `/agent-smith-categorize analyze` to generate rules
    Effort: 15 minutes

  [HIGH] Moderate
    Review category "Other Expenses"
    Issue: $2,340 in catch-all category this month
    Impact: Affects reporting accuracy and tax deduction tracking
    Action: Recategorize transactions or create more specific categories
    Effort: 30 minutes

  [MEDIUM] Quick Win
    Enable automatic account sync
    Issue: Manual sync causing 2-3 day delays
    Impact: Budgets and forecasts using stale data
    Action: Enable daily sync in PocketSmith settings
    Effort: 5 minutes

  [MEDIUM] Moderate
    Reduce budget variance in "Dining Out"
    Issue: Consistently 25% over budget
    Impact: Unrealistic budget affecting financial planning
    Action: Adjust budget or implement spending alerts
    Effort: 15 minutes

  [LOW] Quick Win
    Archive unused categories
    Issue: 8 categories with no transactions in 6+ months
    Impact: Clutters category picker, minor UX issue
    Action: Review and archive or delete unused categories
    Effort: 10 minutes

--------------------------------------------------------------------------------
TREND (Last 4 Weeks)
--------------------------------------------------------------------------------

  Week 1: 68  ████████████████░░░░
  Week 2: 71  █████████████████░░░  (+3)
  Week 3: 72  █████████████████░░░  (+1)
  Week 4: 74  ██████████████████░░  (+2)  <- Current

  Trend: Improving (+6 over 4 weeks)

================================================================================
Next scheduled check: 2025-01-22 00:00
Run `/agent-smith-health compare` to see detailed changes
================================================================================
```

---

## Troubleshooting

### Common Issues

#### "Unable to connect to PocketSmith"

**Cause**: API key missing or invalid

**Solution**:
1. Check `.env` file contains `POCKETSMITH_API_KEY`
2. Verify the key is valid at PocketSmith Developer Settings
3. Ensure no extra whitespace around the key

#### "Health check taking too long"

**Cause**: Large transaction history or slow API response

**Solution**:
1. Use `/agent-smith-health quick` for faster results
2. Check your internet connection
3. Try again during off-peak hours

#### "Scores seem inaccurate"

**Cause**: Stale cached data or sync issues

**Solution**:
1. Force sync your PocketSmith accounts
2. Clear Agent Smith cache: check `data/cache/`
3. Run a full health check: `/agent-smith-health full`

#### "Recommendations don't apply to my situation"

**Cause**: Generic recommendations may not fit all users

**Solution**:
1. Adjust targets in `data/config.json`
2. Use `/agent-smith configure` to set your preferences
3. Dismiss inapplicable recommendations

#### "Missing dimension scores"

**Cause**: Insufficient data for analysis

**Solution**:
1. Ensure you have at least 30 days of transaction history
2. Verify all accounts are synced
3. Check that categories are set up in PocketSmith

### Getting Help

If issues persist:

1. Check `data/logs/` for error details
2. Run `/agent-smith-health --debug` for verbose output
3. Review the design documentation at `docs/design/`

---

## Quick Reference

| Task | Command |
|------|---------|
| Run full health check | `/agent-smith-health` |
| Quick check | `/agent-smith-health quick` |
| Check specific dimension | `/agent-smith-health data-quality` |
| Compare to last check | `/agent-smith-health compare` |
| View trends | `/agent-smith-health trends` |
| Configure alerts | `/agent-smith configure alerts` |

---

*For more information, see the complete [Agent Smith Design Document](../design/2025-11-20-agent-smith-design.md).*
