#!/usr/bin/env python
"""Delete all categories in optimal order (leaf-first) for experimentation.

WARNING: THIS IS DESTRUCTIVE AND IRREVERSIBLE!

This script deletes ALL categories in the PocketSmith account in the optimal order
(children before parents) to validate transaction behavior after deletion.
"""

import sys
import json
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from scripts.core.api_client import PocketSmithClient


def delete_all_categories(dry_run: bool = True, backup_dir: Optional[str] = None) -> Dict[str, Any]:
    """Delete all categories in optimal order.

    Args:
        dry_run: If True, only simulate deletion without actually deleting
        backup_dir: Path to backup directory containing deletion_order.json

    Returns:
        Dictionary with results:
        {
            'total': int,
            'deleted': int,
            'failed': int,
            'failed_categories': [{'id': int, 'title': str, 'error': str}]
        }
    """
    load_dotenv()
    client = PocketSmithClient()

    if not backup_dir:
        print("Error: backup_dir is required", file=sys.stderr)
        return {"total": 0, "deleted": 0, "failed": 0, "failed_categories": []}

    # Load deletion order
    with open(f"{backup_dir}/deletion_order.json") as f:
        deletion_order = json.load(f)

    results: Dict[str, Any] = {
        "total": len(deletion_order),
        "deleted": 0,
        "failed": 0,
        "failed_categories": [],
    }

    print("=" * 70)
    print("CATEGORY DELETION EXPERIMENT")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (simulation only)' if dry_run else 'LIVE DELETION (PERMANENT!)'}")
    print(f"Categories to delete: {results['total']}")
    print(f"Backup location: {backup_dir}")
    print()

    if not dry_run:
        print("⚠️  WARNING: This will PERMANENTLY delete all categories!")
        print("⚠️  All budgets will be deleted!")
        print("⚠️  All transactions will be uncategorized!")
        print("⚠️  This CANNOT be undone via API!")
        print()
        confirmation = input("Type 'DELETE ALL CATEGORIES' to proceed: ")
        if confirmation != "DELETE ALL CATEGORIES":
            print("Aborted.")
            return results
        print()

    # Delete categories in order (leaf-first)
    for i, cat_info in enumerate(deletion_order, 1):
        cat_id = cat_info["id"]
        cat_title = cat_info["title"]
        cat_level = cat_info["level"]

        try:
            total = results["total"]
            if dry_run:
                print(f"[DRY RUN] {i}/{total}: Would delete [{cat_level}] {cat_title}")
            else:
                print(f"Deleting {i}/{total}: [L{cat_level}] {cat_title}...", end="", flush=True)
                client.delete_category(cat_id)
                print(" ✓")
                time.sleep(0.2)  # Rate limiting

            results["deleted"] += 1

            # Progress indicators every 10 deletions
            if results["deleted"] % 10 == 0 and not dry_run:
                print(f"  Progress: {results['deleted']}/{results['total']}")

        except Exception as e:
            error_msg = str(e)
            print(f" ✗ FAILED: {error_msg}")
            results["failed"] += 1
            results["failed_categories"].append(
                {"id": cat_id, "title": cat_title, "error": error_msg}
            )

    print()
    print("=" * 70)
    print("DELETION COMPLETE")
    print("=" * 70)
    print(f"Total: {results['total']}")
    print(f"Deleted: {results['deleted']}")
    print(f"Failed: {results['failed']}")

    if results["failed_categories"]:
        print()
        print("Failed categories:")
        for cat in results["failed_categories"]:
            print(f"  - {cat['title']} (ID: {cat['id']}): {cat['error']}")

    return results


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Delete all categories in optimal order (EXPERIMENTAL)"
    )
    parser.add_argument(
        "--backup-dir", required=True, help="Path to backup directory with deletion_order.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Simulate deletion without actually deleting (default: true)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute deletion (DANGEROUS - overrides dry-run)",
    )
    parser.add_argument(
        "--output", choices=["json", "summary"], default="summary", help="Output format"
    )

    args = parser.parse_args()

    # Execute deletion
    results = delete_all_categories(
        dry_run=not args.execute,  # If --execute, turn off dry_run
        backup_dir=args.backup_dir,
    )

    # Output results
    if args.output == "json":
        print(json.dumps(results, indent=2))

    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
