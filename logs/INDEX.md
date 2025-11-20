# Logs - Index

**Last Updated:** 2025-11-20

**Purpose:** Execution logs for Agent Smith operations

**Retention Policy:** 14 days active, then compress to `archive/YYYY-MM.tar.gz`

---

## Active Logs

Log files are created automatically when operations run:
- **operations.log** - High-level operation logs
- **api_calls.log** - API interaction logs
- **errors.log** - Error tracking

---

## Log Levels

Configured via `LOG_LEVEL` in .env:
- DEBUG - Verbose logging for development
- INFO - Normal operational logging (default)
- WARNING - Warnings and issues
- ERROR - Errors only

---

## Archive

Logs older than 14 days are compressed monthly.

See: `archive/INDEX.md` for archived log inventory

---

**Related:**
- Logging config: `scripts/utils/logging_config.py`
