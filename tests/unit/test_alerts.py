"""Unit tests for smart alerts system."""

import pytest
from datetime import datetime
from scripts.features.alerts import AlertType, AlertSeverity, Alert


def test_alert_type_enum_has_all_types():
    """Test that AlertType enum includes all alert categories."""
    assert AlertType.BUDGET in list(AlertType)
    assert AlertType.TAX in list(AlertType)
    assert AlertType.PATTERN in list(AlertType)
    assert AlertType.OPTIMIZATION in list(AlertType)


def test_alert_severity_enum():
    """Test that AlertSeverity enum has correct levels."""
    assert AlertSeverity.INFO in list(AlertSeverity)
    assert AlertSeverity.WARNING in list(AlertSeverity)
    assert AlertSeverity.CRITICAL in list(AlertSeverity)


def test_alert_creation():
    """Test creating an alert with all required fields."""
    alert = Alert(
        alert_id="alert_001",
        alert_type=AlertType.BUDGET,
        severity=AlertSeverity.WARNING,
        title="Budget Exceeded",
        message="You have exceeded your groceries budget by $50",
        created_at=datetime.now(),
        data={"category": "Groceries", "amount_over": 50.00},
    )

    assert alert.alert_id == "alert_001"
    assert alert.alert_type == AlertType.BUDGET
    assert alert.severity == AlertSeverity.WARNING
    assert alert.title == "Budget Exceeded"
    assert "exceeded" in alert.message
    assert alert.data["amount_over"] == 50.00
    assert alert.acknowledged is False  # Default value


def test_alert_acknowledgment():
    """Test acknowledging an alert."""
    alert = Alert(
        alert_id="alert_002",
        alert_type=AlertType.TAX,
        severity=AlertSeverity.CRITICAL,
        title="EOFY Deadline",
        message="EOFY is in 30 days",
        created_at=datetime.now(),
    )

    assert alert.acknowledged is False
    alert.acknowledge()
    assert alert.acknowledged is True
    assert alert.acknowledged_at is not None


def test_alert_engine_initialization():
    """Test creating alert engine with user ID."""
    from scripts.features.alerts import AlertEngine

    engine = AlertEngine(user_id="user_123")
    assert engine.user_id == "user_123"
    assert len(engine.active_alerts) == 0


def test_alert_engine_create_alert():
    """Test creating and storing an alert."""
    from scripts.features.alerts import AlertEngine

    engine = AlertEngine(user_id="user_123")

    alert = engine.create_alert(
        alert_type=AlertType.BUDGET,
        severity=AlertSeverity.WARNING,
        title="Budget Alert",
        message="Overspending detected",
        data={"category": "Dining", "amount": 500.00},
    )

    assert alert.alert_id.startswith("alert_")
    assert alert.alert_type == AlertType.BUDGET
    assert len(engine.active_alerts) == 1
    assert engine.active_alerts[0] == alert


def test_alert_engine_get_alerts_by_type():
    """Test filtering alerts by type."""
    from scripts.features.alerts import AlertEngine

    engine = AlertEngine(user_id="user_123")

    engine.create_alert(AlertType.BUDGET, AlertSeverity.WARNING, "Budget 1", "Message 1")
    engine.create_alert(AlertType.TAX, AlertSeverity.CRITICAL, "Tax 1", "Message 2")
    engine.create_alert(AlertType.BUDGET, AlertSeverity.INFO, "Budget 2", "Message 3")

    budget_alerts = engine.get_alerts(alert_type=AlertType.BUDGET)
    assert len(budget_alerts) == 2
    assert all(a.alert_type == AlertType.BUDGET for a in budget_alerts)


def test_alert_engine_get_unacknowledged():
    """Test getting only unacknowledged alerts."""
    from scripts.features.alerts import AlertEngine

    engine = AlertEngine(user_id="user_123")

    alert1 = engine.create_alert(AlertType.PATTERN, AlertSeverity.INFO, "Pattern 1", "Msg")
    alert2 = engine.create_alert(AlertType.PATTERN, AlertSeverity.INFO, "Pattern 2", "Msg")

    alert1.acknowledge()

    unack = engine.get_alerts(unacknowledged_only=True)
    assert len(unack) == 1
    assert unack[0] == alert2
