"""Smart alerts and notifications system."""

from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime
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
