#!/usr/bin/env python3
"""
Agent Smith SessionStart hook.

Displays welcome message and adds critical project context about Python environment.
"""

import json
import sys


def main():
    """Execute SessionStart hook for Agent Smith."""
    # Read hook input from stdin (available but not needed for this hook)
    # hook_input = json.loads(sys.stdin.read())

    # Output user-visible message to stderr (shown in verbose mode with ctrl+o)
    # Note: For SessionStart, we want the message visible, so we'll include it
    # in the stdout which gets added to context
    user_message = "✅ Agent Smith active... Use /smith:install to get started."

    # Prepare additional context that will be injected into Claude's context
    # This is added discretely and helps Claude understand project requirements
    additional_context = f"""{user_message}

IMPORTANT: Agent Smith Python Environment Setup

This project uses uv for dependency management. All Python dependencies
(requests, python-dateutil, python-dotenv, etc.) are installed in the .venv
virtual environment.

**CRITICAL**: Always use 'uv run python' when executing Python scripts:
  ✅ CORRECT:   uv run python -u scripts/some_script.py
  ❌ INCORRECT: python scripts/some_script.py  (will fail with ModuleNotFoundError)

The -u flag enables unbuffered output for real-time progress visibility.
"""

    # Prepare hook output as JSON
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context,
        }
    }

    # Output JSON to stdout (will be processed by Claude Code)
    print(json.dumps(output, indent=2))

    # Exit with code 0 to indicate success
    sys.exit(0)


if __name__ == "__main__":
    main()
