#!/usr/bin/env python3
"""Automated categorization for scheduled execution.

Designed to run via cron/systemd/launchd without Claude Code.
Calls categorize_batch.py and logs results for SessionStart dashboard.

Usage:
    uv run python -u scripts/scheduled/auto_categorize.py
    uv run python -u scripts/scheduled/auto_categorize.py --mode smart --period last-30-days
    uv run python -u scripts/scheduled/auto_categorize.py --dry-run
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_categorization_output(output: str) -> dict:
    """Parse output from categorize_batch.py to extract stats.

    Args:
        output: Raw stdout from categorize_batch.py

    Returns:
        Dict with parsed statistics
    """
    stats = {
        "total": 0,
        "processed": 0,
        "auto_applied": 0,
        "flagged": 0,
        "errors": 0,
    }

    # Parse "Total transactions: N"
    match = re.search(r"Total transactions:\s*(\d+)", output)
    if match:
        stats["total"] = int(match.group(1))

    # Parse "Rule matches: N"
    match = re.search(r"Rule matches:\s*(\d+)", output)
    if match:
        stats["processed"] += int(match.group(1))

    # Parse "LLM categorized: N"
    match = re.search(r"LLM categorized:\s*(\d+)", output)
    if match:
        stats["processed"] += int(match.group(1))

    # Parse "Applied N categorizations"
    match = re.search(r"Applied\s+(\d+)\s+categorizations", output)
    if match:
        stats["auto_applied"] = int(match.group(1))

    # Parse "Conflicts (needs review): N"
    match = re.search(r"Conflicts.*?:\s*(\d+)", output)
    if match:
        stats["flagged"] = int(match.group(1))

    # Parse "Failed: N"
    match = re.search(r"Failed:\s*(\d+)", output)
    if match:
        stats["errors"] = int(match.group(1))

    return stats


def main() -> int:
    """Main entry point for scheduled auto-categorization."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["conservative", "smart", "aggressive"],
        default="smart",
        help="Intelligence mode (default: smart)",
    )
    parser.add_argument(
        "--period",
        default="last-30-days",
        help="Period to process (YYYY-MM or 'last-30-days')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying",
    )
    parser.add_argument(
        "--log-file",
        default="data/auto_categorize.log",
        help="Path to activity log file",
    )
    args = parser.parse_args()

    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] Starting auto-categorization...")
    print(f"  Mode: {args.mode}")
    print(f"  Period: {args.period}")
    print(f"  Dry-run: {args.dry_run}")
    print()

    # Build command to call categorize_batch.py
    project_dir = Path(__file__).parent.parent.parent
    cmd = [
        "uv",
        "run",
        "python",
        "-u",
        str(project_dir / "scripts" / "operations" / "categorize_batch.py"),
        f"--mode={args.mode}",
        f"--period={args.period}",
    ]
    if args.dry_run:
        cmd.append("--dry-run")

    # Run categorization
    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minute timeout
        )
        output = result.stdout + result.stderr
        print(output)
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        print("ERROR: Categorization timed out after 30 minutes")
        output = "Timeout"
        exit_code = 1
    except Exception as e:
        print(f"ERROR: {e}")
        output = str(e)
        exit_code = 1

    # Parse results
    stats = parse_categorization_output(output)

    # Create log entry
    log_entry = {
        "timestamp": timestamp,
        "mode": args.mode,
        "period": args.period,
        "dry_run": args.dry_run,
        "exit_code": exit_code,
        "results": {
            "total": stats["total"],
            "processed": stats["processed"],
            "auto_applied": stats["auto_applied"],
            "flagged_for_review": stats["flagged"],
            "errors": stats["errors"],
        },
    }

    # Append to activity log
    log_path = project_dir / args.log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Summary
    print()
    print("=" * 60)
    print("AUTO-CATEGORIZATION COMPLETE")
    print("=" * 60)
    print(f"  Total transactions: {stats['total']}")
    print(f"  Auto-applied: {stats['auto_applied']}")
    print(f"  Flagged for review: {stats['flagged']}")
    if stats["errors"] > 0:
        print(f"  Errors: {stats['errors']}")
    print(f"  Log: {log_path}")
    print("=" * 60)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
