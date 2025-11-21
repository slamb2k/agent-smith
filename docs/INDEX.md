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
│   └── health-check-guide.md             # Health Check System guide
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

## Future Documentation

As implementation progresses, this directory will expand to include:

- **Implementation Guides** - Step-by-step development documentation
- **API Documentation** - Internal API docs for Agent Smith modules
- **Testing Documentation** - Test plans and results
- **Operations Guides** - Deployment and operational procedures

---

## Quick Links

- **Back to Repository:** [../README.md](../README.md)
- **Repository Index:** [../INDEX.md](../INDEX.md)
- **AI Documentation:** [../ai_docs/INDEX.md](../ai_docs/INDEX.md)

---

**Document Count:** 4 documents (1 design specification + 2 user guides + 1 research document)
**Total Size:** ~86KB
