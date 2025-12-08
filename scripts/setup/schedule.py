#!/usr/bin/env python3
"""Set up automated categorization scheduling.

Supports:
- macOS: launchd (automatic)
- Linux with systemd: systemd timer (automatic)
- Linux/other: cron (shows crontab entry to add manually)

Usage:
    uv run python -u scripts/setup/schedule.py --status
    uv run python -u scripts/setup/schedule.py --frequency daily --time 06:00
    uv run python -u scripts/setup/schedule.py --remove
"""

import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

CRON_TEMPLATE = """# Agent Smith Auto-Categorization
# Runs {frequency} at {time}
# Added: {timestamp}
{schedule} cd {project_dir} && uv run python -u \\
    scripts/scheduled/auto_categorize.py --mode smart \\
    >> data/auto_categorize.log 2>&1
"""

LAUNCHD_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" \\
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.agentsmith.autocategorize</string>
    <key>ProgramArguments</key>
    <array>
        <string>{uv_path}</string>
        <string>run</string>
        <string>python</string>
        <string>-u</string>
        <string>scripts/scheduled/auto_categorize.py</string>
        <string>--mode</string>
        <string>smart</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{project_dir}</string>
    <key>StartCalendarInterval</key>
    {calendar_interval}
    <key>StandardOutPath</key>
    <string>{project_dir}/data/auto_categorize.log</string>
    <key>StandardErrorPath</key>
    <string>{project_dir}/data/auto_categorize.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
"""

SYSTEMD_SERVICE_TEMPLATE = """[Unit]
Description=Agent Smith Auto-Categorization
After=network.target

[Service]
Type=oneshot
WorkingDirectory={project_dir}
ExecStart={uv_path} run python -u scripts/scheduled/auto_categorize.py --mode smart
StandardOutput=append:{project_dir}/data/auto_categorize.log
StandardError=append:{project_dir}/data/auto_categorize.log
User={user}

[Install]
WantedBy=multi-user.target
"""

SYSTEMD_TIMER_TEMPLATE = """[Unit]
Description=Agent Smith Auto-Categorization Timer
Requires=agentsmith-autocategorize.service

[Timer]
{on_calendar}
Persistent=true

[Install]
WantedBy=timers.target
"""


def get_project_dir() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.absolute()


def get_uv_path() -> Optional[str]:
    """Get the path to uv executable."""
    return shutil.which("uv")


def get_schedule_config_path() -> Path:
    """Get path to schedule configuration file."""
    return get_project_dir() / "data" / "schedule_config.json"


def load_schedule_config() -> Dict[str, Any]:
    """Load current schedule configuration."""
    config_path = get_schedule_config_path()
    if config_path.exists():
        with open(config_path) as f:
            content: Dict[str, Any] = json.load(f)
            return content
    return {}


def save_schedule_config(config: dict) -> None:
    """Save schedule configuration."""
    config_path = get_schedule_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_cron_schedule(frequency: str, time: str) -> str:
    """Generate cron schedule expression."""
    hour, minute = time.split(":")
    if frequency == "hourly":
        return f"{minute} * * * *"
    elif frequency == "daily":
        return f"{minute} {hour} * * *"
    elif frequency == "weekly":
        return f"{minute} {hour} * * 0"  # Sunday
    else:
        raise ValueError(f"Unknown frequency: {frequency}")


def get_launchd_calendar_interval(frequency: str, time: str) -> str:
    """Generate launchd calendar interval XML."""
    hour, minute = map(int, time.split(":"))

    if frequency == "hourly":
        return f"""<dict>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>"""
    elif frequency == "daily":
        return f"""<dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>"""
    elif frequency == "weekly":
        return f"""<dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>"""
    else:
        raise ValueError(f"Unknown frequency: {frequency}")


def get_systemd_on_calendar(frequency: str, time: str) -> str:
    """Generate systemd OnCalendar expression."""
    if frequency == "hourly":
        minute = time.split(":")[1]
        return f"OnCalendar=*:00/{minute}"
    elif frequency == "daily":
        return f"OnCalendar=*-*-* {time}:00"
    elif frequency == "weekly":
        return f"OnCalendar=Sun {time}:00"
    else:
        raise ValueError(f"Unknown frequency: {frequency}")


def setup_launchd(frequency: str, time: str, project_dir: Path) -> bool:
    """Set up launchd for macOS."""
    uv_path = get_uv_path()
    if not uv_path:
        print("ERROR: Could not find 'uv' executable")
        return False

    plist_content = LAUNCHD_TEMPLATE.format(
        uv_path=uv_path,
        project_dir=project_dir,
        calendar_interval=get_launchd_calendar_interval(frequency, time),
    )

    plist_path = Path.home() / "Library/LaunchAgents/com.agentsmith.autocategorize.plist"
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    # Unload existing if present
    if plist_path.exists():
        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)

    print(f"Creating launchd plist: {plist_path}")
    plist_path.write_text(plist_content)

    print("Loading launchd job...")
    result = subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Warning: launchctl load returned: {result.stderr}")

    return True


def setup_systemd(frequency: str, time: str, project_dir: Path) -> bool:
    """Set up systemd timer for Linux."""
    uv_path = get_uv_path()
    if not uv_path:
        print("ERROR: Could not find 'uv' executable")
        return False

    import os

    user = os.environ.get("USER", "")

    # User systemd directory
    systemd_dir = Path.home() / ".config/systemd/user"
    systemd_dir.mkdir(parents=True, exist_ok=True)

    service_path = systemd_dir / "agentsmith-autocategorize.service"
    timer_path = systemd_dir / "agentsmith-autocategorize.timer"

    service_content = SYSTEMD_SERVICE_TEMPLATE.format(
        project_dir=project_dir,
        uv_path=uv_path,
        user=user,
    )

    timer_content = SYSTEMD_TIMER_TEMPLATE.format(
        on_calendar=get_systemd_on_calendar(frequency, time),
    )

    print(f"Creating systemd service: {service_path}")
    service_path.write_text(service_content)

    print(f"Creating systemd timer: {timer_path}")
    timer_path.write_text(timer_content)

    print("Enabling and starting timer...")
    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
    subprocess.run(
        ["systemctl", "--user", "enable", "agentsmith-autocategorize.timer"],
        capture_output=True,
    )
    subprocess.run(
        ["systemctl", "--user", "start", "agentsmith-autocategorize.timer"],
        capture_output=True,
    )

    return True


def setup_cron(frequency: str, time: str, project_dir: Path) -> bool:
    """Show cron entry for manual setup."""
    schedule = get_cron_schedule(frequency, time)
    cron_entry = CRON_TEMPLATE.format(
        frequency=frequency,
        time=time,
        timestamp=datetime.now().isoformat(),
        schedule=schedule,
        project_dir=project_dir,
    )

    print()
    print("=" * 60)
    print("MANUAL CRON SETUP REQUIRED")
    print("=" * 60)
    print()
    print("Add this to your crontab by running: crontab -e")
    print()
    print("-" * 60)
    print(cron_entry)
    print("-" * 60)
    print()

    return True


def remove_launchd() -> bool:
    """Remove launchd job."""
    plist_path = Path.home() / "Library/LaunchAgents/com.agentsmith.autocategorize.plist"
    if plist_path.exists():
        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
        plist_path.unlink()
        print(f"Removed: {plist_path}")
        return True
    else:
        print("No launchd job found")
        return False


def remove_systemd() -> bool:
    """Remove systemd timer."""
    systemd_dir = Path.home() / ".config/systemd/user"
    service_path = systemd_dir / "agentsmith-autocategorize.service"
    timer_path = systemd_dir / "agentsmith-autocategorize.timer"

    removed = False
    if timer_path.exists():
        subprocess.run(
            ["systemctl", "--user", "stop", "agentsmith-autocategorize.timer"],
            capture_output=True,
        )
        subprocess.run(
            ["systemctl", "--user", "disable", "agentsmith-autocategorize.timer"],
            capture_output=True,
        )
        timer_path.unlink()
        print(f"Removed: {timer_path}")
        removed = True

    if service_path.exists():
        service_path.unlink()
        print(f"Removed: {service_path}")
        removed = True

    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)

    if not removed:
        print("No systemd timer found")

    return removed


def show_status() -> None:
    """Show current schedule status."""
    config = load_schedule_config()
    system = platform.system()

    print()
    print("=" * 60)
    print("AGENT SMITH SCHEDULE STATUS")
    print("=" * 60)
    print()

    if not config:
        print("Status: NOT CONFIGURED")
        print()
        print("To set up scheduling, run:")
        print("  uv run python -u scripts/setup/schedule.py --frequency daily --time 06:00")
        print()
        return

    print("Status: CONFIGURED")
    print(f"  Frequency: {config.get('frequency', 'unknown')}")
    print(f"  Time: {config.get('time', 'unknown')}")
    print(f"  Method: {config.get('method', 'unknown')}")
    print(f"  Configured: {config.get('configured_at', 'unknown')}")
    print()

    # Check if actually running
    if system == "Darwin":
        plist_path = Path.home() / "Library/LaunchAgents/com.agentsmith.autocategorize.plist"
        if plist_path.exists():
            print("launchd: ACTIVE")
            result = subprocess.run(
                ["launchctl", "list", "com.agentsmith.autocategorize"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("  Job loaded in launchctl")
        else:
            print("launchd: NOT FOUND (plist missing)")
    elif system == "Linux":
        result = subprocess.run(
            ["systemctl", "--user", "is-active", "agentsmith-autocategorize.timer"],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip() == "active":
            print("systemd: ACTIVE")
        else:
            print("systemd: INACTIVE (timer not running)")

    # Show recent activity
    log_path = get_project_dir() / "data" / "auto_categorize.log"
    if log_path.exists():
        print()
        print("Recent activity:")
        with open(log_path) as f:
            lines = f.readlines()
            for line in lines[-3:]:  # Last 3 entries
                try:
                    entry = json.loads(line)
                    ts = entry.get("timestamp", "")[:19]
                    results = entry.get("results", {})
                    print(
                        f"  [{ts}] Applied: {results.get('auto_applied', 0)}, "
                        f"Flagged: {results.get('flagged_for_review', 0)}"
                    )
                except json.JSONDecodeError:
                    pass
    print()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current schedule status",
    )
    parser.add_argument(
        "--frequency",
        choices=["hourly", "daily", "weekly"],
        default="daily",
        help="How often to run (default: daily)",
    )
    parser.add_argument(
        "--time",
        default="06:00",
        help="Time to run in HH:MM format (default: 06:00)",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove scheduled job",
    )
    args = parser.parse_args()

    project_dir = get_project_dir()
    system = platform.system()

    if args.status:
        show_status()
        return 0

    if args.remove:
        print("Removing scheduled job...")
        config = load_schedule_config()

        if system == "Darwin":
            remove_launchd()
        elif system == "Linux":
            remove_systemd()
        else:
            print("For cron: run 'crontab -e' and remove the Agent Smith entry")

        # Clear config
        if get_schedule_config_path().exists():
            get_schedule_config_path().unlink()
            print("Removed schedule configuration")

        print()
        print("Scheduling removed.")
        return 0

    # Setup scheduling
    print()
    print("Setting up auto-categorization schedule...")
    print(f"  System: {system}")
    print(f"  Frequency: {args.frequency}")
    print(f"  Time: {args.time}")
    print(f"  Project: {project_dir}")
    print()

    success = False
    method = "unknown"

    if system == "Darwin":
        method = "launchd"
        success = setup_launchd(args.frequency, args.time, project_dir)
    elif system == "Linux":
        # Check if systemd is available
        if shutil.which("systemctl"):
            method = "systemd"
            success = setup_systemd(args.frequency, args.time, project_dir)
        else:
            method = "cron"
            success = setup_cron(args.frequency, args.time, project_dir)
    else:
        method = "cron"
        success = setup_cron(args.frequency, args.time, project_dir)

    if success:
        # Save configuration
        config = {
            "frequency": args.frequency,
            "time": args.time,
            "method": method,
            "configured_at": datetime.now().isoformat(),
            "project_dir": str(project_dir),
        }
        save_schedule_config(config)

        print()
        print("=" * 60)
        print("SCHEDULING CONFIGURED")
        print("=" * 60)
        print(f"  Frequency: {args.frequency}")
        print(f"  Time: {args.time}")
        print(f"  Method: {method}")
        print()
        print("Commands:")
        print("  Check status: uv run python -u scripts/setup/schedule.py --status")
        print("  Remove: uv run python -u scripts/setup/schedule.py --remove")
        print("  View logs: cat data/auto_categorize.log")
        print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
