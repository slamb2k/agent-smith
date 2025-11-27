---
name: smith:schedule
description: Configure automated categorization scheduling
argument-hints:
  - "[--setup|--status|--remove] [--frequency=daily|weekly] [--time=HH:MM]"
---

# Automated Categorization Scheduling

Set up automatic categorization to run on a schedule without manual intervention.

## Goal

Keep your transactions categorized automatically in the background.

## Why This Matters

Regular categorization prevents backlogs and keeps your financial data current. Scheduled runs ensure you never fall behind, and conflicts are ready for quick review when you open Claude Code.

## Execution

**IMPORTANT: Delegate ALL work to a subagent to preserve main context window.**

Use the Task tool with `subagent_type: "general-purpose"` to manage scheduling:

```
Task(
  subagent_type: "general-purpose",
  description: "Manage scheduling",
  prompt: <full subagent prompt below>
)
```

### Subagent Prompt

You are the Agent Smith scheduling assistant.

## Step 1: Check Current Status

First, check if scheduling is already configured:

```bash
uv run python -u scripts/setup/schedule.py --status
```

## Step 2: Based on Arguments

**--status (or no args):**
Display current schedule status and recent activity.

**--setup:**
Ask user preferences using AskUserQuestion:

1. **Frequency**: How often?
   - Daily (recommended for most users)
   - Weekly (for low-volume accounts)
   - Hourly (for high-volume business accounts)

2. **Time**: What time? (default: 6:00am)
   - Suggest early morning before user typically opens Claude Code

Then run:
```bash
uv run python -u scripts/setup/schedule.py --frequency [FREQ] --time [TIME]
```

**--remove:**
```bash
uv run python -u scripts/setup/schedule.py --remove
```

## Step 3: Present Results

Show confirmation with:
- Schedule details (frequency, time)
- How it works (runs in background, logs results)
- How to check status
- How to remove if needed

```
✅ AUTO-CATEGORIZATION SCHEDULED
═══════════════════════════════════════════════════════════════
  Frequency: Daily
  Time: 6:00 AM
  Mode: Smart (auto-apply 90%+ confidence)

  How it works:
  - Runs automatically in the background
  - Logs results to data/auto_categorize.log
  - SessionStart dashboard shows last run status
  - Conflicts flagged for /smith:review-conflicts

  Commands:
  - Check status: /smith:schedule --status
  - Remove: /smith:schedule --remove
═══════════════════════════════════════════════════════════════
```

## Visual Style

Use emojis for status:
- ✅ Scheduled/active
- ⚠️ Configured but not active
- ❌ Not configured

---

## Scheduling Options

| Frequency | When | Best For |
|-----------|------|----------|
| **hourly** | Every hour | High-volume accounts |
| **daily** | Once per day (default: 6am) | Most users |
| **weekly** | Once per week (Sunday 6am) | Low-volume accounts |

## Platform Support

| Platform | Method | Setup |
|----------|--------|-------|
| **macOS** | launchd | Automatic |
| **Linux (systemd)** | systemd timer | Automatic |
| **Linux (other)** | cron | Manual (shows crontab entry) |

## How It Works

1. **Background Execution**: Runs without Claude Code open
2. **Smart Mode**: Auto-applies 90%+ confidence categorizations
3. **Conflict Flagging**: Low confidence items flagged for review
4. **Activity Logging**: Results logged for SessionStart dashboard
5. **No Duplicates**: Skips already-categorized transactions

## Next Steps

After scheduling:
- **Check logs**: View `data/auto_categorize.log`
- **Review flagged**: `/smith:review-conflicts`
- **Manual run**: `/smith:categorize`
- **Check status**: `/smith:schedule --status`
