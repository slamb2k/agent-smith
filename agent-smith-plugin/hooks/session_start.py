#!/usr/bin/env python3
"""Agent Smith SessionStart hook - provides configuration status context.

This hook runs at session start to:
1. Check local configuration and state (no API calls)
2. Identify setup status and recommended actions
3. Inject context so Claude can proactively help the user
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def get_plugin_root() -> Path:
    """Get the plugin root directory."""
    return Path(__file__).parent.parent


def get_project_root() -> Path:
    """Get the project root (parent of plugin)."""
    return get_plugin_root().parent


def get_status_data() -> dict:
    """Fetch status data from the welcome script (local only, no API calls).

    Returns:
        Status dictionary or error info if fetch fails.
    """
    project_root = get_project_root()
    welcome_script = project_root / "scripts" / "status" / "welcome.py"

    if not welcome_script.exists():
        return {"error": "Welcome script not found"}

    try:
        # Set USER_CWD so welcome.py knows where to find .env and data/
        user_cwd = os.getcwd()

        result = subprocess.run(
            ["uv", "run", "python", "-u", str(welcome_script), "--output", "json"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=5,  # Fast timeout since no API calls
            env={**os.environ, "PYTHONPATH": str(project_root), "USER_CWD": user_cwd},
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": f"Welcome script failed: {result.stderr[:200]}"}

    except subprocess.TimeoutExpired:
        return {"error": "Status check timed out"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON from welcome script"}
    except Exception as e:
        return {"error": str(e)[:200]}


def format_status_context(status: dict) -> str:
    """Format status data into context string for Claude.

    Args:
        status: Status dictionary from welcome.py

    Returns:
        Formatted context string with instructions
    """
    lines = []

    # ASCII Art Logo - MUST be displayed at top of welcome message
    logo = r"""
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼   ∼∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈         ∼∼ ∼∼≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼                ∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼                 ∼∼∼∼≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋             ∼∼∼∼∼≈≈≈≋≋∼ ∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋     ∼≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≈   ∼≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋    ∼≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼∼  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋    ∼≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼   ≈≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋∼   ∼∼≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼   ≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≈    ∼∼∼≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼   ∼≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋∼    ∼∼∼∼≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈    ≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≈     ∼∼∼∼≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼   ∼≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋      ∼∼∼≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈≈∼   ≈≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋     ∼∼∼∼∼≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈≈∼   ≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋∼    ∼∼∼∼≈≈∼∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈≈≈∼  ∼≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≈    ∼∼∼∼∼∼∼∼∼≈≈≈≈≋≈≈≈≈≈≈≈∼∼∼∼∼≈∼∼ ≈≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋∼∼  ∼∼            ∼∼≈∼∼           ≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≈                   ∼≈∼           ∼≈≈≈∼≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋∼     ∼           ∼≈≋≋∼         ∼≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋∼∼    ∼∼         ∼≈≋≋≋≋∼      ∼∼≈≈∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≈∼    ∼∼∼∼∼∼   ∼∼∼≈≋≋≋≈≈≈∼∼∼∼∼∼≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≈∼   ∼    ∼∼≈≈≈∼≈≈≈≋≋≋≋≋≋≋≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋∼   ∼  ∼∼∼≈≈≈∼∼ ∼≈≈∼∼≈≈≋≋≋≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼∼   ∼∼∼≈≈∼     ∼≈≈≋≋≈≋≋≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼  ∼∼≈≈≈≈∼∼∼∼≈≈≋≋≋≋≋≋≋≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼   ∼∼≈≈≈≈≈≈≈≈≈≋≋≋≈≋≋≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈    ∼∼∼∼∼∼∼∼∼≈≈∼∼∼≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼   ∼≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈    ∼∼∼∼∼∼∼∼∼∼∼≈≈≈≈≈≈∼∼≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈     ∼∼∼∼∼≈≈≈≈≈≈≈≈≈≈∼∼≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈      ∼∼≈≈≈≈≈≈≈≈≈≈∼∼∼≈≈≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈        ∼∼≈∼≈≈≈≈≈∼∼≈≈≈≈≋≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈∼               ∼∼∼≈≈≈≈≋≋≈ ≈≋≋≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋∼ ∼∼              ∼∼≈≈≈≋≋≋≋≈   ≈≋≋≋≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≋≋≋≈   ∼∼∼∼           ∼≈≈≈≋≋≋≋≋≋≈     ∼≈≋≋≋≋≋≋≋≋≋
≋≋≋≋≋≋≋≋≋≋≋≈      ∼∼∼∼∼∼      ∼∼∼≈≈≋≋≋≋≋≋≋≋∼         ∼∼≈≋≋≋≋
≋≋≋≋≋≋≋≈∼         ∼∼∼∼∼∼∼∼   ∼∼≈≋≋≋≋≋≋≋≋≋≋≋∼              ∼≈
≋≋≈∼               ∼∼∼∼∼∼≈≈     ≈≋≋≋≋≋≋≋≋≋≋
                  ∼∼∼∼≈≈≈≈∼      ≈≋≋≋≋≋≋≋≋≈
                 ∼≈∼≈≈≈≈≋∼        ≋≋≋≋≋≋≋≋∼
                 ∼≋≋≈≋≈≈≋∼        ∼≋≋≋≋≋≋≋

                   WELCOME TO AGENT-SMITH

                 Good Morning Mr. Anderson...


"""
    lines.append(logo)

    # Header
    lines.append("=" * 60)
    lines.append("AGENT SMITH - Financial Intelligence Assistant")
    lines.append("=" * 60)
    lines.append("")

    # Check for errors
    if "error" in status:
        lines.append(f"⚠️ Status unavailable: {status['error']}")
        lines.append("")
        lines.append("Available commands: /smith:health, /smith:categorize, /smith:tax")
        lines.append("")
        lines.append("INSTRUCTION: Greet the user and offer to help with their finances.")
        return "\n".join(lines)

    # Current Status Section
    lines.append("📊 CURRENT STATUS")
    lines.append("-" * 40)

    # API Key status
    api_key = status.get("api_key", {})
    if api_key.get("present") and api_key.get("valid_format"):
        lines.append("  Config: ✅ API Key configured")
    elif api_key.get("present"):
        lines.append("  Config: ⚠️ API Key format invalid")
    else:
        lines.append("  Config: ❌ API Key not configured")

    # Onboarding status
    onboarding = status.get("onboarding", {})
    templates = status.get("templates", {})

    if onboarding.get("status") == "complete":
        # Build template summary
        template_parts = []
        if templates.get("primary"):
            template_parts.append(templates["primary"].replace("-", " ").title())
        for t in templates.get("living", []):
            template_parts.append(t.replace("-", " ").title())

        template_str = " + ".join(template_parts) if template_parts else "Complete"
        lines.append(f"  Setup: ✅ {template_str}")
    elif onboarding.get("status") == "in_progress":
        stage = onboarding.get("current_stage", "?")
        stage_name = onboarding.get("stage_name", "Unknown")
        lines.append(f"  Setup: ⚠️ In progress (Stage {stage}: {stage_name})")
    else:
        lines.append("  Setup: ⚪ Not started")

    # Rules count
    rules = status.get("rules", {})
    rule_count = rules.get("count", 0)
    if rule_count > 0:
        lines.append(f"  Rules: {rule_count} categorization rules active")
    else:
        lines.append("  Rules: No rules configured")

    # Health Score (cached)
    health = status.get("health", {})
    if health.get("score") is not None:
        score = health["score"]
        days_ago = health.get("days_ago")
        days_str = f" ({days_ago} days ago)" if days_ago is not None else ""
        emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
        lines.append(f"  Health: {emoji} {score}/100{days_str}")
    else:
        lines.append("  Health: ⚪ Not yet checked")

    # Last activity
    activity = status.get("activity", {})
    if activity.get("action"):
        date_str = f" ({activity.get('date')})" if activity.get("date") else ""
        lines.append(f"  Activity: {activity['action']}{date_str}")

    lines.append("")

    # Recommendations Section
    recommendations = status.get("recommendations", [])
    if recommendations:
        lines.append("🎯 SUGGESTED ACTIONS")
        lines.append("-" * 40)
        for rec in recommendations:
            lines.append(f"  → {rec.get('command', '/smith:help')}: {rec.get('message', 'Action')}")
        lines.append("")

    # Instructions for Claude
    lines.append("=" * 60)
    lines.append("INSTRUCTIONS FOR CLAUDE:")
    lines.append("")
    lines.append("🚀 IMMEDIATE ACTION REQUIRED:")
    lines.append("Before doing ANYTHING else, output this loading message:")
    lines.append('  "Initialising Agent Smith..."')
    lines.append("This gives users immediate feedback while you construct the welcome screen.")
    lines.append("")
    lines.append("IMPORTANT: Always display the ASCII art logo FIRST at the top of")
    lines.append("any welcome message, exactly as shown above (in a code block).")
    lines.append("")
    lines.append("⚠️ CRITICAL: You MUST display the COMPLETE ASCII art logo - ALL 44 LINES.")
    lines.append("DO NOT truncate, abbreviate, summarize, or cut off ANY part of the logo.")
    lines.append("The logo starts with the wave pattern (≋) and ends with the text")
    lines.append("'Good Morning Mr. Anderson...' - EVERY LINE IN BETWEEN MUST BE SHOWN.")
    lines.append("Cutting off the logo is a FAILURE. The full Agent Smith face must appear.")
    lines.append("")
    lines.append("At the EARLIEST opportunity in this session, present the user")
    lines.append("with their current status summary above. Format it nicely and")
    lines.append("highlight any urgent items. Then offer to help with the top")
    lines.append("suggested action.")
    lines.append("")
    lines.append("If the user greets you or asks an open question, lead with the")
    lines.append("ASCII art logo and status update. If they have a specific request,")
    lines.append("help them first then mention any urgent status items afterward.")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    """Execute SessionStart hook for Agent Smith."""
    # Fetch current status
    status = get_status_data()

    # Format context
    context = format_status_context(status)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
