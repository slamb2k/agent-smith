# Agent Smith Slash Commands

Quick-access commands for common financial management operations.

## All Commands

1. `/agent-smith` - Main conversational entry point
2. `/agent-smith-categorize` - Transaction categorization
3. `/agent-smith-analyze` - Financial analysis
4. `/agent-smith-scenario` - Scenario modeling
5. `/agent-smith-report` - Report generation
6. `/agent-smith-optimize` - Optimization operations
7. `/agent-smith-tax` - Tax intelligence
8. `/agent-smith-health` - Health check

## Command Descriptions

### /agent-smith

Main conversational skill for complex multi-step operations.

**Use for:**
- Understanding your financial situation
- Guided setup and onboarding
- Multi-step workflows
- Custom analysis

### /agent-smith-categorize

Categorize uncategorized transactions with AI assistance.

**Arguments:**
- `--mode=MODE` - conservative|smart|aggressive
- `--period=PERIOD` - YYYY-MM or YYYY
- `--account=ID` - Specific account
- `--dry-run` - Preview only

**Example:**
```bash
/agent-smith-categorize --mode=smart --period=2025-11
```

### /agent-smith-analyze

Run financial analysis on PocketSmith data.

**Types:**
- `spending` - Category and merchant breakdown
- `trends` - MoM and YoY trends
- `category` - Deep dive into specific category
- `tax` - Tax-focused analysis
- `insights` - AI-generated insights

**Example:**
```bash
/agent-smith-analyze spending --period=2025
```

### /agent-smith-scenario

Model financial scenarios with what-if analysis.

**Types:**
- `historical` - What-if on past transactions
- `projection` - Future forecasts
- `optimization` - Savings opportunities
- `tax` - Tax scenario planning

**Example:**
```bash
/agent-smith-scenario historical "What if I reduced dining by 25%?"
```

### /agent-smith-report

Generate comprehensive reports in multiple formats.

**Formats:**
- `summary` - High-level overview
- `detailed` - Complete transaction report
- `tax` - Tax compliance report
- `custom` - Custom sections

**Output:** markdown|csv|json|html|excel|all

**Example:**
```bash
/agent-smith-report tax --period=2024-25 --output=excel
```

### /agent-smith-optimize

AI-assisted optimization for various targets.

**Targets:**
- `categories` - Category structure
- `rules` - Categorization rules
- `spending` - Spending patterns
- `subscriptions` - Recurring charges

**Example:**
```bash
/agent-smith-optimize subscriptions
```

### /agent-smith-tax

Tax-focused analysis and compliance.

**Operations:**
- `deductions` - Track deductible expenses
- `cgt` - Capital gains tax
- `bas` - BAS preparation (GST)
- `eofy` - End of financial year prep
- `scenario` - Tax scenario planning

**Example:**
```bash
/agent-smith-tax deductions --period=2024-25 --level=full
```

### /agent-smith-health

Evaluate PocketSmith setup health.

**Options:**
- `--full` - Complete deep analysis
- `--quick` - Fast essential checks
- `--category=AREA` - Specific area

**Health Areas:**
1. Category health
2. Rule coverage
3. Data quality
4. Tax compliance
5. Budget alignment
6. Account health

**Example:**
```bash
/agent-smith-health --full
```

## Usage Patterns

### Quick Operations

Use specialized commands for single-purpose operations:
```bash
/agent-smith-categorize
/agent-smith-analyze spending
/agent-smith-health --quick
```

### Complex Workflows

Use main command for multi-step guidance:
```bash
/agent-smith
# Then describe your needs in natural language
```

### Automation

Chain commands for regular tasks:
```bash
/agent-smith-categorize --mode=smart
/agent-smith-analyze trends
/agent-smith-health --category=rules
```

## Integration with Orchestration

All commands use the subagent conductor for smart delegation:
- Small operations (< 100 transactions): Direct execution
- Large operations (> 100 transactions): Subagent delegation
- Multi-period analysis: Parallel processing

## Future Commands

Planned for Phase 7:
- `/agent-smith-alert` - Configure alerts and notifications
- `/agent-smith-merchant` - Merchant intelligence
- `/agent-smith-goal` - Goal management
