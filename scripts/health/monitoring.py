"""Health monitoring and automated alerting."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from scripts.health.engine import HealthCheckResult
from scripts.health.scores import HealthStatus


@dataclass
class MonitoringConfig:
    """Configuration for health monitoring."""

    weekly_check_enabled: bool = True
    monthly_full_check_enabled: bool = True
    pre_eofy_check_enabled: bool = True
    alert_on_score_drop: bool = True
    score_drop_threshold: int = 10  # Points
    critical_score_threshold: int = 50  # Alert if below


@dataclass
class HealthAlert:
    """Alert generated from health monitoring."""

    alert_type: str
    title: str
    message: str
    severity: str  # "info", "warning", "critical"
    dimension: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class HealthMonitor:
    """Monitors health scores and generates alerts."""

    def __init__(self, config: Optional[MonitoringConfig] = None) -> None:
        """Initialize monitor.

        Args:
            config: Monitoring configuration
        """
        self.config = config or MonitoringConfig()
        self.last_weekly_check: Optional[datetime] = None
        self.last_monthly_check: Optional[datetime] = None
        self.last_scores: Dict[str, int] = {}

    def should_run_weekly(self) -> bool:
        """Check if weekly health check should run.

        Returns:
            True if check should run
        """
        if not self.config.weekly_check_enabled:
            return False

        if self.last_weekly_check is None:
            return True

        days_since = (datetime.now() - self.last_weekly_check).days
        return days_since >= 7

    def should_run_monthly(self) -> bool:
        """Check if monthly full health check should run.

        Returns:
            True if check should run
        """
        if not self.config.monthly_full_check_enabled:
            return False

        if self.last_monthly_check is None:
            return True

        days_since = (datetime.now() - self.last_monthly_check).days
        return days_since >= 30

    def should_run_pre_eofy(self) -> bool:
        """Check if pre-EOFY health check should run.

        Returns:
            True if within 60 days of EOFY
        """
        if not self.config.pre_eofy_check_enabled:
            return False

        today = datetime.now()
        eofy = datetime(today.year, 6, 30)
        if today > eofy:
            eofy = datetime(today.year + 1, 6, 30)

        days_to_eofy = (eofy - today).days
        return days_to_eofy <= 60

    def detect_score_drops(
        self,
        previous: Dict[str, int],
        current: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """Detect significant score drops between checks.

        Args:
            previous: Previous dimension scores
            current: Current dimension scores

        Returns:
            List of detected drops with details
        """
        drops = []

        for dimension, prev_score in previous.items():
            curr_score = current.get(dimension, prev_score)
            drop = prev_score - curr_score

            if drop >= self.config.score_drop_threshold:
                drops.append(
                    {
                        "dimension": dimension,
                        "previous": prev_score,
                        "current": curr_score,
                        "drop": drop,
                    }
                )

        return drops

    def generate_alerts(self, result: HealthCheckResult) -> List[HealthAlert]:
        """Generate alerts from health check result.

        Args:
            result: Health check result

        Returns:
            List of alerts to send
        """
        alerts: List[HealthAlert] = []

        # Overall score alert
        if result.overall_score < self.config.critical_score_threshold:
            status_value = result.overall_status.value
            alerts.append(
                HealthAlert(
                    alert_type="health_critical",
                    title="Health Score Critical",
                    message=f"Overall health score is {result.overall_score}/100 ({status_value})",
                    severity="critical",
                    data={"score": result.overall_score},
                )
            )
        elif result.overall_status == HealthStatus.POOR:
            alerts.append(
                HealthAlert(
                    alert_type="health_poor",
                    title="Health Score Poor",
                    message=f"Overall health score needs attention: {result.overall_score}/100",
                    severity="warning",
                    data={"score": result.overall_score},
                )
            )

        # Dimension-specific alerts
        for score in result.scores:
            if score.score < 40:
                dim_title = score.dimension.replace("_", " ").title()
                alerts.append(
                    HealthAlert(
                        alert_type="dimension_critical",
                        title=f"{dim_title} Critical",
                        message=f"{score.dimension} score is {score.score}/100",
                        severity="critical",
                        dimension=score.dimension,
                        data={"score": score.score, "issues": score.issues},
                    )
                )

        # Score drop alerts
        if self.last_scores and self.config.alert_on_score_drop:
            current_scores = {s.dimension: s.score for s in result.scores}
            drops = self.detect_score_drops(self.last_scores, current_scores)

            for drop in drops:
                drop_title = drop["dimension"].replace("_", " ").title()
                drop_msg = (
                    f"Score dropped {drop['drop']} points "
                    f"(from {drop['previous']} to {drop['current']})"
                )
                alerts.append(
                    HealthAlert(
                        alert_type="score_drop",
                        title=f"{drop_title} Score Dropped",
                        message=drop_msg,
                        severity="warning",
                        dimension=drop["dimension"],
                        data=drop,
                    )
                )

        # Update last scores
        self.last_scores = {s.dimension: s.score for s in result.scores}

        return alerts

    def record_check(self, check_type: str) -> None:
        """Record that a check was performed.

        Args:
            check_type: "weekly" or "monthly"
        """
        now = datetime.now()
        if check_type == "weekly":
            self.last_weekly_check = now
        elif check_type == "monthly":
            self.last_monthly_check = now
