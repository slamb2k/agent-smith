import pytest
from datetime import datetime, timedelta
from scripts.features.alerts import (
    ScheduleType,
    AlertSchedule,
    AlertType,
    AlertScheduler,
    AlertEngine,
)


def test_schedule_type_enum():
    """Test that ScheduleType enum has all frequency types."""
    assert ScheduleType.WEEKLY in list(ScheduleType)
    assert ScheduleType.MONTHLY in list(ScheduleType)
    assert ScheduleType.QUARTERLY in list(ScheduleType)
    assert ScheduleType.ANNUAL in list(ScheduleType)
    assert ScheduleType.ONE_TIME in list(ScheduleType)


def test_alert_schedule_creation():
    """Test creating an alert schedule."""
    schedule = AlertSchedule(
        schedule_id="sched_001",
        schedule_type=ScheduleType.WEEKLY,
        alert_type=AlertType.BUDGET,
        title="Weekly Spending Summary",
        enabled=True,
        next_run=datetime(2025, 11, 28, 9, 0),
    )

    assert schedule.schedule_id == "sched_001"
    assert schedule.schedule_type == ScheduleType.WEEKLY
    assert schedule.enabled is True
    assert schedule.next_run == datetime(2025, 11, 28, 9, 0)


def test_alert_schedule_is_due():
    """Test checking if a schedule is due to run."""
    now = datetime(2025, 11, 21, 10, 0)

    # Schedule due in the past
    past_schedule = AlertSchedule(
        schedule_id="sched_002",
        schedule_type=ScheduleType.WEEKLY,
        alert_type=AlertType.TAX,
        title="Tax Alert",
        enabled=True,
        next_run=datetime(2025, 11, 21, 9, 0),
    )
    assert past_schedule.is_due(current_time=now) is True

    # Schedule due in the future
    future_schedule = AlertSchedule(
        schedule_id="sched_003",
        schedule_type=ScheduleType.WEEKLY,
        alert_type=AlertType.TAX,
        title="Future Alert",
        enabled=True,
        next_run=datetime(2025, 11, 21, 11, 0),
    )
    assert future_schedule.is_due(current_time=now) is False

    # Disabled schedule
    disabled_schedule = AlertSchedule(
        schedule_id="sched_004",
        schedule_type=ScheduleType.WEEKLY,
        alert_type=AlertType.TAX,
        title="Disabled Alert",
        enabled=False,
        next_run=datetime(2025, 11, 21, 9, 0),
    )
    assert disabled_schedule.is_due(current_time=now) is False


def test_alert_scheduler_initialization():
    """Test creating alert scheduler."""
    engine = AlertEngine(user_id="user_123")
    scheduler = AlertScheduler(alert_engine=engine)

    assert scheduler.alert_engine == engine
    assert len(scheduler.schedules) == 0


def test_alert_scheduler_add_schedule():
    """Test adding a schedule."""
    engine = AlertEngine(user_id="user_123")
    scheduler = AlertScheduler(alert_engine=engine)

    schedule = scheduler.add_schedule(
        schedule_type=ScheduleType.WEEKLY,
        alert_type=AlertType.BUDGET,
        title="Weekly Budget Review",
        next_run=datetime(2025, 11, 28, 9, 0),
        config={"categories": ["Groceries", "Dining"]},
    )

    assert schedule.schedule_id.startswith("sched_")
    assert schedule.enabled is True
    assert len(scheduler.schedules) == 1


def test_alert_scheduler_process_due_schedules():
    """Test processing schedules that are due."""
    engine = AlertEngine(user_id="user_123")
    scheduler = AlertScheduler(alert_engine=engine)

    now = datetime(2025, 11, 21, 10, 0)

    # Add due schedule
    scheduler.add_schedule(
        schedule_type=ScheduleType.WEEKLY,
        alert_type=AlertType.BUDGET,
        title="Due Alert",
        next_run=datetime(2025, 11, 21, 9, 0),
    )

    # Add future schedule
    scheduler.add_schedule(
        schedule_type=ScheduleType.WEEKLY,
        alert_type=AlertType.TAX,
        title="Future Alert",
        next_run=datetime(2025, 11, 21, 11, 0),
    )

    # Process schedules
    processed = scheduler.process_due_schedules(current_time=now)

    assert len(processed) == 1
    assert len(engine.active_alerts) == 1
    assert engine.active_alerts[0].title == "Due Alert"

    # Verify next_run was updated
    due_schedule = scheduler.schedules[0]
    assert due_schedule.next_run > now
    assert due_schedule.last_run == now
