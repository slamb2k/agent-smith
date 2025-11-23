# Agent Smith Onboarding System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a guided first-run onboarding workflow that discovers user's PocketSmith data, helps customize rule templates, and incrementally categorizes transactions with visible progress tracking.

**Architecture:** Eight-stage interactive workflow orchestrated by `/smith:install` slash command. Discovery phase analyzes PocketSmith account structure, template selector recommends based on user data, interactive customization validates accounts/categories/merchants, incremental categorization processes transactions in batches, and health checks show before/after improvement.

**Tech Stack:** Python 3.9+, PocketSmith API (via scripts.core.api_client), YAML rules (scripts.core.unified_rules), Health check system (scripts.health.*), Claude SDK for conversational orchestration

---

## Task 1: Discovery Script - Account Analysis

**Files:**
- Create: `scripts/onboarding/discovery.py`
- Create: `scripts/onboarding/__init__.py`
- Create: `tests/unit/test_discovery.py`
- Reference: `scripts/core/api_client.py` (PocketSmith API wrapper)

**Step 1: Write the failing test**

Create `tests/unit/test_discovery.py`:

```python
"""Tests for onboarding discovery module."""

from datetime import date
from decimal import Decimal
from scripts.onboarding.discovery import (
    DiscoveryAnalyzer,
    DiscoveryReport,
    AccountSummary,
    CategorySummary,
    TransactionSummary,
)


def test_discovery_report_structure():
    """Test DiscoveryReport dataclass structure."""
    report = DiscoveryReport(
        user_id=12345,
        user_email="test@example.com",
        accounts=[],
        categories=[],
        transactions=TransactionSummary(
            total_count=0,
            uncategorized_count=0,
            date_range_start=None,
            date_range_end=None,
            by_account={},
        ),
        baseline_health_score=None,
        recommendation="simple",
    )

    assert report.user_id == 12345
    assert report.user_email == "test@example.com"
    assert report.recommendation == "simple"


def test_account_summary_creation():
    """Test AccountSummary dataclass."""
    account = AccountSummary(
        id=123,
        name="Personal Checking",
        institution="Test Bank",
        transaction_count=100,
        uncategorized_count=50,
    )

    assert account.id == 123
    assert account.name == "Personal Checking"
    assert account.uncategorized_count == 50


def test_category_summary_creation():
    """Test CategorySummary dataclass."""
    category = CategorySummary(
        id=456,
        title="Groceries",
        parent_title=None,
        transaction_count=25,
        total_amount=Decimal("-500.00"),
    )

    assert category.id == 456
    assert category.title == "Groceries"
    assert category.total_amount == Decimal("-500.00")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_discovery.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'scripts.onboarding.discovery'"

**Step 3: Write minimal implementation for dataclasses**

Create `scripts/onboarding/__init__.py`:

```python
"""Onboarding module for first-time Agent Smith setup."""
```

Create `scripts/onboarding/discovery.py`:

```python
"""Discovery analyzer for PocketSmith account structure."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List, Dict, Optional


@dataclass
class AccountSummary:
    """Summary of a PocketSmith account."""

    id: int
    name: str
    institution: str
    transaction_count: int
    uncategorized_count: int


@dataclass
class CategorySummary:
    """Summary of a PocketSmith category."""

    id: int
    title: str
    parent_title: Optional[str]
    transaction_count: int
    total_amount: Decimal


@dataclass
class TransactionSummary:
    """Summary of transaction data."""

    total_count: int
    uncategorized_count: int
    date_range_start: Optional[date]
    date_range_end: Optional[date]
    by_account: Dict[int, int] = field(default_factory=dict)


@dataclass
class DiscoveryReport:
    """Complete discovery report for onboarding."""

    user_id: int
    user_email: str
    accounts: List[AccountSummary]
    categories: List[CategorySummary]
    transactions: TransactionSummary
    baseline_health_score: Optional[int]
    recommendation: str


class DiscoveryAnalyzer:
    """Analyzer for PocketSmith account discovery."""

    def __init__(self, client=None):
        """Initialize with optional PocketSmith client.

        Args:
            client: PocketSmithClient instance (or None for testing)
        """
        self.client = client
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_discovery.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add scripts/onboarding/__init__.py scripts/onboarding/discovery.py tests/unit/test_discovery.py
git commit -m "feat: add discovery dataclasses for onboarding"
```

---

## Task 2: Discovery Script - Data Fetching

**Files:**
- Modify: `scripts/onboarding/discovery.py`
- Modify: `tests/unit/test_discovery.py`
- Reference: `scripts/core/api_client.py` (for PocketSmithClient interface)

**Step 1: Write the failing test**

Add to `tests/unit/test_discovery.py`:

```python
from unittest.mock import Mock, MagicMock
from datetime import datetime


def test_discovery_analyzer_fetch_accounts():
    """Test fetching account summaries."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 12345,
        "login": "test@example.com",
    }
    mock_client.get_accounts.return_value = [
        {
            "id": 100,
            "title": "Checking",
            "institution": {"title": "Test Bank"},
        },
        {
            "id": 200,
            "title": "Savings",
            "institution": {"title": "Test Bank"},
        },
    ]

    analyzer = DiscoveryAnalyzer(client=mock_client)
    accounts = analyzer._fetch_accounts()

    assert len(accounts) == 2
    assert accounts[0].id == 100
    assert accounts[0].name == "Checking"
    assert accounts[0].institution == "Test Bank"


def test_discovery_analyzer_fetch_categories():
    """Test fetching category summaries."""
    mock_client = Mock()
    mock_client.get_user.return_value = {"id": 12345}
    mock_client.get_categories.return_value = [
        {
            "id": 300,
            "title": "Groceries",
            "parent_id": None,
        },
        {
            "id": 301,
            "title": "Supermarket",
            "parent_id": 300,
        },
    ]

    analyzer = DiscoveryAnalyzer(client=mock_client)
    categories = analyzer._fetch_categories()

    assert len(categories) == 2
    assert categories[0].id == 300
    assert categories[0].title == "Groceries"
    assert categories[0].parent_title is None


def test_discovery_analyzer_fetch_transactions():
    """Test fetching transaction summary."""
    mock_client = Mock()
    mock_client.get_user.return_value = {"id": 12345}
    mock_client.get_transactions.return_value = [
        {
            "id": 1,
            "payee": "Woolworths",
            "amount": -50.00,
            "date": "2025-11-01",
            "category": {"id": 300},
            "transaction_account": {"id": 100},
        },
        {
            "id": 2,
            "payee": "Unknown",
            "amount": -25.00,
            "date": "2025-11-15",
            "category": None,
            "transaction_account": {"id": 100},
        },
    ]

    analyzer = DiscoveryAnalyzer(client=mock_client)
    summary = analyzer._fetch_transaction_summary()

    assert summary.total_count == 2
    assert summary.uncategorized_count == 1
    assert summary.date_range_start == date(2025, 11, 1)
    assert summary.date_range_end == date(2025, 11, 15)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_discovery.py::test_discovery_analyzer_fetch_accounts -v`

Expected: FAIL with "AttributeError: 'DiscoveryAnalyzer' object has no attribute '_fetch_accounts'"

**Step 3: Write minimal implementation**

Modify `scripts/onboarding/discovery.py`, add to `DiscoveryAnalyzer` class:

```python
from datetime import datetime
from typing import List


class DiscoveryAnalyzer:
    """Analyzer for PocketSmith account discovery."""

    def __init__(self, client=None):
        """Initialize with optional PocketSmith client.

        Args:
            client: PocketSmithClient instance (or None for testing)
        """
        self.client = client

    def _fetch_accounts(self) -> List[AccountSummary]:
        """Fetch account summaries from PocketSmith.

        Returns:
            List of AccountSummary objects
        """
        accounts_data = self.client.get_accounts()
        summaries = []

        for acc in accounts_data:
            summary = AccountSummary(
                id=acc["id"],
                name=acc["title"],
                institution=acc["institution"]["title"],
                transaction_count=0,  # Will be populated by transaction fetch
                uncategorized_count=0,
            )
            summaries.append(summary)

        return summaries

    def _fetch_categories(self) -> List[CategorySummary]:
        """Fetch category summaries from PocketSmith.

        Returns:
            List of CategorySummary objects
        """
        categories_data = self.client.get_categories()
        summaries = []

        # Build category map for parent lookup
        category_map = {cat["id"]: cat for cat in categories_data}

        for cat in categories_data:
            parent_title = None
            if cat.get("parent_id"):
                parent = category_map.get(cat["parent_id"])
                if parent:
                    parent_title = parent["title"]

            summary = CategorySummary(
                id=cat["id"],
                title=cat["title"],
                parent_title=parent_title,
                transaction_count=0,  # Will be populated by transaction fetch
                total_amount=Decimal("0.00"),
            )
            summaries.append(summary)

        return summaries

    def _fetch_transaction_summary(self) -> TransactionSummary:
        """Fetch transaction summary statistics.

        Returns:
            TransactionSummary object
        """
        transactions = self.client.get_transactions()

        total_count = len(transactions)
        uncategorized_count = 0
        dates = []
        by_account: Dict[int, int] = {}

        for txn in transactions:
            # Count uncategorized
            if not txn.get("category"):
                uncategorized_count += 1

            # Track dates
            if txn.get("date"):
                txn_date = datetime.fromisoformat(txn["date"].replace("Z", "+00:00")).date()
                dates.append(txn_date)

            # Count by account
            account_id = txn.get("transaction_account", {}).get("id")
            if account_id:
                by_account[account_id] = by_account.get(account_id, 0) + 1

        date_range_start = min(dates) if dates else None
        date_range_end = max(dates) if dates else None

        return TransactionSummary(
            total_count=total_count,
            uncategorized_count=uncategorized_count,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            by_account=by_account,
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_discovery.py -v`

Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add scripts/onboarding/discovery.py tests/unit/test_discovery.py
git commit -m "feat: add data fetching methods to discovery analyzer"
```

---

## Task 3: Discovery Script - Template Recommendation

**Files:**
- Modify: `scripts/onboarding/discovery.py`
- Modify: `tests/unit/test_discovery.py`

**Step 1: Write the failing test**

Add to `tests/unit/test_discovery.py`:

```python
def test_recommend_template_simple():
    """Test simple template recommendation for single user."""
    mock_client = Mock()
    mock_client.get_user.return_value = {"id": 12345}
    mock_client.get_accounts.return_value = [
        {"id": 100, "title": "Checking", "institution": {"title": "Bank"}},
    ]
    mock_client.get_categories.return_value = [
        {"id": 300, "title": "Groceries", "parent_id": None},
    ]
    mock_client.get_transactions.return_value = []

    analyzer = DiscoveryAnalyzer(client=mock_client)
    recommendation = analyzer._recommend_template(
        accounts=[AccountSummary(100, "Checking", "Bank", 0, 0)],
        categories=[CategorySummary(300, "Groceries", None, 0, Decimal("0"))],
    )

    assert recommendation == "simple"


def test_recommend_template_shared_household():
    """Test shared household template for joint accounts."""
    accounts = [
        AccountSummary(100, "Joint Savings", "Bank", 50, 10),
        AccountSummary(200, "Personal", "Bank", 30, 5),
    ]
    categories = [
        CategorySummary(300, "Groceries", None, 25, Decimal("-500")),
        CategorySummary(301, "Shared Expense", None, 15, Decimal("-300")),
    ]

    analyzer = DiscoveryAnalyzer(client=None)
    recommendation = analyzer._recommend_template(accounts, categories)

    assert recommendation == "shared-household"


def test_recommend_template_separated_families():
    """Test separated families template for child support tracking."""
    accounts = [
        AccountSummary(100, "Personal", "Bank", 50, 10),
    ]
    categories = [
        CategorySummary(300, "Child Support", None, 10, Decimal("-800")),
        CategorySummary(301, "Kids Activities", None, 5, Decimal("-200")),
    ]

    analyzer = DiscoveryAnalyzer(client=None)
    recommendation = analyzer._recommend_template(accounts, categories)

    assert recommendation == "separated-families"


def test_recommend_template_advanced():
    """Test advanced template for investment tracking."""
    accounts = [
        AccountSummary(100, "Personal", "Bank", 100, 20),
        AccountSummary(200, "Business", "Bank", 50, 10),
    ]
    categories = [
        CategorySummary(300, "Investment", None, 15, Decimal("5000")),
        CategorySummary(301, "Capital Gains", None, 3, Decimal("1200")),
        CategorySummary(302, "Business Expenses", None, 25, Decimal("-3000")),
    ]

    analyzer = DiscoveryAnalyzer(client=None)
    recommendation = analyzer._recommend_template(accounts, categories)

    assert recommendation == "advanced"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_discovery.py::test_recommend_template_simple -v`

Expected: FAIL with "AttributeError: 'DiscoveryAnalyzer' object has no attribute '_recommend_template'"

**Step 3: Write minimal implementation**

Modify `scripts/onboarding/discovery.py`, add to `DiscoveryAnalyzer` class:

```python
def _recommend_template(
    self,
    accounts: List[AccountSummary],
    categories: List[CategorySummary],
) -> str:
    """Recommend a template based on account and category structure.

    Args:
        accounts: List of account summaries
        categories: List of category summaries

    Returns:
        Template name: simple, separated-families, shared-household, or advanced
    """
    # Extract category titles for pattern matching
    category_titles = {cat.title.lower() for cat in categories}
    account_names = {acc.name.lower() for acc in accounts}

    # Check for separated families indicators
    separated_indicators = {
        "child support", "kids activities", "kids", "children",
        "child care", "school fees", "custody"
    }
    if any(indicator in category_titles for indicator in separated_indicators):
        return "separated-families"

    # Check for advanced indicators
    advanced_indicators = {
        "investment", "capital gains", "cgt", "business expenses",
        "dividends", "rental income", "crypto", "shares"
    }
    business_accounts = any("business" in name for name in account_names)
    has_investments = any(indicator in category_titles for indicator in advanced_indicators)

    if has_investments or business_accounts:
        return "advanced"

    # Check for shared household indicators
    shared_indicators = {
        "shared", "joint", "household", "split"
    }
    has_shared = any(indicator in category_titles for indicator in shared_indicators)
    joint_accounts = any("joint" in name or "shared" in name for name in account_names)

    if has_shared or (joint_accounts and len(accounts) > 1):
        return "shared-household"

    # Default to simple
    return "simple"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_discovery.py -v`

Expected: PASS (10 tests)

**Step 5: Commit**

```bash
git add scripts/onboarding/discovery.py tests/unit/test_discovery.py
git commit -m "feat: add template recommendation logic to discovery"
```

---

## Task 4: Discovery Script - Main Analyze Method

**Files:**
- Modify: `scripts/onboarding/discovery.py`
- Modify: `tests/unit/test_discovery.py`

**Step 1: Write the failing test**

Add to `tests/unit/test_discovery.py`:

```python
def test_discovery_analyzer_analyze():
    """Test complete discovery analysis."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 12345,
        "login": "test@example.com",
    }
    mock_client.get_accounts.return_value = [
        {"id": 100, "title": "Checking", "institution": {"title": "Test Bank"}},
    ]
    mock_client.get_categories.return_value = [
        {"id": 300, "title": "Groceries", "parent_id": None},
    ]
    mock_client.get_transactions.return_value = [
        {
            "id": 1,
            "payee": "Store",
            "amount": -50.00,
            "date": "2025-11-01",
            "category": {"id": 300},
            "transaction_account": {"id": 100},
        },
    ]

    analyzer = DiscoveryAnalyzer(client=mock_client)
    report = analyzer.analyze()

    assert report.user_id == 12345
    assert report.user_email == "test@example.com"
    assert len(report.accounts) == 1
    assert report.accounts[0].transaction_count == 1
    assert len(report.categories) == 1
    assert report.transactions.total_count == 1
    assert report.transactions.uncategorized_count == 0
    assert report.recommendation == "simple"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_discovery.py::test_discovery_analyzer_analyze -v`

Expected: FAIL with "AttributeError: 'DiscoveryAnalyzer' object has no attribute 'analyze'"

**Step 3: Write minimal implementation**

Modify `scripts/onboarding/discovery.py`, add to `DiscoveryAnalyzer` class:

```python
def analyze(self, include_health_check: bool = False) -> DiscoveryReport:
    """Run complete discovery analysis.

    Args:
        include_health_check: Whether to run baseline health check

    Returns:
        DiscoveryReport with all analysis results
    """
    # Fetch user info
    user_data = self.client.get_user()
    user_id = user_data["id"]
    user_email = user_data.get("login", "unknown")

    # Fetch all data
    accounts = self._fetch_accounts()
    categories = self._fetch_categories()
    transactions = self._fetch_transaction_summary()

    # Update account transaction counts
    for account in accounts:
        account.transaction_count = transactions.by_account.get(account.id, 0)
        # Uncategorized count would need separate query - simplified for now

    # Update category transaction counts
    # (Would need to count from transactions - simplified for now)

    # Get template recommendation
    recommendation = self._recommend_template(accounts, categories)

    # Optional: Run baseline health check
    baseline_health_score = None
    if include_health_check:
        # TODO: Integrate with health check system
        # from scripts.health.engine import HealthCheckEngine
        # engine = HealthCheckEngine()
        # result = engine.run_all(...)
        # baseline_health_score = result.overall_score
        pass

    return DiscoveryReport(
        user_id=user_id,
        user_email=user_email,
        accounts=accounts,
        categories=categories,
        transactions=transactions,
        baseline_health_score=baseline_health_score,
        recommendation=recommendation,
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_discovery.py -v`

Expected: PASS (11 tests)

**Step 5: Commit**

```bash
git add scripts/onboarding/discovery.py tests/unit/test_discovery.py
git commit -m "feat: add main analyze method to discovery analyzer"
```

---

## Task 5: Discovery Script - CLI Interface

**Files:**
- Modify: `scripts/onboarding/discovery.py`
- Create: `tests/integration/test_discovery_integration.py`

**Step 1: Write the failing test**

Create `tests/integration/test_discovery_integration.py`:

```python
"""Integration tests for discovery module."""

import pytest
from scripts.core.api_client import PocketSmithClient
from scripts.onboarding.discovery import DiscoveryAnalyzer


@pytest.mark.integration
def test_discovery_with_real_api():
    """Test discovery with real PocketSmith API."""
    client = PocketSmithClient()
    analyzer = DiscoveryAnalyzer(client=client)

    report = analyzer.analyze(include_health_check=False)

    # Basic assertions
    assert report.user_id > 0
    assert report.user_email
    assert isinstance(report.accounts, list)
    assert isinstance(report.categories, list)
    assert report.transactions.total_count >= 0
    assert report.recommendation in ["simple", "separated-families", "shared-household", "advanced"]

    # Print summary for manual verification
    print(f"\n{'='*60}")
    print(f"Discovery Report for {report.user_email}")
    print(f"{'='*60}")
    print(f"User ID: {report.user_id}")
    print(f"Accounts: {len(report.accounts)}")
    print(f"Categories: {len(report.categories)}")
    print(f"Transactions: {report.transactions.total_count}")
    print(f"Uncategorized: {report.transactions.uncategorized_count}")
    print(f"Date Range: {report.transactions.date_range_start} to {report.transactions.date_range_end}")
    print(f"Recommended Template: {report.recommendation}")
    print(f"{'='*60}")
```

**Step 2: Run test to verify it works**

Run: `pytest tests/integration/test_discovery_integration.py -v -m integration`

Expected: PASS with printed discovery report

**Step 3: Add CLI main function**

Modify `scripts/onboarding/discovery.py`, add at bottom:

```python
def main() -> None:
    """CLI entry point for discovery analysis."""
    import sys
    from scripts.core.api_client import PocketSmithClient

    print("=" * 70)
    print("Agent Smith - PocketSmith Discovery Analysis")
    print("=" * 70)
    print()

    try:
        client = PocketSmithClient()
        analyzer = DiscoveryAnalyzer(client=client)

        print("Analyzing your PocketSmith account...")
        print()

        report = analyzer.analyze(include_health_check=False)

        # Print report
        print(f"✓ Connected as: {report.user_email}")
        print(f"✓ User ID: {report.user_id}")
        print()

        print(f"Accounts ({len(report.accounts)}):")
        for acc in report.accounts:
            print(f"  • {acc.name} ({acc.institution})")
            print(f"    Transactions: {acc.transaction_count}")
        print()

        print(f"Categories ({len(report.categories)}):")
        # Show top 10 by title
        for cat in sorted(report.categories, key=lambda c: c.title)[:10]:
            parent_info = f" (under {cat.parent_title})" if cat.parent_title else ""
            print(f"  • {cat.title}{parent_info}")
        if len(report.categories) > 10:
            print(f"  ... and {len(report.categories) - 10} more")
        print()

        print(f"Transactions:")
        print(f"  Total: {report.transactions.total_count}")
        print(f"  Uncategorized: {report.transactions.uncategorized_count} ({report.transactions.uncategorized_count / report.transactions.total_count * 100:.1f}%)")
        if report.transactions.date_range_start:
            print(f"  Date Range: {report.transactions.date_range_start} to {report.transactions.date_range_end}")
        print()

        print(f"Recommended Template: {report.recommendation}")
        print()

        print("=" * 70)
        print("Discovery complete!")
        print()
        print("Next steps:")
        print(f"1. Run: uv run python scripts/setup/template_selector.py")
        print(f"2. Select template: {report.recommendation}")
        print(f"3. Customize data/rules.yaml for your needs")

    except Exception as e:
        print(f"Error during discovery: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 4: Test CLI**

Run: `uv run python -u scripts/onboarding/discovery.py`

Expected: Prints discovery report for your PocketSmith account

**Step 5: Commit**

```bash
git add scripts/onboarding/discovery.py tests/integration/test_discovery_integration.py
git commit -m "feat: add CLI interface to discovery analyzer"
```

---

## Task 6: Baseline Health Check Integration

**Files:**
- Modify: `scripts/onboarding/discovery.py`
- Create: `scripts/onboarding/baseline_health.py`
- Create: `tests/unit/test_baseline_health.py`

**Step 1: Write the failing test**

Create `tests/unit/test_baseline_health.py`:

```python
"""Tests for baseline health check."""

from unittest.mock import Mock, MagicMock
from scripts.onboarding.baseline_health import BaselineHealthChecker


def test_baseline_health_checker_creation():
    """Test BaselineHealthChecker initialization."""
    mock_client = Mock()
    checker = BaselineHealthChecker(client=mock_client)

    assert checker.client == mock_client


def test_run_baseline_check():
    """Test running baseline health check."""
    mock_client = Mock()
    mock_client.get_user.return_value = {"id": 12345}

    checker = BaselineHealthChecker(client=mock_client)
    score = checker.run_baseline_check()

    assert isinstance(score, int)
    assert 0 <= score <= 100
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_baseline_health.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'scripts.onboarding.baseline_health'"

**Step 3: Write minimal implementation**

Create `scripts/onboarding/baseline_health.py`:

```python
"""Baseline health check for onboarding."""

from typing import Optional, Dict, Any
from scripts.health.engine import HealthCheckEngine
from scripts.health.collector import HealthDataCollector


class BaselineHealthChecker:
    """Run baseline health check before onboarding changes."""

    def __init__(self, client=None):
        """Initialize with optional PocketSmith client.

        Args:
            client: PocketSmithClient instance
        """
        self.client = client
        self.engine = HealthCheckEngine()
        self.collector = HealthDataCollector(client=client)

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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_baseline_health.py -v`

Expected: PASS (2 tests)

**Step 5: Integrate with discovery**

Modify `scripts/onboarding/discovery.py`, update the `analyze` method:

```python
def analyze(self, include_health_check: bool = False) -> DiscoveryReport:
    """Run complete discovery analysis.

    Args:
        include_health_check: Whether to run baseline health check

    Returns:
        DiscoveryReport with all analysis results
    """
    # Fetch user info
    user_data = self.client.get_user()
    user_id = user_data["id"]
    user_email = user_data.get("login", "unknown")

    # Fetch all data
    accounts = self._fetch_accounts()
    categories = self._fetch_categories()
    transactions = self._fetch_transaction_summary()

    # Update account transaction counts
    for account in accounts:
        account.transaction_count = transactions.by_account.get(account.id, 0)

    # Get template recommendation
    recommendation = self._recommend_template(accounts, categories)

    # Optional: Run baseline health check
    baseline_health_score = None
    if include_health_check:
        from scripts.onboarding.baseline_health import BaselineHealthChecker
        checker = BaselineHealthChecker(client=self.client)
        baseline_health_score = checker.run_baseline_check()

    return DiscoveryReport(
        user_id=user_id,
        user_email=user_email,
        accounts=accounts,
        categories=categories,
        transactions=transactions,
        baseline_health_score=baseline_health_score,
        recommendation=recommendation,
    )
```

**Step 6: Commit**

```bash
git add scripts/onboarding/baseline_health.py tests/unit/test_baseline_health.py scripts/onboarding/discovery.py
git commit -m "feat: integrate baseline health check with discovery"
```

---

## Task 7: Onboarding Slash Command - Initial Structure

**Files:**
- Create: `.claude/commands/smith:install.md`
- Modify: `.claude/commands/INDEX.md`

**Step 1: Create slash command file**

Create `.claude/commands/smith:install.md`:

```markdown
---
name: agent-smith-onboard
description: Interactive first-time setup wizard for Agent Smith
---

# Agent Smith Onboarding Wizard

You are guiding a user through their first-time Agent Smith setup. This is an interactive, multi-stage process.

## Your Role

- Be encouraging and supportive
- Explain each step clearly
- Show progress throughout the journey
- Celebrate wins (data discovered, rules created, transactions categorized)
- Provide concrete next steps

## Workflow Stages

### Stage 1: Welcome & Prerequisites Check

Greet the user and verify they have:
1. ✓ Agent Smith installed
2. ✓ API key configured in .env
3. ✓ PocketSmith account accessible

If any prerequisite is missing, guide them to INSTALL.md.

### Stage 2: Discovery

Run the discovery script to analyze their PocketSmith account:

```bash
uv run python -u scripts/onboarding/discovery.py
```

**What to look for:**
- Account count and types
- Category structure
- Transaction volume and date range
- Uncategorized transaction count
- Baseline health score (if available)

**Present findings:**
- Summarize their PocketSmith setup
- Highlight the uncategorized transaction count
- Show the recommended template

### Stage 3: Template Selection

Based on discovery, recommend a template:

```bash
uv run python scripts/setup/template_selector.py
```

**Templates:**
- `simple` - Single person, basic tracking
- `separated-families` - Child support, custody tracking
- `shared-household` - Joint accounts, shared expenses
- `advanced` - Investments, business expenses, tax optimization

**User chooses template** → Applied to `data/rules.yaml`

### Stage 4: Template Customization

Guide the user to customize the template:

1. **Account Mapping**: Map template account names to their actual accounts
2. **Category Validation**: Check if template categories exist in PocketSmith
3. **Merchant Localization**: Update merchant patterns for their region (AU/US/etc.)

**For now:** Inform user they need to manually edit `data/rules.yaml`
**Future:** Interactive customization script will automate this

### Stage 5: Intelligence Mode Selection

Ask user to choose their preferred intelligence mode:

**Categorization mode:**
- Conservative: Approve every AI suggestion
- Smart (recommended): Auto-apply high confidence (≥90%)
- Aggressive: Auto-apply medium+ confidence (≥80%)

**Tax intelligence level:**
- Reference: Basic ATO category mapping
- Smart: Deduction detection, thresholds
- Full: BAS prep, compliance checks

Save to `data/config.json`.

### Stage 6: Incremental Categorization

Recommend starting with recent transactions:

**Suggested batch strategy:**
1. Start with current month (test rules on small dataset)
2. Expand to last 3 months (validate at scale)
3. Backfill historical data (complete the archive)

**Run categorization:**
```bash
# Dry run first
uv run python scripts/operations/batch_categorize.py --mode=dry_run --period=2025-11

# Apply if satisfied
uv run python scripts/operations/batch_categorize.py --mode=apply --period=2025-11
```

**After each batch:**
- Show results (matched, auto-applied, needs review, failed)
- Review medium-confidence suggestions
- Learn new rules from user corrections
- Track progress

### Stage 7: Post-Onboarding Health Check

After categorization, run health check to show improvement:

```bash
/smith:health --full
```

**Show before/after:**
- Baseline health score (from Stage 2)
- Current health score (after categorization)
- Improvement in each dimension
- Remaining priorities

### Stage 8: Next Steps & Usage Guide

Provide the user with ongoing usage patterns:

**Daily/Weekly:**
- Categorize new transactions: `/smith:categorize --mode=smart`

**Monthly:**
- Spending analysis: `/smith:analyze spending --period=YYYY-MM`
- Quick health check: `/smith:health --quick`

**Quarterly:**
- Tax deduction review: `/smith:tax deductions --period=YYYY-YY`

**Annual (EOFY):**
- Tax preparation: `/smith:tax eofy`

## Important Notes

- **Use `uv run python -u`** for all Python scripts (ensures unbuffered output)
- **Save onboarding state** in `data/onboarding_state.json` to resume if interrupted
- **Celebrate progress** - Show metrics like "1,245 → 87 uncategorized transactions"
- **Be patient** - First categorization can take time for large datasets

## Execution

Start with Stage 1 and proceed sequentially. After each stage, confirm user is ready to continue before proceeding.
```

**Step 2: Update INDEX.md**

Modify `.claude/commands/INDEX.md`:

Add entry:
```markdown
### agent-smith-onboard.md
**Description:** Interactive first-time setup wizard for Agent Smith

**Purpose:** Guide new users through discovery, template selection, customization, and initial categorization

**Usage:** `/smith:install`

**Stages:**
1. Prerequisites check
2. PocketSmith account discovery
3. Template selection and customization
4. Intelligence mode configuration
5. Incremental categorization
6. Health check and progress tracking
7. Ongoing usage guidance

**Created:** 2025-11-22
**Status:** Active
```

**Step 3: Test the command**

Run in Claude Code: `/smith:install`

Expected: Claude starts the onboarding wizard, greeting user and checking prerequisites

**Step 4: Commit**

```bash
git add .claude/commands/smith:install.md .claude/commands/INDEX.md
git commit -m "feat: add onboarding slash command with 8-stage workflow"
```

---

## Task 8: Onboarding State Tracking

**Files:**
- Create: `scripts/onboarding/state.py`
- Create: `tests/unit/test_onboarding_state.py`
- Create: `data/onboarding_state.json` (template)

**Step 1: Write the failing test**

Create `tests/unit/test_onboarding_state.py`:

```python
"""Tests for onboarding state tracking."""

import json
from pathlib import Path
from scripts.onboarding.state import OnboardingState, OnboardingStage


def test_onboarding_state_creation():
    """Test OnboardingState initialization."""
    state = OnboardingState()

    assert state.current_stage == OnboardingStage.NOT_STARTED
    assert state.completed_stages == []
    assert state.discovery_report is None
    assert state.template_selected is None


def test_onboarding_state_advance_stage():
    """Test advancing to next stage."""
    state = OnboardingState()

    state.advance_stage(OnboardingStage.DISCOVERY)
    assert state.current_stage == OnboardingStage.DISCOVERY
    assert OnboardingStage.NOT_STARTED in state.completed_stages

    state.advance_stage(OnboardingStage.TEMPLATE_SELECTION)
    assert state.current_stage == OnboardingStage.TEMPLATE_SELECTION
    assert OnboardingStage.DISCOVERY in state.completed_stages


def test_onboarding_state_save_load(tmp_path):
    """Test saving and loading state."""
    state_file = tmp_path / "onboarding_state.json"

    # Create and save state
    state = OnboardingState(state_file=state_file)
    state.advance_stage(OnboardingStage.DISCOVERY)
    state.discovery_report = {"user_id": 12345, "recommendation": "simple"}
    state.save()

    # Load state
    loaded_state = OnboardingState(state_file=state_file)
    loaded_state.load()

    assert loaded_state.current_stage == OnboardingStage.DISCOVERY
    assert loaded_state.discovery_report["user_id"] == 12345
    assert OnboardingStage.NOT_STARTED in loaded_state.completed_stages
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_onboarding_state.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'scripts.onboarding.state'"

**Step 3: Write minimal implementation**

Create `scripts/onboarding/state.py`:

```python
"""Onboarding state tracking."""

import json
from pathlib import Path
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict


class OnboardingStage(Enum):
    """Onboarding workflow stages."""

    NOT_STARTED = "not_started"
    PREREQUISITES = "prerequisites"
    DISCOVERY = "discovery"
    TEMPLATE_SELECTION = "template_selection"
    CUSTOMIZATION = "customization"
    INTELLIGENCE_CONFIG = "intelligence_config"
    CATEGORIZATION = "categorization"
    HEALTH_CHECK = "health_check"
    COMPLETE = "complete"


@dataclass
class OnboardingState:
    """Tracks progress through onboarding workflow."""

    current_stage: OnboardingStage = OnboardingStage.NOT_STARTED
    completed_stages: List[OnboardingStage] = field(default_factory=list)
    discovery_report: Optional[Dict[str, Any]] = None
    template_selected: Optional[str] = None
    intelligence_mode: Optional[str] = None
    tax_level: Optional[str] = None
    baseline_health_score: Optional[int] = None
    current_health_score: Optional[int] = None
    categorization_batches: List[Dict[str, Any]] = field(default_factory=list)
    state_file: Optional[Path] = None

    def __post_init__(self):
        """Initialize state file path if not provided."""
        if self.state_file is None:
            self.state_file = Path(__file__).parent.parent.parent / "data" / "onboarding_state.json"

    def advance_stage(self, next_stage: OnboardingStage) -> None:
        """Advance to next stage.

        Args:
            next_stage: The stage to advance to
        """
        if self.current_stage not in self.completed_stages:
            self.completed_stages.append(self.current_stage)
        self.current_stage = next_stage

    def save(self) -> None:
        """Save state to JSON file."""
        data = {
            "current_stage": self.current_stage.value,
            "completed_stages": [stage.value for stage in self.completed_stages],
            "discovery_report": self.discovery_report,
            "template_selected": self.template_selected,
            "intelligence_mode": self.intelligence_mode,
            "tax_level": self.tax_level,
            "baseline_health_score": self.baseline_health_score,
            "current_health_score": self.current_health_score,
            "categorization_batches": self.categorization_batches,
        }

        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """Load state from JSON file."""
        if not self.state_file.exists():
            return

        with open(self.state_file, "r") as f:
            data = json.load(f)

        self.current_stage = OnboardingStage(data.get("current_stage", "not_started"))
        self.completed_stages = [
            OnboardingStage(stage) for stage in data.get("completed_stages", [])
        ]
        self.discovery_report = data.get("discovery_report")
        self.template_selected = data.get("template_selected")
        self.intelligence_mode = data.get("intelligence_mode")
        self.tax_level = data.get("tax_level")
        self.baseline_health_score = data.get("baseline_health_score")
        self.current_health_score = data.get("current_health_score")
        self.categorization_batches = data.get("categorization_batches", [])

    def reset(self) -> None:
        """Reset onboarding state."""
        self.current_stage = OnboardingStage.NOT_STARTED
        self.completed_stages = []
        self.discovery_report = None
        self.template_selected = None
        self.intelligence_mode = None
        self.tax_level = None
        self.baseline_health_score = None
        self.current_health_score = None
        self.categorization_batches = []

        if self.state_file.exists():
            self.state_file.unlink()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_onboarding_state.py -v`

Expected: PASS (3 tests)

**Step 5: Create template state file**

Create `data/onboarding_state.json`:

```json
{
  "current_stage": "not_started",
  "completed_stages": [],
  "discovery_report": null,
  "template_selected": null,
  "intelligence_mode": null,
  "tax_level": null,
  "baseline_health_score": null,
  "current_health_score": null,
  "categorization_batches": []
}
```

**Step 6: Update .gitignore**

Ensure `data/onboarding_state.json` is tracked (it's a template), but add note:

```gitignore
# Onboarding state (tracked as template, but user's state will be overwritten)
```

**Step 7: Commit**

```bash
git add scripts/onboarding/state.py tests/unit/test_onboarding_state.py data/onboarding_state.json
git commit -m "feat: add onboarding state tracking with persistence"
```

---

## Task 9: Documentation - Onboarding User Guide

**Files:**
- Create: `docs/guides/onboarding-guide.md`
- Modify: `docs/INDEX.md`
- Modify: `README.md`

**Step 1: Create onboarding guide**

Create `docs/guides/onboarding-guide.md`:

```markdown
# Agent Smith Onboarding Guide

Welcome to Agent Smith! This guide walks you through your first-time setup and helps you get the most out of your PocketSmith integration.

## Before You Begin

**Prerequisites:**
1. ✅ Agent Smith installed (see [INSTALL.md](../../INSTALL.md))
2. ✅ PocketSmith account with API access
3. ✅ API key configured in `.env` file
4. ✅ Python 3.9+ and `uv` installed

**Time Required:** 30-60 minutes (depending on transaction volume)

---

## The Onboarding Journey

Agent Smith's onboarding is an 8-stage interactive process that:
- Discovers your PocketSmith account structure
- Recommends and customizes rule templates
- Incrementally categorizes your transactions
- Shows measurable improvement with health scores

### Quick Start

```bash
# Launch the onboarding wizard
/smith:install
```

Claude will guide you through each stage interactively.

---

## Stage 1: Prerequisites Check

**What happens:**
- Verifies Agent Smith installation
- Checks API key configuration
- Tests PocketSmith connection

**If something is missing:**
- Follow the prompts to complete installation
- Refer to [INSTALL.md](../../INSTALL.md) for detailed setup

**Time:** 2 minutes

---

## Stage 2: Discovery

**What happens:**
- Analyzes your PocketSmith account structure
- Counts accounts, categories, and transactions
- Identifies uncategorized transactions
- Calculates baseline health score

**What you'll see:**
```
✓ Connected as: your@email.com
✓ Accounts: 3 (Checking, Savings, Credit Card)
✓ Categories: 47
✓ Transactions: 2,387
✓ Uncategorized: 1,245 (52%)
✓ Date Range: Jan 2023 - Nov 2025
✓ Baseline Health Score: 45/100 (Critical)
✓ Recommended Template: shared-household
```

**Time:** 5-10 minutes (depends on data volume)

---

## Stage 3: Template Selection

**What happens:**
- Shows 4 template options
- Recommends best fit based on discovery
- Applies selected template to `data/rules.yaml`

**Templates:**

| Template | Best For | Includes |
|----------|----------|----------|
| **Simple** | Single person, basic tracking | Common categories, essential rules |
| **Separated Families** | Child support, shared custody | Kids expenses, contributor tracking |
| **Shared Household** | Couples, roommates | Shared expense tracking, approval workflows |
| **Advanced** | Business owners, investors | Tax optimization, investment tracking, CGT |

**What you'll do:**
- Review the recommendation
- Choose a template (or browse all)
- Confirm application

**Time:** 3-5 minutes

---

## Stage 4: Template Customization

**What happens:**
- Guides you to customize the template for your needs

**Customizations needed:**

1. **Account Mapping**
   - Template uses generic names like "Shared Bills", "Personal"
   - Update to match your actual account names

2. **Category Validation**
   - Check if template categories exist in PocketSmith
   - Create missing categories or map to existing ones

3. **Merchant Localization**
   - Template has Australian merchants (WOOLWORTHS, COLES)
   - Update for your region (SAFEWAY, KROGER, etc.)

**How to customize:**
- Edit `data/rules.yaml` manually (for now)
- Future versions will have interactive customization tool

**Example:**
```yaml
# Before (template)
- type: category
  patterns: [WOOLWORTHS, COLES]
  category: Food & Dining > Groceries

# After (customized for US)
- type: category
  patterns: [SAFEWAY, KROGER, WHOLE FOODS]
  category: Food & Dining > Groceries
```

**Time:** 10-20 minutes

---

## Stage 5: Intelligence Mode Selection

**What happens:**
- Configure AI categorization behavior
- Set tax intelligence level

**Categorization Mode:**

| Mode | Auto-Apply Threshold | Best For |
|------|---------------------|----------|
| Conservative | 100% (manual approval all) | First-time setup, learning |
| **Smart** (default) | ≥90% confidence | Most users, balanced |
| Aggressive | ≥80% confidence | High volume, trust AI |

**Tax Intelligence Level:**

| Level | Capabilities | Best For |
|-------|-------------|----------|
| Reference | ATO category mapping, basic reports | Users with accountants |
| **Smart** (default) | Deduction detection, thresholds | Most taxpayers |
| Full | BAS prep, compliance checks | Business owners, power users |

**Time:** 2 minutes

---

## Stage 6: Incremental Categorization

**What happens:**
- Categorize transactions in manageable batches
- Start recent, expand to historical

**Recommended Strategy:**

1. **Current Month** (test rules on small dataset)
   ```bash
   uv run python scripts/operations/batch_categorize.py --mode=dry_run --period=2025-11
   uv run python scripts/operations/batch_categorize.py --mode=apply --period=2025-11
   ```

2. **Last 3 Months** (validate at scale)
   ```bash
   uv run python scripts/operations/batch_categorize.py --mode=apply --period=2025-09:2025-11
   ```

3. **Full Backfill** (complete the archive)
   ```bash
   uv run python scripts/operations/batch_categorize.py --mode=apply --period=2023-01:2025-11
   ```

**After Each Batch:**
- Review results (matched, auto-applied, needs review)
- Approve medium-confidence suggestions
- Agent Smith learns new rules from your corrections

**Time:** 20-60 minutes (depends on volume and mode)

---

## Stage 7: Health Check & Progress

**What happens:**
- Run post-categorization health check
- Show before/after improvement
- Identify remaining priorities

**What you'll see:**
```
═══════════════════════════════════════════════
AGENT SMITH HEALTH CHECK - PROGRESS REPORT
═══════════════════════════════════════════════

Baseline (before):    45/100 (Critical)
Current:              78/100 (Good) ⬆ +33 points

Improvements:
• Data Quality:        42 → 88 (+46) ✅
• Rule Engine:         15 → 72 (+57) ✅
• Category Structure:  58 → 81 (+23) ✅

Remaining priorities:
1. Review tax category mappings
2. Add 3 more rules for recurring merchants
3. Create budgets for top 5 categories
```

**Time:** 5 minutes

---

## Stage 8: Ongoing Usage

**What happens:**
- Receive guidance on regular Agent Smith usage
- Get quick reference for common operations

**Daily/Weekly:**
```bash
/smith:categorize --mode=smart --period=2025-11
```

**Monthly:**
```bash
/smith:analyze spending --period=2025-11
/smith:health --quick
```

**Quarterly:**
```bash
/smith:tax deductions --period=2024-25
```

**Annual (EOFY):**
```bash
/smith:tax eofy
```

**Time:** 2 minutes

---

## Troubleshooting

### Onboarding Interrupted

If onboarding is interrupted, your progress is saved in `data/onboarding_state.json`.

**Resume:**
```bash
/smith:install
```

Claude will detect saved state and offer to resume from where you left off.

**Start Over:**
```bash
uv run python -c "from scripts.onboarding.state import OnboardingState; OnboardingState().reset()"
/smith:install
```

### Discovery Fails

**Problem:** "Error during discovery: ..."

**Solutions:**
- Check `.env` has valid `POCKETSMITH_API_KEY`
- Verify PocketSmith account has API access enabled
- Check internet connection to api.pocketsmith.com

### Template Customization Unclear

**Problem:** Not sure how to customize `data/rules.yaml`

**Solutions:**
- Review [Unified Rules Guide](unified-rules-guide.md) for YAML syntax
- Check [Example Files](../examples/) for patterns
- Start with dry-run to test rules before applying

### Categorization Too Slow

**Problem:** Batch categorization taking too long

**Solutions:**
- Use smaller date ranges (1 month at a time)
- Switch to "Aggressive" mode for faster auto-apply
- Run in background with progress monitoring

---

## Next Steps

After completing onboarding:

1. **Set Up Alerts**
   - Weekly budget reviews
   - Monthly trend analysis
   - Tax deadline reminders

2. **Create Budgets**
   - Use health check recommendations
   - Focus on top spending categories
   - Track vs. budget monthly

3. **Optimize Rules**
   - Review rule performance metrics
   - Add rules for recurring merchants
   - Refine confidence scores

4. **Explore Advanced Features**
   - Scenario analysis
   - Tax optimization
   - Investment tracking

---

## Getting Help

- **Documentation:** [docs/](../INDEX.md)
- **API Reference:** [ai_docs/pocketsmith-api-documentation.md](../../ai_docs/pocketsmith-api-documentation.md)
- **Health Check Guide:** [health-check-guide.md](health-check-guide.md)
- **GitHub Issues:** [github.com/slamb2k/agent-smith/issues](https://github.com/slamb2k/agent-smith/issues)

---

**Welcome to Agent Smith! Let's transform your PocketSmith into an intelligent financial system.**
```

**Step 2: Update docs INDEX**

Modify `docs/INDEX.md`:

Add entry:
```markdown
### onboarding-guide.md
**Description:** Complete user guide for first-time Agent Smith setup

**Contents:**
- 8-stage onboarding journey walkthrough
- Prerequisites and time estimates
- Step-by-step instructions for each stage
- Template selection guidance
- Customization examples
- Troubleshooting common issues
- Next steps after onboarding

**Created:** 2025-11-22
**Target Audience:** New Agent Smith users
**Related:** INSTALL.md, unified-rules-guide.md, health-check-guide.md
```

**Step 3: Update README**

Modify `README.md` "Quick Start" section:

```markdown
## Quick Start

### Prerequisites

- Python 3.9+
- PocketSmith account with API access
- Developer API key from PocketSmith (Settings > Security)

### Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

### First-Time Setup

**Launch the interactive onboarding wizard:**

```bash
/smith:install
```

This guided 8-stage process will:
1. Discover your PocketSmith account structure
2. Recommend and apply a rule template
3. Help you customize rules for your needs
4. Configure intelligence modes
5. Incrementally categorize your transactions
6. Show measurable improvement with health scores
7. Provide ongoing usage guidance

**Time required:** 30-60 minutes

**For detailed walkthrough:** See [Onboarding Guide](docs/guides/onboarding-guide.md)
```

**Step 4: Commit**

```bash
git add docs/guides/onboarding-guide.md docs/INDEX.md README.md
git commit -m "docs: add comprehensive onboarding user guide"
```

---

## Task 10: Update Installation Documentation

**Files:**
- Modify: `INSTALL.md`

**Step 1: Update INSTALL.md**

Modify `INSTALL.md`, add section after "Verification":

```markdown
## First-Time Setup

After installation and verification, run the interactive onboarding wizard:

```bash
/smith:install
```

**What it does:**
- Analyzes your PocketSmith account structure
- Recommends the best rule template for your needs
- Guides you through customization
- Incrementally categorizes your transactions
- Shows measurable improvement with health scores

**Time required:** 30-60 minutes

**Alternative:** Run components individually:

```bash
# 1. Discovery - Analyze your PocketSmith account
uv run python -u scripts/onboarding/discovery.py

# 2. Template Selection - Choose rule template
uv run python scripts/setup/template_selector.py

# 3. Customize data/rules.yaml manually

# 4. Categorize transactions
uv run python scripts/operations/batch_categorize.py --mode=dry_run --period=2025-11
uv run python scripts/operations/batch_categorize.py --mode=apply --period=2025-11

# 5. Health Check
/smith:health --full
```

**For detailed walkthrough:** See [Onboarding Guide](docs/guides/onboarding-guide.md)
```

**Step 2: Commit**

```bash
git add INSTALL.md
git commit -m "docs: add first-time setup section to installation guide"
```

---

## Summary

This implementation plan creates a comprehensive onboarding system for Agent Smith with:

✅ **Discovery Script** - Analyzes PocketSmith account structure, recommends templates
✅ **Baseline Health Check** - Establishes "before" metrics to show improvement
✅ **Onboarding Slash Command** - `/smith:install` guides users through 8-stage workflow
✅ **State Tracking** - Saves progress, allows resume if interrupted
✅ **Documentation** - Complete user guide with troubleshooting

**Not Implemented (Future Enhancement):**
- ❌ Interactive account mapping tool
- ❌ Category validator with auto-creation
- ❌ Merchant localization script
- ❌ Batch strategy optimizer
- ❌ Progress visualization dashboard

**Testing Coverage:**
- Unit tests: Discovery, state tracking, baseline health
- Integration tests: Discovery with real API

**Files Created:** 9 new files
**Files Modified:** 5 existing files
**Estimated Implementation Time:** 3-4 hours

---

## Execution Notes

**Important:**
- Use `uv run python -u` for all Python scripts (unbuffered output)
- Test each task independently before proceeding
- Commit after each task (frequent commits)
- Run integration tests with real API to verify

**Dependencies:**
- Requires existing health check system (Phase 8)
- Requires batch categorization (Phase 2-6)
- Requires template system (already exists)

**Post-Implementation:**
- Update changelog
- Create release notes
- Test full onboarding journey end-to-end
- Gather user feedback for improvements
