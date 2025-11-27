# AI Documentation Index

**Last Updated:** 2025-11-27
**Document Count:** 13
**Total Size:** ~195KB

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

### PocketSmith API Reference

#### [pocketsmith-api-documentation.md](pocketsmith-api-documentation.md)

**PocketSmith API v2.0 Reference (Offline)**

**Source:** https://developers.pocketsmith.com/
**Last Updated:** 2025-11-16
**Version:** v2.0
**Size:** 7.3KB

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

#### [pocketsmith-api-quick-reference.md](pocketsmith-api-quick-reference.md)

**PocketSmith API Quick Reference**

**Source:** https://developers.pocketsmith.com
**Last Updated:** 2025-11-27
**Version:** v2.0
**Size:** ~8KB

**Contents:**
- Base URL and authentication methods
- All API endpoints organized by resource
- Pagination and query parameters
- Error codes and rate limiting
- Example API calls

**Purpose:** Quick lookup for API endpoints and common operations.

**Use Cases:**
- Quick endpoint reference
- Parameter lookup
- Authentication setup
- Request/response examples

#### [pocketsmith-api-errors.md](pocketsmith-api-errors.md)

**PocketSmith API Error Handling**

**Source:** https://developers.pocketsmith.com/docs/errors
**Last Updated:** 2025-11-27
**Version:** v2.0
**Size:** ~3KB

**Contents:**
- HTTP status codes and meanings
- Error response format
- OAuth-specific errors
- Error handling best practices

**Purpose:** Guide for handling API errors gracefully.

**Use Cases:**
- Debugging API failures
- Implementing error handling
- Understanding error responses

#### [pocketsmith-api-pagination.md](pocketsmith-api-pagination.md)

**PocketSmith API Pagination Guide**

**Source:** https://developers.pocketsmith.com/docs/pagination
**Last Updated:** 2025-11-27
**Version:** v2.0
**Size:** ~4KB

**Contents:**
- Response headers (Per-Page, Total, Link)
- Link header parsing
- Page navigation
- Adjusting page size (10-1000)
- Python example for fetching all records

**Purpose:** Guide for handling paginated API responses.

**Use Cases:**
- Fetching large datasets
- Implementing pagination logic
- Optimizing API call efficiency

#### [pocketsmith-api-budgeting.md](pocketsmith-api-budgeting.md)

**PocketSmith API Budgeting Guide**

**Source:** https://developers.pocketsmith.com/docs/budgeting
**Last Updated:** 2025-11-27
**Version:** v2.0
**Size:** ~5KB

**Contents:**
- Budget analysis data model
- Contextual vs noncontextual packages
- Time period vs event period analysis
- Budget endpoints (budget, budget_summary, trend analysis)
- Handling time period alternatives

**Purpose:** Comprehensive guide for working with budget analysis API.

**Use Cases:**
- Budget tracking and reporting
- Trend analysis
- Actual vs forecast comparisons

#### [pocketsmith-api-oauth.md](pocketsmith-api-oauth.md)

**PocketSmith API OAuth 2.0 Guide**

**Source:** https://developers.pocketsmith.com/docs/oauth
**Last Updated:** 2025-11-27
**Version:** v2.0
**Size:** ~6KB

**Contents:**
- OAuth endpoints and client credentials
- Authorization code flow (steps 1-4)
- Available scopes
- Token refresh process
- Implicit flow for client-side apps
- Security best practices

**Purpose:** Guide for implementing OAuth authentication.

**Use Cases:**
- Third-party app integration
- User authorization flows
- Token management

#### [pocketsmith-api-openapi.json](pocketsmith-api-openapi.json)

**PocketSmith API OpenAPI 3.0 Schema Definitions**

**Source:** https://github.com/pocketsmith/api
**Last Updated:** 2025-11-27
**Version:** v2.0
**Size:** ~25KB

**Contents:**
- OpenAPI 3.0.1 specification
- Complete schema definitions for all API objects:
  - User, Institution, Account, TransactionAccount
  - Transaction, Category, CategoryRule
  - Scenario, Event, Attachment
  - BudgetAnalysis, Period, BudgetAnalysisPackage
  - Currency, TimeZone, SavedSearch
- Security schemes (Developer Key, OAuth 2.0)
- Error response schemas

**Purpose:** Machine-readable schema definitions for validating API responses and understanding object structures.

**Use Cases:**
- Understanding exact field types and descriptions
- Validating API response structures
- Reference for nested object relationships
- Enum values for fields like account type, transaction status

### Claude Code Documentation

#### [cc-skill-authoring-best-practices.md](cc-skill-authoring-best-practices.md)

**Skill Authoring Best Practices**

**Source:** Anthropic Claude Code Documentation
**Last Updated:** 2025-11-23
**Version:** Current
**Size:** 42KB

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

#### [cc-plugins-overview.md](cc-plugins-overview.md)

**Plugins Overview**

**Source:** Anthropic Claude Code Documentation
**Last Updated:** 2025-11-23
**Version:** Current
**Size:** 13KB

**Contents:**
- Quickstart guide for creating plugins
- Plugin system overview
- Custom commands, agents, hooks, skills, and MCP servers
- Local testing and development
- Plugin structure and organization

**Purpose:** Comprehensive guide for understanding and creating Claude Code plugins.

**Use Cases:**
- Plugin development and architecture
- Understanding plugin capabilities
- Creating custom commands and hooks
- Local plugin testing

#### [cc-plugins-reference.md](cc-plugins-reference.md)

**Plugins Technical Reference**

**Source:** Anthropic Claude Code Documentation
**Last Updated:** 2025-11-23
**Version:** Current
**Size:** 13KB

**Contents:**
- Plugin component schemas (commands, agents, hooks, skills, MCP servers)
- CLI commands reference
- plugin.json and marketplace.json specifications
- Technical specifications and development tools

**Purpose:** Complete technical specifications for the Claude Code plugin system.

**Use Cases:**
- Plugin configuration and schema validation
- CLI command reference
- Component development
- Marketplace creation

#### [cc-plugin-marketplaces.md](cc-plugin-marketplaces.md)

**Plugin Marketplaces**

**Source:** Anthropic Claude Code Documentation
**Last Updated:** 2025-11-23
**Version:** Current
**Size:** 14KB

**Contents:**
- Marketplace overview and benefits
- Adding and using marketplaces
- Creating custom marketplaces
- Version management
- Team distribution strategies

**Purpose:** Guide for creating and managing plugin marketplaces for team and community distribution.

**Use Cases:**
- Marketplace creation and management
- Team plugin distribution
- Version tracking and updates
- Source configuration (git, GitHub, local paths)

#### [cc-slash-commands.md](cc-slash-commands.md)

**Slash Commands Reference**

**Source:** Anthropic Claude Code Documentation
**Last Updated:** 2025-11-23
**Version:** Current
**Size:** 22KB

**Contents:**
- Built-in slash commands reference
- Plugin commands
- Command invocation patterns
- Command structure and frontmatter

**Purpose:** Complete reference for Claude Code slash commands, both built-in and plugin-provided.

**Use Cases:**
- Command development
- Understanding built-in commands
- Plugin command creation
- Command frontmatter configuration

#### [cc-hooks.md](cc-hooks.md)

**Hooks Reference**

**Source:** Anthropic Claude Code Documentation
**Last Updated:** 2025-11-23
**Version:** Current
**Size:** 36KB

**Contents:**
- Hook configuration and structure
- Event types and matchers
- Hook types (command, blocking, user-prompt-submit)
- Advanced patterns and examples
- Environment variables and context

**Purpose:** Complete reference for implementing and configuring hooks in Claude Code.

**Use Cases:**
- Hook development and configuration
- Event handling
- Workflow automation
- Custom validation and preprocessing

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
- **Contributing Guide:** [../CONTRIBUTING.md](../CONTRIBUTING.md)
- **Design Documentation:** [../docs/INDEX.md](../docs/INDEX.md)
- **Agent Smith Design:** [../docs/design/2025-11-20-agent-smith-design.md](../docs/design/2025-11-20-agent-smith-design.md)

---

**Summary:**
- **PocketSmith API:** 7 documents (~58KB)
- **Claude Code:** 6 documents (140KB)
- **Total:** 13 documents (~195KB)
