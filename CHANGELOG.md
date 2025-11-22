# Changelog

All notable changes to Agent Smith will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.4] - 2025-11-23

### Changed
- **Onboarding Command Consolidated into Main Command**
  - Removed separate `/agent-smith-onboard` command
  - Main `/agent-smith` command now includes conditional onboarding (first time) and intelligent suggestions (every time)
  - First-time users: Run full 8-stage onboarding workflow automatically
  - Returning users: Skip directly to Stage 9 (Intelligent Suggestions)
  - Simplified command structure from 9 commands to 8 commands

### Added
- **Stage 9: Intelligent Suggestions**
  - Always runs after onboarding or when invoked by returning users
  - Analyzes current setup to provide priority actions, opportunities, insights, and maintenance tasks
  - Context-aware suggestions based on selected templates (PAYG, Sole Trader, Property Investor, etc.)
  - Seasonal recommendations (EOFY prep, BAS deadlines, tax planning)
  - Priority ranking based on urgency (uncategorized transactions, tax deadlines, health score, etc.)

### Removed
- `/agent-smith-onboard` command (functionality merged into `/agent-smith`)

## [1.3.3] - 2025-11-23

### Changed
- **Converted to Plugin-Only Distribution**
  - Removed `marketplace.json` - now distributed as a standalone plugin only
  - Simpler installation: `claude plugin install https://github.com/slamb2k/agent-smith`
  - Better suited for single-plugin architecture

- **Living Templates Refactored to Label-Based Approach**
  - Removed special categories from `shared-hybrid` and `separated-parents` templates
  - Now use standard expense categories (Bills, Groceries, Medical, Education, etc.)
  - Account context indicates whether expense is shared
  - Labels track who paid (Contributor: Partner A/B, Parent A/B)
  - Labels identify child-related expenses (Kids Expense, Child Support, etc.)
  - Benefits: Cleaner category structure, better alignment with existing PocketSmith setups

## [1.3.1] - 2025-11-23

### Changed
- **Multi-Living Arrangement Support** - Living layer now allows multiple selections
  - Removed conflict between `shared-hybrid` and `separated-parents` templates
  - Users can now select both templates for complex situations (e.g., divorced with kids + living with new partner)
  - Updated onboarding documentation to clarify multi-select capability
  - Example use case: Track both child support/custody expenses AND shared household expenses

## [1.3.0] - 2025-11-23

### Removed
- **build/ directory** - Temporary reference materials from previous migration work
  - 40+ Python scripts from previous PocketSmith migration
  - 9 migration documentation files
  - All patterns and insights already incorporated into Agent Smith implementation

### Added
- **LESSONS_LEARNED.md** - Comprehensive migration insights documentation
  - PocketSmith API quirks and workarounds
  - Category hierarchy best practices
  - Transaction categorization patterns
  - Merchant name normalization strategies
  - User experience lessons from real-world migration
- **CHANGELOG.md** - This file for tracking version history

### Changed
- Repository marked as publication-ready
- Documentation updated to remove build/ references
- INDEX.md updated to reflect clean repository structure

## [1.2.0] - 2025-11-21

### Added
- **Composable Template System** - Flexible rule template architecture
  - Template schema with YAML support
  - Label-based composition (`base_templates`, `addons`, `extras`)
  - Template merger with validation
  - Interactive template selector
  - Four built-in templates: simple, shared-household, separated-families, advanced

- **Enhanced Onboarding Workflow**
  - Plugin-aware execution for marketplace installs
  - Template-based rule initialization
  - Incremental categorization with progress tracking
  - Health score improvements visualization

### Changed
- Onboarding workflow refactored to use template system
- Rule engine supports both legacy and YAML-based rules

## [1.1.1] - 2025-11-21

### Fixed
- Plugin mode onboarding path resolution
- Corrected script filenames in onboarding workflow

## [1.1.0] - 2025-11-21

### Added
- **Phase 8: Health Check & Polish** - Complete
  - HealthCheckEngine for comprehensive PocketSmith setup evaluation
  - 6 health dimensions: Data Quality, Category Structure, Rule Engine, Tax Readiness, Automation, Budget Alignment
  - RecommendationEngine for prioritized improvement suggestions
  - HealthMonitor for automated weekly checks and alerts
  - HealthCheckCache for performance optimization
  - Health check guide documentation

- **Phase 7: Advanced Features** - Complete
  - Smart Alerts & Notifications with scheduling
  - Merchant Intelligence with variation detection
  - Document Management with ATO compliance tracking
  - Multi-User Shared Expenses with settlement optimization
  - Privacy-first Benchmarking with anonymization
  - Comprehensive Audit Trail with undo capability

- **Phase 6: Orchestration & UX** - Complete
  - Intelligent SubagentConductor for delegation decisions
  - ContextManager for user preferences
  - 8 specialized slash commands
  - Interactive categorization workflow
  - LLM-powered AI categorization with Claude

### Changed
- Test coverage: 350 tests (all passing)
- Complete 8-phase implementation (100% roadmap)

## [1.0.0] - 2025-11-20

### Added
- **Phase 5: Scenario Analysis** - Complete
  - Historical "what-if" modeling
  - Future spending projections with inflation
  - Optimization engine (subscriptions, trends, recurring)
  - Tax scenario planning
  - Cash flow forecasting
  - Goal tracking and progress monitoring

- **Phase 4: Tax Intelligence** - Complete
  - 3-tier tax intelligence system (Reference/Smart/Full)
  - ATO category mappings
  - Deduction detection with confidence scoring
  - CGT tracking with FIFO matching
  - BAS preparation for quarterly reporting
  - Tax reports with GST tracking

- **Phase 3: Analysis & Reporting** - Complete
  - Spending analysis by category, merchant, time period
  - Trend detection (increasing/decreasing/stable)
  - Multi-format reports (Markdown, CSV, JSON, HTML)

- **Phase 2: Rule Engine** - Complete
  - Hybrid rule system (platform + local rules)
  - Pattern matching with regex, amount ranges, exclusions
  - Intelligence modes (Conservative/Smart/Aggressive)
  - Performance tracking (matches, accuracy, overrides)
  - Merchant normalization and intelligence
  - Batch categorization with dry-run mode

- **Phase 1: Foundation** - Complete
  - Directory structure and INDEX.md templates
  - PocketSmithClient API wrapper with rate limiting
  - BackupManager with timestamped backups
  - Logging infrastructure
  - Configuration management
  - Test framework with pytest

### Technical
- Test coverage: 194 tests (167 unit + 27 integration)
- Python 3.10+ support
- Full type hints with mypy
- Code formatting with Black
- Linting with flake8

## [0.1.0] - 2025-11-20

### Added
- Initial project structure
- Design specification complete
- Repository setup with .gitignore, requirements.txt
- Documentation framework

---

[Unreleased]: https://github.com/slamb2k/agent-smith/compare/v1.3.1...HEAD
[1.3.1]: https://github.com/slamb2k/agent-smith/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/slamb2k/agent-smith/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/slamb2k/agent-smith/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/slamb2k/agent-smith/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/slamb2k/agent-smith/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/slamb2k/agent-smith/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/slamb2k/agent-smith/releases/tag/v0.1.0
