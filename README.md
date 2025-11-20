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
    └── commands/                # Slash commands (future)
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

- ✅ **Phase 1:** Foundation (Weeks 1-2) - **COMPLETE**
- ✅ **Phase 2:** Rule Engine (Weeks 3-4) - **COMPLETE**
- ✅ **Phase 3:** Analysis & Reporting (Weeks 5-6) - **COMPLETE**
- [ ] **Phase 4:** Tax Intelligence (Weeks 7-8)
- [ ] **Phase 5:** Scenario Analysis (Weeks 9-10)
- [ ] **Phase 6:** Orchestration & UX (Weeks 11-12)
- [ ] **Phase 7:** Advanced Features (Weeks 13-14)
- [ ] **Phase 8:** Health Check & Polish (Weeks 15-16)

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

### Next Phase

**Phase 4:** Tax Intelligence (Weeks 7-8)
- Australian tax-specific features
- Deduction tracking and CGT calculations
- BAS preparation and compliance checks
- Tax report generation

See [design document](docs/design/2025-11-20-agent-smith-design.md) for complete roadmap.

## License

[To be determined]

## Support

For questions or issues, please refer to the design documentation or create an issue in the repository.

---

**Note:** This project is in active development. The `build/` directory contains reference materials from previous migration work and will be removed before final publication.
