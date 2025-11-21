Run financial analysis on your PocketSmith data.

## Usage

```
/agent-smith-analyze <type> [options]
```

## Analysis Types

- `spending` - Spending breakdown by category and merchant
- `trends` - Month-over-month and year-over-year trends
- `category` - Deep dive into specific category
- `tax` - Tax-focused analysis (deductions, CGT, etc.)
- `insights` - AI-generated insights and recommendations

## Options

- `--period=PERIOD` - Analysis period (YYYY-MM or YYYY) [default: current year]
- `--category=NAME` - Focus on specific category
- `--compare=PERIOD` - Compare with another period (YoY, MoM)
- `--tax-level=LEVEL` - Tax intelligence (reference|smart|full) [default: smart]

## Examples

```bash
# Spending analysis for 2025
/agent-smith-analyze spending --period=2025

# Trend analysis comparing 2024 vs 2025
/agent-smith-analyze trends --period=2025 --compare=2024

# Category deep-dive for Dining
/agent-smith-analyze category --category="Dining"

# Tax analysis for FY 2024-25 (full intelligence)
/agent-smith-analyze tax --period=2024-25 --tax-level=full

# AI insights for current month
/agent-smith-analyze insights
```

## What You'll Get

**Spending Analysis:**
- Total expenses by category
- Top 10 merchants
- Average daily/weekly/monthly spending
- Comparison vs. previous periods

**Trends:**
- Month-over-month changes
- Year-over-year growth rates
- Trending up/down categories
- Anomaly detection

**Category Deep-Dive:**
- Transaction count and total
- Merchant breakdown
- Spending patterns (day of week, time of day)
- Optimization opportunities

**Tax Analysis:**
- Deductible expenses by ATO category
- Substantiation requirements
- CGT events and timing
- Tax-saving opportunities

**AI Insights:**
- Spending pattern observations
- Budget recommendations
- Subscription optimization
- Goal tracking suggestions

---

**Starting analysis...**
