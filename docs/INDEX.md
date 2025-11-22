# Documentation Index

**Last Updated:** 2025-11-22

This directory contains all project documentation for Agent Smith.

---

## Directory Structure

```
docs/
├── INDEX.md                               # This file
├── design/                                # Design specifications
│   └── 2025-11-20-agent-smith-design.md  # Complete Agent Smith design
├── guides/                                # User guides
│   ├── backup-and-restore-guide.md       # Backup & Restore System guide
│   ├── health-check-guide.md             # Health Check System guide
│   ├── platform-to-local-migration.md    # Platform to Local Rules Migration guide
│   └── unified-rules-guide.md            # Unified Rules System guide
├── examples/                              # Example YAML files
│   ├── README.md                          # Examples overview
│   ├── basic-rules.yaml                   # Basic category and label rules
│   ├── advanced-patterns.yaml             # Advanced patterns and techniques
│   ├── household-workflow.yaml            # Shared household setup
│   └── tax-deductible.yaml               # Tax deduction tracking
└── research/                              # Research documents
    └── pocketsmith-backup-and-limitations-research.md  # PocketSmith capabilities research
```

---

## Design Specifications

### [design/2025-11-20-agent-smith-design.md](design/2025-11-20-agent-smith-design.md)

**Complete Agent Smith Design Specification**

**Status:** Approved, ready for implementation
**Version:** 1.0
**Date:** 2025-11-20

**Contents:**
1. Core Architecture (3-tier system)
2. Directory Structure (with smart archiving & INDEX.md)
3. Hybrid Rule Engine (platform + local)
4. Tax Intelligence Module (3 levels: Reference, Smart, Full)
5. Scenario Analysis Engine (4 types)
6. Subagent Orchestration Strategy
7. Slash Commands (8 commands)
8. Additional Features (10 high-value capabilities)
9. Health Check System (6 scores)
10. Configuration (.env, config.json)
11. Implementation Roadmap (16-week, 8 phases)

**Size:** 37KB
**Lines:** 600+
**Scope:** Complete specification from design to implementation

**Key Sections:**
- **Executive Summary** - Project overview and value proposition
- **Architecture** - Three-tier system design
- **Features** - Comprehensive feature specifications
- **Roadmap** - Detailed 16-week implementation plan

---

## User Guides

### [guides/unified-rules-guide.md](guides/unified-rules-guide.md)

**Unified Rules System - Complete Guide**

**Status:** Complete
**Date:** 2025-11-22

Comprehensive guide to the YAML-based unified rule system for transaction categorization and labeling.

**Contents:**
- Quick start with template selection
- Category and label rule syntax reference
- Two-phase execution explanation (categories → labels)
- Intelligence modes (Conservative/Smart/Aggressive)
- LLM integration (fallback, validation, learning)
- Advanced patterns (cross-category, account-based, tax tracking)
- Operational modes (DRY_RUN/VALIDATE/APPLY)
- Update strategies (SKIP_EXISTING/REPLACE_ALL/etc.)
- Template system overview
- Migration from platform rules
- Troubleshooting guide

**Key Features:**
- Pattern matching with exclusions
- Confidence scoring (0-100%)
- Account-specific routing
- Amount-based conditions
- LLM fallback for unmatched transactions
- Rule learning from LLM suggestions

**Size:** ~45KB
**Sections:** 12 major sections with examples

### [guides/platform-to-local-migration.md](guides/platform-to-local-migration.md)

**Platform to Local Rules Migration Guide**

**Status:** Complete
**Date:** 2025-11-22

Guide for migrating existing PocketSmith platform rules to the unified YAML system.

**Contents:**
- Why migrate (limitations of platform rules)
- Migration process (export, convert, test, switch)
- Python migration script usage
- Testing and validation
- Rollback procedures

**Size:** ~10KB

### [guides/health-check-guide.md](guides/health-check-guide.md)

**Health Check System User Guide**

**Status:** Complete
**Date:** 2025-11-21

Comprehensive guide covering:
- The 6 health dimensions and their weights
- How to run health checks
- Interpreting scores and recommendations
- Automated monitoring configuration
- Example output and troubleshooting

**Size:** ~14KB

### [guides/backup-and-restore-guide.md](guides/backup-and-restore-guide.md)

**Backup & Restore System User Guide**

**Status:** Complete
**Date:** 2025-11-22

Comprehensive guide covering:
- What can/cannot be backed up and restored
- Activity-specific backup operations (9 activity types)
- Rollback capabilities and limitations
- PocketSmith subscription tiers and API access
- Usage examples with Python API
- Best practices and troubleshooting

**Key Features:**
- Activity-based backup metadata
- Clear rollback capability indicators
- API limitation warnings (category rules cannot be updated/deleted)
- Tier requirement notifications (API works on all tiers)

**Size:** ~12KB

### [guides/onboarding-guide.md](guides/onboarding-guide.md)

**Agent Smith Onboarding Guide**

**Status:** Complete
**Date:** 2025-11-22

Complete user guide for first-time Agent Smith setup.

**Contents:**
- 8-stage onboarding journey walkthrough
- Prerequisites and time estimates
- Step-by-step instructions for each stage
- Template selection guidance
- Customization examples
- Troubleshooting common issues
- Next steps after onboarding

**Key Stages:**
1. Prerequisites Check (2 min)
2. Discovery (5-10 min)
3. Template Selection (3-5 min)
4. Template Customization (10-20 min)
5. Intelligence Mode Selection (2 min)
6. Incremental Categorization (20-60 min)
7. Health Check & Progress (5 min)
8. Ongoing Usage (2 min)

**Target Audience:** New Agent Smith users
**Total Time:** 30-60 minutes
**Related:** INSTALL.md, unified-rules-guide.md, health-check-guide.md

**Size:** ~10KB

---

## Example Files

### [examples/](examples/)

**YAML Rule Examples**

**Status:** Complete
**Date:** 2025-11-22

Example YAML files demonstrating various patterns and use cases.

**Available Examples:**

1. **[basic-rules.yaml](examples/basic-rules.yaml)** - Beginner-level examples
   - Simple pattern matching
   - Basic labels (Essential, Discretionary)
   - Large purchase flagging
   - Uncategorized flagging

2. **[advanced-patterns.yaml](examples/advanced-patterns.yaml)** - Advanced features
   - Account-specific categorization
   - Amount-based rules
   - Complex exclusions
   - Multi-condition labels
   - Cross-category patterns

3. **[household-workflow.yaml](examples/household-workflow.yaml)** - Shared household
   - Shared vs personal expense separation
   - Contributor tracking
   - Approval workflows
   - Reconciliation items
   - Error detection

4. **[tax-deductible.yaml](examples/tax-deductible.yaml)** - Tax optimization
   - Work-related expenses (ATO codes)
   - Home office deductions
   - Investment deductions
   - Substantiation requirements
   - CGT event tracking
   - GST tracking

**See also:** [data/templates/](../data/templates/) for ready-to-use templates

---

## Research Documents

### [research/pocketsmith-backup-and-limitations-research.md](research/pocketsmith-backup-and-limitations-research.md)

**PocketSmith Backup, Subscription Tiers, and API Limitations Research**

**Status:** Complete
**Date:** 2025-11-22
**Version:** 1.0

Comprehensive research covering:
- **Backup Best Practices** - What can/cannot be backed up via API and web interface
- **Subscription Tiers** - Feature comparison across Free, Foundation, Flourish, Fortune
- **Category Rules & Optimization** - API limitations, management, and backup strategies
- **Reconciliation** - PocketSmith's approach vs traditional accounting reconciliation
- **Key Takeaways** - Critical implementation guidance for Agent Smith

**Key Findings:**
- API access is free and unrestricted for all subscription tiers
- Category rules cannot be backed up via CSV export (must track separately)
- No PUT/DELETE API endpoints for category rules (create-only)
- PocketSmith has no traditional reconciliation (uses balance verification instead)
- Attachments not included in CSV backups (must download via API)
- Budgets excluded from CSV backups

**Size:** ~23KB
**Sources:** 20+ official PocketSmith documentation pages and API references

---

## Implementation Documentation

### [implementation/llm-categorization-implementation-summary.md](implementation/llm-categorization-implementation-summary.md)

**LLM Categorization & Labeling - Implementation Summary**

**Status:** Complete
**Date:** 2025-11-22

Comprehensive summary of the LLM-powered categorization and labeling system implementation.

**Contents:**
- Executive summary and architecture overview
- Features delivered (6 major components)
- File structure (57 scripts, 61 tests)
- Test coverage (445 tests, 95% coverage)
- Code quality metrics (mypy, flake8, black)
- Usage examples and integration points
- Performance characteristics
- Next steps (4 phases)
- Known limitations and API constraints

**Key Achievements:**
- Hybrid categorization (rules + LLM fallback)
- Two-phase execution (categories → labels)
- Rule learning from LLM patterns
- Template system (4 household types)
- Intelligence modes (Conservative/Smart/Aggressive)
- Comprehensive documentation

**Size:** ~25KB

### [implementation/task-6-integration-summary.md](implementation/task-6-integration-summary.md)

**Task 6: Integration with Categorization Workflow**

**Status:** Complete
**Date:** 2025-11-22

Detailed technical summary of Task 6 from the LLM categorization plan.

**Contents:**
- Hybrid categorization flow diagram
- Intelligence mode integration
- Two-phase execution logic
- Rule learning implementation
- API reference and examples

**Size:** ~10KB

---

## Future Documentation

As implementation progresses, this directory will expand to include:

- **API Documentation** - Internal API docs for Agent Smith modules
- **Testing Documentation** - Test plans and results
- **Operations Guides** - Deployment and operational procedures

---

## Quick Links

- **Back to Repository:** [../README.md](../README.md)
- **Repository Index:** [../INDEX.md](../INDEX.md)
- **AI Documentation:** [../ai_docs/INDEX.md](../ai_docs/INDEX.md)

---

**Document Count:** 12 documents (1 design + 5 guides + 4 examples + 1 research + 2 implementation)
**Total Size:** ~181KB
