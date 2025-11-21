Generate comprehensive financial reports in various formats.

## Usage

```
/agent-smith-report <format> [options]
```

## Report Formats

- `summary` - High-level financial summary
- `detailed` - Comprehensive transaction report
- `tax` - Tax compliance report (deductions, CGT, BAS)
- `custom` - Custom report with specific sections

## Options

- `--period=PERIOD` - Report period (YYYY-MM, YYYY, or YYYY-Q#) [default: current FY]
- `--output=FORMAT` - Output format (markdown|csv|json|html|excel|all) [default: markdown]
- `--tax-level=LEVEL` - Tax intelligence level [default: smart]
- `--sections=LIST` - Custom sections (spending,trends,tax,goals)

## Examples

```bash
# Summary report for Q4 2025
/agent-smith-report summary --period=2025-Q4

# Detailed transaction report in Excel
/agent-smith-report detailed --period=2025-11 --output=excel

# Tax report for FY 2024-25 (full intelligence)
/agent-smith-report tax --period=2024-25 --tax-level=full

# Custom report with specific sections
/agent-smith-report custom --sections=spending,trends,goals

# Generate all formats
/agent-smith-report summary --output=all
```

## Report Sections

**Summary Report:**
- Income & expense totals
- Net position and savings rate
- Top spending categories (top 10)
- Month-over-month trends
- Goal progress

**Detailed Report:**
- Complete transaction list
- Category breakdown
- Merchant analysis
- Uncategorized transactions
- Duplicate detection

**Tax Report (Level 3):**
- Deductible expenses by ATO category
- Substantiation status
- CGT events with discount eligibility
- BAS worksheet (GST calculations)
- Tax-saving recommendations
- Compliance checklist

**Custom Report:**
- Choose specific sections
- Flexible output formats
- Tailored to your needs

## Output Formats

- **Markdown:** Human-readable, great for documentation
- **CSV:** Spreadsheet import, data analysis
- **JSON:** Machine-readable, API integration
- **HTML:** Shareable web page
- **Excel:** Full-featured workbook with sheets
- **All:** Generate all formats at once

## What You'll Get

Reports are saved to `output/reports/` with timestamps. Tax reports include:
- Disclaimer (Level 3 tax advice)
- ATO category codes
- Substantiation requirements
- Recommended next steps

---

**Generating report...**
