# Budget Smith - Repository Index

**Last Updated:** 2025-11-21

This index provides a comprehensive overview of the repository structure for both human readers and AI agents.

---

## Root Directory

| File/Directory | Type | Description | Status |
|----------------|------|-------------|--------|
| `README.md` | File | Project overview and quick start guide | Active |
| `INDEX.md` | File | This file - complete directory index | Active |
| `.gitignore` | File | Git ignore rules (protects sensitive data) | Active |
| `.env` | File | API configuration (NEVER commit - protected) | Protected |
| `.claude/` | Directory | Claude Code configuration and commands | Active |
| `docs/` | Directory | Documentation and design specifications | Active |
| `ai_docs/` | Directory | Documentation for AI agents/subagents | Active |
| `build/` | Directory | Reference materials (temporary, pre-publish) | Temporary |

---

## Directory Details

### `/docs/` - Documentation

Contains all project documentation including design specifications and operation logs.

| Path | Description | Type |
|------|-------------|------|
| `docs/INDEX.md` | Documentation index | Index |
| `docs/design/2025-11-20-agent-smith-design.md` | Complete Agent Smith design specification | Design Doc |
| `docs/plans/2025-11-20-phase-2-rule-engine.md` | Phase 2 implementation plan | Plan |
| `docs/plans/2025-11-20-phase-3-analysis-reporting.md` | Phase 3 implementation plan | Plan |
| `docs/operations/2025-11-20_phase1_testing.md` | Phase 1 testing operation log | Operation Log |
| `docs/operations/2025-11-20_phase2_completion.md` | Phase 2 completion operation log | Operation Log |
| `docs/operations/2025-11-20_phase3_completion.md` | Phase 3 completion operation log | Operation Log |
| `docs/operations/2025-11-20_phase4_completion.md` | Phase 4 completion operation log | Operation Log |
| `docs/operations/2025-11-21_phase5_completion.md` | Phase 5 completion operation log | Operation Log |
| `docs/operations/2025-11-21_phase6_completion.md` | Phase 6 completion operation log | Operation Log |

**Purpose:** Central location for all project documentation, design specs, implementation guides, and user documentation.

**See:** [docs/INDEX.md](docs/INDEX.md)

---

### `/ai_docs/` - AI Agent Documentation

Documentation specifically formatted for AI agents and subagents to reference during operations.

| Path | Description | Type |
|------|-------------|------|
| `ai_docs/INDEX.md` | AI documentation index | Index |
| `ai_docs/pocketsmith-api-documentation.md` | PocketSmith API v2 reference | API Docs |

**Purpose:** Provides AI agents with comprehensive references without needing to download documentation repeatedly. Optimized for LLM consumption.

**See:** [ai_docs/INDEX.md](ai_docs/INDEX.md)

---

### `/build/` - Reference Materials (Temporary)

Contains reference materials from previous PocketSmith migration work. This directory will be removed before final publication as useful content is incorporated into Agent Smith.

| Path | Description | Type |
|------|-------------|------|
| `build/docs/` | Migration documentation (9 files) | Reference |
| `build/scripts/` | Python scripts from migration work (40+ files) | Reference |

**Purpose:** Preserve previous work for reference during Agent Smith development.

**Status:** Temporary - will be removed before publish

**Contents:**
- `build/docs/` - Category hierarchy planning, migration guides, implementation notes
- `build/scripts/` - Python scripts for categorization, analysis, migration, reporting

---

### `/.claude/` - Claude Code Configuration

Claude Code configuration directory (managed by Claude Code itself).

| Path | Description | Type |
|------|-------------|------|
| `.claude/commands/agent-smith.md` | Main conversational entry point | Slash Command |
| `.claude/commands/agent-smith-categorize.md` | Transaction categorization | Slash Command |
| `.claude/commands/agent-smith-analyze.md` | Financial analysis | Slash Command |
| `.claude/commands/agent-smith-scenario.md` | Scenario modeling | Slash Command |
| `.claude/commands/agent-smith-report.md` | Report generation | Slash Command |
| `.claude/commands/agent-smith-optimize.md` | Optimization operations | Slash Command |
| `.claude/commands/agent-smith-tax.md` | Tax intelligence | Slash Command |
| `.claude/commands/agent-smith-health.md` | Health check | Slash Command |
| `.claude/commands/INDEX.md` | Command reference | Index |

**Purpose:** Stores Claude Code settings, slash commands, and skill configurations.

**Status:** 8 slash commands implemented (Phase 6)

---

### `/scripts/` - Python Code

Contains all Python source code organized by function.

| Path | Description | Type |
|------|-------------|------|
| `scripts/core/api_client.py` | PocketSmith API v2 client with rate limiting | Core Library |
| `scripts/core/rule_engine.py` | Hybrid rule engine (Phase 2) | Core Library |
| `scripts/core/index_updater.py` | INDEX.md automation utility | Core Library |
| `scripts/analysis/spending.py` | Spending analysis by category/merchant/period (Phase 3) | Analysis |
| `scripts/analysis/trends.py` | Trend detection and pattern analysis (Phase 3) | Analysis |
| `scripts/reporting/formatters.py` | Multi-format report generation (Phase 3) | Reporting |
| `scripts/tax/ato_categories.py` | ATO category mappings for tax compliance (Phase 4, Level 1) | Tax |
| `scripts/tax/reporting.py` | Tax-specific reports and GST tracking (Phase 4, Level 1) | Tax |
| `scripts/tax/deduction_detector.py` | Pattern-based deduction detection (Phase 4, Level 2) | Tax |
| `scripts/tax/cgt_tracker.py` | Capital gains tax tracking with FIFO (Phase 4, Level 2) | Tax |
| `scripts/tax/bas_preparation.py` | BAS worksheet generation (Phase 4, Level 3) | Tax |
| `scripts/scenarios/historical.py` | Historical scenario analysis (what-if modeling) (Phase 5) | Scenarios |
| `scripts/scenarios/projections.py` | Future spending forecasts and affordability (Phase 5) | Scenarios |
| `scripts/scenarios/optimization.py` | Savings optimization engine (Phase 5) | Scenarios |
| `scripts/scenarios/tax_scenarios.py` | Tax planning and optimization scenarios (Phase 5) | Scenarios |
| `scripts/scenarios/cash_flow.py` | Cash flow forecasting and emergency fund (Phase 5) | Scenarios |
| `scripts/scenarios/goals.py` | Goal tracking and progress monitoring (Phase 5) | Scenarios |
| `scripts/orchestration/conductor.py` | Subagent conductor with smart delegation (Phase 6) | Orchestration |
| `scripts/orchestration/INDEX.md` | Orchestration API reference | Index |
| `scripts/workflows/categorization.py` | Interactive categorization workflow (Phase 6) | Workflows |
| `scripts/workflows/INDEX.md` | Workflow API reference | Index |
| `scripts/operations/categorize.py` | Transaction categorization workflow (Phase 2) | Operations |
| `scripts/features/alerts.py` | Smart alerts and notification scheduling (Phase 7) | Features |
| `scripts/features/merchant_intelligence.py` | Merchant variation detection and grouping (Phase 7) | Features |
| `scripts/features/documents.py` | Document and receipt requirement tracking (Phase 7) | Features |
| `scripts/features/multi_user.py` | Shared expense and settlement tracking (Phase 7) | Features |
| `scripts/features/benchmarking.py` | Privacy-first comparative benchmarking (Phase 7) | Features |
| `scripts/features/audit.py` | Audit trail and activity logging (Phase 7) | Features |
| `scripts/features/INDEX.md` | Features API reference | Index |
| `scripts/utils/backup.py` | Backup/restore utilities | Utility |
| `scripts/utils/validation.py` | Data validation functions | Utility |
| `scripts/utils/logging_config.py` | Logging infrastructure | Utility |
| `scripts/utils/merchant_normalizer.py` | Merchant name normalization (Phase 2) | Utility |

**Purpose:** All executable Python code for Agent Smith functionality.

**Structure:**
- `core/` - Core libraries (API client, rule engine, etc.)
- `analysis/` - Analysis modules (spending, trends, etc.)
- `reporting/` - Report generation and formatting
- `tax/` - Tax intelligence (3-tier: Reference, Smart, Full compliance)
- `scenarios/` - Scenario analysis (what-if, projections, optimization, goals)
- `orchestration/` - Subagent conductor and orchestration logic (26 files, Phase 6)
  - `conductor.py` - Smart delegation, complexity estimation, context management
  - `INDEX.md` - Orchestration API reference
- `workflows/` - Interactive workflows for guided operations (15 files, Phase 6)
  - `categorization.py` - Categorization workflow with subagent delegation
  - `INDEX.md` - Workflow API reference
- `operations/` - High-level operations (categorization, analysis, etc.)
- `features/` - Advanced features (7 files, Phase 7)
  - `alerts.py` - Smart alerts and notification scheduling
  - `merchant_intelligence.py` - Merchant variation detection and grouping
  - `documents.py` - Document and receipt requirement tracking
  - `multi_user.py` - Shared expense and settlement tracking
  - `benchmarking.py` - Privacy-first comparative benchmarking
  - `audit.py` - Audit trail and activity logging
  - `INDEX.md` - Features API reference
- `utils/` - Utility functions (backup, validation, logging, etc.)

---

### `/data/` - Working Data

Contains runtime data, user configuration, and persistent state.

| Path | Description | Type |
|------|-------------|------|
| `data/config.json` | User preferences and settings | Config |
| `data/local_rules.json` | Local rule engine rules (Phase 2) | Data |
| `data/platform_rules.json` | Platform rule tracking (Phase 2) | Data |
| `data/merchants/merchant_mappings.json` | Merchant normalization mappings (Phase 2) | Data |
| `data/tax/ato_category_mappings.json` | ATO category mappings (Phase 4) | Tax Data |
| `data/tax/deduction_patterns.json` | Deduction detection patterns (Phase 4) | Tax Data |

**Purpose:** Persistent storage for configuration, rules, and learned patterns.

**Note:** All files except INDEX.md are git-ignored to protect user data.

---

### `/tests/` - Test Suite

Contains all unit and integration tests.

| Path | Description | Type |
|------|-------------|------|
| `tests/unit/test_api_client.py` | API client unit tests | Unit Test |
| `tests/unit/test_backup.py` | Backup utilities unit tests | Unit Test |
| `tests/unit/test_validation.py` | Validation unit tests | Unit Test |
| `tests/unit/test_index_updater.py` | Index updater unit tests | Unit Test |
| `tests/unit/test_rule_engine.py` | Rule engine unit tests (Phase 2) | Unit Test |
| `tests/unit/test_merchant_normalizer.py` | Merchant normalizer unit tests (Phase 2) | Unit Test |
| `tests/unit/test_categorize.py` | Categorization unit tests (Phase 2) | Unit Test |
| `tests/unit/test_spending.py` | Spending analysis unit tests (Phase 3) | Unit Test |
| `tests/unit/test_trends.py` | Trend detection unit tests (Phase 3) | Unit Test |
| `tests/unit/test_reporting.py` | Report formatters unit tests (Phase 3) | Unit Test |
| `tests/unit/test_ato_categories.py` | ATO category mapping unit tests (Phase 4) | Unit Test |
| `tests/unit/test_tax_reporting.py` | Tax reporting unit tests (Phase 4) | Unit Test |
| `tests/unit/test_deduction_detector.py` | Deduction detector unit tests (Phase 4) | Unit Test |
| `tests/unit/test_cgt_tracker.py` | CGT tracker unit tests (Phase 4) | Unit Test |
| `tests/unit/test_bas_preparation.py` | BAS preparation unit tests (Phase 4) | Unit Test |
| `tests/unit/test_historical_scenarios.py` | Historical scenario unit tests (Phase 5) | Unit Test |
| `tests/unit/test_projections.py` | Projection scenario unit tests (Phase 5) | Unit Test |
| `tests/unit/test_optimization.py` | Optimization engine unit tests (Phase 5) | Unit Test |
| `tests/unit/test_tax_scenarios.py` | Tax scenario unit tests (Phase 5) | Unit Test |
| `tests/unit/test_cash_flow.py` | Cash flow forecast unit tests (Phase 5) | Unit Test |
| `tests/unit/test_goals.py` | Goal tracking unit tests (Phase 5) | Unit Test |
| `tests/integration/test_api_client_integration.py` | API integration tests | Integration Test |
| `tests/integration/test_rule_engine_integration.py` | Rule engine integration tests (Phase 2) | Integration Test |
| `tests/integration/test_analysis_integration.py` | Analysis workflow integration tests (Phase 3) | Integration Test |
| `tests/integration/test_tax_intelligence.py` | Tax intelligence integration tests (Phase 4) | Integration Test |
| `tests/integration/test_scenario_analysis.py` | Scenario analysis integration tests (Phase 5) | Integration Test |
| `tests/unit/test_conductor.py` | Subagent conductor unit tests (Phase 6) | Unit Test |
| `tests/unit/test_context_preservation.py` | Context preservation unit tests (Phase 6) | Unit Test |
| `tests/unit/test_categorization_workflow.py` | Categorization workflow unit tests (Phase 6) | Unit Test |
| `tests/unit/test_alerts.py` | Alert foundation unit tests (Phase 7) | Unit Test |
| `tests/unit/test_alert_scheduler.py` | Alert scheduler unit tests (Phase 7) | Unit Test |
| `tests/unit/test_merchant_intelligence.py` | Merchant intelligence unit tests (Phase 7) | Unit Test |
| `tests/unit/test_documents.py` | Document management unit tests (Phase 7) | Unit Test |
| `tests/unit/test_multi_user.py` | Multi-user support unit tests (Phase 7) | Unit Test |
| `tests/unit/test_benchmarking.py` | Benchmarking unit tests (Phase 7) | Unit Test |
| `tests/unit/test_audit.py` | Audit trail unit tests (Phase 7) | Unit Test |
| `tests/integration/test_orchestration.py` | Orchestration integration tests (Phase 6) | Integration Test |
| `tests/integration/test_advanced_features.py` | Advanced features integration tests (Phase 7) | Integration Test |

**Test Coverage:** 287 tests (243 unit + 44 integration), all passing
- Phase 1-6: 227 tests (189 unit + 38 integration)
- Phase 7: 60 tests (54 unit + 6 integration)

**Purpose:** Comprehensive test coverage for all Agent Smith functionality.

---

## Quick Navigation

### For Developers

- **Getting Started:** [README.md](README.md)
- **Design Specification:** [docs/design/2025-11-20-agent-smith-design.md](docs/design/2025-11-20-agent-smith-design.md)
- **Implementation Roadmap:** See design doc Section 11

### For AI Agents

- **PocketSmith API Reference:** [ai_docs/pocketsmith-api-documentation.md](ai_docs/pocketsmith-api-documentation.md)
- **Agent Smith Architecture:** [docs/design/2025-11-20-agent-smith-design.md](docs/design/2025-11-20-agent-smith-design.md)
- **Reference Scripts:** [build/scripts/](build/scripts/)

### Key Documents

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](README.md) | Project overview | All |
| [docs/design/2025-11-20-agent-smith-design.md](docs/design/2025-11-20-agent-smith-design.md) | Complete design spec | Developers, AI agents |
| [ai_docs/pocketsmith-api-documentation.md](ai_docs/pocketsmith-api-documentation.md) | API reference | AI agents |

---

## File Counts

- **Documentation Files:** 2 (+ 9 in build/docs)
- **Design Specifications:** 1
- **AI Reference Docs:** 1
- **Reference Scripts:** 40+ (in build/scripts)

---

## Repository Size

- **Active Files:** ~812KB
- **Build Reference:** ~1MB
- **Total:** ~2MB
- **Backup (original work):** 341MB at `../budget-smith-backup-20251120_093733/`

---

## Notes

- `.env` file contains sensitive API keys and is protected by `.gitignore`
- `build/` directory is temporary and will be removed before publication
- All useful content from `build/` will be incorporated into Agent Smith skill structure
- Complete backup of original work exists at `../budget-smith-backup-20251120_093733/`

---

**Last Updated:** 2025-11-21
**Repository Version:** Phase 7 Complete (87.5% Implementation)
