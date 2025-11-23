# AI Documentation Index

**Last Updated:** 2025-11-23

This directory contains documentation specifically formatted for AI agents and subagents to reference during Agent Smith operations.

---

## Purpose

AI agents need quick access to comprehensive references without repeatedly downloading documentation. This directory provides:

- **API References** - Complete API documentation for external services
- **Protocol Documentation** - Agent communication protocols
- **Operational Guides** - AI-specific operational procedures
- **Context-Optimized** - Formatted for efficient LLM consumption

---

## Current Documentation

### [pocketsmith-api-documentation.md](pocketsmith-api-documentation.md)

**PocketSmith API v2.0 Reference (Offline)**

**Source:** https://developers.pocketsmith.com/
**Last Updated:** 2025-11-16
**Version:** v2.0

**Contents:**
- Introduction & Overview
- Authentication (Developer Keys & OAuth 2.0)
- API Reference:
  - Users
  - Institutions
  - Accounts
  - Transaction Accounts
  - Transactions
  - Categories
  - Budgeting
  - Supporting Resources
- Common Topics (Pagination, Error Handling)
- Changelog
- Support & Resources

**Purpose:** Provides Agent Smith subagents with complete PocketSmith API reference without needing internet access for basic operations.

**Use Cases:**
- Transaction operations (create, read, update, delete)
- Category management
- Account operations
- Budget analysis
- API error troubleshooting

### [skill-suthoring-best-practices.md](skill-suthoring-best-practices.md)

**Skill Authoring Best Practices (Claude Code)**

**Source:** Anthropic Claude Code Documentation
**Last Updated:** 2025-11-23
**Version:** Current

**Contents:**
- Core principles (Concise is key, Progressive disclosure)
- Structure and organization
- Writing effective instructions
- Code examples and templates
- Testing and validation
- Common patterns and anti-patterns

**Purpose:** Reference guide for developing and maintaining the Agent Smith skill package, ensuring adherence to Claude Code best practices for skill authoring.

**Use Cases:**
- Skill development and maintenance
- SKILL.md optimization
- Documentation structure decisions
- Progressive disclosure implementation
- Context window optimization

---

## Future Documentation

As Agent Smith implementation progresses, this directory will expand to include:

### Planned Documents

- **`ato-tax-guidelines.md`** - Australian Tax Office guidelines and regulations
  - Deduction rules
  - Substantiation requirements
  - CGT guidelines
  - BAS preparation
  - Threshold tables

- **`category-optimization-guide.md`** - Best practices for category structure
  - Hierarchy recommendations
  - Naming conventions
  - Tax-aligned categorization
  - Common patterns

- **`rule-engine-architecture.md`** - Hybrid rule engine documentation
  - Rule schema
  - Performance metrics
  - Platform vs. local rules
  - Rule lifecycle

- **`subagent-protocols.md`** - Agent communication standards
  - Delegation message format
  - Response schemas
  - Error handling
  - Context management

### Tax Documentation (Cached)

Future subdirectory: `tax/`
- ATO guidelines (cached with version tracking)
- Tax legislation
- Threshold tables
- Compliance checklists
- Cache metadata for freshness tracking

---

## Document Standards

All documentation in this directory follows these standards:

1. **Self-Contained** - No external dependencies for core information
2. **Version Tracked** - Include source URL and last updated date
3. **LLM-Optimized** - Clear structure, comprehensive tables, examples
4. **Offline-First** - Usable without internet access
5. **Freshness Metadata** - Track when cache needs refresh

---

## Usage by AI Agents

### When to Reference

Agent Smith subagents should reference these documents when:

- Making PocketSmith API calls
- Analyzing transactions for tax implications
- Creating or applying categorization rules
- Optimizing category structures
- Generating compliance reports
- Troubleshooting API errors

### How to Reference

Subagents receive document references in their delegation messages:

```markdown
REFERENCES:
- API Documentation: ai_docs/pocketsmith-api-documentation.md
- Tax Guidelines: ai_docs/ato-tax-guidelines.md (when available)
```

### Caching Strategy

Documents in this directory are:
- **Locally cached** for offline access
- **Version tracked** for freshness
- **Periodically refreshed** from authoritative sources
- **Compared on update** to detect changes

---

## Quick Links

- **Back to Repository:** [../README.md](../README.md)
- **Repository Index:** [../INDEX.md](../INDEX.md)
- **Design Documentation:** [../docs/INDEX.md](../docs/INDEX.md)
- **Agent Smith Design:** [../docs/design/2025-11-20-agent-smith-design.md](../docs/design/2025-11-20-agent-smith-design.md)

---

**Current Document Count:** 2
**Planned Documents:** 4+ core documents + tax subdirectory
**Total Size:** ~54KB (current)
