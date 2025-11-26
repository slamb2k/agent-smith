# Welcome Screen Design

**Date:** 2025-11-26
**Status:** Approved
**Author:** Claude + User collaboration

## Overview

Replace the current session start hook's API-dependent dashboard with a local-only welcome screen. This provides faster startup, no network dependencies, and clear status visibility based on local configuration and state files.

## Goals

1. **No API calls** - Use only local filesystem data
2. **Fast execution** - Target <100ms startup time
3. **Clear status** - Show configuration and onboarding state at a glance
4. **Actionable** - Always recommend the next logical action
5. **Branded** - Keep the Agent Smith ASCII logo

## Data Sources

The welcome script reads these local files:

| File | Data Extracted |
|------|----------------|
| `.env` | `POCKETSMITH_API_KEY` presence and format validation |
| `data/onboarding_state.json` | `onboarding_completed`, current stage, timestamps |
| `data/rules.yaml` | Rule count |
| `data/health_cache.json` | Last score, status, timestamp |
| `data/activity_log.json` | Last action and timestamp |
| `data/template_config.json` | Active templates (PAYG, sole-trader, etc.) |
| `data/config.json` | Intelligence mode, tax level settings |

All file reads are wrapped in try/except - missing files are expected states, not errors.

## Status Checks

### A. API Key Check
```python
def check_api_key() -> dict:
    # Returns: {"present": bool, "valid_format": bool}
    # - Check .env in USER_CWD (plugin mode) or current dir
    # - Valid format: 128-char hex string (basic sanity check)
```

### B. Onboarding State
```python
def check_onboarding() -> dict:
    # Returns: {"status": "not_started"|"in_progress"|"complete",
    #           "current_stage": int|None, "stage_name": str|None}
    # - not_started: data/ doesn't exist or no onboarding_state.json
    # - in_progress: file exists but onboarding_completed != true
    # - complete: onboarding_completed == true
```

### C. Rules Count
```python
def check_rules() -> dict:
    # Returns: {"count": int, "file_exists": bool}
    # - Parse data/rules.yaml, count rule entries
    # - 0 if file doesn't exist
```

### D. Health Check Cache
```python
def check_health_cache() -> dict:
    # Returns: {"score": int|None, "status": str, "days_ago": int|None}
    # - Read data/health_cache.json
    # - Calculate days since last check
    # - None values if no cache exists
```

### E. Last Activity
```python
def check_last_activity() -> dict:
    # Returns: {"action": str|None, "date": str|None, "days_ago": int|None}
    # - Read last line of data/activity_log.json (JSONL format)
```

### G. Template Config
```python
def check_templates() -> dict:
    # Returns: {"primary": str|None, "living": list, "additional": list}
    # - Read data/template_config.json or data/onboarding_state.json
```

## Action Priority Waterfall

The recommended action follows this priority order (first matching condition wins):

| Priority | Condition | Recommended Action |
|----------|-----------|-------------------|
| 1 | API key missing | "Add your PocketSmith API key to .env" |
| 2 | API key invalid format | "Check your API key format in .env" |
| 3 | Onboarding not started | "Run `/smith:install` to set up Agent Smith" |
| 4 | Onboarding in progress | "Continue setup with `/smith:install` (Stage {N}: {name})" |
| 5 | No rules configured | "Create categorization rules with `/smith:install`" |
| 6 | Health check never run | "Run `/smith:health` to assess your financial data" |
| 7 | Health check stale (>7 days) | "Run `/smith:health` - last check was {N} days ago" |
| 8 | Health score < 50 | "Run `/smith:categorize` to improve your health score" |
| 9 | Default (all good) | "Run `/smith:categorize` or `/smith:insights`" |

Two actions are always shown when available (primary + secondary from waterfall).

## Output Format

### Formatted Output (for display)

```
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
[... full ASCII art logo ...]
                   WELCOME TO AGENT SMITH
                 Good Morning Mr. Anderson...

══════════════════════════════════════════════════════════════
 STATUS
══════════════════════════════════════════════════════════════
 Config      API Key: ✓ configured
 Setup       Onboarding: ✓ Complete (PAYG Employee + Shared Hybrid)
 Rules       47 categorization rules active
 Health      Score: 82/100 (3 days ago)
 Activity    Categorized 23 transactions (Nov 24)

══════════════════════════════════════════════════════════════
 NEXT STEPS
══════════════════════════════════════════════════════════════
 → /smith:categorize    Process new transactions
 → /smith:insights      View spending analysis

══════════════════════════════════════════════════════════════
```

### Status Indicators

- `✓` = good/complete
- `⚠` = warning/needs attention
- `✗` = error/missing
- `○` = not started/unknown

### JSON Output (for hook consumption)

```json
{
  "api_key": {"present": true, "valid_format": true},
  "onboarding": {"status": "complete", "current_stage": null, "stage_name": null},
  "rules": {"count": 47, "file_exists": true},
  "health": {"score": 82, "status": "good", "days_ago": 3},
  "activity": {"action": "Categorized 23 transactions", "date": "2025-11-24", "days_ago": 2},
  "templates": {"primary": "payg-employee", "living": ["shared-hybrid"], "additional": []},
  "recommendations": [
    {"priority": 9, "message": "Process new transactions", "command": "/smith:categorize"},
    {"priority": 9, "message": "View spending analysis", "command": "/smith:insights"}
  ]
}
```

## CLI Interface

```bash
# For hook (JSON output)
uv run python -u scripts/status/welcome.py --output json

# For direct display (formatted)
uv run python -u scripts/status/welcome.py --output formatted
```

## Integration

### Changes to session_start.py

```python
# BEFORE: Called dashboard.py (makes API calls)
def get_status_data() -> dict:
    dashboard_script = project_root / "scripts" / "status" / "dashboard.py"
    # ... subprocess call to dashboard.py

# AFTER: Call welcome.py (local only)
def get_status_data() -> dict:
    welcome_script = project_root / "scripts" / "status" / "welcome.py"
    # ... subprocess call to welcome.py --output json
```

### Error Handling

If welcome.py fails or times out, session_start.py falls back to a minimal "Agent Smith ready" message rather than blocking the session.

## File Changes

### Files to Create

| File | Purpose |
|------|---------|
| `scripts/status/welcome.py` | Main welcome script (local-only checks) |

### Files to Modify

| File | Change |
|------|--------|
| `agent-smith-plugin/hooks/session_start.py` | Replace `dashboard.py` call with `welcome.py` |

### Files Unchanged

- `scripts/status/dashboard.py` - Keep for `/smith:health` (appropriate for API calls there)

## Testing

Unit tests should cover:
1. Each status check function with various file states (missing, empty, valid, invalid)
2. Action waterfall priority logic
3. Output formatting (JSON and formatted modes)
4. Error handling for malformed files
