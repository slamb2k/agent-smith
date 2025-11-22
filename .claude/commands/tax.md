---
name: agent-smith:tax
description: Tax-focused analysis and compliance for Australian tax requirements
argument-hints:
  - "<deductions|cgt|bas|eofy|scenario> [--period=PERIOD] [--level=LEVEL] [--output=FORMAT]"
---

Tax-focused analysis and compliance for Australian tax requirements.

## Usage

```
/agent-smith-tax <operation> [options]
```

## Tax Operations

- `deductions` - Track tax-deductible expenses
- `cgt` - Capital gains tax tracking and optimization
- `bas` - BAS preparation (GST calculations)
- `eofy` - End of financial year tax prep
- `scenario` - Tax scenario planning

## Options

- `--period=PERIOD` - Financial year (YYYY-YY format) [default: current FY]
- `--level=LEVEL` - Tax intelligence (reference|smart|full) [default: smart]
- `--output=FORMAT` - Output format [default: markdown]

## Examples

```bash
# Track deductible expenses for FY 2024-25
/agent-smith-tax deductions --period=2024-25

# CGT analysis with timing recommendations
/agent-smith-tax cgt --period=2024-25 --level=full

# BAS worksheet preparation (GST only)
/agent-smith-tax bas --period=2024-Q4

# Complete EOFY tax prep checklist
/agent-smith-tax eofy

# Tax scenario: equipment purchase timing
/agent-smith-tax scenario "Buy $25k equipment before or after EOFY?"
```

## Tax Intelligence Levels

**Reference (Level 1):**
- Basic ATO category mapping
- Links to ATO resources
- General guidance

**Smart (Level 2 - default):**
- Deduction detection with confidence scoring
- Substantiation threshold monitoring
- CGT discount eligibility tracking
- Tax-saving suggestions

**Full (Level 3):**
- BAS preparation (GST calculations)
- Compliance checks and validation
- Audit-ready documentation
- Detailed tax scenarios

**Important:** Level 3 outputs include disclaimer to consult a registered tax agent.

## Tax Operations Detail

**Deductions:**
- Expenses by ATO category code
- Substantiation requirements (>$300)
- Confidence scoring (high/medium/low)
- Missing documentation alerts
- Instant asset write-off eligibility

**CGT Tracking:**
- Purchase and sale events
- Cost base calculations
- 12-month discount eligibility
- Capital gains/losses by FY
- Optimization recommendations

**BAS Preparation (Level 3):**
- G1: Total sales
- G10/G11: Capital/non-capital purchases
- 1A/1B: GST calculations
- 1C: Net GST position
- Scope: GST only (W1, W2 excluded)

**EOFY Preparation:**
- Deduction summary
- CGT event summary
- Missing substantiation
- Compliance checklist
- Tax-saving opportunities
- Deadlines and due dates

## Australian Tax Compliance

**ATO Guidelines:**
- Substantiation thresholds
- CGT 50% discount (>12 months)
- Instant asset write-off (<$20k)
- Commuting vs. business travel
- Home office deductions

**Financial Year:**
- July 1 - June 30
- EOFY deadline: October 31
- BAS deadlines: Quarterly (monthly for some)

---

**Starting tax analysis...**
