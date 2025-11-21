"""Integration tests for Phase 7 advanced features."""

import pytest
from datetime import datetime, timedelta
from scripts.features.alerts import (
    AlertEngine,
    AlertScheduler,
    AlertType,
    AlertSeverity,
    ScheduleType,
)
from scripts.features.merchant_intelligence import MerchantMatcher
from scripts.features.documents import DocumentManager
from scripts.features.multi_user import SharedExpenseTracker
from scripts.features.benchmarking import BenchmarkEngine, PeerCriteria
from scripts.features.audit import AuditLogger, AuditAction


def test_alert_workflow_end_to_end():
    """Test complete alert workflow from scheduling to acknowledgment."""
    # Create alert engine and scheduler
    engine = AlertEngine(user_id="user_123")
    scheduler = AlertScheduler(alert_engine=engine)

    # Schedule a weekly budget alert
    now = datetime(2025, 11, 21, 10, 0)
    schedule = scheduler.add_schedule(
        schedule_type=ScheduleType.WEEKLY,
        alert_type=AlertType.BUDGET,
        title="Weekly Budget Review",
        next_run=now - timedelta(hours=1),  # Due 1 hour ago
        config={"categories": ["Groceries", "Dining"]},
    )

    # Process due schedules
    created_alerts = scheduler.process_due_schedules(current_time=now)

    # Verify alert was created
    assert len(created_alerts) == 1
    alert = created_alerts[0]
    assert alert.alert_type == AlertType.BUDGET
    assert alert.title == "Weekly Budget Review"
    assert not alert.acknowledged

    # Acknowledge alert
    alert.acknowledge()
    assert alert.acknowledged
    assert alert.acknowledged_at is not None

    # Verify schedule was updated
    assert schedule.next_run > now
    assert schedule.last_run == now


def test_merchant_intelligence_learning_workflow():
    """Test merchant intelligence learning from user corrections."""
    matcher = MerchantMatcher()

    # Initial payee variations for Woolworths
    variations = [
        "WOOLWORTHS PTY LTD",
        "Woolworths Pty Ltd",
        "WOOLWORTH",
        "WOOLIES",
    ]

    # Learn canonical name from first transaction
    matcher.add_variation("Woolworths", variations[0])

    # Process remaining variations
    for variation in variations[1:]:
        # Check if we can suggest a match
        suggestions = matcher.suggest_matches(variation, threshold=0.7)

        if suggestions:
            # Use suggested canonical name
            canonical = suggestions[0][0]
            matcher.add_variation(canonical, variation)
        else:
            # Would prompt user for canonical name
            matcher.add_variation("Woolworths", variation)

    # Verify all variations are grouped
    # Note: "WOOLWORTHS PTY LTD" and "Woolworths Pty Ltd" normalize to same value
    # So we expect 3 unique normalized variations, not 4
    group = matcher.canonical_names["woolworths"]
    assert group.canonical_name == "Woolworths"
    assert len(group.variations) >= 3  # At least the unique normalized forms

    # Verify the normalized forms are present
    expected_variations = {"woolworths", "woolworth", "woolies"}
    assert group.variations == expected_variations

    # Test lookup of new variation (should find match or None based on threshold)
    matcher.find_canonical("woolworth supermarket")


def test_document_management_workflow():
    """Test document requirement tracking workflow."""
    manager = DocumentManager()

    # Track several transactions
    transactions = [
        (1, 450.00, "Work Expenses", datetime(2025, 11, 15)),  # Required
        (2, 150.00, "Office Supplies", datetime(2025, 11, 16)),  # Recommended
        (3, 50.00, "Groceries", datetime(2025, 11, 17)),  # Optional
        (4, 350.00, "Professional Development", datetime(2025, 11, 18)),  # Required
    ]

    for txn_id, amount, category, date in transactions:
        manager.track_transaction(txn_id, amount, category, date)

    # Get missing required documents
    missing_required = manager.get_missing_documents(required_only=True)
    assert len(missing_required) == 2
    assert {d.transaction_id for d in missing_required} == {1, 4}

    # Attach document to first transaction
    doc1 = manager.documents[1]
    doc1.attach_document("https://example.com/receipt1.pdf")

    # Verify missing count decreased
    missing_required = manager.get_missing_documents(required_only=True)
    assert len(missing_required) == 1
    assert missing_required[0].transaction_id == 4


def test_multi_user_settlement_workflow():
    """Test complete shared expense and settlement workflow."""
    tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])

    # Add several shared expenses
    tracker.add_expense(
        transaction_id=1,
        amount=150.00,
        description="Dinner at restaurant",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        split_equally=True,
    )

    tracker.add_expense(
        transaction_id=2,
        amount=90.00,
        description="Groceries",
        paid_by="bob",
        date=datetime(2025, 11, 16),
        split_equally=True,
    )

    tracker.add_expense(
        transaction_id=3,
        amount=60.00,
        description="Coffee",
        paid_by="charlie",
        date=datetime(2025, 11, 17),
        split_equally=True,
    )

    # Calculate balances
    balances = tracker.calculate_balances()

    # Alice: paid $150, owes $100 = +$50
    # Bob: paid $90, owes $100 = -$10
    # Charlie: paid $60, owes $100 = -$40
    assert balances["alice"] == 50.00
    assert balances["bob"] == -10.00
    assert balances["charlie"] == -40.00

    # Generate settlements
    settlements = tracker.generate_settlements()

    # Should have 2 settlements (Bob -> Alice, Charlie -> Alice)
    assert len(settlements) == 2

    total_to_alice = sum(s.amount for s in settlements if s.to_user == "alice")
    assert total_to_alice == 50.00


def test_benchmarking_comparison_workflow():
    """Test benchmarking comparison workflow."""
    engine = BenchmarkEngine()

    criteria = PeerCriteria(household_size=2, income_bracket="50k-75k")

    # Simulate peer data collection
    peer_data = [
        ("peer_1", 450.00),
        ("peer_2", 500.00),
        ("peer_3", 550.00),
        ("peer_4", 600.00),
        ("peer_5", 650.00),
    ]

    for user_id, amount in peer_data:
        engine.add_data_point(
            category="Groceries",
            amount=amount,
            user_id=user_id,
            criteria=criteria,
        )

    # Compare user spending
    result = engine.compare(
        category="Groceries",
        user_amount=525.00,
        criteria=criteria,
    )

    assert result is not None
    assert result.category == "Groceries"
    assert result.user_amount == 525.00
    assert result.peer_count == 5
    assert 40 <= result.percentile <= 60  # Around median


def test_audit_trail_workflow():
    """Test audit logging and query workflow."""
    logger = AuditLogger(user_id="user_123")

    # Log several actions
    logger.log_action(
        action=AuditAction.TRANSACTION_MODIFY,
        description="Changed category from 'Food' to 'Groceries'",
        before_state={"category": "Food"},
        after_state={"category": "Groceries"},
        affected_ids=[123],
    )

    logger.log_action(
        action=AuditAction.RULE_CREATE,
        description="Created rule for Woolworths",
        after_state={"pattern": "woolworths", "category": "Groceries"},
        affected_ids=[1],
    )

    logger.log_action(
        action=AuditAction.TRANSACTION_MODIFY,
        description="Updated amount for transaction 123",
        before_state={"amount": 50.00},
        after_state={"amount": 55.00},
        affected_ids=[123],
    )

    # Query by action type
    modify_entries = logger.get_entries(action=AuditAction.TRANSACTION_MODIFY)
    assert len(modify_entries) == 2

    # Query by affected ID
    txn_123_entries = logger.get_entries(affected_id=123)
    assert len(txn_123_entries) == 2

    # Check undo capability
    for entry in logger.entries:
        if entry.action == AuditAction.TRANSACTION_MODIFY:
            assert logger.can_undo(entry.entry_id) is True
        elif entry.action == AuditAction.RULE_CREATE:
            # Rule creation has no before_state
            assert logger.can_undo(entry.entry_id) is False
