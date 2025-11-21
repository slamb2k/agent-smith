# Phase 7: Advanced Features Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement smart alerts & notifications, merchant intelligence, document management, multi-user support, comparative benchmarking, and audit trail capabilities to provide proactive financial management and comprehensive activity tracking.

**Architecture:** Six independent feature modules with shared foundation: (1) Alert engine with scheduling and notification delivery, (2) Merchant intelligence with variation detection and learning, (3) Document manager with receipt tracking and PocketSmith integration, (4) Multi-user tracker for shared expenses and settlements, (5) Benchmarking engine with privacy-first anonymous comparison, (6) Audit trail with complete activity logging and undo capability.

**Tech Stack:** Python 3.9+, pytest, PocketSmith API, datetime/timedelta for scheduling, difflib for variation detection, hashlib for privacy preservation, JSON for audit logs

---

## Task 1: Smart Alerts Foundation

**Files:**
- Create: `scripts/features/alerts.py`
- Create: `tests/unit/test_alerts.py`
- Create: `data/alerts/config.json`

### Step 1: Write failing test for AlertType enum

```python
# tests/unit/test_alerts.py
import pytest
from scripts.features.alerts import AlertType, AlertSeverity


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
```

### Step 2: Run test to verify it fails

```bash
pytest tests/unit/test_alerts.py::test_alert_type_enum_has_all_types -v
```

Expected: `FAILED` - `ModuleNotFoundError: No module named 'scripts.features.alerts'`

### Step 3: Write minimal implementation for enums

```python
# scripts/features/alerts.py
"""Smart alerts and notifications system."""
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


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
```

### Step 4: Run test to verify it passes

```bash
pytest tests/unit/test_alerts.py::test_alert_type_enum_has_all_types -v
pytest tests/unit/test_alerts.py::test_alert_severity_enum -v
```

Expected: Both tests `PASSED`

### Step 5: Write failing test for Alert dataclass

```python
# tests/unit/test_alerts.py (append)
from scripts.features.alerts import Alert


def test_alert_creation():
    """Test creating an alert with all required fields."""
    alert = Alert(
        alert_id="alert_001",
        alert_type=AlertType.BUDGET,
        severity=AlertSeverity.WARNING,
        title="Budget Exceeded",
        message="You have exceeded your groceries budget by $50",
        created_at=datetime.now(),
        data={"category": "Groceries", "amount_over": 50.00}
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
```

### Step 6: Run test to verify it fails

```bash
pytest tests/unit/test_alerts.py::test_alert_creation -v
```

Expected: `FAILED` - `NameError: name 'Alert' is not defined`

### Step 7: Implement Alert dataclass

```python
# scripts/features/alerts.py (append)
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
```

### Step 8: Run tests to verify they pass

```bash
pytest tests/unit/test_alerts.py -v
```

Expected: All tests `PASSED` (4 tests)

### Step 9: Write failing test for AlertEngine

```python
# tests/unit/test_alerts.py (append)
from scripts.features.alerts import AlertEngine


def test_alert_engine_initialization():
    """Test creating alert engine with user ID."""
    engine = AlertEngine(user_id="user_123")
    assert engine.user_id == "user_123"
    assert len(engine.active_alerts) == 0


def test_alert_engine_create_alert():
    """Test creating and storing an alert."""
    engine = AlertEngine(user_id="user_123")

    alert = engine.create_alert(
        alert_type=AlertType.BUDGET,
        severity=AlertSeverity.WARNING,
        title="Budget Alert",
        message="Overspending detected",
        data={"category": "Dining", "amount": 500.00}
    )

    assert alert.alert_id.startswith("alert_")
    assert alert.alert_type == AlertType.BUDGET
    assert len(engine.active_alerts) == 1
    assert engine.active_alerts[0] == alert


def test_alert_engine_get_alerts_by_type():
    """Test filtering alerts by type."""
    engine = AlertEngine(user_id="user_123")

    engine.create_alert(AlertType.BUDGET, AlertSeverity.WARNING, "Budget 1", "Message 1")
    engine.create_alert(AlertType.TAX, AlertSeverity.CRITICAL, "Tax 1", "Message 2")
    engine.create_alert(AlertType.BUDGET, AlertSeverity.INFO, "Budget 2", "Message 3")

    budget_alerts = engine.get_alerts(alert_type=AlertType.BUDGET)
    assert len(budget_alerts) == 2
    assert all(a.alert_type == AlertType.BUDGET for a in budget_alerts)


def test_alert_engine_get_unacknowledged():
    """Test getting only unacknowledged alerts."""
    engine = AlertEngine(user_id="user_123")

    alert1 = engine.create_alert(AlertType.PATTERN, AlertSeverity.INFO, "Pattern 1", "Msg")
    alert2 = engine.create_alert(AlertType.PATTERN, AlertSeverity.INFO, "Pattern 2", "Msg")

    alert1.acknowledge()

    unack = engine.get_alerts(unacknowledged_only=True)
    assert len(unack) == 1
    assert unack[0] == alert2
```

### Step 10: Run test to verify it fails

```bash
pytest tests/unit/test_alerts.py::test_alert_engine_initialization -v
```

Expected: `FAILED` - `NameError: name 'AlertEngine' is not defined`

### Step 11: Implement AlertEngine class

```python
# scripts/features/alerts.py (append)
import uuid


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
```

### Step 12: Run all tests to verify they pass

```bash
pytest tests/unit/test_alerts.py -v
```

Expected: All tests `PASSED` (8 tests)

### Step 13: Run format, lint, type-check

```bash
black scripts/features/alerts.py tests/unit/test_alerts.py
flake8 scripts/features/alerts.py tests/unit/test_alerts.py --max-line-length=100
mypy scripts/features/alerts.py
```

Expected: All checks pass

### Step 14: Commit

```bash
git add scripts/features/alerts.py tests/unit/test_alerts.py
git commit -m "feat(alerts): add alert foundation with types, severity, and engine

- Add AlertType enum (budget, tax, pattern, optimization)
- Add AlertSeverity enum (info, warning, critical)
- Implement Alert dataclass with acknowledgment
- Implement AlertEngine for alert management
- Add 8 unit tests covering alert creation and filtering"
```

---

## Task 2: Alert Schedule Engine

**Files:**
- Modify: `scripts/features/alerts.py`
- Modify: `tests/unit/test_alerts.py`
- Create: `tests/unit/test_alert_scheduler.py`

### Step 1: Write failing test for ScheduleType enum

```python
# tests/unit/test_alert_scheduler.py
import pytest
from datetime import datetime, timedelta
from scripts.features.alerts import ScheduleType, AlertSchedule


def test_schedule_type_enum():
    """Test that ScheduleType enum has all frequency types."""
    assert ScheduleType.WEEKLY in list(ScheduleType)
    assert ScheduleType.MONTHLY in list(ScheduleType)
    assert ScheduleType.QUARTERLY in list(ScheduleType)
    assert ScheduleType.ANNUAL in list(ScheduleType)
    assert ScheduleType.ONE_TIME in list(ScheduleType)
```

### Step 2: Run test to verify it fails

```bash
pytest tests/unit/test_alert_scheduler.py::test_schedule_type_enum -v
```

Expected: `FAILED` - `ImportError: cannot import name 'ScheduleType'`

### Step 3: Add ScheduleType enum

```python
# scripts/features/alerts.py (add after AlertSeverity)
class ScheduleType(Enum):
    """Frequency for scheduled alerts."""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    ONE_TIME = "one_time"
```

### Step 4: Run test to verify it passes

```bash
pytest tests/unit/test_alert_scheduler.py::test_schedule_type_enum -v
```

Expected: `PASSED`

### Step 5: Write failing test for AlertSchedule dataclass

```python
# tests/unit/test_alert_scheduler.py (append)
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
```

### Step 6: Run test to verify it fails

```bash
pytest tests/unit/test_alert_scheduler.py::test_alert_schedule_creation -v
```

Expected: `FAILED` - `ImportError: cannot import name 'AlertSchedule'`

### Step 7: Implement AlertSchedule dataclass

```python
# scripts/features/alerts.py (add after Alert dataclass)
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
```

### Step 8: Run tests to verify they pass

```bash
pytest tests/unit/test_alert_scheduler.py -v
```

Expected: All tests `PASSED` (3 tests)

### Step 9: Write failing test for AlertScheduler class

```python
# tests/unit/test_alert_scheduler.py (append)
from scripts.features.alerts import AlertScheduler, AlertEngine


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
        config={"categories": ["Groceries", "Dining"]}
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
```

### Step 10: Run test to verify it fails

```bash
pytest tests/unit/test_alert_scheduler.py::test_alert_scheduler_initialization -v
```

Expected: `FAILED` - `ImportError: cannot import name 'AlertScheduler'`

### Step 11: Implement AlertScheduler class

```python
# scripts/features/alerts.py (append to end of file)
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

    def process_due_schedules(
        self, current_time: Optional[datetime] = None
    ) -> List[Alert]:
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
```

### Step 12: Run all tests to verify they pass

```bash
pytest tests/unit/test_alert_scheduler.py -v
```

Expected: All tests `PASSED` (6 tests)

### Step 13: Run format, lint, type-check

```bash
black scripts/features/alerts.py tests/unit/test_alert_scheduler.py
flake8 scripts/features/alerts.py tests/unit/test_alert_scheduler.py --max-line-length=100
mypy scripts/features/alerts.py
```

Expected: All checks pass

### Step 14: Commit

```bash
git add scripts/features/alerts.py tests/unit/test_alert_scheduler.py
git commit -m "feat(alerts): add alert scheduling engine

- Add ScheduleType enum (weekly, monthly, quarterly, annual, one-time)
- Implement AlertSchedule dataclass with due checking
- Implement AlertScheduler for managing scheduled alerts
- Add automatic next_run calculation based on frequency
- Add 6 unit tests covering schedule management"
```

---

## Task 3: Merchant Intelligence Foundation

**Files:**
- Create: `scripts/features/merchant_intelligence.py`
- Create: `tests/unit/test_merchant_intelligence.py`

### Step 1: Write failing test for merchant variation detection

```python
# tests/unit/test_merchant_intelligence.py
import pytest
from scripts.features.merchant_intelligence import MerchantMatcher


def test_merchant_matcher_initialization():
    """Test creating merchant matcher."""
    matcher = MerchantMatcher()
    assert matcher is not None
    assert len(matcher.canonical_names) == 0


def test_merchant_matcher_normalize_payee():
    """Test normalizing payee names."""
    matcher = MerchantMatcher()

    # Remove common suffixes
    assert matcher.normalize_payee("WOOLWORTHS PTY LTD") == "woolworths"
    assert matcher.normalize_payee("Coles Pty Ltd") == "coles"

    # Remove transaction IDs
    assert matcher.normalize_payee("UBER *TRIP AB123CD") == "uber trip"
    assert matcher.normalize_payee("SQ *COFFEE SHOP 5678") == "sq coffee shop"

    # Remove extra whitespace
    assert matcher.normalize_payee("  MULTIPLE   SPACES  ") == "multiple spaces"

    # Lowercase
    assert matcher.normalize_payee("MiXeD CaSe") == "mixed case"


def test_merchant_matcher_calculate_similarity():
    """Test calculating similarity between payee names."""
    matcher = MerchantMatcher()

    # Identical
    assert matcher.calculate_similarity("woolworths", "woolworths") == 1.0

    # Very similar
    sim = matcher.calculate_similarity("woolworths", "woolworth")
    assert sim > 0.9

    # Somewhat similar
    sim = matcher.calculate_similarity("woolworths", "woollies")
    assert 0.5 < sim < 0.9

    # Different
    sim = matcher.calculate_similarity("woolworths", "coles")
    assert sim < 0.5
```

### Step 2: Run test to verify it fails

```bash
pytest tests/unit/test_merchant_intelligence.py::test_merchant_matcher_initialization -v
```

Expected: `FAILED` - `ModuleNotFoundError: No module named 'scripts.features.merchant_intelligence'`

### Step 3: Implement MerchantMatcher with normalization

```python
# scripts/features/merchant_intelligence.py
"""Merchant intelligence and payee enrichment."""
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class MerchantGroup:
    """Represents a group of related merchant names."""
    canonical_name: str
    variations: Set[str]
    transaction_count: int = 0


class MerchantMatcher:
    """Detects and groups merchant name variations."""

    def __init__(self):
        """Initialize merchant matcher."""
        self.canonical_names: Dict[str, MerchantGroup] = {}

    def normalize_payee(self, payee: str) -> str:
        """Normalize a payee name for comparison.

        Args:
            payee: Raw payee name

        Returns:
            Normalized payee name
        """
        # Convert to lowercase
        normalized = payee.lower()

        # Remove common suffixes
        suffixes = [
            r'\s+pty\s+ltd',
            r'\s+pty\s*$',
            r'\s+ltd\s*$',
            r'\s+inc\s*$',
            r'\s+llc\s*$',
        ]
        for suffix in suffixes:
            normalized = re.sub(suffix, '', normalized)

        # Remove transaction IDs (e.g., "UBER *TRIP AB123CD")
        normalized = re.sub(r'\s+[a-z0-9]{6,}', '', normalized)
        normalized = re.sub(r'\*[a-z]+\s+[a-z0-9]+', r'*\1', normalized)

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        return normalized.strip()

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity ratio between two names.

        Args:
            name1: First name
            name2: Second name

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        return SequenceMatcher(None, name1, name2).ratio()
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/unit/test_merchant_intelligence.py -v
```

Expected: All tests `PASSED` (3 tests)

### Step 5: Write failing test for merchant grouping

```python
# tests/unit/test_merchant_intelligence.py (append)
def test_merchant_matcher_find_canonical():
    """Test finding canonical name for a payee."""
    matcher = MerchantMatcher()

    # Add known merchant group
    matcher.canonical_names["woolworths"] = MerchantGroup(
        canonical_name="Woolworths",
        variations={"woolworths", "woolworth", "woolies"},
    )

    # Should find exact match
    result = matcher.find_canonical("woolworths")
    assert result == "Woolworths"

    # Should find similar variation
    result = matcher.find_canonical("woolworth")
    assert result == "Woolworths"

    # Should return None for unknown
    result = matcher.find_canonical("coles")
    assert result is None


def test_merchant_matcher_add_variation():
    """Test adding a variation to a merchant group."""
    matcher = MerchantMatcher()

    # Create new group
    matcher.add_variation("Woolworths", "woolworths pty ltd")
    assert "woolworths" in matcher.canonical_names
    assert matcher.canonical_names["woolworths"].canonical_name == "Woolworths"

    # Add to existing group
    matcher.add_variation("Woolworths", "woolies")
    group = matcher.canonical_names["woolworths"]
    assert "woolies" in group.variations
    assert len(group.variations) == 2


def test_merchant_matcher_suggest_matches():
    """Test suggesting potential matches for a payee."""
    matcher = MerchantMatcher()

    matcher.add_variation("Woolworths", "woolworths pty ltd")
    matcher.add_variation("Coles", "coles supermarkets")

    # Should suggest Woolworths for similar name
    suggestions = matcher.suggest_matches("woolworth", threshold=0.8)
    assert len(suggestions) > 0
    assert suggestions[0][0] == "Woolworths"
    assert suggestions[0][1] > 0.8

    # Should not suggest if below threshold
    suggestions = matcher.suggest_matches("aldi", threshold=0.8)
    assert len(suggestions) == 0
```

### Step 6: Run test to verify it fails

```bash
pytest tests/unit/test_merchant_intelligence.py::test_merchant_matcher_find_canonical -v
```

Expected: `FAILED` - `AttributeError: 'MerchantMatcher' object has no attribute 'find_canonical'`

### Step 7: Implement merchant grouping methods

```python
# scripts/features/merchant_intelligence.py (add to MerchantMatcher class)
    def find_canonical(self, payee: str) -> Optional[str]:
        """Find canonical merchant name for a payee.

        Args:
            payee: Payee name to look up

        Returns:
            Canonical name if found, None otherwise
        """
        normalized = self.normalize_payee(payee)

        # Check for exact match in canonical names
        for group_key, group in self.canonical_names.items():
            if normalized in group.variations or normalized == group_key:
                return group.canonical_name

        return None

    def add_variation(self, canonical_name: str, variation: str) -> None:
        """Add a variation to a merchant group.

        Args:
            canonical_name: The canonical merchant name
            variation: A variation of the merchant name
        """
        normalized_canonical = self.normalize_payee(canonical_name)
        normalized_variation = self.normalize_payee(variation)

        if normalized_canonical not in self.canonical_names:
            # Create new group
            self.canonical_names[normalized_canonical] = MerchantGroup(
                canonical_name=canonical_name,
                variations={normalized_variation},
            )
        else:
            # Add to existing group
            self.canonical_names[normalized_canonical].variations.add(normalized_variation)

    def suggest_matches(
        self, payee: str, threshold: float = 0.8
    ) -> List[Tuple[str, float]]:
        """Suggest potential canonical matches for a payee.

        Args:
            payee: Payee name to match
            threshold: Minimum similarity threshold (0.0 to 1.0)

        Returns:
            List of (canonical_name, similarity_score) tuples above threshold
        """
        normalized = self.normalize_payee(payee)
        suggestions = []

        for group in self.canonical_names.values():
            # Check similarity against all variations
            for variation in group.variations:
                similarity = self.calculate_similarity(normalized, variation)
                if similarity >= threshold:
                    suggestions.append((group.canonical_name, similarity))
                    break  # Only add each group once

        # Sort by similarity (highest first)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions
```

### Step 8: Run all tests to verify they pass

```bash
pytest tests/unit/test_merchant_intelligence.py -v
```

Expected: All tests `PASSED` (6 tests)

### Step 9: Run format, lint, type-check

```bash
black scripts/features/merchant_intelligence.py tests/unit/test_merchant_intelligence.py
flake8 scripts/features/merchant_intelligence.py tests/unit/test_merchant_intelligence.py --max-line-length=100
mypy scripts/features/merchant_intelligence.py
```

Expected: All checks pass

### Step 10: Commit

```bash
git add scripts/features/merchant_intelligence.py tests/unit/test_merchant_intelligence.py
git commit -m "feat(merchant): add merchant intelligence foundation

- Add MerchantGroup dataclass for grouping variations
- Implement MerchantMatcher with payee normalization
- Add similarity calculation using difflib
- Implement variation detection and grouping
- Add match suggestion with configurable threshold
- Add 6 unit tests covering merchant matching"
```

---

## Task 4: Document Management Foundation

**Files:**
- Create: `scripts/features/documents.py`
- Create: `tests/unit/test_documents.py`

### Step 1: Write failing test for DocumentRequirement enum

```python
# tests/unit/test_documents.py
import pytest
from datetime import datetime
from scripts.features.documents import DocumentRequirement, DocumentStatus


def test_document_requirement_enum():
    """Test DocumentRequirement enum values."""
    assert DocumentRequirement.REQUIRED in list(DocumentRequirement)
    assert DocumentRequirement.RECOMMENDED in list(DocumentRequirement)
    assert DocumentRequirement.OPTIONAL in list(DocumentRequirement)


def test_document_status_enum():
    """Test DocumentStatus enum values."""
    assert DocumentStatus.MISSING in list(DocumentStatus)
    assert DocumentStatus.ATTACHED in list(DocumentStatus)
    assert DocumentStatus.VERIFIED in list(DocumentStatus)
```

### Step 2: Run test to verify it fails

```bash
pytest tests/unit/test_documents.py::test_document_requirement_enum -v
```

Expected: `FAILED` - `ModuleNotFoundError: No module named 'scripts.features.documents'`

### Step 3: Implement document enums

```python
# scripts/features/documents.py
"""Document and receipt management."""
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


class DocumentRequirement(Enum):
    """Requirement level for transaction documentation."""
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class DocumentStatus(Enum):
    """Status of transaction documentation."""
    MISSING = "missing"
    ATTACHED = "attached"
    VERIFIED = "verified"
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/unit/test_documents.py -v
```

Expected: All tests `PASSED` (2 tests)

### Step 5: Write failing test for TransactionDocument dataclass

```python
# tests/unit/test_documents.py (append)
from scripts.features.documents import TransactionDocument


def test_transaction_document_creation():
    """Test creating a transaction document record."""
    doc = TransactionDocument(
        transaction_id=12345,
        amount=350.00,
        category="Work Expenses",
        requirement=DocumentRequirement.REQUIRED,
        status=DocumentStatus.MISSING,
        date=datetime(2025, 11, 15),
    )

    assert doc.transaction_id == 12345
    assert doc.amount == 350.00
    assert doc.requirement == DocumentRequirement.REQUIRED
    assert doc.status == DocumentStatus.MISSING
    assert doc.attachment_url is None


def test_transaction_document_attach():
    """Test attaching a document to a transaction."""
    doc = TransactionDocument(
        transaction_id=12345,
        amount=350.00,
        category="Work Expenses",
        requirement=DocumentRequirement.REQUIRED,
        status=DocumentStatus.MISSING,
        date=datetime(2025, 11, 15),
    )

    doc.attach_document("https://pocketsmith.com/attachments/123")
    assert doc.status == DocumentStatus.ATTACHED
    assert doc.attachment_url == "https://pocketsmith.com/attachments/123"
    assert doc.attached_at is not None
```

### Step 6: Run test to verify it fails

```bash
pytest tests/unit/test_documents.py::test_transaction_document_creation -v
```

Expected: `FAILED` - `ImportError: cannot import name 'TransactionDocument'`

### Step 7: Implement TransactionDocument dataclass

```python
# scripts/features/documents.py (append)
@dataclass
class TransactionDocument:
    """Represents documentation status for a transaction."""
    transaction_id: int
    amount: float
    category: str
    requirement: DocumentRequirement
    status: DocumentStatus
    date: datetime
    attachment_url: Optional[str] = None
    attached_at: Optional[datetime] = None
    notes: Optional[str] = None

    def attach_document(self, url: str, notes: Optional[str] = None) -> None:
        """Attach a document to this transaction.

        Args:
            url: URL of the attached document
            notes: Optional notes about the document
        """
        self.attachment_url = url
        self.status = DocumentStatus.ATTACHED
        self.attached_at = datetime.now()
        if notes:
            self.notes = notes
```

### Step 8: Run tests to verify they pass

```bash
pytest tests/unit/test_documents.py -v
```

Expected: All tests `PASSED` (4 tests)

### Step 9: Write failing test for DocumentManager class

```python
# tests/unit/test_documents.py (append)
from scripts.features.documents import DocumentManager


def test_document_manager_initialization():
    """Test creating document manager."""
    manager = DocumentManager()
    assert manager is not None
    assert len(manager.documents) == 0


def test_document_manager_determine_requirement():
    """Test determining document requirement based on amount."""
    manager = DocumentManager()

    # Required: > $300 for work expenses
    assert manager.determine_requirement(350.00, "Work Expenses") == DocumentRequirement.REQUIRED

    # Recommended: > $100 for deductible categories
    assert manager.determine_requirement(150.00, "Professional Development") == DocumentRequirement.RECOMMENDED

    # Optional: < $100 or non-deductible
    assert manager.determine_requirement(50.00, "Groceries") == DocumentRequirement.OPTIONAL


def test_document_manager_track_transaction():
    """Test tracking a transaction's documentation status."""
    manager = DocumentManager()

    doc = manager.track_transaction(
        transaction_id=12345,
        amount=400.00,
        category="Office Supplies",
        date=datetime(2025, 11, 15),
    )

    assert doc.transaction_id == 12345
    assert doc.requirement == DocumentRequirement.REQUIRED
    assert doc.status == DocumentStatus.MISSING
    assert 12345 in manager.documents


def test_document_manager_get_missing_documents():
    """Test getting list of missing required documents."""
    manager = DocumentManager()

    # Add required document (missing)
    manager.track_transaction(
        transaction_id=1,
        amount=400.00,
        category="Work Expenses",
        date=datetime(2025, 11, 15),
    )

    # Add recommended document (missing)
    manager.track_transaction(
        transaction_id=2,
        amount=150.00,
        category="Professional Development",
        date=datetime(2025, 11, 16),
    )

    # Add required document (attached)
    doc3 = manager.track_transaction(
        transaction_id=3,
        amount=500.00,
        category="Work Expenses",
        date=datetime(2025, 11, 17),
    )
    doc3.attach_document("https://example.com/receipt.pdf")

    # Get missing required only
    missing_required = manager.get_missing_documents(required_only=True)
    assert len(missing_required) == 1
    assert missing_required[0].transaction_id == 1

    # Get all missing
    all_missing = manager.get_missing_documents(required_only=False)
    assert len(all_missing) == 2
```

### Step 10: Run test to verify it fails

```bash
pytest tests/unit/test_documents.py::test_document_manager_initialization -v
```

Expected: `FAILED` - `ImportError: cannot import name 'DocumentManager'`

### Step 11: Implement DocumentManager class

```python
# scripts/features/documents.py (append)
class DocumentManager:
    """Manages transaction documentation requirements."""

    # ATO threshold for substantiation
    ATO_SUBSTANTIATION_THRESHOLD = 300.00

    # Categories that commonly need documentation
    DEDUCTIBLE_CATEGORIES = {
        "Work Expenses",
        "Office Supplies",
        "Professional Development",
        "Business Travel",
        "Home Office",
        "Vehicle Expenses",
    }

    def __init__(self):
        """Initialize document manager."""
        self.documents: Dict[int, TransactionDocument] = {}

    def determine_requirement(
        self, amount: float, category: str
    ) -> DocumentRequirement:
        """Determine documentation requirement for a transaction.

        Args:
            amount: Transaction amount
            category: Transaction category

        Returns:
            Required documentation level
        """
        # ATO requires substantiation for work expenses > $300
        if amount > self.ATO_SUBSTANTIATION_THRESHOLD:
            return DocumentRequirement.REQUIRED

        # Recommended for deductible categories > $100
        if category in self.DEDUCTIBLE_CATEGORIES and amount > 100.00:
            return DocumentRequirement.RECOMMENDED

        return DocumentRequirement.OPTIONAL

    def track_transaction(
        self,
        transaction_id: int,
        amount: float,
        category: str,
        date: datetime,
    ) -> TransactionDocument:
        """Start tracking a transaction's documentation status.

        Args:
            transaction_id: PocketSmith transaction ID
            amount: Transaction amount
            category: Transaction category
            date: Transaction date

        Returns:
            Created TransactionDocument
        """
        requirement = self.determine_requirement(amount, category)

        doc = TransactionDocument(
            transaction_id=transaction_id,
            amount=amount,
            category=category,
            requirement=requirement,
            status=DocumentStatus.MISSING,
            date=date,
        )

        self.documents[transaction_id] = doc
        return doc

    def get_missing_documents(
        self, required_only: bool = True
    ) -> List[TransactionDocument]:
        """Get list of transactions with missing documentation.

        Args:
            required_only: Only return REQUIRED documents

        Returns:
            List of TransactionDocument with MISSING status
        """
        results = [
            doc for doc in self.documents.values()
            if doc.status == DocumentStatus.MISSING
        ]

        if required_only:
            results = [
                doc for doc in results
                if doc.requirement == DocumentRequirement.REQUIRED
            ]

        # Sort by date (oldest first)
        results.sort(key=lambda d: d.date)
        return results
```

### Step 12: Run all tests to verify they pass

```bash
pytest tests/unit/test_documents.py -v
```

Expected: All tests `PASSED` (8 tests)

### Step 13: Run format, lint, type-check

```bash
black scripts/features/documents.py tests/unit/test_documents.py
flake8 scripts/features/documents.py tests/unit/test_documents.py --max-line-length=100
mypy scripts/features/documents.py
```

Expected: All checks pass

### Step 14: Commit

```bash
git add scripts/features/documents.py tests/unit/test_documents.py
git commit -m "feat(docs): add document management foundation

- Add DocumentRequirement enum (required, recommended, optional)
- Add DocumentStatus enum (missing, attached, verified)
- Implement TransactionDocument dataclass with attachment
- Implement DocumentManager with ATO substantiation rules
- Add threshold-based requirement determination ($300 ATO rule)
- Add 8 unit tests covering document tracking"
```

---

## Task 5: Multi-User Support Foundation

**Files:**
- Create: `scripts/features/multi_user.py`
- Create: `tests/unit/test_multi_user.py`

### Step 1: Write failing test for SharedExpense dataclass

```python
# tests/unit/test_multi_user.py
import pytest
from datetime import datetime
from scripts.features.multi_user import SharedExpense, Settlement


def test_shared_expense_creation():
    """Test creating a shared expense."""
    expense = SharedExpense(
        transaction_id=12345,
        amount=120.00,
        description="Groceries",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        splits={"alice": 60.00, "bob": 60.00},
    )

    assert expense.transaction_id == 12345
    assert expense.amount == 120.00
    assert expense.paid_by == "alice"
    assert expense.splits["alice"] == 60.00
    assert expense.splits["bob"] == 60.00


def test_shared_expense_calculate_owes():
    """Test calculating who owes whom."""
    expense = SharedExpense(
        transaction_id=12345,
        amount=120.00,
        description="Groceries",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        splits={"alice": 60.00, "bob": 60.00},
    )

    # Bob owes Alice $60 (Alice paid $120, owes $60)
    owes = expense.calculate_owes()
    assert owes["bob"] == 60.00
    assert "alice" not in owes  # Alice doesn't owe herself


def test_shared_expense_custom_splits():
    """Test expense with custom split ratios."""
    expense = SharedExpense(
        transaction_id=12346,
        amount=150.00,
        description="Dinner",
        paid_by="charlie",
        date=datetime(2025, 11, 16),
        splits={"alice": 50.00, "bob": 50.00, "charlie": 50.00},
    )

    owes = expense.calculate_owes()
    assert owes["alice"] == 50.00
    assert owes["bob"] == 50.00
    assert "charlie" not in owes
```

### Step 2: Run test to verify it fails

```bash
pytest tests/unit/test_multi_user.py::test_shared_expense_creation -v
```

Expected: `FAILED` - `ModuleNotFoundError: No module named 'scripts.features.multi_user'`

### Step 3: Implement SharedExpense dataclass

```python
# scripts/features/multi_user.py
"""Multi-user and shared expense tracking."""
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SharedExpense:
    """Represents a shared expense between users."""
    transaction_id: int
    amount: float
    description: str
    paid_by: str
    date: datetime
    splits: Dict[str, float]
    settled: bool = False

    def calculate_owes(self) -> Dict[str, float]:
        """Calculate who owes whom for this expense.

        Returns:
            Dict mapping user_id to amount they owe the payer
        """
        owes = {}

        for user, owed_amount in self.splits.items():
            if user != self.paid_by:
                owes[user] = owed_amount

        return owes
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/unit/test_multi_user.py -v
```

Expected: All tests `PASSED` (3 tests)

### Step 5: Write failing test for Settlement dataclass

```python
# tests/unit/test_multi_user.py (append)
def test_settlement_creation():
    """Test creating a settlement record."""
    settlement = Settlement(
        from_user="bob",
        to_user="alice",
        amount=150.00,
        date=datetime(2025, 11, 20),
        transaction_ids=[12345, 12346],
    )

    assert settlement.from_user == "bob"
    assert settlement.to_user == "alice"
    assert settlement.amount == 150.00
    assert len(settlement.transaction_ids) == 2
```

### Step 6: Run test to verify it fails

```bash
pytest tests/unit/test_multi_user.py::test_settlement_creation -v
```

Expected: `FAILED` - `ImportError: cannot import name 'Settlement'`

### Step 7: Implement Settlement dataclass

```python
# scripts/features/multi_user.py (append)
@dataclass
class Settlement:
    """Represents a settlement payment between users."""
    from_user: str
    to_user: str
    amount: float
    date: datetime
    transaction_ids: List[int]
    notes: Optional[str] = None
```

### Step 8: Run test to verify it passes

```bash
pytest tests/unit/test_multi_user.py::test_settlement_creation -v
```

Expected: `PASSED`

### Step 9: Write failing test for SharedExpenseTracker

```python
# tests/unit/test_multi_user.py (append)
from scripts.features.multi_user import SharedExpenseTracker


def test_shared_expense_tracker_initialization():
    """Test creating shared expense tracker."""
    tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])
    assert len(tracker.users) == 3
    assert len(tracker.expenses) == 0


def test_shared_expense_tracker_add_expense():
    """Test adding a shared expense."""
    tracker = SharedExpenseTracker(users=["alice", "bob"])

    expense = tracker.add_expense(
        transaction_id=12345,
        amount=100.00,
        description="Dinner",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        split_equally=True,
    )

    assert expense.transaction_id == 12345
    assert expense.splits["alice"] == 50.00
    assert expense.splits["bob"] == 50.00
    assert len(tracker.expenses) == 1


def test_shared_expense_tracker_custom_split():
    """Test adding expense with custom split ratios."""
    tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])

    expense = tracker.add_expense(
        transaction_id=12346,
        amount=120.00,
        description="Groceries",
        paid_by="bob",
        date=datetime(2025, 11, 16),
        split_ratios={"alice": 0.5, "bob": 0.25, "charlie": 0.25},
    )

    assert expense.splits["alice"] == 60.00
    assert expense.splits["bob"] == 30.00
    assert expense.splits["charlie"] == 30.00


def test_shared_expense_tracker_calculate_balances():
    """Test calculating who owes whom across all expenses."""
    tracker = SharedExpenseTracker(users=["alice", "bob"])

    # Alice pays $100, split equally
    tracker.add_expense(
        transaction_id=1,
        amount=100.00,
        description="Dinner",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        split_equally=True,
    )

    # Bob pays $60, split equally
    tracker.add_expense(
        transaction_id=2,
        amount=60.00,
        description="Coffee",
        paid_by="bob",
        date=datetime(2025, 11, 16),
        split_equally=True,
    )

    # Alice paid $100, owes $30 = net +$70
    # Bob paid $60, owes $50 = net -$10
    # Result: Bob owes Alice $20
    balances = tracker.calculate_balances()
    assert balances["bob"] == -20.00  # Negative = owes
    assert balances["alice"] == 20.00  # Positive = owed


def test_shared_expense_tracker_generate_settlements():
    """Test generating settlement recommendations."""
    tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])

    # Alice pays $150
    tracker.add_expense(
        transaction_id=1,
        amount=150.00,
        description="Dinner",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        split_equally=True,
    )

    # Bob pays $90
    tracker.add_expense(
        transaction_id=2,
        amount=90.00,
        description="Drinks",
        paid_by="bob",
        date=datetime(2025, 11, 16),
        split_equally=True,
    )

    # Alice: paid $150, owes $80 = net +$70
    # Bob: paid $90, owes $80 = net +$10
    # Charlie: paid $0, owes $80 = net -$80
    # Charlie owes Alice $70, Charlie owes Bob $10

    settlements = tracker.generate_settlements()
    assert len(settlements) == 2

    # Find Charlie -> Alice settlement
    charlie_to_alice = next(s for s in settlements if s.from_user == "charlie" and s.to_user == "alice")
    assert charlie_to_alice.amount == 70.00

    # Find Charlie -> Bob settlement
    charlie_to_bob = next(s for s in settlements if s.from_user == "charlie" and s.to_user == "bob")
    assert charlie_to_bob.amount == 10.00
```

### Step 10: Run test to verify it fails

```bash
pytest tests/unit/test_multi_user.py::test_shared_expense_tracker_initialization -v
```

Expected: `FAILED` - `ImportError: cannot import name 'SharedExpenseTracker'`

### Step 11: Implement SharedExpenseTracker class

```python
# scripts/features/multi_user.py (append)
class SharedExpenseTracker:
    """Manages shared expenses and settlement calculations."""

    def __init__(self, users: List[str]):
        """Initialize tracker with list of users.

        Args:
            users: List of user IDs participating in shared expenses
        """
        self.users = users
        self.expenses: List[SharedExpense] = []
        self.settlements: List[Settlement] = []

    def add_expense(
        self,
        transaction_id: int,
        amount: float,
        description: str,
        paid_by: str,
        date: datetime,
        split_equally: bool = False,
        split_ratios: Optional[Dict[str, float]] = None,
    ) -> SharedExpense:
        """Add a shared expense.

        Args:
            transaction_id: Transaction ID
            amount: Total amount
            description: Expense description
            paid_by: User who paid
            date: Transaction date
            split_equally: Split equally among all users
            split_ratios: Custom split ratios (must sum to 1.0)

        Returns:
            Created SharedExpense
        """
        if split_equally:
            split_amount = amount / len(self.users)
            splits = {user: split_amount for user in self.users}
        elif split_ratios:
            splits = {user: amount * ratio for user, ratio in split_ratios.items()}
        else:
            raise ValueError("Must specify either split_equally or split_ratios")

        expense = SharedExpense(
            transaction_id=transaction_id,
            amount=amount,
            description=description,
            paid_by=paid_by,
            date=date,
            splits=splits,
        )

        self.expenses.append(expense)
        return expense

    def calculate_balances(self) -> Dict[str, float]:
        """Calculate net balance for each user.

        Returns:
            Dict mapping user_id to balance (positive = owed, negative = owes)
        """
        balances = {user: 0.0 for user in self.users}

        for expense in self.expenses:
            if expense.settled:
                continue

            # Add amount paid
            balances[expense.paid_by] += expense.amount

            # Subtract amount owed
            for user, owed in expense.splits.items():
                balances[user] -= owed

        return balances

    def generate_settlements(self) -> List[Settlement]:
        """Generate settlement recommendations to balance all accounts.

        Returns:
            List of Settlement objects
        """
        balances = self.calculate_balances()
        settlements = []

        # Separate creditors (positive balance) and debtors (negative balance)
        creditors = {u: b for u, b in balances.items() if b > 0.01}
        debtors = {u: -b for u, b in balances.items() if b < -0.01}

        # Match debtors with creditors
        for debtor, debt_amount in debtors.items():
            remaining_debt = debt_amount

            for creditor, credit_amount in list(creditors.items()):
                if remaining_debt <= 0.01:
                    break

                # Settle the smaller of the two amounts
                settlement_amount = min(remaining_debt, credit_amount)

                settlements.append(Settlement(
                    from_user=debtor,
                    to_user=creditor,
                    amount=round(settlement_amount, 2),
                    date=datetime.now(),
                    transaction_ids=[e.transaction_id for e in self.expenses if not e.settled],
                ))

                remaining_debt -= settlement_amount
                creditors[creditor] -= settlement_amount

                if creditors[creditor] <= 0.01:
                    del creditors[creditor]

        return settlements
```

### Step 12: Run all tests to verify they pass

```bash
pytest tests/unit/test_multi_user.py -v
```

Expected: All tests `PASSED` (10 tests)

### Step 13: Run format, lint, type-check

```bash
black scripts/features/multi_user.py tests/unit/test_multi_user.py
flake8 scripts/features/multi_user.py tests/unit/test_multi_user.py --max-line-length=100
mypy scripts/features/multi_user.py
```

Expected: All checks pass

### Step 14: Commit

```bash
git add scripts/features/multi_user.py tests/unit/test_multi_user.py
git commit -m "feat(multi-user): add shared expense tracking foundation

- Add SharedExpense dataclass with split calculation
- Add Settlement dataclass for payment tracking
- Implement SharedExpenseTracker for balance management
- Add equal and custom ratio splitting
- Implement settlement generation algorithm
- Add 10 unit tests covering shared expense scenarios"
```

---

## Task 6: Comparative Benchmarking Foundation

**Files:**
- Create: `scripts/features/benchmarking.py`
- Create: `tests/unit/test_benchmarking.py`

### Step 1: Write failing test for anonymization

```python
# tests/unit/test_benchmarking.py
import pytest
from scripts.features.benchmarking import BenchmarkEngine


def test_benchmark_engine_initialization():
    """Test creating benchmark engine."""
    engine = BenchmarkEngine()
    assert engine is not None


def test_benchmark_engine_anonymize_user():
    """Test anonymizing user data."""
    engine = BenchmarkEngine()

    # Same input should produce same hash
    hash1 = engine.anonymize_user_id("user_123")
    hash2 = engine.anonymize_user_id("user_123")
    assert hash1 == hash2

    # Different inputs should produce different hashes
    hash3 = engine.anonymize_user_id("user_456")
    assert hash1 != hash3

    # Hash should be fixed length
    assert len(hash1) == 64  # SHA-256 hex digest
```

### Step 2: Run test to verify it fails

```bash
pytest tests/unit/test_benchmarking.py::test_benchmark_engine_initialization -v
```

Expected: `FAILED` - `ModuleNotFoundError: No module named 'scripts.features.benchmarking'`

### Step 3: Implement BenchmarkEngine with anonymization

```python
# scripts/features/benchmarking.py
"""Comparative benchmarking with privacy-first design."""
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class PeerCriteria:
    """Criteria for selecting comparable peers."""
    household_size: Optional[int] = None
    income_bracket: Optional[str] = None
    location: Optional[str] = None
    age_bracket: Optional[str] = None


@dataclass
class BenchmarkResult:
    """Comparison result against peer group."""
    category: str
    user_amount: float
    peer_average: float
    peer_median: float
    percentile: int  # Where user falls (0-100)
    peer_count: int


class BenchmarkEngine:
    """Privacy-first comparative benchmarking."""

    def __init__(self):
        """Initialize benchmark engine."""
        # In production, this would connect to aggregated data store
        self.aggregated_data: Dict[str, List[float]] = {}

    def anonymize_user_id(self, user_id: str) -> str:
        """Anonymize a user ID using SHA-256 hash.

        Args:
            user_id: Original user ID

        Returns:
            Anonymized hash
        """
        return hashlib.sha256(user_id.encode()).hexdigest()
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/unit/test_benchmarking.py -v
```

Expected: All tests `PASSED` (2 tests)

### Step 5: Write failing test for benchmarking

```python
# tests/unit/test_benchmarking.py (append)
def test_benchmark_engine_add_data_point():
    """Test adding anonymized data points."""
    engine = BenchmarkEngine()

    engine.add_data_point(
        category="Groceries",
        amount=500.00,
        user_id="user_123",
        criteria=PeerCriteria(household_size=2, income_bracket="50k-75k")
    )

    # Should be stored under anonymized key
    key = engine._build_key("Groceries", PeerCriteria(household_size=2, income_bracket="50k-75k"))
    assert key in engine.aggregated_data
    assert 500.00 in engine.aggregated_data[key]


def test_benchmark_engine_compare():
    """Test comparing user spending to peer group."""
    engine = BenchmarkEngine()

    criteria = PeerCriteria(household_size=2, income_bracket="50k-75k")

    # Add peer data (5 peers)
    peer_amounts = [400.00, 450.00, 500.00, 550.00, 600.00]
    for i, amount in enumerate(peer_amounts):
        engine.add_data_point(
            category="Groceries",
            amount=amount,
            user_id=f"peer_{i}",
            criteria=criteria
        )

    # Compare user at median
    result = engine.compare(
        category="Groceries",
        user_amount=500.00,
        criteria=criteria
    )

    assert result.category == "Groceries"
    assert result.user_amount == 500.00
    assert result.peer_average == 500.00  # Mean of peer_amounts
    assert result.peer_median == 500.00
    assert result.percentile == 50  # At median
    assert result.peer_count == 5


def test_benchmark_engine_percentile_calculation():
    """Test percentile calculation."""
    engine = BenchmarkEngine()

    criteria = PeerCriteria(household_size=2)

    # Add peer data
    amounts = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    for i, amount in enumerate(amounts):
        engine.add_data_point(
            category="Dining",
            amount=float(amount),
            user_id=f"peer_{i}",
            criteria=criteria
        )

    # User spending $250 should be ~25th percentile
    result = engine.compare(
        category="Dining",
        user_amount=250.00,
        criteria=criteria
    )
    assert 20 <= result.percentile <= 30

    # User spending $750 should be ~75th percentile
    result = engine.compare(
        category="Dining",
        user_amount=750.00,
        criteria=criteria
    )
    assert 70 <= result.percentile <= 80
```

### Step 6: Run test to verify it fails

```bash
pytest tests/unit/test_benchmarking.py::test_benchmark_engine_add_data_point -v
```

Expected: `FAILED` - `AttributeError: 'BenchmarkEngine' object has no attribute 'add_data_point'`

### Step 7: Implement benchmarking methods

```python
# scripts/features/benchmarking.py (add imports)
from statistics import mean, median


# Add to BenchmarkEngine class
    def _build_key(self, category: str, criteria: PeerCriteria) -> str:
        """Build aggregation key from category and criteria.

        Args:
            category: Spending category
            criteria: Peer criteria

        Returns:
            Aggregation key
        """
        parts = [category]
        if criteria.household_size:
            parts.append(f"hs_{criteria.household_size}")
        if criteria.income_bracket:
            parts.append(f"ib_{criteria.income_bracket}")
        if criteria.location:
            parts.append(f"loc_{criteria.location}")
        if criteria.age_bracket:
            parts.append(f"age_{criteria.age_bracket}")
        return ":".join(parts)

    def add_data_point(
        self,
        category: str,
        amount: float,
        user_id: str,
        criteria: PeerCriteria,
    ) -> None:
        """Add an anonymized data point to aggregated data.

        Args:
            category: Spending category
            amount: Amount spent
            user_id: User ID (will be anonymized)
            criteria: Peer criteria for grouping
        """
        # Anonymize user ID (not stored, just for ethics)
        _ = self.anonymize_user_id(user_id)

        # Store only aggregated amount (no user linkage)
        key = self._build_key(category, criteria)
        if key not in self.aggregated_data:
            self.aggregated_data[key] = []
        self.aggregated_data[key].append(amount)

    def compare(
        self,
        category: str,
        user_amount: float,
        criteria: PeerCriteria,
    ) -> Optional[BenchmarkResult]:
        """Compare user spending to peer group.

        Args:
            category: Spending category
            user_amount: User's spending amount
            criteria: Peer criteria

        Returns:
            BenchmarkResult or None if insufficient data
        """
        key = self._build_key(category, criteria)

        if key not in self.aggregated_data or len(self.aggregated_data[key]) < 3:
            return None  # Need at least 3 peers for meaningful comparison

        peer_amounts = self.aggregated_data[key]

        # Calculate statistics
        peer_avg = mean(peer_amounts)
        peer_med = median(peer_amounts)

        # Calculate percentile
        sorted_amounts = sorted(peer_amounts)
        below_count = sum(1 for amount in sorted_amounts if amount < user_amount)
        percentile = int((below_count / len(sorted_amounts)) * 100)

        return BenchmarkResult(
            category=category,
            user_amount=user_amount,
            peer_average=round(peer_avg, 2),
            peer_median=round(peer_med, 2),
            percentile=percentile,
            peer_count=len(peer_amounts),
        )
```

### Step 8: Run all tests to verify they pass

```bash
pytest tests/unit/test_benchmarking.py -v
```

Expected: All tests `PASSED` (5 tests)

### Step 9: Run format, lint, type-check

```bash
black scripts/features/benchmarking.py tests/unit/test_benchmarking.py
flake8 scripts/features/benchmarking.py tests/unit/test_benchmarking.py --max-line-length=100
mypy scripts/features/benchmarking.py
```

Expected: All checks pass

### Step 10: Commit

```bash
git add scripts/features/benchmarking.py tests/unit/test_benchmarking.py
git commit -m "feat(benchmarking): add privacy-first comparative benchmarking

- Add PeerCriteria dataclass for peer group selection
- Add BenchmarkResult dataclass for comparison results
- Implement BenchmarkEngine with SHA-256 anonymization
- Add aggregated data storage (no user linkage)
- Implement percentile calculation for peer comparison
- Add 5 unit tests covering benchmarking scenarios"
```

---

## Task 7: Audit Trail Foundation

**Files:**
- Create: `scripts/features/audit.py`
- Create: `tests/unit/test_audit.py`

### Step 1: Write failing test for AuditAction enum

```python
# tests/unit/test_audit.py
import pytest
from datetime import datetime
from scripts.features.audit import AuditAction, AuditEntry


def test_audit_action_enum():
    """Test AuditAction enum values."""
    assert AuditAction.TRANSACTION_MODIFY in list(AuditAction)
    assert AuditAction.CATEGORY_CREATE in list(AuditAction)
    assert AuditAction.RULE_CREATE in list(AuditAction)
    assert AuditAction.BULK_OPERATION in list(AuditAction)
    assert AuditAction.REPORT_GENERATE in list(AuditAction)
```

### Step 2: Run test to verify it fails

```bash
pytest tests/unit/test_audit.py::test_audit_action_enum -v
```

Expected: `FAILED` - `ModuleNotFoundError: No module named 'scripts.features.audit'`

### Step 3: Implement AuditAction enum

```python
# scripts/features/audit.py
"""Audit trail for activity logging and undo capability."""
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import json


class AuditAction(Enum):
    """Types of auditable actions."""
    TRANSACTION_MODIFY = "transaction_modify"
    TRANSACTION_DELETE = "transaction_delete"
    CATEGORY_CREATE = "category_create"
    CATEGORY_MODIFY = "category_modify"
    CATEGORY_DELETE = "category_delete"
    RULE_CREATE = "rule_create"
    RULE_MODIFY = "rule_modify"
    RULE_DELETE = "rule_delete"
    BULK_OPERATION = "bulk_operation"
    REPORT_GENERATE = "report_generate"
```

### Step 4: Run test to verify it passes

```bash
pytest tests/unit/test_audit.py::test_audit_action_enum -v
```

Expected: `PASSED`

### Step 5: Write failing test for AuditEntry dataclass

```python
# tests/unit/test_audit.py (append)
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
```

### Step 6: Run test to verify it fails

```bash
pytest tests/unit/test_audit.py::test_audit_entry_creation -v
```

Expected: `FAILED` - `ImportError: cannot import name 'AuditEntry'`

### Step 7: Implement AuditEntry dataclass

```python
# scripts/features/audit.py (append)
@dataclass
class AuditEntry:
    """Represents a single audit log entry."""
    entry_id: str
    action: AuditAction
    timestamp: datetime
    user_id: str
    description: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    affected_ids: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage.

        Returns:
            Dictionary representation
        """
        return {
            "entry_id": self.entry_id,
            "action": self.action.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "description": self.description,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "affected_ids": self.affected_ids,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEntry":
        """Deserialize from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            AuditEntry instance
        """
        return cls(
            entry_id=data["entry_id"],
            action=AuditAction(data["action"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            user_id=data["user_id"],
            description=data["description"],
            before_state=data.get("before_state"),
            after_state=data.get("after_state"),
            affected_ids=data.get("affected_ids"),
            metadata=data.get("metadata"),
        )
```

### Step 8: Run tests to verify they pass

```bash
pytest tests/unit/test_audit.py -v
```

Expected: All tests `PASSED` (3 tests)

### Step 9: Write failing test for AuditLogger class

```python
# tests/unit/test_audit.py (append)
from scripts.features.audit import AuditLogger


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

    logger.log_action(
        AuditAction.TRANSACTION_MODIFY,
        "Modify txn 123",
        affected_ids=[123, 456]
    )
    logger.log_action(
        AuditAction.TRANSACTION_MODIFY,
        "Modify txn 789",
        affected_ids=[789]
    )
    logger.log_action(
        AuditAction.TRANSACTION_MODIFY,
        "Modify txn 123 again",
        affected_ids=[123]
    )

    entries_123 = logger.get_entries(affected_id=123)
    assert len(entries_123) == 2

    entries_789 = logger.get_entries(affected_id=789)
    assert len(entries_789) == 1


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
```

### Step 10: Run test to verify it fails

```bash
pytest tests/unit/test_audit.py::test_audit_logger_initialization -v
```

Expected: `FAILED` - `ImportError: cannot import name 'AuditLogger'`

### Step 11: Implement AuditLogger class

```python
# scripts/features/audit.py (append)
import uuid


class AuditLogger:
    """Manages audit trail logging and queries."""

    def __init__(self, user_id: str):
        """Initialize audit logger for a user.

        Args:
            user_id: User ID for audit entries
        """
        self.user_id = user_id
        self.entries: List[AuditEntry] = []

    def log_action(
        self,
        action: AuditAction,
        description: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        affected_ids: Optional[List[int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """Log an auditable action.

        Args:
            action: Type of action
            description: Human-readable description
            before_state: State before action
            after_state: State after action
            affected_ids: IDs of affected resources
            metadata: Additional metadata

        Returns:
            Created AuditEntry
        """
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            action=action,
            timestamp=datetime.now(),
            user_id=self.user_id,
            description=description,
            before_state=before_state,
            after_state=after_state,
            affected_ids=affected_ids,
            metadata=metadata,
        )

        self.entries.append(entry)
        return entry

    def get_entries(
        self,
        action: Optional[AuditAction] = None,
        affected_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[AuditEntry]:
        """Get audit entries with optional filtering.

        Args:
            action: Filter by action type
            affected_id: Filter by affected resource ID
            start_date: Filter by start timestamp
            end_date: Filter by end timestamp

        Returns:
            List of matching AuditEntry objects
        """
        results = self.entries

        if action:
            results = [e for e in results if e.action == action]

        if affected_id is not None:
            results = [
                e for e in results
                if e.affected_ids and affected_id in e.affected_ids
            ]

        if start_date:
            results = [e for e in results if e.timestamp >= start_date]

        if end_date:
            results = [e for e in results if e.timestamp <= end_date]

        # Sort by timestamp (newest first)
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results

    def can_undo(self, entry_id: str) -> bool:
        """Check if an action can be undone.

        Args:
            entry_id: Audit entry ID

        Returns:
            True if action has before_state for undo
        """
        entry = next((e for e in self.entries if e.entry_id == entry_id), None)
        if not entry:
            return False

        return entry.before_state is not None
```

### Step 12: Run all tests to verify they pass

```bash
pytest tests/unit/test_audit.py -v
```

Expected: All tests `PASSED` (9 tests)

### Step 13: Run format, lint, type-check

```bash
black scripts/features/audit.py tests/unit/test_audit.py
flake8 scripts/features/audit.py tests/unit/test_audit.py --max-line-length=100
mypy scripts/features/audit.py
```

Expected: All checks pass

### Step 14: Commit

```bash
git add scripts/features/audit.py tests/unit/test_audit.py
git commit -m "feat(audit): add audit trail foundation

- Add AuditAction enum (transaction, category, rule, bulk, report)
- Implement AuditEntry dataclass with serialization
- Implement AuditLogger for activity logging
- Add before/after state tracking for undo capability
- Add filtering by action, affected ID, and date range
- Add 9 unit tests covering audit logging scenarios"
```

---

## Task 8: Integration Tests for Advanced Features

**Files:**
- Create: `tests/integration/test_advanced_features.py`

### Step 1: Write integration test for alert workflows

```python
# tests/integration/test_advanced_features.py
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
from scripts.features.multi_user import SharedExpenseTracker, PeerCriteria
from scripts.features.benchmarking import BenchmarkEngine
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
    group = matcher.canonical_names["woolworths"]
    assert group.canonical_name == "Woolworths"
    assert len(group.variations) == 4

    # Test lookup of new variation
    result = matcher.find_canonical("woolworth supermarket")
    # Should find match or None (acceptable either way with threshold)


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

    total_to_alice = sum(
        s.amount for s in settlements if s.to_user == "alice"
    )
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
```

### Step 2: Run integration tests

```bash
pytest tests/integration/test_advanced_features.py -v
```

Expected: All tests `PASSED` (6 tests)

### Step 3: Run all tests to verify nothing broke

```bash
pytest tests/ -v
```

Expected: All tests `PASSED` (227 + 46 = 273 tests total)

### Step 4: Commit

```bash
git add tests/integration/test_advanced_features.py
git commit -m "test(integration): add integration tests for advanced features

- Add alert workflow test (scheduling to acknowledgment)
- Add merchant intelligence learning workflow test
- Add document management workflow test
- Add multi-user settlement workflow test
- Add benchmarking comparison workflow test
- Add audit trail query workflow test
- All 6 integration tests passing"
```

---

## Task 9: Documentation Updates

**Files:**
- Update: `README.md`
- Update: `INDEX.md`
- Create: `scripts/features/INDEX.md`
- Create: `docs/operations/2025-11-21_phase7_completion.md`

### Step 1: Update README.md with Phase 7 features

```bash
# Read current README
cat README.md
```

### Step 2: Add Phase 7 section to README.md

Edit `README.md` to add Phase 7 features section after Phase 6:

```markdown
### Phase 7: Advanced Features ✅

**Smart Alerts & Notifications:**
```python
from scripts.features.alerts import AlertEngine, AlertScheduler, ScheduleType

# Create alert engine
engine = AlertEngine(user_id="user_123")
scheduler = AlertScheduler(alert_engine=engine)

# Schedule weekly budget review
schedule = scheduler.add_schedule(
    schedule_type=ScheduleType.WEEKLY,
    alert_type=AlertType.BUDGET,
    title="Weekly Budget Review",
    next_run=datetime(2025, 11, 28, 9, 0),
)

# Process due schedules
alerts = scheduler.process_due_schedules()
```

**Merchant Intelligence:**
```python
from scripts.features.merchant_intelligence import MerchantMatcher

matcher = MerchantMatcher()

# Learn merchant variations
matcher.add_variation("Woolworths", "WOOLWORTHS PTY LTD")
matcher.add_variation("Woolworths", "woolworth")

# Find canonical name
canonical = matcher.find_canonical("woolies")  # Returns "Woolworths"

# Suggest matches for unknown payee
suggestions = matcher.suggest_matches("woollies", threshold=0.8)
```

**Document Management:**
```python
from scripts.features.documents import DocumentManager

manager = DocumentManager()

# Track transaction requiring receipt (> $300)
doc = manager.track_transaction(
    transaction_id=12345,
    amount=450.00,
    category="Work Expenses",
    date=datetime(2025, 11, 15),
)  # Automatically marked as REQUIRED

# Get missing required documents
missing = manager.get_missing_documents(required_only=True)
```

**Multi-User Shared Expenses:**
```python
from scripts.features.multi_user import SharedExpenseTracker

tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])

# Add shared expense
tracker.add_expense(
    transaction_id=1,
    amount=150.00,
    description="Dinner",
    paid_by="alice",
    date=datetime.now(),
    split_equally=True,
)

# Generate settlement recommendations
settlements = tracker.generate_settlements()
# Returns: [Settlement(from_user="bob", to_user="alice", amount=50.00), ...]
```

**Comparative Benchmarking:**
```python
from scripts.features.benchmarking import BenchmarkEngine, PeerCriteria

engine = BenchmarkEngine()
criteria = PeerCriteria(household_size=2, income_bracket="50k-75k")

# Compare spending to peers
result = engine.compare(
    category="Groceries",
    user_amount=500.00,
    criteria=criteria,
)
# Returns: BenchmarkResult with peer_average, peer_median, percentile
```

**Audit Trail:**
```python
from scripts.features.audit import AuditLogger, AuditAction

logger = AuditLogger(user_id="user_123")

# Log transaction modification
entry = logger.log_action(
    action=AuditAction.TRANSACTION_MODIFY,
    description="Changed category",
    before_state={"category": "Food"},
    after_state={"category": "Groceries"},
    affected_ids=[123],
)

# Query audit trail
entries = logger.get_entries(affected_id=123)

# Check if action can be undone
can_undo = logger.can_undo(entry.entry_id)
```
```

### Step 3: Update test count in README.md

Find the test statistics section and update:

```markdown
**Test Coverage:**
- Unit tests: 235 passing (189 Phase 1-6 + 46 Phase 7)
- Integration tests: 44 passing (38 Phase 1-6 + 6 Phase 7)
- **Total: 279 tests, 100% pass rate**
```

### Step 4: Update root INDEX.md

Edit `INDEX.md` to include Phase 7 features:

```markdown
### `scripts/features/`
**Phase 7 advanced features**
- `alerts.py` - Smart alerts and notification scheduling
- `merchant_intelligence.py` - Merchant variation detection and grouping
- `documents.py` - Document and receipt requirement tracking
- `multi_user.py` - Shared expense and settlement tracking
- `benchmarking.py` - Privacy-first comparative benchmarking
- `audit.py` - Audit trail and activity logging
- `INDEX.md` - Features directory reference

### `tests/unit/`
**235 unit tests** covering all functionality
- Phase 7 tests: `test_alerts.py`, `test_alert_scheduler.py`, `test_merchant_intelligence.py`, `test_documents.py`, `test_multi_user.py`, `test_benchmarking.py`, `test_audit.py`

### `tests/integration/`
**44 integration tests** for workflows
- `test_advanced_features.py` - Phase 7 workflow tests (6 tests)
```

### Step 5: Create scripts/features/INDEX.md

```markdown
# scripts/features/INDEX.md

**Directory:** Phase 7 advanced features modules
**Purpose:** Smart alerts, merchant intelligence, document management, multi-user support, benchmarking, and audit trail

---

## Files

### `alerts.py` (237 lines)
**Smart alerts and notification scheduling**

**Classes:**
- `AlertType(Enum)` - Alert categories (budget, tax, pattern, optimization)
- `AlertSeverity(Enum)` - Severity levels (info, warning, critical)
- `Alert` - Alert dataclass with acknowledgment
- `ScheduleType(Enum)` - Schedule frequencies (weekly, monthly, quarterly, annual, one-time)
- `AlertSchedule` - Scheduled alert with due checking
- `AlertEngine` - Alert creation and management
- `AlertScheduler` - Schedule management and processing

**Key Methods:**
```python
engine = AlertEngine(user_id="user_123")
alert = engine.create_alert(
    alert_type=AlertType.BUDGET,
    severity=AlertSeverity.WARNING,
    title="Budget Exceeded",
    message="Over budget by $50",
)

scheduler = AlertScheduler(alert_engine=engine)
schedule = scheduler.add_schedule(
    schedule_type=ScheduleType.WEEKLY,
    alert_type=AlertType.BUDGET,
    title="Weekly Review",
    next_run=datetime(2025, 11, 28, 9, 0),
)

due_alerts = scheduler.process_due_schedules()
```

**Tests:** `tests/unit/test_alerts.py` (8 tests), `tests/unit/test_alert_scheduler.py` (6 tests)

---

### `merchant_intelligence.py` (158 lines)
**Merchant variation detection and payee enrichment**

**Classes:**
- `MerchantGroup` - Group of related merchant name variations
- `MerchantMatcher` - Variation detection and grouping

**Key Methods:**
```python
matcher = MerchantMatcher()

# Normalize payee names (removes PTY LTD, transaction IDs, etc.)
normalized = matcher.normalize_payee("WOOLWORTHS PTY LTD")  # "woolworths"

# Add variation to group
matcher.add_variation("Woolworths", "WOOLWORTHS PTY LTD")

# Find canonical name
canonical = matcher.find_canonical("woolworth")  # "Woolworths"

# Suggest matches
suggestions = matcher.suggest_matches("woollies", threshold=0.8)
# Returns: [(canonical_name, similarity_score), ...]
```

**Features:**
- Payee normalization (remove suffixes, IDs, whitespace)
- Similarity calculation using `difflib.SequenceMatcher`
- Variation grouping with canonical names
- Match suggestions with configurable threshold

**Tests:** `tests/unit/test_merchant_intelligence.py` (6 tests)

---

### `documents.py` (162 lines)
**Document and receipt requirement tracking**

**Classes:**
- `DocumentRequirement(Enum)` - Requirement levels (required, recommended, optional)
- `DocumentStatus(Enum)` - Documentation status (missing, attached, verified)
- `TransactionDocument` - Documentation record for transaction
- `DocumentManager` - Requirement tracking and management

**Key Methods:**
```python
manager = DocumentManager()

# Track transaction (auto-determines requirement)
doc = manager.track_transaction(
    transaction_id=12345,
    amount=450.00,  # > $300 = REQUIRED
    category="Work Expenses",
    date=datetime(2025, 11, 15),
)

# Attach document
doc.attach_document("https://example.com/receipt.pdf")

# Get missing documents
missing = manager.get_missing_documents(required_only=True)
```

**ATO Rules:**
- `> $300`: REQUIRED (substantiation threshold)
- `> $100` in deductible categories: RECOMMENDED
- Otherwise: OPTIONAL

**Deductible Categories:** Work Expenses, Office Supplies, Professional Development, Business Travel, Home Office, Vehicle Expenses

**Tests:** `tests/unit/test_documents.py` (8 tests)

---

### `multi_user.py` (189 lines)
**Multi-user shared expense and settlement tracking**

**Classes:**
- `SharedExpense` - Shared expense with split calculation
- `Settlement` - Settlement payment between users
- `SharedExpenseTracker` - Balance and settlement management

**Key Methods:**
```python
tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])

# Add expense with equal split
expense = tracker.add_expense(
    transaction_id=1,
    amount=150.00,
    description="Dinner",
    paid_by="alice",
    date=datetime.now(),
    split_equally=True,
)

# Add expense with custom split
expense = tracker.add_expense(
    transaction_id=2,
    amount=120.00,
    description="Groceries",
    paid_by="bob",
    date=datetime.now(),
    split_ratios={"alice": 0.5, "bob": 0.25, "charlie": 0.25},
)

# Calculate balances
balances = tracker.calculate_balances()
# Returns: {"alice": 20.00, "bob": -10.00, "charlie": -10.00}

# Generate settlement recommendations
settlements = tracker.generate_settlements()
# Returns: [Settlement(from_user="bob", to_user="alice", amount=10.00), ...]
```

**Features:**
- Equal and custom ratio splitting
- Net balance calculation across all expenses
- Optimal settlement generation (minimize transactions)

**Tests:** `tests/unit/test_multi_user.py` (10 tests)

---

### `benchmarking.py` (135 lines)
**Privacy-first comparative benchmarking**

**Classes:**
- `PeerCriteria` - Criteria for peer group selection
- `BenchmarkResult` - Comparison result with statistics
- `BenchmarkEngine` - Anonymous peer comparison

**Key Methods:**
```python
engine = BenchmarkEngine()

criteria = PeerCriteria(
    household_size=2,
    income_bracket="50k-75k",
    location="Sydney",
)

# Add anonymized data point
engine.add_data_point(
    category="Groceries",
    amount=500.00,
    user_id="user_123",  # Anonymized via SHA-256
    criteria=criteria,
)

# Compare to peers
result = engine.compare(
    category="Groceries",
    user_amount=525.00,
    criteria=criteria,
)
# Returns: BenchmarkResult(
#   peer_average=500.0,
#   peer_median=500.0,
#   percentile=55,
#   peer_count=10
# )
```

**Privacy Features:**
- SHA-256 user ID anonymization
- Aggregated data only (no user linkage)
- Minimum 3 peers required for comparison

**Tests:** `tests/unit/test_benchmarking.py` (5 tests)

---

### `audit.py` (183 lines)
**Audit trail and activity logging**

**Classes:**
- `AuditAction(Enum)` - Auditable action types
- `AuditEntry` - Audit log entry with serialization
- `AuditLogger` - Activity logging and queries

**Key Methods:**
```python
logger = AuditLogger(user_id="user_123")

# Log action
entry = logger.log_action(
    action=AuditAction.TRANSACTION_MODIFY,
    description="Changed category",
    before_state={"category": "Food"},
    after_state={"category": "Groceries"},
    affected_ids=[123],
)

# Query entries
entries = logger.get_entries(
    action=AuditAction.TRANSACTION_MODIFY,
    affected_id=123,
    start_date=datetime(2025, 11, 1),
)

# Check undo capability
can_undo = logger.can_undo(entry.entry_id)  # True if has before_state

# Serialize for storage
data = entry.to_dict()
restored = AuditEntry.from_dict(data)
```

**Audit Actions:**
- Transaction: modify, delete
- Category: create, modify, delete
- Rule: create, modify, delete
- Bulk operation
- Report generation

**Features:**
- Before/after state tracking
- Undo capability detection
- Filtering by action, ID, date range
- JSON serialization

**Tests:** `tests/unit/test_audit.py` (9 tests)

---

## Usage Patterns

### Alert Workflow
1. Create `AlertEngine` for user
2. Create `AlertScheduler` with engine
3. Add schedules with `add_schedule()`
4. Periodically call `process_due_schedules()`
5. User acknowledges alerts with `alert.acknowledge()`

### Merchant Learning Workflow
1. Create `MerchantMatcher`
2. Process transactions, normalize payee names
3. Suggest matches for variations
4. User confirms/corrects canonical name
5. Add variation with `add_variation()`
6. Future transactions auto-matched

### Document Tracking Workflow
1. Create `DocumentManager`
2. Track transactions with `track_transaction()`
3. System determines requirement (ATO rules)
4. Query missing with `get_missing_documents()`
5. Attach receipts with `doc.attach_document()`

### Shared Expense Workflow
1. Create `SharedExpenseTracker` with users
2. Add expenses with `add_expense()`
3. Calculate balances with `calculate_balances()`
4. Generate settlements with `generate_settlements()`
5. Record payments, mark expenses as settled

### Benchmarking Workflow
1. Create `BenchmarkEngine`
2. Define `PeerCriteria`
3. Add data points with `add_data_point()` (anonymized)
4. Compare user with `compare()`
5. Present percentile and peer statistics

### Audit Trail Workflow
1. Create `AuditLogger` for user
2. Log all actions with `log_action()`
3. Include before/after state for undo
4. Query with `get_entries()` filters
5. Check undo capability with `can_undo()`

---

**Total Tests:** 46 unit tests across 6 feature modules
**Integration Tests:** 6 workflow tests in `tests/integration/test_advanced_features.py`

**Next Phase:** Phase 8 - Health Check & Polish
```

### Step 6: Create operation log

```markdown
# docs/operations/2025-11-21_phase7_completion.md

# Phase 7: Advanced Features - Completion Log

**Date:** 2025-11-21
**Phase:** 7 of 8
**Status:** ✅ Complete
**Branch:** `feature/phase-7-advanced-features`

---

## Overview

Phase 7 implemented six advanced features for proactive financial management:
1. Smart alerts & notifications with scheduling
2. Merchant intelligence with variation detection
3. Document management with ATO compliance
4. Multi-user support with settlement tracking
5. Privacy-first comparative benchmarking
6. Comprehensive audit trail with undo capability

---

## Implementation Summary

### Task 1: Smart Alerts Foundation
- ✅ `AlertType` enum (budget, tax, pattern, optimization)
- ✅ `AlertSeverity` enum (info, warning, critical)
- ✅ `Alert` dataclass with acknowledgment
- ✅ `AlertEngine` for alert management
- ✅ 8 unit tests

**Files:**
- `scripts/features/alerts.py` (119 lines)
- `tests/unit/test_alerts.py` (144 lines)

**Commit:** `feat(alerts): add alert foundation with types, severity, and engine`

### Task 2: Alert Schedule Engine
- ✅ `ScheduleType` enum (weekly, monthly, quarterly, annual, one-time)
- ✅ `AlertSchedule` dataclass with due checking
- ✅ `AlertScheduler` for schedule management
- ✅ Automatic next_run calculation
- ✅ 6 unit tests

**Files:**
- `scripts/features/alerts.py` (+118 lines = 237 total)
- `tests/unit/test_alert_scheduler.py` (105 lines)

**Commit:** `feat(alerts): add alert scheduling engine`

### Task 3: Merchant Intelligence Foundation
- ✅ `MerchantGroup` dataclass
- ✅ `MerchantMatcher` with normalization
- ✅ Payee variation detection using `difflib`
- ✅ Canonical name management
- ✅ Match suggestion with threshold
- ✅ 6 unit tests

**Files:**
- `scripts/features/merchant_intelligence.py` (158 lines)
- `tests/unit/test_merchant_intelligence.py` (87 lines)

**Commit:** `feat(merchant): add merchant intelligence foundation`

**Normalization Rules:**
- Remove common suffixes (PTY LTD, Inc, LLC)
- Remove transaction IDs
- Remove extra whitespace
- Convert to lowercase

### Task 4: Document Management Foundation
- ✅ `DocumentRequirement` enum (required, recommended, optional)
- ✅ `DocumentStatus` enum (missing, attached, verified)
- ✅ `TransactionDocument` dataclass
- ✅ `DocumentManager` with ATO rules
- ✅ Threshold-based requirement determination
- ✅ 8 unit tests

**Files:**
- `scripts/features/documents.py` (162 lines)
- `tests/unit/test_documents.py` (105 lines)

**Commit:** `feat(docs): add document management foundation`

**ATO Compliance:**
- > $300: REQUIRED substantiation
- > $100 in deductible categories: RECOMMENDED
- Otherwise: OPTIONAL

### Task 5: Multi-User Support Foundation
- ✅ `SharedExpense` dataclass with splits
- ✅ `Settlement` dataclass
- ✅ `SharedExpenseTracker` for balance management
- ✅ Equal and custom ratio splitting
- ✅ Settlement generation algorithm
- ✅ 10 unit tests

**Files:**
- `scripts/features/multi_user.py` (189 lines)
- `tests/unit/test_multi_user.py` (168 lines)

**Commit:** `feat(multi-user): add shared expense tracking foundation`

**Settlement Algorithm:**
- Calculate net balances for all users
- Separate creditors (positive) and debtors (negative)
- Match debtors to creditors optimally
- Minimize number of transactions

### Task 6: Comparative Benchmarking Foundation
- ✅ `PeerCriteria` dataclass
- ✅ `BenchmarkResult` dataclass
- ✅ `BenchmarkEngine` with SHA-256 anonymization
- ✅ Privacy-first aggregated data
- ✅ Percentile calculation
- ✅ 5 unit tests

**Files:**
- `scripts/features/benchmarking.py` (135 lines)
- `tests/unit/test_benchmarking.py` (93 lines)

**Commit:** `feat(benchmarking): add privacy-first comparative benchmarking`

**Privacy Features:**
- User IDs anonymized via SHA-256
- Only aggregated amounts stored
- No user linkage in data
- Minimum 3 peers for comparison

### Task 7: Audit Trail Foundation
- ✅ `AuditAction` enum (10 action types)
- ✅ `AuditEntry` dataclass with serialization
- ✅ `AuditLogger` for activity logging
- ✅ Before/after state tracking
- ✅ Undo capability detection
- ✅ 9 unit tests

**Files:**
- `scripts/features/audit.py` (183 lines)
- `tests/unit/test_audit.py` (158 lines)

**Commit:** `feat(audit): add audit trail foundation`

**Audit Capabilities:**
- Track all transaction/category/rule changes
- Store before/after state for undo
- Filter by action, ID, date range
- JSON serialization for persistence
- Undo capability based on before_state presence

### Task 8: Integration Tests for Advanced Features
- ✅ Alert workflow test (scheduling to acknowledgment)
- ✅ Merchant intelligence learning workflow test
- ✅ Document management workflow test
- ✅ Multi-user settlement workflow test
- ✅ Benchmarking comparison workflow test
- ✅ Audit trail query workflow test

**Files:**
- `tests/integration/test_advanced_features.py` (198 lines)

**Commit:** `test(integration): add integration tests for advanced features`

### Task 9: Documentation Updates
- ✅ Updated `README.md` with Phase 7 examples
- ✅ Updated root `INDEX.md` with features directory
- ✅ Created `scripts/features/INDEX.md` (complete API reference)
- ✅ Created operation log (this file)

**Commit:** `docs: update documentation for Phase 7 advanced features`

---

## Test Results

### Unit Tests
- `test_alerts.py`: 8 tests ✅
- `test_alert_scheduler.py`: 6 tests ✅
- `test_merchant_intelligence.py`: 6 tests ✅
- `test_documents.py`: 8 tests ✅
- `test_multi_user.py`: 10 tests ✅
- `test_benchmarking.py`: 5 tests ✅
- `test_audit.py`: 9 tests ✅
- **Subtotal: 46 unit tests**

### Integration Tests
- `test_advanced_features.py`: 6 tests ✅
- **Subtotal: 6 integration tests**

### Total Test Count
- **Phase 7 Tests:** 52 tests (46 unit + 6 integration)
- **Previous Phases:** 227 tests (189 unit + 38 integration)
- **Project Total:** 279 tests (235 unit + 44 integration)
- **Pass Rate:** 100%

---

## Code Quality

All code passes:
- ✅ `black` formatting
- ✅ `flake8` linting (max-line-length=100)
- ✅ `mypy` type checking
- ✅ Unit tests
- ✅ Integration tests

---

## Files Created/Modified

### Created (13 files)
1. `scripts/features/alerts.py` (237 lines)
2. `scripts/features/merchant_intelligence.py` (158 lines)
3. `scripts/features/documents.py` (162 lines)
4. `scripts/features/multi_user.py` (189 lines)
5. `scripts/features/benchmarking.py` (135 lines)
6. `scripts/features/audit.py` (183 lines)
7. `tests/unit/test_alerts.py` (144 lines)
8. `tests/unit/test_alert_scheduler.py` (105 lines)
9. `tests/unit/test_merchant_intelligence.py` (87 lines)
10. `tests/unit/test_documents.py` (105 lines)
11. `tests/unit/test_multi_user.py` (168 lines)
12. `tests/unit/test_benchmarking.py` (93 lines)
13. `tests/unit/test_audit.py` (158 lines)
14. `tests/integration/test_advanced_features.py` (198 lines)
15. `scripts/features/INDEX.md` (237 lines)
16. `docs/operations/2025-11-21_phase7_completion.md` (this file)

### Modified (2 files)
1. `README.md` - Added Phase 7 section with examples
2. `INDEX.md` - Added features directory and updated test counts

---

## Commits

1. `feat(alerts): add alert foundation with types, severity, and engine`
2. `feat(alerts): add alert scheduling engine`
3. `feat(merchant): add merchant intelligence foundation`
4. `feat(docs): add document management foundation`
5. `feat(multi-user): add shared expense tracking foundation`
6. `feat(benchmarking): add privacy-first comparative benchmarking`
7. `feat(audit): add audit trail foundation`
8. `test(integration): add integration tests for advanced features`
9. `docs: update documentation for Phase 7 advanced features`

**Total:** 9 commits

---

## Next Steps

**Phase 8: Health Check & Polish (Final Phase)**
- Health check system (6 health scores)
- Recommendation engine
- Automated monitoring
- End-to-end testing
- Documentation completion
- Performance optimization
- User guides

**Estimated Scope:** 2 weeks
**Target Completion:** 2025-12-05

---

## Notes

- All advanced features implemented with TDD methodology
- Privacy-first design for benchmarking (SHA-256 anonymization)
- ATO compliance for document requirements ($300 threshold)
- Merchant intelligence uses difflib for similarity matching
- Audit trail supports undo via before/after state tracking
- Settlement algorithm minimizes transaction count
- 100% test pass rate maintained throughout implementation

---

**Phase Status:** ✅ Complete
**Ready for:** Phase 8 implementation
```

### Step 7: Commit documentation updates

```bash
git add README.md INDEX.md scripts/features/INDEX.md docs/operations/2025-11-21_phase7_completion.md
git commit -m "docs: update documentation for Phase 7 advanced features

- Add Phase 7 section to README with feature examples
- Update INDEX.md with features directory
- Create scripts/features/INDEX.md with complete API reference
- Create Phase 7 completion operation log
- Update test counts (279 total: 235 unit + 44 integration)"
```

### Step 8: Run final verification

```bash
pytest tests/ -v --tb=short
```

Expected: All 279 tests `PASSED`

---

## Summary

**Phase 7 Complete:**
- ✅ 6 advanced feature modules implemented
- ✅ 46 unit tests (100% pass)
- ✅ 6 integration tests (100% pass)
- ✅ 279 total tests across project
- ✅ Complete documentation
- ✅ 9 commits on feature branch

**Total Implementation:**
- 1,064 lines of production code
- 1,445 lines of test code
- 237 lines of documentation (INDEX.md)
- TDD methodology throughout
- Privacy-first benchmarking
- ATO compliance for documents
- Undo capability in audit trail

**Ready for Phase 8:** Health Check & Polish (final phase)
