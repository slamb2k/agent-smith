# Agent Smith

**An intelligent financial management skill for Claude Code**

Agent Smith provides comprehensive PocketSmith API integration with advanced AI-powered analysis, rule management, tax intelligence, and scenario planning.

## Project Status

🎨 **Design Phase Complete** - Full specification ready for implementation

📋 **Design Document:** [docs/design/2025-11-20-agent-smith-design.md](docs/design/2025-11-20-agent-smith-design.md)

## What is Agent Smith?

Agent Smith transforms PocketSmith from a passive tracking tool into an active financial intelligence system. Named after the Matrix AI agent, it serves as your intelligent assistant for managing your financial matrix.

### Key Features

- **Hybrid Rule Engine** - Platform-native + enhanced local rules with performance tracking
- **3-Tier Tax Intelligence** - Reference, Smart, and Full compliance modes (Australian ATO)
- **Scenario Analysis** - Historical analysis, projections, optimization, tax planning
- **Multi-Format Reports** - Markdown, CSV/JSON, HTML dashboards, Excel
- **Smart Orchestration** - Context-preserving subagent architecture
- **Proactive Insights** - Automated alerts, optimization recommendations
- **Health Checks** - Comprehensive PocketSmith setup evaluation

## Repository Structure

```
agent-smith/
├── README.md                    # This file
├── INDEX.md                     # Directory navigation guide
├── .gitignore                   # Git ignore rules
├── .env                         # API configuration (not committed)
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
│
├── backups/                     # Timestamped backups (30-day retention)
│   └── INDEX.md
│
├── data/                        # Working data and state
│   ├── INDEX.md
│   └── config.json              # User preferences
│
├── docs/                        # Documentation
│   ├── INDEX.md
│   ├── design/                  # Design specifications
│   └── operations/              # Operation logs
│
├── ai_docs/                     # AI agent documentation
│   ├── INDEX.md
│   └── pocketsmith-api-documentation.md
│
├── logs/                        # Execution logs (14-day retention)
│   └── INDEX.md
│
├── reports/                     # Generated reports (90-day retention)
│   └── INDEX.md
│
├── scripts/                     # Python code
│   ├── INDEX.md
│   ├── core/                    # Core libraries
│   │   ├── api_client.py        # PocketSmith API wrapper ✓
│   │   ├── rule_engine.py       # Hybrid rule engine ✓
│   │   └── index_updater.py     # INDEX.md manager ✓
│   ├── analysis/                # Analysis modules
│   │   ├── spending.py          # Spending analysis ✓
│   │   └── trends.py            # Trend detection ✓
│   ├── reporting/               # Reporting modules
│   │   └── formatters.py        # Multi-format reports ✓
│   ├── tax/                     # Tax intelligence (3-tier system)
│   │   ├── ato_categories.py    # ATO category mappings (Level 1) ✓
│   │   ├── reporting.py         # Tax reports & GST tracking (Level 1) ✓
│   │   ├── deduction_detector.py # Deduction detection (Level 2) ✓
│   │   ├── cgt_tracker.py       # Capital gains tracking (Level 2) ✓
│   │   └── bas_preparation.py   # BAS worksheet generation (Level 3) ✓
│   ├── scenarios/               # Scenario analysis
│   │   ├── historical.py        # What-if modeling ✓
│   │   ├── projections.py       # Spending forecasts ✓
│   │   ├── optimization.py      # Savings optimization ✓
│   │   ├── tax_scenarios.py     # Tax planning scenarios ✓
│   │   ├── cash_flow.py         # Cash flow forecasting ✓
│   │   └── goals.py             # Goal tracking ✓
│   ├── orchestration/           # Subagent orchestration ✓
│   │   └── conductor.py         # Smart delegation & context mgmt ✓
│   ├── workflows/               # Interactive workflows ✓
│   │   └── categorization.py    # Categorization workflow ✓
│   ├── operations/              # Operations
│   │   └── categorize.py        # Transaction categorization ✓
│   └── utils/                   # Utilities
│       ├── backup.py            # Backup/restore ✓
│       ├── validation.py        # Data validation ✓
│       ├── logging_config.py    # Logging setup ✓
│       └── merchant_normalizer.py  # Merchant normalization ✓
│
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
│
└── .claude/                     # Claude Code configuration
    └── commands/                # Slash commands (8 commands) ✓
```

## Quick Start

### Prerequisites

- Python 3.9+
- PocketSmith account with API access
- Developer API key from PocketSmith (Settings > Security)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd agent-smith

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.sample .env
# Edit .env and add your POCKETSMITH_API_KEY
```

### Running Tests

```bash
# Run all unit tests
pytest tests/unit -v

# Run integration tests (requires API key)
pytest tests/integration -v -m integration

# Run all tests with coverage
pytest --cov=scripts tests/
```

### Usage

Currently in development. Phase 1 foundation is complete.

Python usage example:

```python
from scripts.core.api_client import PocketSmithClient

# Initialize client
client = PocketSmithClient()

# Get user info
user = client.get_user()
print(f"Connected as: {user['login']}")

# Get categories
categories = client.get_categories(user_id=user['id'])
print(f"Found {len(categories)} categories")
```

## Contributing Workflow

This repository uses branch protection and requires all changes to go through pull requests.

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit**
   - Git hooks will automatically run format, lint, and type checks on commit
   - Unit tests run on push
   ```bash
   git add .
   git commit -m "feat: add your feature"
   git push -u origin feature/your-feature-name
   ```

3. **Create a pull request**
   ```bash
   gh pr create --fill
   ```

4. **Wait for CI validation**
   - PR validation runs format, lint, type-check, tests, and build checks
   - All checks must pass across Python 3.9, 3.10, 3.11, and 3.12

5. **Squash and merge**
   - PRs are squash-merged to maintain clean history
   - Feature branches are automatically deleted after merge

### Pre-commit Checks

Git hooks (via lefthook) run automatically:
- **Pre-commit**: Black formatting, flake8 linting, mypy type checking
- **Pre-push**: Unit tests, build verification

## Documentation

- **[Design Specification](docs/design/2025-11-20-agent-smith-design.md)** - Complete Agent Smith design
- **[Repository Index](INDEX.md)** - Detailed directory structure
- **[PocketSmith API Docs](ai_docs/pocketsmith-api-documentation.md)** - API reference

## Development Status

**Current Phase:** Phase 1 - Foundation ✅ **COMPLETE**

### Phase 1 Completion Checklist

#### Core Infrastructure
- ✅ Directory structure created (backups, data, logs, reports, scripts, tests)
- ✅ .env.sample configuration template
- ✅ INDEX.md templates for all directories
- ✅ pytest configuration and test structure

#### Core Libraries
- ✅ **api_client.py** - PocketSmith API wrapper with rate limiting
- ✅ **index_updater.py** - INDEX.md automation
- ✅ **backup.py** - Backup/restore utilities
- ✅ **validation.py** - Data validation
- ✅ **logging_config.py** - Logging infrastructure

#### Basic Functionality
- ✅ API authentication and basic queries
- ✅ Backup/restore system
- ✅ Logging infrastructure (operations, errors, API calls)
- ✅ Configuration management (data/config.json)

#### Testing
- ✅ Unit tests for all core utilities (100% coverage)
- ✅ Integration tests for API client
- ✅ Test framework configured (pytest)

### Phase 2: Rule Engine ✅ **COMPLETE**

#### Hybrid Rule System
- ✅ Rule class with pattern matching (regex, amount ranges, exclusions)
- ✅ Local rule engine with JSON persistence
- ✅ Platform rule creation for simple patterns
- ✅ Intelligence modes (Conservative/Smart/Aggressive)
- ✅ Performance tracking (matches, accuracy, overrides)
- ✅ Rule finding with priority sorting

#### Categorization Workflow
- ✅ Single transaction categorization
- ✅ Batch categorization operations
- ✅ Dry-run mode for testing
- ✅ Auto-apply based on confidence thresholds
- ✅ API integration for updates

#### Merchant Intelligence
- ✅ Merchant name normalization
- ✅ Location code and suffix removal
- ✅ Canonical name mapping
- ✅ Learning from transaction history
- ✅ Variation grouping

**Test Coverage:** 75 unit tests + 12 integration tests = 87 tests, all passing

### Implementation Roadmap

- ✅ **Phase 1:** Foundation (Weeks 1-2) - API client, utilities, backups
- ✅ **Phase 2:** Rule Engine (Weeks 3-4) - Hybrid platform + local rules
- ✅ **Phase 3:** Analysis & Reporting (Weeks 5-6) - Spending analysis, tax reports
- ✅ **Phase 4:** Tax Intelligence (Weeks 7-8) - 3-tier tax system, deductions, BAS
- ✅ **Phase 5:** Scenario Analysis (Weeks 9-10) - What-if, projections, optimization
- ✅ **Phase 6:** Orchestration & UX (Weeks 11-12) - Subagent conductor, slash commands
- ✅ **Phase 7:** Advanced Features (Weeks 13-14) - Alerts, merchant intelligence, audit trail
- ⏳ **Phase 8:** Health Check & Polish (Weeks 15-16) - Health scores, optimization

**Progress:** 7/8 phases complete (87.5%)

### Phase 3: Analysis & Reporting ✅

**Spending Analysis:**
- Analyze spending by category, merchant, time period
- Period filtering (year, month)
- Summary statistics (income, expenses, net)
- Trend detection (increasing, decreasing, stable)

**Report Formats:**
- Markdown reports with tables and summaries
- CSV export for data analysis
- JSON output for programmatic access
- Multi-format generation support

**Test Coverage:** 101 tests (87 existing + 14 new), all passing

### Phase 4: Tax Intelligence ✅

**3-Tier Tax Intelligence System:**
- Level 1 (Reference): ATO category mappings, basic tax reports, GST tracking
- Level 2 (Smart): Deduction detection, CGT tracking, confidence scoring
- Level 3 (Full): BAS preparation with GST calculations and compliance checks

**Deduction Detection:**
- 14 pattern-based detection rules
- Confidence scoring (high/medium/low)
- Substantiation threshold checking ($300 default, $75 taxi/Uber)
- Time-based commuting detection (weekday 6-9:30am, 4:30-7pm)
- Instant asset write-off tracking ($20,000 threshold)

**Capital Gains Tax (CGT):**
- Asset tracking (shares, crypto, property)
- FIFO matching for sales
- Cost base calculation (price + fees)
- Holding period calculation with 50% discount eligibility (>365 days)
- Financial year reporting (July 1 - June 30)

**BAS Preparation (Level 3):**
- Quarterly BAS worksheet generation
- GST calculations (G1, G10, G11, 1A, 1B, 1C)
- Capital vs non-capital purchase classification
- GST-free category exclusions
- Professional advice disclaimers

**Code Examples:**

```python
# ATO Category Mapping (Level 1)
from scripts.tax.ato_categories import ATOCategoryMapper

mapper = ATOCategoryMapper()
ato_info = mapper.get_ato_category("Office Supplies")
# Returns: {"ato_code": "D5", "ato_category": "Work-related other expenses", ...}

# Deduction Detection (Level 2)
from scripts.tax.deduction_detector import DeductionDetector

detector = DeductionDetector()
result = detector.detect_deduction(transaction)
# Returns: {"is_deductible": True, "confidence": "high",
#           "reason": "Office supplies", "substantiation_required": True}

# CGT Tracking (Level 2)
from scripts.tax.cgt_tracker import CGTTracker, AssetType
from decimal import Decimal
from datetime import date

tracker = CGTTracker()
tracker.track_purchase(
    asset_type=AssetType.SHARES,
    name="BHP Group",
    quantity=Decimal("100"),
    purchase_date=date(2023, 1, 1),
    purchase_price=Decimal("45.50"),
    fees=Decimal("19.95")
)

event = tracker.track_sale(
    asset_type=AssetType.SHARES,
    name="BHP Group",
    quantity=Decimal("100"),
    sale_date=date(2024, 6, 1),
    sale_price=Decimal("52.00"),
    fees=Decimal("19.95")
)
# Returns CGTEvent with capital_gain, discount_eligible, holding_period_days

# BAS Preparation (Level 3)
from scripts.tax.bas_preparation import generate_bas_worksheet

worksheet = generate_bas_worksheet(
    transactions=transactions,
    start_date="2024-07-01",
    end_date="2024-09-30"
)
# Returns: {"G1_total_sales": 33000.00, "1A_gst_on_sales": 3000.00,
#           "1B_gst_on_purchases": 1500.00, "1C_net_gst": 1500.00, ...}
```

**Test Coverage:** 163 tests (141 unit + 22 integration), all passing
- Phase 4 specific: 62 tests (54 unit + 8 integration)

### Phase 5: Scenario Analysis ✅

**Scenario Analysis:**
- Historical "what-if" modeling for spending changes
- Future spending projections with inflation
- Optimization engine (subscriptions, trends, recurring expenses)
- Tax scenario planning and optimization
- Cash flow forecasting with emergency fund tracking
- Goal tracking and progress monitoring

**Example Usage:**

```python
from scripts.scenarios.historical import calculate_what_if_spending
from scripts.scenarios.projections import forecast_spending
from scripts.scenarios.optimization import suggest_optimizations

# What-if analysis
scenario = calculate_what_if_spending(
    transactions=transactions,
    category_name="Dining",
    adjustment_percent=-30.0,  # 30% reduction
    start_date="2025-01-01",
    end_date="2025-12-31"
)
print(f"Savings: ${scenario['savings']:.2f}")

# Spending forecast
forecast = forecast_spending(
    transactions=transactions,
    category_name="Groceries",
    months_forward=6,
    inflation_rate=3.0
)

# Optimization suggestions
optimizations = suggest_optimizations(transactions=transactions)
print(f"Potential savings: ${optimizations['potential_annual_savings']:.2f}")
```

**Test Coverage:** 194 tests (167 unit + 27 integration), all passing
- Phase 5 specific: 30 tests (23 unit + 7 integration)

### Phase 6: Orchestration & UX ✅

**Intelligent Orchestration:**
```python
from scripts.orchestration.conductor import SubagentConductor, OperationType

# Smart delegation based on complexity
conductor = SubagentConductor()
should_delegate = conductor.should_delegate_operation(
    operation_type=OperationType.CATEGORIZATION,
    transaction_count=150  # > 100 triggers delegation
)

# Context preservation
from scripts.orchestration.conductor import ContextManager
context = ContextManager(user_id="12345")
context.set_preference("intelligence_mode", "smart")
context.set_preference("tax_level", "full")
```

**Slash Commands (8 commands):**
```bash
# Main conversational entry
/agent-smith

# Quick operations
/agent-smith-categorize --mode=smart --period=2025-11
/agent-smith-analyze spending --period=2025
/agent-smith-scenario historical "What if I cut dining by 25%?"
/agent-smith-report tax --period=2024-25 --tax-level=full
/agent-smith-optimize subscriptions
/agent-smith-tax deductions --period=2024-25
/agent-smith-health --full
```

**Interactive Workflows:**
- Guided categorization with AI assistance
- Multi-step scenario planning
- Smart recommendations with context
- Progress tracking and feedback

**Features:**
- Smart subagent delegation (>100 transactions, >5000 tokens)
- Context preservation across operations
- Parallel processing for multi-period analysis
- Result aggregation from distributed subagents
- 8 specialized slash commands
- Interactive workflows with user approval
- Natural language scenario descriptions

**Test Coverage:** 227 tests (189 unit + 38 integration), all passing
- Phase 6 specific: 31 tests (25 unit + 6 integration)

### Phase 7: Advanced Features ✅

**Smart Alerts & Notifications:**
```python
from scripts.features.alerts import AlertEngine, AlertScheduler, ScheduleType

# Create alert engine
engine = AlertEngine(user_id="user_123")
scheduler = AlertScheduler(alert_engine=engine)

# Schedule weekly budget review
schedule = scheduler.add_schedule(
    schedule_type=ScheduleType.WEEKLY,
    alert_type=AlertType.BUDGET,
    title="Weekly Budget Review",
    next_run=datetime(2025, 11, 28, 9, 0),
)

# Process due schedules
alerts = scheduler.process_due_schedules()
```

**Merchant Intelligence:**
```python
from scripts.features.merchant_intelligence import MerchantMatcher

matcher = MerchantMatcher()

# Learn merchant variations
matcher.add_variation("Woolworths", "WOOLWORTHS PTY LTD")
matcher.add_variation("Woolworths", "woolworth")

# Find canonical name
canonical = matcher.find_canonical("woolies")  # Returns "Woolworths"

# Suggest matches for unknown payee
suggestions = matcher.suggest_matches("woollies", threshold=0.8)
```

**Document Management:**
```python
from scripts.features.documents import DocumentManager

manager = DocumentManager()

# Track transaction requiring receipt (> $300)
doc = manager.track_transaction(
    transaction_id=12345,
    amount=450.00,
    category="Work Expenses",
    date=datetime(2025, 11, 15),
)  # Automatically marked as REQUIRED

# Get missing required documents
missing = manager.get_missing_documents(required_only=True)
```

**Multi-User Shared Expenses:**
```python
from scripts.features.multi_user import SharedExpenseTracker

tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])

# Add shared expense
tracker.add_expense(
    transaction_id=1,
    amount=150.00,
    description="Dinner",
    paid_by="alice",
    date=datetime.now(),
    split_equally=True,
)

# Generate settlement recommendations
settlements = tracker.generate_settlements()
# Returns: [Settlement(from_user="bob", to_user="alice", amount=50.00), ...]
```

**Comparative Benchmarking:**
```python
from scripts.features.benchmarking import BenchmarkEngine, PeerCriteria

engine = BenchmarkEngine()
criteria = PeerCriteria(household_size=2, income_bracket="50k-75k")

# Compare spending to peers
result = engine.compare(
    category="Groceries",
    user_amount=500.00,
    criteria=criteria,
)
# Returns: BenchmarkResult with peer_average, peer_median, percentile
```

**Audit Trail:**
```python
from scripts.features.audit import AuditLogger, AuditAction

logger = AuditLogger(user_id="user_123")

# Log transaction modification
entry = logger.log_action(
    action=AuditAction.TRANSACTION_MODIFY,
    description="Changed category",
    before_state={"category": "Food"},
    after_state={"category": "Groceries"},
    affected_ids=[123],
)

# Query audit trail
entries = logger.get_entries(affected_id=123)

# Check if action can be undone
can_undo = logger.can_undo(entry.entry_id)
```

**Features:**
- Smart alerts with scheduling (weekly, monthly, quarterly, annual, one-time)
- Merchant intelligence with variation detection and grouping
- Document tracking with ATO compliance ($300 threshold)
- Multi-user shared expenses with settlement optimization
- Privacy-first benchmarking (SHA-256 anonymization, min 3 peers)
- Comprehensive audit trail with undo capability

**Test Coverage:** 287 tests (243 unit + 44 integration), all passing
- Phase 7 specific: 60 tests (54 unit + 6 integration)

### Next Phase

**Phase 8:** Health Check & Polish (Weeks 15-16)
- Health check system with 6 health scores
- Recommendation engine
- Automated monitoring
- Performance optimization

See [design document](docs/design/2025-11-20-agent-smith-design.md) for complete roadmap.

## License

[To be determined]

## Support

For questions or issues, please refer to the design documentation or create an issue in the repository.

---

**Note:** This project is in active development. The `build/` directory contains reference materials from previous migration work and will be removed before final publication.
