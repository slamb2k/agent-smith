# Data - Index

**Last Updated:** 2025-11-22

**Purpose:** Working data and persistent state for Agent Smith

---

## Rules

| File | Description | Format | Status |
|------|-------------|--------|--------|
| `rules.yaml` | Active unified rules file | YAML | Active (git-ignored) |
| `rules.yaml.backup` | Backup of rules before template application | YAML | Created when needed |
| `platform_rules.json` | Platform rule tracking (deprecated) | JSON | Legacy |
| `local_rules.json` | Old local rules format (deprecated) | JSON | Legacy |

**Note:** Use `rules.yaml` for all new rule management. The unified YAML system replaces both platform and local JSON rules.

---

## Templates

Pre-built rule templates for common household types (see `templates/README.md`):

| Template | File | Description |
|----------|------|-------------|
| Simple | `templates/simple.yaml` | Single person, no shared expenses |
| Separated Families | `templates/separated-families.yaml` | Divorced/separated with shared custody |
| Shared Household | `templates/shared-household.yaml` | Couples, roommates, families |
| Advanced | `templates/advanced.yaml` | Business owners, investors, complex finances |

Apply with: `uv run python scripts/setup/template_selector.py`

---

## Configuration

- **config.json** - User preferences and settings (smart mode defaults)

---

## State Files

These will be created during operations:
- `rule_metadata.json` - Rule tracking and performance (deprecated for YAML rules)
- `session_state.json` - Current session context

---

## Subdirectories

- **templates/** - Pre-built rule templates (4 household types)
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
