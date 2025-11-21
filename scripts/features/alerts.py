"""Smart alerts and notifications system."""

from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid


class AlertType(Enum):
    """Types of alerts that can be generated."""

    BUDGET = "budget"
    TAX = "tax"
    PATTERN = "pattern"
    OPTIMIZATION = "optimization"


class AlertSeverity(Enum):
    """Severity levels for alerts."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ScheduleType(Enum):
    """Frequency for scheduled alerts."""

    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    ONE_TIME = "one_time"


@dataclass
class Alert:
    """Represents a single alert."""

    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    created_at: datetime
    data: Optional[Dict[str, Any]] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None

    def acknowledge(self) -> None:
        """Mark alert as acknowledged."""
        self.acknowledged = True
        self.acknowledged_at = datetime.now()


@dataclass
class AlertSchedule:
    """Represents a scheduled alert."""

    schedule_id: str
    schedule_type: ScheduleType
    alert_type: AlertType
    title: str
    enabled: bool
    next_run: datetime
    config: Optional[Dict[str, Any]] = None
    last_run: Optional[datetime] = None

    def is_due(self, current_time: Optional[datetime] = None) -> bool:
        """Check if this schedule is due to run.

        Args:
            current_time: Time to check against (default: now)

        Returns:
            True if schedule is due and enabled
        """
        if not self.enabled:
            return False

        check_time = current_time or datetime.now()
        return check_time >= self.next_run

    def calculate_next_run(self) -> datetime:
        """Calculate next run time based on schedule type.

        Returns:
            Next scheduled run time
        """
        now = datetime.now()

        if self.schedule_type == ScheduleType.WEEKLY:
            return now + timedelta(weeks=1)
        elif self.schedule_type == ScheduleType.MONTHLY:
            return now + timedelta(days=30)
        elif self.schedule_type == ScheduleType.QUARTERLY:
            return now + timedelta(days=90)
        elif self.schedule_type == ScheduleType.ANNUAL:
            return now + timedelta(days=365)
        else:  # ONE_TIME
            return self.next_run


class AlertEngine:
    """Manages alert creation, storage, and retrieval."""

    def __init__(self, user_id: str):
        """Initialize alert engine for a user.

        Args:
            user_id: PocketSmith user ID
        """
        self.user_id = user_id
        self.active_alerts: List[Alert] = []

    def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Alert:
        """Create a new alert and add to active alerts.

        Args:
            alert_type: Type of alert
            severity: Severity level
            title: Short title
            message: Detailed message
            data: Optional additional data

        Returns:
            Created Alert object
        """
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            created_at=datetime.now(),
            data=data,
        )
        self.active_alerts.append(alert)
        return alert

    def get_alerts(
        self,
        alert_type: Optional[AlertType] = None,
        severity: Optional[AlertSeverity] = None,
        unacknowledged_only: bool = False,
    ) -> List[Alert]:
        """Retrieve alerts with optional filtering.

        Args:
            alert_type: Filter by alert type
            severity: Filter by severity
            unacknowledged_only: Only return unacknowledged alerts

        Returns:
            List of matching alerts
        """
        results = self.active_alerts

        if alert_type:
            results = [a for a in results if a.alert_type == alert_type]

        if severity:
            results = [a for a in results if a.severity == severity]

        if unacknowledged_only:
            results = [a for a in results if not a.acknowledged]

        return results


class AlertScheduler:
    """Manages scheduled alerts."""

    def __init__(self, alert_engine: AlertEngine):
        """Initialize scheduler with alert engine.

        Args:
            alert_engine: AlertEngine to create alerts with
        """
        self.alert_engine = alert_engine
        self.schedules: List[AlertSchedule] = []

    def add_schedule(
        self,
        schedule_type: ScheduleType,
        alert_type: AlertType,
        title: str,
        next_run: datetime,
        config: Optional[Dict[str, Any]] = None,
        enabled: bool = True,
    ) -> AlertSchedule:
        """Add a new alert schedule.

        Args:
            schedule_type: Frequency of schedule
            alert_type: Type of alert to create
            title: Schedule title
            next_run: When to first run
            config: Optional configuration
            enabled: Whether schedule is active

        Returns:
            Created AlertSchedule
        """
        schedule = AlertSchedule(
            schedule_id=f"sched_{uuid.uuid4().hex[:8]}",
            schedule_type=schedule_type,
            alert_type=alert_type,
            title=title,
            enabled=enabled,
            next_run=next_run,
            config=config,
        )
        self.schedules.append(schedule)
        return schedule

    def process_due_schedules(self, current_time: Optional[datetime] = None) -> List[Alert]:
        """Process all schedules that are due and create alerts.

        Args:
            current_time: Time to check against (default: now)

        Returns:
            List of created alerts
        """
        check_time = current_time or datetime.now()
        created_alerts = []

        for schedule in self.schedules:
            if schedule.is_due(current_time=check_time):
                # Create alert
                alert = self.alert_engine.create_alert(
                    alert_type=schedule.alert_type,
                    severity=AlertSeverity.INFO,
                    title=schedule.title,
                    message=f"Scheduled {schedule.schedule_type.value} alert",
                    data=schedule.config,
                )
                created_alerts.append(alert)

                # Update schedule
                schedule.last_run = check_time
                schedule.next_run = schedule.calculate_next_run()

        return created_alerts
