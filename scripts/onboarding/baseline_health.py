"""Baseline health check for onboarding."""

from typing import Any, Optional

from scripts.health.collector import HealthDataCollector
from scripts.health.engine import HealthCheckEngine


class BaselineHealthChecker:
    """Run baseline health check before onboarding changes."""

    def __init__(self, client: Optional[Any] = None, user_id: Optional[int] = None) -> None:
        """Initialize with optional PocketSmith client.

        Args:
            client: PocketSmithClient instance
            user_id: PocketSmith user ID
        """
        self.client = client
        self.user_id = user_id
        self.engine = HealthCheckEngine()
        if client and user_id:
            self.collector = HealthDataCollector(api_client=client, user_id=user_id)
        else:
            self.collector = None  # type: ignore[assignment]

    def run_baseline_check(self) -> int:
        """Run baseline health check.

        Returns:
            Overall health score (0-100)
        """
        if not self.collector:
            raise ValueError("BaselineHealthChecker requires both client and user_id")

        # Collect health data
        health_data = self.collector.collect_all()

        # Run health check
        result = self.engine.run_all(health_data)

        return result.overall_score
