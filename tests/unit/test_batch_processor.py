"""Tests for batch processing operational modes."""

import pytest
from datetime import datetime, timedelta
from scripts.operations.batch_processor import (
    BatchProcessor,
    ProcessingMode,
    UpdateStrategy,
    DateRange,
)


def test_dry_run_mode():
    """Test dry-run mode doesn't modify transactions."""
    processor = BatchProcessor(mode=ProcessingMode.DRY_RUN)

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "category": None},
        {"id": 2, "payee": "UBER", "category": None},
    ]

    results = processor.process_batch(transactions)

    # Dry-run should show what would happen but not apply
    assert results["total"] == 2
    assert results["would_categorize"] == 2
    assert results["applied"] == 0
    assert results["dry_run"] is True


def test_validate_mode_detects_changes():
    """Test validate mode identifies transactions that would change."""
    processor = BatchProcessor(mode=ProcessingMode.VALIDATE)

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "category": {"title": "Shopping"}},
        {"id": 2, "payee": "COLES", "category": {"title": "Groceries"}},
    ]

    # Rules would categorize both as "Groceries"
    results = processor.process_batch(transactions)

    assert results["total"] == 2
    assert results["would_change"] == 1  # Transaction 1 would change
    assert results["unchanged"] == 1  # Transaction 2 already correct


def test_update_strategy_skip_existing():
    """Test SKIP_EXISTING strategy."""
    processor = BatchProcessor(
        mode=ProcessingMode.APPLY,
        update_strategy=UpdateStrategy.SKIP_EXISTING,
    )

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "category": None},
        {"id": 2, "payee": "COLES", "category": {"title": "Shopping"}},
    ]

    results = processor.process_batch(transactions)

    # Should only process uncategorized
    assert results["processed"] == 1
    assert results["skipped"] == 1


def test_update_strategy_replace_all():
    """Test REPLACE_ALL strategy."""
    processor = BatchProcessor(
        mode=ProcessingMode.APPLY,
        update_strategy=UpdateStrategy.REPLACE_ALL,
    )

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "category": None},
        {"id": 2, "payee": "COLES", "category": {"title": "Shopping"}},
    ]

    results = processor.process_batch(transactions)

    # Should process all transactions
    assert results["processed"] == 2
    assert results["skipped"] == 0


def test_update_strategy_upgrade_confidence():
    """Test UPGRADE_CONFIDENCE strategy."""
    processor = BatchProcessor(
        mode=ProcessingMode.APPLY,
        update_strategy=UpdateStrategy.UPGRADE_CONFIDENCE,
    )

    transactions = [
        {
            "id": 1,
            "payee": "WOOLWORTHS",
            "category": {"title": "Groceries"},
            "_category_confidence": 75,  # Lower confidence
        },
        {
            "id": 2,
            "payee": "COLES",
            "category": {"title": "Groceries"},
            "_category_confidence": 95,  # Higher confidence
        },
    ]

    # New rule has 95% confidence
    results = processor.process_batch(transactions)

    # Should upgrade first, skip second
    assert results["upgraded"] == 1
    assert results["skipped"] == 1


def test_date_range_filtering():
    """Test filtering transactions by date range."""
    today = datetime.now()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    transactions = [
        {"id": 1, "payee": "TEST1", "date": today.strftime("%Y-%m-%d")},
        {"id": 2, "payee": "TEST2", "date": last_week.strftime("%Y-%m-%d")},
        {"id": 3, "payee": "TEST3", "date": last_month.strftime("%Y-%m-%d")},
    ]

    # Filter to last 2 weeks
    date_range = DateRange(
        start_date=last_week - timedelta(days=7),
        end_date=today,
    )

    processor = BatchProcessor(date_range=date_range)
    filtered = processor.filter_transactions(transactions)

    assert len(filtered) == 2  # Today and last week only


def test_account_filtering():
    """Test filtering transactions by account."""
    transactions = [
        {"id": 1, "payee": "TEST1", "_account_name": "Personal"},
        {"id": 2, "payee": "TEST2", "_account_name": "Shared Bills"},
        {"id": 3, "payee": "TEST3", "_account_name": "Work"},
    ]

    processor = BatchProcessor(accounts=["Personal", "Work"])
    filtered = processor.filter_transactions(transactions)

    assert len(filtered) == 2  # Personal and Work only


def test_limit_processing():
    """Test limiting number of transactions processed."""
    transactions = [{"id": i, "payee": f"TEST{i}"} for i in range(100)]

    processor = BatchProcessor(limit=10)
    filtered = processor.filter_transactions(transactions)

    assert len(filtered) == 10


def test_progress_callback():
    """Test progress reporting via callback."""
    progress_updates = []

    def progress_callback(current: int, total: int, transaction_id: int):
        progress_updates.append({"current": current, "total": total, "id": transaction_id})

    processor = BatchProcessor(
        mode=ProcessingMode.DRY_RUN,
        progress_callback=progress_callback,
    )

    transactions = [
        {"id": 1, "payee": "TEST1"},
        {"id": 2, "payee": "TEST2"},
        {"id": 3, "payee": "TEST3"},
    ]

    processor.process_batch(transactions)

    # Should have 3 progress updates
    assert len(progress_updates) == 3
    assert progress_updates[0] == {"current": 1, "total": 3, "id": 1}
    assert progress_updates[2] == {"current": 3, "total": 3, "id": 3}


def test_update_strategy_replace_if_different():
    """Test REPLACE_IF_DIFFERENT strategy."""
    processor = BatchProcessor(
        mode=ProcessingMode.APPLY,
        update_strategy=UpdateStrategy.REPLACE_IF_DIFFERENT,
    )

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "category": {"title": "Shopping"}},  # Different
        {"id": 2, "payee": "COLES", "category": {"title": "Groceries"}},  # Same
    ]

    results = processor.process_batch(transactions)

    # Should replace first (different), skip second (same)
    assert results["processed"] == 1
    assert results["skipped"] == 1


def test_combined_filters():
    """Test combining date range, accounts, and limit filters."""
    today = datetime.now()
    last_week = today - timedelta(days=7)

    transactions = [
        {
            "id": 1,
            "payee": "TEST1",
            "date": today.strftime("%Y-%m-%d"),
            "_account_name": "Personal",
        },
        {"id": 2, "payee": "TEST2", "date": today.strftime("%Y-%m-%d"), "_account_name": "Work"},
        {
            "id": 3,
            "payee": "TEST3",
            "date": last_week.strftime("%Y-%m-%d"),
            "_account_name": "Personal",
        },
        {
            "id": 4,
            "payee": "TEST4",
            "date": last_week.strftime("%Y-%m-%d"),
            "_account_name": "Work",
        },
        {
            "id": 5,
            "payee": "TEST5",
            "date": today.strftime("%Y-%m-%d"),
            "_account_name": "Personal",
        },
    ]

    date_range = DateRange(start_date=last_week - timedelta(days=1), end_date=today)
    processor = BatchProcessor(
        date_range=date_range,
        accounts=["Personal"],
        limit=2,
    )

    filtered = processor.filter_transactions(transactions)

    # Should filter to Personal account, within date range, limit to 2
    assert len(filtered) == 2
    assert all(t["_account_name"] == "Personal" for t in filtered)


def test_validate_mode_shows_from_to_changes():
    """Test validate mode shows what would change from/to."""
    processor = BatchProcessor(mode=ProcessingMode.VALIDATE)

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "category": {"title": "Shopping"}},
    ]

    results = processor.process_batch(transactions)

    # Should show the change details
    assert len(results["details"]) > 0
    detail = results["details"][0]
    assert detail["action"] == "would_change"
    assert "from" in detail
    assert "to" in detail
    assert detail["from"] == "Shopping"
    assert detail["to"] == "Groceries"
