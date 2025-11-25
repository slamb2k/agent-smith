#!/usr/bin/env python3
"""PocketSmith Health Check CLI.

Command-line interface for running comprehensive health checks on PocketSmith setups.
Part of the Agent Smith health check system.

Usage:
    uv run python -u scripts/health/check.py [--full|--quick] [--category=AREA]

Examples:
    # Quick health check (essential checks only)
    uv run python -u scripts/health/check.py --quick

    # Full comprehensive analysis
    uv run python -u scripts/health/check.py --full

    # Focus on specific area
    uv run python -u scripts/health/check.py --category=categories
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
# Search up the directory tree for .env (works from any location)
current_path = Path(__file__).resolve()
for parent in [current_path.parent] + list(current_path.parents):
    env_file = parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

# noqa: E402 - imports after dotenv load and path setup
from scripts.core.api_client import PocketSmithClient  # noqa: E402
from scripts.health.collector import HealthDataCollector  # noqa: E402
from scripts.health.engine import HealthCheckEngine  # noqa: E402
from scripts.health.recommendations import RecommendationEngine  # noqa: E402
from scripts.health import HealthStatus  # noqa: E402

if TYPE_CHECKING:
    from scripts.health.engine import HealthCheckResult


def format_score_bar(score: int, width: int = 30) -> str:
    """Create a visual score bar."""
    filled = int((score / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar


def format_status(status: HealthStatus) -> str:
    """Format status with emoji."""
    emoji_map = {
        HealthStatus.EXCELLENT: "✅",
        HealthStatus.GOOD: "👍",
        HealthStatus.FAIR: "⚠️",
        HealthStatus.POOR: "❌",
    }
    color_map = {
        HealthStatus.EXCELLENT: "32",  # Green
        HealthStatus.GOOD: "32",  # Green
        HealthStatus.FAIR: "33",  # Yellow
        HealthStatus.POOR: "31",  # Red
    }
    emoji = emoji_map.get(status, "?")
    color = color_map.get(status, "0")
    return f"\033[{color}m{emoji} {status.value.upper()}\033[0m"


def print_header(text: str) -> None:
    """Print section header."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_health_check_results(
    result: "HealthCheckResult",
    recommendations: Optional[List[Any]] = None,
    quick_mode: bool = False,
) -> None:
    """Print comprehensive health check results."""

    # Overall score
    print_header("POCKETSMITH HEALTH CHECK")
    print(f"Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"Overall Health Score: {result.overall_score}/100")
    print(f"{format_score_bar(result.overall_score)}")
    print(f"Status: {format_status(result.overall_status)}\n")

    # Individual dimension scores
    if not quick_mode:
        print_header("DIMENSION SCORES")

        for score in result.scores:
            print(f"\n{score.dimension.replace('_', ' ').title()}")
            print(f"  Score: {score.score}/100  {format_status(score.status)}")
            print(f"  {format_score_bar(score.score)}")

            if score.details:
                print("\n  Key Metrics:")
                for key, value in score.details.items():
                    key_formatted = key.replace("_", " ").title()
                    if isinstance(value, float) and value < 1:
                        print(f"    • {key_formatted}: {value:.1%}")
                    else:
                        print(f"    • {key_formatted}: {value}")

            if score.recommendations:
                print("\n  Recommendations:")
                for rec in score.recommendations[:3]:  # Top 3
                    print(f"    → {rec}")

    # Top recommendations
    if result.top_recommendations:
        print_header("TOP 5 PRIORITY RECOMMENDATIONS")
        for i, rec in enumerate(result.top_recommendations, 1):
            print(f"{i}. {rec}")

    # Detailed recommendations from RecommendationEngine
    if recommendations and not quick_mode:
        print_header("DETAILED ACTION PLAN")

        # Group by priority
        high_priority = [r for r in recommendations if r.priority == "high"]
        medium_priority = [r for r in recommendations if r.priority == "medium"]
        low_priority = [r for r in recommendations if r.priority == "low"]

        if high_priority:
            print("\n🔴 HIGH PRIORITY (Do First):\n")
            for rec in high_priority:
                print(f"  • {rec.title}")
                print(f"    Impact: {rec.impact_estimate}")
                print(f"    Effort: {rec.effort_estimate}")
                if rec.command:
                    print(f"    Command: {rec.command}")
                print()

        if medium_priority:
            print("\n🟡 MEDIUM PRIORITY:\n")
            for rec in medium_priority:
                print(f"  • {rec.title}")
                print(f"    Impact: {rec.impact_estimate}  |  Effort: {rec.effort_estimate}")
                print()

        if low_priority:
            print("\n🟢 LOW PRIORITY (Nice to Have):\n")
            for rec in low_priority:
                print(f"  • {rec.title}")
                print()


def run_quick_check(client: PocketSmithClient, user_id: int, data_dir: Path) -> None:
    """Run quick essential checks only."""
    print("Running quick health check (essential checks only)...\n")

    collector = HealthDataCollector(client, user_id, data_dir)
    engine = HealthCheckEngine()

    # Quick check - just the most important dimensions
    quick_dimensions = ["data_quality", "category_structure", "rule_engine"]

    print("Collecting data...")
    all_data = collector.collect_all()

    # Filter to quick dimensions
    quick_data = {dim: all_data[dim] for dim in quick_dimensions if dim in all_data}

    print("Running health checks...\n")

    # Run individual checks and display
    scores = []
    for dimension, data in quick_data.items():
        score = engine.run_single(dimension, data)
        scores.append(score)
        dim_title = dimension.replace("_", " ").title()
        status_str = format_status(score.status)
        print(f"{dim_title}: {score.score}/100  {status_str}")

    # Calculate quick overall score
    avg_score = sum(s.score for s in scores) // len(scores) if scores else 0
    overall_status = HealthStatus.from_score(avg_score)

    print(f"\nQuick Health Score: {avg_score}/100  {format_status(overall_status)}")

    # Show most urgent recommendations
    print("\nMost Urgent Actions:")
    for score in scores:
        if score.recommendations:
            print(f"\n{score.dimension.replace('_', ' ').title()}:")
            for rec in score.recommendations[:2]:
                print(f"  → {rec}")


def run_full_check(client: PocketSmithClient, user_id: int, data_dir: Path) -> None:
    """Run complete comprehensive health check."""
    print("Running full health check (comprehensive analysis)...\n")

    collector = HealthDataCollector(client, user_id, data_dir)
    engine = HealthCheckEngine()
    rec_engine = RecommendationEngine()

    print("Collecting data from PocketSmith...")
    data = collector.collect_all()

    print("Running health checks across all dimensions...\n")
    result = engine.run_all(data)

    print("Generating recommendations...\n")
    recommendations = rec_engine.generate(result.scores)

    # Print comprehensive results
    print_health_check_results(result, recommendations, quick_mode=False)

    # Save results
    output_dir = data_dir / "health"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(result.to_dict(), f, indent=2)

    print(f"\n\nResults saved to: {output_file}")


def run_category_check(
    client: PocketSmithClient, user_id: int, data_dir: Path, category: str
) -> None:
    """Run health check for specific category."""
    print(f"Running health check for: {category}\n")

    collector = HealthDataCollector(client, user_id, data_dir)
    engine = HealthCheckEngine()

    # Map friendly names to dimension names
    category_map = {
        "categories": "category_structure",
        "rules": "rule_engine",
        "tax": "tax_readiness",
        "data": "data_quality",
        "automation": "automation",
        "budget": "budget_alignment",
    }

    dimension = category_map.get(category.lower())
    if not dimension:
        print(f"Unknown category: {category}")
        print(f"Available categories: {', '.join(category_map.keys())}")
        return

    print(f"Collecting {dimension.replace('_', ' ')} data...")

    # Collect specific dimension data
    if dimension == "data_quality":
        data = collector.collect_data_quality()
    elif dimension == "category_structure":
        data = collector.collect_category_structure()
    elif dimension == "rule_engine":
        data = collector.collect_rule_engine()
    elif dimension == "tax_readiness":
        data = collector.collect_tax_readiness()
    elif dimension == "automation":
        data = collector.collect_automation()
    elif dimension == "budget_alignment":
        data = collector.collect_budget_alignment()
    else:
        print(f"Unknown dimension: {dimension}")
        return

    print("Running health check...\n")
    score = engine.run_single(dimension, data)

    # Print detailed results for this dimension
    print_header(f"{dimension.replace('_', ' ').upper()} HEALTH CHECK")
    print(f"Score: {score.score}/100  {format_status(score.status)}")
    print(f"{format_score_bar(score.score)}\n")

    if score.details:
        print("Metrics:")
        for key, value in score.details.items():
            key_formatted = key.replace("_", " ").title()
            if isinstance(value, float) and value < 1:
                print(f"  • {key_formatted}: {value:.1%}")
            else:
                print(f"  • {key_formatted}: {value}")

    if score.recommendations:
        print("\nRecommendations:")
        for i, rec in enumerate(score.recommendations, 1):
            print(f"{i}. {rec}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run PocketSmith health check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--full", action="store_true", help="Run full comprehensive check")
    parser.add_argument("--quick", action="store_true", help="Run quick essential checks only")
    parser.add_argument(
        "--category",
        type=str,
        help="Check specific category (categories|rules|tax|data|automation|budget)",
    )

    args = parser.parse_args()

    # Determine mode
    if args.category:
        mode = "category"
    elif args.quick:
        mode = "quick"
    elif args.full:
        mode = "full"
    else:
        # Default to quick if no mode specified
        mode = "quick"

    try:
        # Initialize API client
        print("Initializing PocketSmith API client...")
        client = PocketSmithClient()

        # Verify connection
        user = client.get_user()
        user_id: int = user.get("id")  # type: ignore[assignment]
        print(f"Connected as: {user.get('login', 'Unknown')} (ID: {user_id})\n")

        # Get data directory
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        if not data_dir.exists():
            data_dir.mkdir(parents=True)

        # Run appropriate check
        if mode == "quick":
            run_quick_check(client, user_id, data_dir)
        elif mode == "full":
            run_full_check(client, user_id, data_dir)
        elif mode == "category":
            run_category_check(client, user_id, data_dir, args.category)

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("\nMake sure POCKETSMITH_API_KEY is set in your .env file", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running health check: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
