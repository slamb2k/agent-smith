#!/usr/bin/env python3
"""Generate Agent Smith welcome screen using local data only.

Provides session-start status information without any API calls:
- API key configuration status
- Onboarding progress
- Rules count
- Cached health score
- Last activity
- Active templates

This script is designed for fast execution (<100ms) at session start.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


# ASCII Art Logo
LOGO = r"""
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

                   WELCOME TO AGENT SMITH

                 Good Morning Mr. Anderson...
"""

# Onboarding stage names for display
ONBOARDING_STAGES = {
    1: "Welcome & Prerequisites",
    2: "Discovery",
    3: "Template Selection",
    4: "Template Application",
    5: "Intelligence Mode",
    6: "Categorization",
    7: "Health Check",
    8: "Next Steps",
}


def get_data_dir() -> Path:
    """Get the data directory path.

    Checks USER_CWD for plugin mode, falls back to script's project root.
    """
    user_cwd = os.environ.get("USER_CWD")
    if user_cwd:
        return Path(user_cwd) / "data"

    # Development mode - relative to script location
    return Path(__file__).parent.parent.parent / "data"


def get_env_path() -> Path:
    """Get the .env file path.

    Checks USER_CWD for plugin mode, falls back to script's project root.
    """
    user_cwd = os.environ.get("USER_CWD")
    if user_cwd:
        return Path(user_cwd) / ".env"

    # Development mode - relative to script location
    return Path(__file__).parent.parent.parent / ".env"


def check_api_key() -> Dict[str, Any]:
    """Check if PocketSmith API key is configured.

    Returns:
        Dictionary with 'present' and 'valid_format' boolean flags.
    """
    env_path = get_env_path()

    if not env_path.exists():
        return {"present": False, "valid_format": False}

    try:
        content = env_path.read_text()
        # Look for POCKETSMITH_API_KEY=<value> (handle quoted or unquoted values)
        match = re.search(r"POCKETSMITH_API_KEY=(.+?)(?:\n|$)", content)

        if not match:
            return {"present": False, "valid_format": False}

        api_key = match.group(1).strip().strip('"').strip("'")

        # Check if it's a placeholder or empty
        placeholder_patterns = [
            "<Your Developer API Key>",
            "your_key_here",
            "<your-api-key>",
            "",
        ]
        if api_key in placeholder_patterns or api_key.startswith("<"):
            return {"present": False, "valid_format": False}

        # Basic format validation: should be 128-char hex string
        valid_format = bool(re.match(r"^[a-fA-F0-9]{128}$", api_key))

        return {"present": True, "valid_format": valid_format}

    except Exception:
        return {"present": False, "valid_format": False}


def check_onboarding() -> Dict[str, Any]:
    """Check onboarding state.

    Returns:
        Dictionary with 'status', 'current_stage', and 'stage_name'.
    """
    data_dir = get_data_dir()
    state_file = data_dir / "onboarding_state.json"

    if not data_dir.exists():
        return {"status": "not_started", "current_stage": None, "stage_name": None}

    if not state_file.exists():
        return {"status": "not_started", "current_stage": None, "stage_name": None}

    try:
        with open(state_file) as f:
            state = json.load(f)

        if state.get("onboarding_completed"):
            return {"status": "complete", "current_stage": None, "stage_name": None}

        # In progress - find current stage
        current_stage = state.get("current_stage", 1)
        stage_name = ONBOARDING_STAGES.get(current_stage, f"Stage {current_stage}")

        return {
            "status": "in_progress",
            "current_stage": current_stage,
            "stage_name": stage_name,
        }

    except (json.JSONDecodeError, KeyError):
        return {"status": "not_started", "current_stage": None, "stage_name": None}


def check_rules() -> Dict[str, Any]:
    """Check categorization rules count.

    Returns:
        Dictionary with 'count' and 'file_exists'.
    """
    data_dir = get_data_dir()
    rules_file = data_dir / "rules.yaml"

    if not rules_file.exists():
        return {"count": 0, "file_exists": False}

    try:
        # Import yaml only if needed
        import yaml

        with open(rules_file) as f:
            rules_data = yaml.safe_load(f)

        if not rules_data:
            return {"count": 0, "file_exists": True}

        # Count rules - could be a list or dict with 'rules' key
        if isinstance(rules_data, list):
            count = len(rules_data)
        elif isinstance(rules_data, dict):
            rules_list = rules_data.get("rules", [])
            count = len(rules_list) if isinstance(rules_list, list) else 0
        else:
            count = 0

        return {"count": count, "file_exists": True}

    except Exception:
        return {"count": 0, "file_exists": True}


def check_health_cache() -> Dict[str, Any]:
    """Check cached health score.

    Returns:
        Dictionary with 'score', 'status', and 'days_ago'.
    """
    data_dir = get_data_dir()
    cache_file = data_dir / "health_cache.json"

    if not cache_file.exists():
        return {"score": None, "status": "unknown", "days_ago": None}

    try:
        with open(cache_file) as f:
            cache = json.load(f)

        score = cache.get("score")
        status = cache.get("status", "unknown")
        timestamp_str = cache.get("timestamp")

        days_ago = None
        if timestamp_str:
            try:
                cached_time = datetime.fromisoformat(timestamp_str)
                days_ago = (datetime.now() - cached_time).days
            except ValueError:
                pass

        return {"score": score, "status": status, "days_ago": days_ago}

    except (json.JSONDecodeError, KeyError):
        return {"score": None, "status": "unknown", "days_ago": None}


def check_last_activity() -> Dict[str, Any]:
    """Check last Agent Smith activity.

    Returns:
        Dictionary with 'action', 'date', and 'days_ago'.
    """
    data_dir = get_data_dir()
    log_file = data_dir / "activity_log.json"

    if not log_file.exists():
        return {"action": None, "date": None, "days_ago": None}

    try:
        # Read last line (JSONL format)
        with open(log_file) as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            return {"action": None, "date": None, "days_ago": None}

        last_entry = json.loads(lines[-1])
        action = last_entry.get("action")
        timestamp_str = last_entry.get("timestamp")

        date_display = None
        days_ago = None

        if timestamp_str:
            try:
                activity_time = datetime.fromisoformat(timestamp_str)
                date_display = activity_time.strftime("%b %d")
                days_ago = (datetime.now() - activity_time).days
            except ValueError:
                date_display = timestamp_str

        return {"action": action, "date": date_display, "days_ago": days_ago}

    except (json.JSONDecodeError, KeyError):
        return {"action": None, "date": None, "days_ago": None}


def check_templates() -> Dict[str, Any]:
    """Check active template configuration.

    Returns:
        Dictionary with 'primary', 'living', and 'additional' templates.
    """
    data_dir = get_data_dir()

    # Try template_config.json first
    config_file = data_dir / "template_config.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)

            return {
                "primary": config.get("primary_template"),
                "living": config.get("living_templates", []),
                "additional": config.get("additional_templates", []),
            }
        except (json.JSONDecodeError, KeyError):
            pass

    # Fall back to onboarding_state.json
    state_file = data_dir / "onboarding_state.json"
    if state_file.exists():
        try:
            with open(state_file) as f:
                state = json.load(f)

            templates = state.get("templates", {})
            return {
                "primary": templates.get("primary"),
                "living": templates.get("living", []),
                "additional": templates.get("additional", []),
            }
        except (json.JSONDecodeError, KeyError):
            pass

    return {"primary": None, "living": [], "additional": []}


def get_recommended_actions(
    api_key: Dict[str, Any],
    onboarding: Dict[str, Any],
    rules: Dict[str, Any],
    health: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Get recommended actions based on current state.

    Uses a simple priority waterfall - first matching condition wins.

    Returns:
        List of up to 2 recommended actions.
    """
    actions = []

    # Priority 1: API key missing
    if not api_key["present"]:
        actions.append(
            {
                "priority": 1,
                "message": "Add your PocketSmith API key to .env",
                "command": "See: https://app.pocketsmith.com/keys/new",
            }
        )

    # Priority 2: API key invalid format
    elif not api_key["valid_format"]:
        actions.append(
            {
                "priority": 2,
                "message": "Check your API key format in .env",
                "command": "Key should be 128 hex characters",
            }
        )

    # Priority 3: Onboarding not started
    if onboarding["status"] == "not_started":
        actions.append(
            {
                "priority": 3,
                "message": "Set up Agent Smith",
                "command": "/smith:install",
            }
        )

    # Priority 4: Onboarding in progress
    elif onboarding["status"] == "in_progress":
        stage = onboarding["current_stage"]
        stage_name = onboarding["stage_name"]
        actions.append(
            {
                "priority": 4,
                "message": f"Continue setup (Stage {stage}: {stage_name})",
                "command": "/smith:install",
            }
        )

    # Priority 5: No rules configured
    if onboarding["status"] == "complete" and rules["count"] == 0:
        actions.append(
            {
                "priority": 5,
                "message": "Create categorization rules",
                "command": "/smith:install",
            }
        )

    # Priority 6: Health check never run
    if onboarding["status"] == "complete" and health["score"] is None:
        actions.append(
            {
                "priority": 6,
                "message": "Run health check to assess your data",
                "command": "/smith:health",
            }
        )

    # Priority 7: Health check stale (>7 days)
    elif (
        onboarding["status"] == "complete"
        and health["days_ago"] is not None
        and health["days_ago"] > 7
    ):
        actions.append(
            {
                "priority": 7,
                "message": f"Run health check (last: {health['days_ago']} days ago)",
                "command": "/smith:health",
            }
        )

    # Priority 8: Health score < 50
    if onboarding["status"] == "complete" and health["score"] is not None and health["score"] < 50:
        actions.append(
            {
                "priority": 8,
                "message": "Categorize transactions to improve health score",
                "command": "/smith:categorize",
            }
        )

    # Priority 9: Default actions (all good)
    if onboarding["status"] == "complete" and len(actions) == 0:
        actions.append(
            {
                "priority": 9,
                "message": "Process new transactions",
                "command": "/smith:categorize",
            }
        )
        actions.append(
            {
                "priority": 9,
                "message": "View spending analysis",
                "command": "/smith:insights",
            }
        )

    # Sort by priority and return top 2
    actions.sort(key=lambda x: int(x["priority"]))  # type: ignore[call-overload]
    return actions[:2]


def get_status_summary() -> Dict[str, Any]:
    """Gather all status information.

    Returns:
        Complete status dictionary for JSON output or formatting.
    """
    api_key = check_api_key()
    onboarding = check_onboarding()
    rules = check_rules()
    health = check_health_cache()
    activity = check_last_activity()
    templates = check_templates()

    recommendations = get_recommended_actions(api_key, onboarding, rules, health)

    return {
        "api_key": api_key,
        "onboarding": onboarding,
        "rules": rules,
        "health": health,
        "activity": activity,
        "templates": templates,
        "recommendations": recommendations,
    }


def format_status_line(label: str, value: str, indicator: str = "") -> str:
    """Format a single status line.

    Args:
        label: The label (e.g., "Config")
        value: The value to display
        indicator: Optional status indicator

    Returns:
        Formatted line string.
    """
    if indicator:
        return f" {label:<12}{indicator} {value}"
    return f" {label:<12}{value}"


def format_output(status: Dict[str, Any]) -> str:
    """Format status as human-readable output.

    Args:
        status: Status dictionary from get_status_summary()

    Returns:
        Formatted string for display.
    """
    lines = [LOGO]

    # Status section
    lines.append("=" * 62)
    lines.append(" STATUS")
    lines.append("=" * 62)

    # API Key
    api_key = status["api_key"]
    if api_key["present"] and api_key["valid_format"]:
        lines.append(format_status_line("Config", "API Key configured", "\u2713"))
    elif api_key["present"]:
        lines.append(format_status_line("Config", "API Key format invalid", "\u2717"))
    else:
        lines.append(format_status_line("Config", "API Key not configured", "\u2717"))

    # Onboarding
    onboarding = status["onboarding"]
    templates = status["templates"]

    if onboarding["status"] == "complete":
        # Build template summary
        template_parts = []
        if templates["primary"]:
            template_parts.append(templates["primary"].replace("-", " ").title())
        if templates["living"]:
            for t in templates["living"]:
                template_parts.append(t.replace("-", " ").title())

        template_str = " + ".join(template_parts) if template_parts else "Complete"
        lines.append(format_status_line("Setup", template_str, "\u2713"))

    elif onboarding["status"] == "in_progress":
        stage_info = f"Stage {onboarding['current_stage']}: {onboarding['stage_name']}"
        lines.append(format_status_line("Setup", stage_info, "\u26a0"))

    else:
        lines.append(format_status_line("Setup", "Not started", "\u25cb"))

    # Rules
    rules = status["rules"]
    if rules["count"] > 0:
        lines.append(
            format_status_line("Rules", f"{rules['count']} categorization rules active", "")
        )
    else:
        lines.append(format_status_line("Rules", "No rules configured", ""))

    # Health
    health = status["health"]
    if health["score"] is not None:
        days_str = f" ({health['days_ago']} days ago)" if health["days_ago"] else ""
        lines.append(format_status_line("Health", f"Score: {health['score']}/100{days_str}", ""))
    else:
        lines.append(format_status_line("Health", "Not yet checked", ""))

    # Activity
    activity = status["activity"]
    if activity["action"]:
        date_str = f" ({activity['date']})" if activity["date"] else ""
        lines.append(format_status_line("Activity", f"{activity['action']}{date_str}", ""))

    # Next Steps section
    lines.append("")
    lines.append("=" * 62)
    lines.append(" NEXT STEPS")
    lines.append("=" * 62)

    recommendations = status["recommendations"]
    for rec in recommendations:
        lines.append(f" \u2192 {rec['command']:<20} {rec['message']}")

    lines.append("")
    lines.append("=" * 62)

    return "\n".join(lines)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        choices=["json", "formatted"],
        default="json",
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    status = get_status_summary()

    if args.output == "json":
        print(json.dumps(status, indent=2, default=str))
    else:
        print(format_output(status))

    return 0


if __name__ == "__main__":
    sys.exit(main())
