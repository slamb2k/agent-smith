#!/usr/bin/env python3
"""Generate Agent Smith status dashboard data.

Provides current status information including:
- Health score (cached)
- Uncategorized transaction count
- Conflict count (transactions flagged for review)
- Tax deadline alerts
- Prioritized suggestions for next actions
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Import lazily to allow testing with mocks
PocketSmithClient = None


def _get_client() -> Any:
    """Get PocketSmith client, importing lazily."""
    global PocketSmithClient
    if PocketSmithClient is None:
        from scripts.core.api_client import PocketSmithClient as PSClient

        PocketSmithClient = PSClient
    return PocketSmithClient()


def get_status_summary() -> Dict[str, Any]:
    """Gather current status from PocketSmith and local state.

    Returns:
        Dictionary with health_score, uncategorized_count, conflict_count,
        tax_alerts, suggestions, and last_activity.
    """
    client = _get_client()
    user = client.get_user()

    # Get recent transactions (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    transactions = client.get_transactions(
        user_id=user["id"],
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    )

    # Count uncategorized
    uncategorized = [t for t in transactions if not t.get("category")]

    # Count conflicts (transactions with Review labels)
    conflicts = [
        t
        for t in transactions
        if any("Review" in (label or "") for label in (t.get("labels") or []))
    ]

    # Get health score (cached if available)
    health_score = _get_cached_health_score()

    # Check for tax deadlines
    tax_alerts = _check_tax_deadlines()

    # Get last activity
    last_activity = _get_last_activity()

    return {
        "health_score": health_score,
        "uncategorized_count": len(uncategorized),
        "uncategorized_days": 7,
        "conflict_count": len(conflicts),
        "tax_alerts": tax_alerts,
        "last_activity": last_activity,
        "suggestions": _generate_suggestions(
            uncategorized_count=len(uncategorized),
            conflict_count=len(conflicts),
            health_score=health_score,
            tax_alerts=tax_alerts,
        ),
    }


def _get_cached_health_score() -> Dict[str, Any]:
    """Get cached health score or return unknown.

    Reads from data/health_cache.json if available.
    """
    cache_path = Path(__file__).parent.parent.parent / "data" / "health_cache.json"

    if cache_path.exists():
        try:
            with open(cache_path) as f:
                cache = json.load(f)
                # Check if cache is recent (less than 24 hours old)
                cached_time = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
                if datetime.now() - cached_time < timedelta(hours=24):
                    return {
                        "score": cache.get("score"),
                        "status": cache.get("status", "unknown"),
                    }
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

    return {"score": None, "status": "unknown"}


def _check_tax_deadlines() -> List[Dict[str, Any]]:
    """Check for upcoming tax deadlines.

    Returns list of alerts for EOFY and other tax-related deadlines.
    """
    alerts = []
    today = datetime.now()

    # Calculate days to EOFY (June 30)
    current_year = today.year
    if today.month <= 6:
        eofy = datetime(current_year, 6, 30)
    else:
        eofy = datetime(current_year + 1, 6, 30)

    days_to_eofy = (eofy - today).days

    if days_to_eofy <= 180:
        priority = "high" if days_to_eofy <= 60 else "medium"
        alerts.append(
            {
                "type": "eofy",
                "message": f"EOFY in {days_to_eofy} days - start tax planning",
                "priority": priority,
            }
        )

    return alerts


def _get_last_activity() -> Dict[str, Any]:
    """Get last Agent Smith activity.

    Reads from data/activity_log.json if available.
    """
    log_path = Path(__file__).parent.parent.parent / "data" / "activity_log.json"

    if log_path.exists():
        try:
            with open(log_path) as f:
                logs = [json.loads(line) for line in f if line.strip()]
                if logs:
                    last = logs[-1]
                    return {
                        "action": last.get("action"),
                        "date": last.get("timestamp"),
                    }
        except (json.JSONDecodeError, KeyError):
            pass

    return {"action": None, "date": None}


def _generate_suggestions(
    uncategorized_count: int,
    conflict_count: int,
    health_score: Dict[str, Any],
    tax_alerts: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Generate prioritized suggestions based on current state.

    Args:
        uncategorized_count: Number of uncategorized transactions
        conflict_count: Number of transactions flagged for review
        health_score: Health score dictionary with 'score' and 'status'
        tax_alerts: List of tax deadline alerts

    Returns:
        List of up to 3 prioritized suggestions
    """
    suggestions = []

    # Priority 1: Uncategorized transactions
    if uncategorized_count > 0:
        suggestions.append(
            {
                "priority": 1,
                "title": f"Categorize {uncategorized_count} new transactions",
                "natural": "categorize my transactions",
                "command": "/smith:categorize",
            }
        )

    # Priority 2: Conflicts to review
    if conflict_count > 0:
        suggestions.append(
            {
                "priority": 2,
                "title": f"Review {conflict_count} flagged conflicts",
                "natural": "review conflicts",
                "command": "/smith:review-conflicts",
            }
        )

    # Priority 3: Health check not run
    if health_score.get("score") is None:
        suggestions.append(
            {
                "priority": 3,
                "title": "Run health check to see your financial score",
                "natural": "check my financial health",
                "command": "/smith:health",
            }
        )

    # Priority 4: Tax alerts
    for alert in tax_alerts:
        suggestions.append(
            {
                "priority": 4,
                "title": alert["message"],
                "natural": "show my tax deductions",
                "command": "/smith:tax deductions",
            }
        )

    # Sort by priority and limit to 3
    suggestions.sort(key=lambda x: int(x["priority"]))  # type: ignore[call-overload]
    return suggestions[:3]


def _print_formatted(status: Dict[str, Any]) -> None:
    """Print formatted dashboard.

    Args:
        status: Status dictionary from get_status_summary()
    """
    # Header
    print("=" * 63)
    print("                    🤖 AGENT SMITH")
    print("              Your Financial Intelligence Assistant")
    print("=" * 63)
    print()

    # Current Status
    print("📊 CURRENT STATUS")
    print("─" * 63)

    # Health Score
    hs = status.get("health_score", {})
    if hs.get("score") is not None:
        score = hs["score"]
        if score >= 90:
            emoji = "🟢"
        elif score >= 70:
            emoji = "🟢"
        elif score >= 50:
            emoji = "🟡"
        else:
            emoji = "🔴"
        print(f"  Health Score: {emoji} {score}/100 ({hs.get('status', 'Unknown')})")
    else:
        print("  Health Score: ⚪ Not yet checked")

    # Uncategorized count
    uc = status.get("uncategorized_count", 0)
    if uc > 0:
        print(
            f"  Uncategorized: {uc} transactions (last {status.get('uncategorized_days', 7)} days)"
        )
    else:
        print("  Uncategorized: ✅ All caught up!")

    # Last activity
    la = status.get("last_activity", {})
    if la.get("action"):
        print(f"  Last Activity: {la['action']} ({la.get('date', 'recently')})")

    print()

    # Suggestions
    suggestions = status.get("suggestions", [])
    if suggestions:
        print("🎯 SUGGESTED NEXT STEPS")
        print("─" * 63)
        for i, s in enumerate(suggestions, 1):
            print(f"  {i}. {s['title']}")
            print(f"     → Say \"{s['natural']}\" or {s['command']}")
            print()

    # Help section
    print("💡 WHAT CAN I HELP WITH?")
    print("─" * 63)
    print('  • "Categorize my transactions"')
    print('  • "Show my spending this month"')
    print('  • "How\'s my financial health?"')
    print('  • "What are my tax deductions?"')
    print('  • "Show me insights"')
    print()
    print("  Power users: Type /smith: to see all commands")
    print("=" * 63)


def main() -> int:
    """Main entry point for the dashboard script.

    Returns:
        Exit code (0 for success)
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
        _print_formatted(status)

    return 0


if __name__ == "__main__":
    sys.exit(main())
