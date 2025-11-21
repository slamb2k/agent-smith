import pytest
from datetime import datetime
from scripts.features.audit import AuditAction, AuditEntry, AuditLogger


def test_audit_action_enum():
    """Test AuditAction enum values."""
    assert AuditAction.TRANSACTION_MODIFY in list(AuditAction)
    assert AuditAction.CATEGORY_CREATE in list(AuditAction)
    assert AuditAction.RULE_CREATE in list(AuditAction)
    assert AuditAction.BULK_OPERATION in list(AuditAction)
    assert AuditAction.REPORT_GENERATE in list(AuditAction)


def test_audit_entry_creation():
    """Test creating an audit entry."""
    entry = AuditEntry(
        entry_id="audit_001",
        action=AuditAction.TRANSACTION_MODIFY,
        timestamp=datetime(2025, 11, 21, 10, 0),
        user_id="user_123",
        description="Changed category from 'Food' to 'Groceries'",
        before_state={"category": "Food"},
        after_state={"category": "Groceries"},
        affected_ids=[12345],
    )

    assert entry.entry_id == "audit_001"
    assert entry.action == AuditAction.TRANSACTION_MODIFY
    assert entry.user_id == "user_123"
    assert entry.before_state["category"] == "Food"
    assert entry.after_state["category"] == "Groceries"


def test_audit_entry_to_dict():
    """Test serializing audit entry to dict."""
    entry = AuditEntry(
        entry_id="audit_002",
        action=AuditAction.RULE_CREATE,
        timestamp=datetime(2025, 11, 21, 10, 0),
        user_id="user_123",
        description="Created rule for Woolworths",
        after_state={"pattern": "woolworths", "category": "Groceries"},
        affected_ids=[1],
    )

    data = entry.to_dict()
    assert data["entry_id"] == "audit_002"
    assert data["action"] == "rule_create"
    assert data["description"] == "Created rule for Woolworths"
    assert "timestamp" in data


def test_audit_logger_initialization():
    """Test creating audit logger."""
    logger = AuditLogger(user_id="user_123")
    assert logger.user_id == "user_123"
    assert len(logger.entries) == 0


def test_audit_logger_log_action():
    """Test logging an action."""
    logger = AuditLogger(user_id="user_123")

    entry = logger.log_action(
        action=AuditAction.TRANSACTION_MODIFY,
        description="Changed category",
        before_state={"category": "Food"},
        after_state={"category": "Groceries"},
        affected_ids=[12345],
    )

    assert entry.entry_id.startswith("audit_")
    assert entry.action == AuditAction.TRANSACTION_MODIFY
    assert len(logger.entries) == 1


def test_audit_logger_get_entries_by_action():
    """Test filtering entries by action type."""
    logger = AuditLogger(user_id="user_123")

    logger.log_action(AuditAction.TRANSACTION_MODIFY, "Modify 1")
    logger.log_action(AuditAction.RULE_CREATE, "Create rule")
    logger.log_action(AuditAction.TRANSACTION_MODIFY, "Modify 2")

    modify_entries = logger.get_entries(action=AuditAction.TRANSACTION_MODIFY)
    assert len(modify_entries) == 2
    assert all(e.action == AuditAction.TRANSACTION_MODIFY for e in modify_entries)


def test_audit_logger_get_entries_for_id():
    """Test getting all entries affecting a specific ID."""
    logger = AuditLogger(user_id="user_123")

    logger.log_action(AuditAction.TRANSACTION_MODIFY, "Modify txn 123", affected_ids=[123, 456])
    logger.log_action(AuditAction.TRANSACTION_MODIFY, "Modify txn 789", affected_ids=[789])
    logger.log_action(AuditAction.TRANSACTION_MODIFY, "Modify txn 123 again", affected_ids=[123])

    entries_123 = logger.get_entries(affected_id=123)
    assert len(entries_123) == 2

    entries_789 = logger.get_entries(affected_id=789)
    assert len(entries_789) == 1


def test_audit_logger_get_entries_by_date_range():
    """Test filtering entries by date range."""
    logger = AuditLogger(user_id="user_123")

    # Create entries with different timestamps
    logger.entries.append(
        AuditEntry(
            entry_id="audit_001",
            action=AuditAction.TRANSACTION_MODIFY,
            timestamp=datetime(2025, 11, 20, 10, 0),
            user_id="user_123",
            description="Old entry",
        )
    )
    logger.entries.append(
        AuditEntry(
            entry_id="audit_002",
            action=AuditAction.TRANSACTION_MODIFY,
            timestamp=datetime(2025, 11, 21, 10, 0),
            user_id="user_123",
            description="Recent entry",
        )
    )
    logger.entries.append(
        AuditEntry(
            entry_id="audit_003",
            action=AuditAction.TRANSACTION_MODIFY,
            timestamp=datetime(2025, 11, 22, 10, 0),
            user_id="user_123",
            description="Future entry",
        )
    )

    # Filter by date range
    results = logger.get_entries(
        start_date=datetime(2025, 11, 21, 0, 0),
        end_date=datetime(2025, 11, 21, 23, 59),
    )
    assert len(results) == 1
    assert results[0].entry_id == "audit_002"


def test_audit_logger_can_undo():
    """Test checking if an action can be undone."""
    logger = AuditLogger(user_id="user_123")

    # Create entry with before_state (can undo)
    entry1 = logger.log_action(
        AuditAction.TRANSACTION_MODIFY,
        "Change category",
        before_state={"category": "Food"},
        after_state={"category": "Groceries"},
        affected_ids=[123],
    )
    assert logger.can_undo(entry1.entry_id) is True

    # Create entry without before_state (cannot undo)
    entry2 = logger.log_action(
        AuditAction.REPORT_GENERATE,
        "Generate report",
    )
    assert logger.can_undo(entry2.entry_id) is False
