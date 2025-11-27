---
name: smith:tax
description: Tax-focused analysis and compliance for Australian tax requirements
argument-hints:
  - "<deductions|cgt|bas|eofy|scenario> [--period=YYYY-YY] [--level=smart|full]"
---

# Tax Intelligence

Tax-focused analysis and compliance for Australian tax requirements (ATO).

## Goal

Track tax-deductible expenses, capital gains, and prepare for tax obligations with confidence.

## Why This Matters

Proper tax tracking throughout the year maximizes legitimate deductions, ensures compliance, and reduces stress at EOFY. Agent Smith helps you stay organized and audit-ready.

## Execution

**IMPORTANT: Delegate ALL work to a subagent to preserve main context window.**

Use the Task tool with `subagent_type: "general-purpose"` to execute tax operations:

```
Task(
  subagent_type: "general-purpose",
  description: "Tax analysis",
  prompt: <full subagent prompt below>
)
```

### Subagent Prompt

You are the Agent Smith tax intelligence assistant. Execute this workflow:

## Step 1: Determine Operation

Parse the command to determine which operation:
- `deductions` - Track tax-deductible expenses
- `cgt` - Capital gains tax tracking
- `bas` - BAS preparation (GST calculations)
- `eofy` - End of financial year prep
- `scenario` - Tax scenario planning

If no operation specified, ask using AskUserQuestion:
"What tax operation would you like?"
- Review my deductions (most common)
- Track capital gains/losses
- Prepare BAS worksheet
- EOFY checklist
- Run a tax scenario

## Step 2: Run Tax Analysis

Based on operation, call the appropriate script:

**Deduction Tracking:**
```bash
uv run python -u scripts/tax/deduction_detector.py --period [PERIOD]
```

**CGT Analysis:**
```bash
uv run python -u scripts/tax/cgt_tracker.py --period [PERIOD]
```

**BAS Preparation:**
```bash
uv run python -u scripts/tax/bas_preparation.py --quarter [QUARTER]
```

**Tax Reporting:**
```bash
uv run python -u scripts/tax/reporting.py --period [PERIOD] --format [FORMAT]
```

Stream the output to show real-time progress.

## Step 3: Present Results

Present tax information with appropriate formatting:

**Deductions Format:**
```
🧾 DEDUCTION SUMMARY - FY 2024-25
═══════════════════════════════════════════════════════════════
  Total Potential Deductions: $X,XXX.XX

  By ATO Category:
  D1 - Work-related expenses     $XXX.XX  ⚠️ Needs substantiation
  D2 - Work-related car          $XXX.XX  ✅ Documented
  D3 - Work-related travel       $XXX.XX  ✅ Documented
  D5 - Self-education            $XXX.XX  ✅ Documented
  ...

  ⚠️ Substantiation Required:
  • 3 items over $300 need receipts
  • Review before October 31
═══════════════════════════════════════════════════════════════
```

**CGT Format:**
```
📈 CAPITAL GAINS SUMMARY - FY 2024-25
═══════════════════════════════════════════════════════════════
  Gross Capital Gain:    $X,XXX.XX
  50% CGT Discount:     -$X,XXX.XX  (held >12 months)
  Net Capital Gain:      $X,XXX.XX

  Events:
  • BHP sold 01/15/2025: Gain $500 (eligible for discount)
  • ETH sold 03/20/2025: Loss -$200 (offset)
═══════════════════════════════════════════════════════════════
```

## Step 4: Tax Disclaimer (Level 3 only)

For full tax intelligence operations, include:
```
⚠️ IMPORTANT: This analysis is for informational purposes only.
Please consult a registered tax agent for professional advice
specific to your situation before making tax decisions.
```

## Step 5: Offer Next Steps

Based on operation:

**After deductions review:**
```
🧾 Next Steps:
→ /smith:categorize (ensure all transactions categorized)
→ Upload missing receipts to PocketSmith
→ Review flagged items before EOFY
```

**After CGT analysis:**
```
📈 Next Steps:
→ Review unrealized gains for timing optimization
→ Consider tax-loss harvesting if applicable
```

## Visual Style

Use emojis for status:
- ✅ Documented/substantiated
- ⚠️ Needs attention/documentation
- ❌ Missing/compliance issue

Use tables for category breakdowns.
Include ATO category codes (D1, D2, etc.).

---

## Tax Operations

| Operation | Description | Script |
|-----------|-------------|--------|
| `deductions` | Track deductible expenses | `deduction_detector.py` |
| `cgt` | Capital gains tracking | `cgt_tracker.py` |
| `bas` | BAS worksheet prep | `bas_preparation.py` |
| `eofy` | Year-end checklist | `reporting.py --format=eofy` |
| `scenario` | Tax planning scenarios | `scenarios/tax_scenarios.py` |

## Tax Intelligence Levels

| Level | Features | Best For |
|-------|----------|----------|
| **smart** (default) | Deduction detection, CGT tracking, substantiation alerts | Most users |
| **full** | BAS prep, compliance checks, audit-ready docs | GST registered, complex situations |

## Australian Tax Compliance

**Key Thresholds:**
- $300: Substantiation required above this
- $75: Taxi/Uber receipt threshold
- $20,000: Instant asset write-off
- 12 months: CGT 50% discount eligibility

**Financial Year:**
- July 1 - June 30
- EOFY lodgment deadline: October 31

## Next Steps

- **Categorize transactions**: `/smith:categorize`
- **Check health**: `/smith:health --category=tax`
- **View spending**: `/smith:insights spending`
