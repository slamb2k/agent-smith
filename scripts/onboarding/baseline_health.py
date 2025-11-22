"""Baseline health check for onboarding."""

from typing import Any, Optional

from scripts.health.collector import HealthDataCollector
from scripts.health.engine import HealthCheckEngine


class BaselineHealthChecker:
    """Run baseline health check before onboarding changes."""

    def __init__(self, client: Optional[Any] = None) -> None:
        """Initialize with optional PocketSmith client.

        Args:
            client: PocketSmithClient instance
        """
        self.client = client
        self.engine = HealthCheckEngine()
        self.collector = HealthDataCollector(api_client=client)

    def run_baseline_check(self) -> int:
        """Run baseline health check.

        Returns:
            Overall health score (0-100)
        """
        # Collect health data
        health_data = self.collector.collect_all()

        # Run health check
        result = self.engine.run_all(health_data)

        return result.overall_score
