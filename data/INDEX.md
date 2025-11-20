# Data - Index

**Last Updated:** 2025-11-20

**Purpose:** Working data and persistent state for Agent Smith

---

## Configuration

- **config.json** - User preferences and settings (smart mode defaults)

---

## State Files

No state files yet. These will be created during operations:
- `rule_metadata.json` - Rule tracking and performance
- `platform_rules.json` - PocketSmith native rules
- `local_rules.json` - Enhanced local rules
- `session_state.json` - Current session context

---

## Subdirectories

- **alerts/** - Alert rules and history
- **tax/** - Tax intelligence data (ATO mappings, deductions, CGT) - see `tax/INDEX.md`
- **scenarios/** - Saved scenarios and results
- **merchants/** - Merchant intelligence data
- **investments/** - Investment tracking
- **goals/** - Financial goal tracking
- **health/** - Health scores and recommendations
- **audit/** - Change logs and activity tracking
- **cache/** - API response cache (7-day TTL)

---

**Related:**
- Design: `docs/design/2025-11-20-agent-smith-design.md`
