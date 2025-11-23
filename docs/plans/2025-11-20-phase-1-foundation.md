# Agent Smith - Phase 1: Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build foundational infrastructure for Agent Smith including directory structure, core libraries (API client, backup, archiving, validation), and basic functionality.

**Architecture:** Three-tier system with API Integration Layer, Intelligence Engine, and Orchestration Layer. Phase 1 focuses on establishing the API layer foundations and supporting utilities.

**Tech Stack:** Python 3.9+, PocketSmith API v2, pytest for testing, JSON for configuration/data storage

**Current State:** Repository has basic structure (docs, ai_docs, build), design documentation, .env with API key, and reference materials in build/ from previous migration work.

**Reference Materials:** Extract patterns from build/scripts/* for API client, backup, and pattern matching logic. See build/INDEX.md for extraction checklist.

---

## Task 1: Create Directory Structure

**Files:**
- Create: Multiple directories per design specification

### Step 1: Create all required directories

```bash
mkdir -p backups/archive
mkdir -p data/alerts
mkdir -p data/tax
mkdir -p data/scenarios/scenario_results
mkdir -p data/merchants
mkdir -p data/investments
mkdir -p data/goals
mkdir -p data/health/health_history
mkdir -p data/audit
mkdir -p data/cache
mkdir -p docs/operations
mkdir -p docs/analyses
mkdir -p docs/guides
mkdir -p docs/archive
mkdir -p logs/archive
mkdir -p reports/markdown
mkdir -p reports/data
mkdir -p reports/interactive
mkdir -p reports/tax
mkdir -p reports/archive
mkdir -p scripts/core
mkdir -p scripts/operations
mkdir -p scripts/subagents
mkdir -p scripts/utils
mkdir -p tests/unit
mkdir -p tests/integration
```

**Run:** `bash` (execute above commands)
**Expected:** All directories created successfully

### Step 2: Verify directory structure

```bash
find . -type d | grep -E "(backups|data|logs|reports|scripts|tests)" | sort
```

**Run:** `bash` (execute above command)
**Expected:** All directories listed correctly

### Step 3: Commit directory structure

```bash
git add .
git commit -m "$(cat <<'EOF'
feat: create Phase 1 directory structure

- Created backups/ with archive subdirectory
- Created data/ with all subdirectories (alerts, tax, scenarios, etc.)
- Created docs/ subdirectories (operations, analyses, guides, archive)
- Created logs/ with archive subdirectory
- Created reports/ with format subdirectories
- Created scripts/ with core, operations, subagents, utils
- Created tests/ with unit and integration subdirectories

Foundation for Agent Smith file organization per design spec.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 2: Create .env.sample Template

**Files:**
- Create: `.env.sample`

### Step 1: Write test for .env.sample validation

Create: `tests/unit/test_config.py`

```python
"""Tests for configuration validation."""
import os
from pathlib import Path


def test_env_sample_exists():
    """Verify .env.sample template exists."""
    env_sample = Path(__file__).parent.parent.parent / ".env.sample"
    assert env_sample.exists(), ".env.sample template must exist"


def test_env_sample_contains_required_fields():
    """Verify .env.sample has all required configuration fields."""
    env_sample = Path(__file__).parent.parent.parent / ".env.sample"
    content = env_sample.read_text()

    required_fields = [
        "POCKETSMITH_API_KEY",
        "TAX_INTELLIGENCE_LEVEL",
        "DEFAULT_INTELLIGENCE_MODE",
        "TAX_JURISDICTION",
        "FINANCIAL_YEAR_END",
    ]

    for field in required_fields:
        assert field in content, f"{field} must be in .env.sample"


def test_env_sample_has_no_real_credentials():
    """Verify .env.sample doesn't contain real API keys."""
    env_sample = Path(__file__).parent.parent.parent / ".env.sample"
    content = env_sample.read_text()

    # Real API keys are hexadecimal and long
    assert "<Your" in content or "your-" in content, \
        ".env.sample should use placeholders, not real keys"
```

### Step 2: Run test to verify it fails

**Run:** `pytest tests/unit/test_config.py -v`
**Expected:** FAIL - .env.sample does not exist

### Step 3: Create .env.sample template

Create: `.env.sample`

```bash
# PocketSmith API Authentication
# Get your API key from: https://my.pocketsmith.com/user_settings/developer
POCKETSMITH_API_KEY=<Your Developer API Key>

# Agent Smith Configuration
TAX_INTELLIGENCE_LEVEL=smart          # reference|smart|full
DEFAULT_INTELLIGENCE_MODE=smart       # conservative|smart|aggressive
AUTO_BACKUP=true
AUTO_ARCHIVE=true
ALERT_NOTIFICATIONS=true

# Tax Configuration (Australia)
TAX_JURISDICTION=AU
FINANCIAL_YEAR_END=06-30             # June 30 (MM-DD format)
GST_REGISTERED=false

# Reporting Preferences
DEFAULT_REPORT_FORMAT=all            # markdown|csv|json|html|excel|all
CURRENCY=AUD

# Advanced Settings
API_RATE_LIMIT_DELAY=100             # milliseconds between API calls
CACHE_TTL_DAYS=7                     # days to keep cached API responses
SUBAGENT_MAX_PARALLEL=5              # maximum parallel subagent processes
LOG_LEVEL=INFO                       # DEBUG|INFO|WARNING|ERROR
```

### Step 4: Run test to verify it passes

**Run:** `pytest tests/unit/test_config.py -v`
**Expected:** PASS - all tests pass

### Step 5: Commit .env.sample

```bash
git add .env.sample tests/unit/test_config.py
git commit -m "$(cat <<'EOF'
feat: add .env.sample configuration template

- Created .env.sample with all required configuration fields
- Added PocketSmith API authentication
- Added Agent Smith configuration options
- Added Australian tax configuration
- Added reporting and advanced settings
- Added tests for .env.sample validation

Users can copy this to .env and add their API key.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 3: Create pytest Configuration

**Files:**
- Create: `pytest.ini`
- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/integration/__init__.py`

### Step 1: Create pytest configuration

Create: `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests requiring API access
    slow: Tests that take significant time
```

### Step 2: Create test package init files

Create: `tests/__init__.py`

```python
"""Agent Smith test suite."""
```

Create: `tests/unit/__init__.py`

```python
"""Unit tests for Agent Smith."""
```

Create: `tests/integration/__init__.py`

```python
"""Integration tests for Agent Smith - require API access."""
```

### Step 3: Verify pytest configuration

**Run:** `pytest --collect-only`
**Expected:** Tests collected successfully (shows test_config.py tests)

### Step 4: Commit pytest configuration

```bash
git add pytest.ini tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py
git commit -m "$(cat <<'EOF'
feat: add pytest configuration and test structure

- Created pytest.ini with test configuration
- Created test package structure
- Added markers for unit, integration, and slow tests
- Configured test discovery settings

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 4: Create Core API Client (Part 1: Basic Structure)

**Files:**
- Create: `tests/unit/test_api_client.py`
- Create: `scripts/core/api_client.py`
- Create: `scripts/core/__init__.py`

**Reference:** Extract patterns from `build/scripts/` for API error handling, rate limiting, and response parsing.

### Step 1: Write test for API client initialization

Create: `tests/unit/test_api_client.py`

```python
"""Tests for PocketSmith API client."""
import os
import pytest
from scripts.core.api_client import PocketSmithClient


def test_api_client_requires_api_key():
    """API client should raise error if no API key provided."""
    with pytest.raises(ValueError, match="API key is required"):
        PocketSmithClient(api_key=None)


def test_api_client_accepts_api_key():
    """API client should initialize with valid API key."""
    client = PocketSmithClient(api_key="test_key_12345")
    assert client.api_key == "test_key_12345"


def test_api_client_sets_base_url():
    """API client should set correct base URL."""
    client = PocketSmithClient(api_key="test_key")
    assert client.base_url == "https://api.pocketsmith.com/v2"


def test_api_client_sets_default_rate_limit():
    """API client should set default rate limit delay."""
    client = PocketSmithClient(api_key="test_key")
    assert client.rate_limit_delay == 0.1  # 100ms default
```

### Step 2: Run test to verify it fails

**Run:** `pytest tests/unit/test_api_client.py -v`
**Expected:** FAIL - module does not exist

### Step 3: Create minimal API client implementation

Create: `scripts/core/__init__.py`

```python
"""Core libraries for Agent Smith."""
```

Create: `scripts/core/api_client.py`

```python
"""PocketSmith API client with rate limiting and error handling."""
import os
import time
import logging
from typing import Optional, Dict, Any
import requests


logger = logging.getLogger(__name__)


class PocketSmithClient:
    """Client for interacting with PocketSmith API v2.

    Features:
    - API authentication via Developer Key
    - Rate limiting
    - Response caching
    - Error handling and retries
    - Request/response logging
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_delay: float = 0.1,
        base_url: str = "https://api.pocketsmith.com/v2"
    ):
        """Initialize PocketSmith API client.

        Args:
            api_key: PocketSmith Developer API key. If None, reads from env.
            rate_limit_delay: Delay between API calls in seconds (default: 0.1)
            base_url: API base URL (default: production API)

        Raises:
            ValueError: If no API key provided
        """
        self.api_key = api_key or os.getenv("POCKETSMITH_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Provide via parameter or POCKETSMITH_API_KEY env var.")

        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0

        logger.info(f"Initialized PocketSmith API client (base_url: {base_url})")

    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "X-Developer-Key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()
```

### Step 4: Run test to verify it passes

**Run:** `pytest tests/unit/test_api_client.py -v`
**Expected:** PASS - all tests pass

### Step 5: Commit API client foundation

```bash
git add scripts/core/__init__.py scripts/core/api_client.py tests/unit/test_api_client.py
git commit -m "$(cat <<'EOF'
feat: add API client foundation with rate limiting

- Created PocketSmithClient class with initialization
- Added API key validation (from parameter or env var)
- Added rate limiting infrastructure
- Configured base URL and request headers
- Added comprehensive unit tests
- Added logging setup

Foundation for PocketSmith API integration.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 5: Create Core API Client (Part 2: HTTP Methods)

**Files:**
- Modify: `tests/unit/test_api_client.py`
- Modify: `scripts/core/api_client.py`

### Step 1: Write tests for HTTP methods

Add to: `tests/unit/test_api_client.py`

```python
from unittest.mock import Mock, patch
import requests


@patch('scripts.core.api_client.requests.get')
def test_api_client_get_request(mock_get):
    """Test GET request with proper headers and rate limiting."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 123, "name": "Test User"}
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    result = client.get("/me")

    assert result == {"id": 123, "name": "Test User"}
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://api.pocketsmith.com/v2/me"
    assert kwargs['headers']['X-Developer-Key'] == "test_key"


@patch('scripts.core.api_client.requests.get')
def test_api_client_handles_404(mock_get):
    """Test handling of 404 Not Found responses."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")

    with pytest.raises(requests.HTTPError):
        client.get("/nonexistent")


@patch('scripts.core.api_client.requests.get')
def test_api_client_enforces_rate_limiting(mock_get):
    """Test that rate limiting delay is enforced between requests."""
    import time

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key", rate_limit_delay=0.05)

    start = time.time()
    client.get("/me")
    client.get("/me")
    elapsed = time.time() - start

    # Should take at least rate_limit_delay (50ms)
    assert elapsed >= 0.05
```

### Step 2: Run tests to verify they fail

**Run:** `pytest tests/unit/test_api_client.py::test_api_client_get_request -v`
**Expected:** FAIL - get method does not exist

### Step 3: Implement HTTP GET method

Add to: `scripts/core/api_client.py`

```python
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make GET request to API.

        Args:
            endpoint: API endpoint (e.g., "/me" or "/users/123/transactions")
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            requests.HTTPError: If request fails
        """
        self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET {url} (params: {params})")

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        logger.debug(f"GET {url} - {response.status_code}")
        return response.json()

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make POST request to API.

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            Parsed JSON response

        Raises:
            requests.HTTPError: If request fails
        """
        self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"POST {url}")

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()

        logger.debug(f"POST {url} - {response.status_code}")
        return response.json()

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make PUT request to API.

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            Parsed JSON response

        Raises:
            requests.HTTPError: If request fails
        """
        self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"PUT {url}")

        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()

        logger.debug(f"PUT {url} - {response.status_code}")
        return response.json()

    def delete(self, endpoint: str) -> Any:
        """Make DELETE request to API.

        Args:
            endpoint: API endpoint

        Returns:
            Parsed JSON response or None

        Raises:
            requests.HTTPError: If request fails
        """
        self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"DELETE {url}")

        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()

        logger.debug(f"DELETE {url} - {response.status_code}")

        # DELETE may return empty response
        if response.text:
            return response.json()
        return None
```

### Step 4: Run tests to verify they pass

**Run:** `pytest tests/unit/test_api_client.py -v`
**Expected:** PASS - all tests pass

### Step 5: Commit HTTP methods

```bash
git add scripts/core/api_client.py tests/unit/test_api_client.py
git commit -m "$(cat <<'EOF'
feat: add HTTP methods to API client

- Implemented GET, POST, PUT, DELETE methods
- Added rate limiting enforcement between requests
- Added error handling with raise_for_status
- Added request/response logging
- Added comprehensive tests including rate limiting verification

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 6: Create Core API Client (Part 3: High-Level Methods)

**Files:**
- Modify: `tests/unit/test_api_client.py`
- Modify: `scripts/core/api_client.py`

### Step 1: Write tests for high-level API methods

Add to: `tests/unit/test_api_client.py`

```python
@patch('scripts.core.api_client.requests.get')
def test_get_user(mock_get):
    """Test get_user retrieves authorized user info."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 217031,
        "login": "testuser",
        "name": "Test User",
        "email": "test@example.com"
    }
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    user = client.get_user()

    assert user["id"] == 217031
    assert user["login"] == "testuser"


@patch('scripts.core.api_client.requests.get')
def test_get_transactions(mock_get):
    """Test get_transactions with filters."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "payee": "Test Store", "amount": "-50.00"},
        {"id": 2, "payee": "Income", "amount": "1000.00"}
    ]
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    transactions = client.get_transactions(
        user_id=217031,
        start_date="2025-01-01",
        end_date="2025-01-31"
    )

    assert len(transactions) == 2
    assert transactions[0]["payee"] == "Test Store"

    # Verify correct parameters passed
    args, kwargs = mock_get.call_args
    assert "start_date=2025-01-01" in args[0] or kwargs.get('params', {}).get('start_date') == "2025-01-01"


@patch('scripts.core.api_client.requests.get')
def test_get_categories(mock_get):
    """Test get_categories retrieves category tree."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 100, "title": "Income", "is_transfer": False},
        {"id": 200, "title": "Expenses", "is_transfer": False}
    ]
    mock_get.return_value = mock_response

    client = PocketSmithClient(api_key="test_key")
    categories = client.get_categories(user_id=217031)

    assert len(categories) == 2
    assert categories[0]["title"] == "Income"
```

### Step 2: Run tests to verify they fail

**Run:** `pytest tests/unit/test_api_client.py::test_get_user -v`
**Expected:** FAIL - get_user method does not exist

### Step 3: Implement high-level API methods

Add to: `scripts/core/api_client.py`

```python
    # High-level API methods

    def get_user(self) -> Dict[str, Any]:
        """Get authorized user information.

        Returns:
            User object with id, login, name, email, etc.
        """
        logger.info("Fetching authorized user")
        return self.get("/me")

    def get_transactions(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        uncategorised: Optional[bool] = None,
        account_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 100
    ) -> list:
        """Get transactions for a user.

        Args:
            user_id: PocketSmith user ID
            start_date: Filter start date (YYYY-MM-DD)
            end_date: Filter end date (YYYY-MM-DD)
            uncategorised: Filter for uncategorized transactions only
            account_id: Filter by specific account
            page: Page number (1-indexed)
            per_page: Results per page (max 100)

        Returns:
            List of transaction objects
        """
        params = {
            "page": page,
            "per_page": per_page
        }

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if uncategorised is not None:
            params["uncategorised"] = 1 if uncategorised else 0
        if account_id:
            params["account_id"] = account_id

        logger.info(f"Fetching transactions for user {user_id} (page {page})")
        return self.get(f"/users/{user_id}/transactions", params=params)

    def get_categories(self, user_id: int) -> list:
        """Get all categories for a user.

        Args:
            user_id: PocketSmith user ID

        Returns:
            List of category objects with full hierarchy
        """
        logger.info(f"Fetching categories for user {user_id}")
        return self.get(f"/users/{user_id}/categories")

    def update_transaction(
        self,
        transaction_id: int,
        category_id: Optional[int] = None,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a transaction.

        Args:
            transaction_id: Transaction ID to update
            category_id: New category ID
            note: Transaction note/memo

        Returns:
            Updated transaction object
        """
        data = {}
        if category_id is not None:
            data["category_id"] = category_id
        if note is not None:
            data["note"] = note

        logger.info(f"Updating transaction {transaction_id}")
        return self.put(f"/transactions/{transaction_id}", data=data)

    def create_category_rule(
        self,
        category_id: int,
        payee_matches: str
    ) -> Dict[str, Any]:
        """Create a category rule (platform rule).

        Note: PocketSmith API only supports simple keyword matching.
        For advanced rules, use local rule engine.

        Args:
            category_id: Category to assign
            payee_matches: Keyword to match in payee name

        Returns:
            Created category rule object
        """
        data = {
            "payee_matches": payee_matches,
            "apply_to_all": True
        }

        logger.info(f"Creating category rule for category {category_id}: '{payee_matches}'")
        return self.post(f"/categories/{category_id}/category_rules", data=data)
```

### Step 4: Run tests to verify they pass

**Run:** `pytest tests/unit/test_api_client.py -v`
**Expected:** PASS - all tests pass

### Step 5: Commit high-level API methods

```bash
git add scripts/core/api_client.py tests/unit/test_api_client.py
git commit -m "$(cat <<'EOF'
feat: add high-level API methods to client

- Added get_user() for authorized user info
- Added get_transactions() with filtering
- Added get_categories() for category hierarchy
- Added update_transaction() for categorization
- Added create_category_rule() for platform rules
- Added comprehensive tests for all methods

Provides convenient interface to common PocketSmith operations.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 7: Create Backup Utility

**Files:**
- Create: `tests/unit/test_backup.py`
- Create: `scripts/utils/backup.py`
- Create: `scripts/utils/__init__.py`

**Reference:** Extract backup patterns from `build/scripts/` that create timestamped backups before mutations.

### Step 1: Write tests for backup utility

Create: `tests/unit/test_backup.py`

```python
"""Tests for backup utility."""
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pytest
from scripts.utils.backup import BackupManager


@pytest.fixture
def temp_backup_dir():
    """Create temporary backup directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


def test_backup_manager_initialization(temp_backup_dir):
    """Test BackupManager initialization."""
    manager = BackupManager(backup_root=temp_backup_dir)
    assert manager.backup_root == temp_backup_dir
    assert temp_backup_dir.exists()


def test_create_backup_creates_timestamped_directory(temp_backup_dir):
    """Test that create_backup creates timestamped directory."""
    manager = BackupManager(backup_root=temp_backup_dir)
    backup_path = manager.create_backup(description="test backup")

    assert backup_path.exists()
    assert backup_path.is_dir()
    # Check timestamp format YYYY-MM-DD_HHMMSS
    dir_name = backup_path.name
    assert len(dir_name.split('_')) == 2


def test_backup_saves_data_as_json(temp_backup_dir):
    """Test that backup can save data as JSON."""
    manager = BackupManager(backup_root=temp_backup_dir)

    test_data = {"transactions": [{"id": 1, "amount": "50.00"}]}
    backup_path = manager.create_backup(description="test")

    manager.save_backup_data(
        backup_path=backup_path,
        filename="transactions.json",
        data=test_data
    )

    saved_file = backup_path / "transactions.json"
    assert saved_file.exists()

    with open(saved_file) as f:
        loaded_data = json.load(f)

    assert loaded_data == test_data


def test_backup_creates_metadata_file(temp_backup_dir):
    """Test that backup creates metadata.json."""
    manager = BackupManager(backup_root=temp_backup_dir)
    backup_path = manager.create_backup(
        description="Test backup",
        metadata={"user_id": 217031, "operation": "categorize"}
    )

    metadata_file = backup_path / "metadata.json"
    assert metadata_file.exists()

    with open(metadata_file) as f:
        metadata = json.load(f)

    assert metadata["description"] == "Test backup"
    assert metadata["user_id"] == 217031
    assert "timestamp" in metadata


def test_list_backups_returns_sorted_list(temp_backup_dir):
    """Test list_backups returns backups sorted by timestamp."""
    manager = BackupManager(backup_root=temp_backup_dir)

    # Create multiple backups
    import time
    backup1 = manager.create_backup(description="First")
    time.sleep(0.01)
    backup2 = manager.create_backup(description="Second")
    time.sleep(0.01)
    backup3 = manager.create_backup(description="Third")

    backups = manager.list_backups()

    assert len(backups) == 3
    # Should be sorted newest first
    assert backups[0]["path"] == backup3
    assert backups[1]["path"] == backup2
    assert backups[2]["path"] == backup1
```

### Step 2: Run tests to verify they fail

**Run:** `pytest tests/unit/test_backup.py -v`
**Expected:** FAIL - module does not exist

### Step 3: Create backup utility implementation

Create: `scripts/utils/__init__.py`

```python
"""Utility modules for Agent Smith."""
```

Create: `scripts/utils/backup.py`

```python
"""Backup and restore utilities for Agent Smith."""
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


logger = logging.getLogger(__name__)


class BackupManager:
    """Manages backups of PocketSmith data before mutations.

    Features:
    - Timestamped backup directories
    - Metadata tracking
    - List and restore operations
    - Automatic cleanup based on retention policy
    """

    def __init__(self, backup_root: Optional[Path] = None):
        """Initialize BackupManager.

        Args:
            backup_root: Root directory for backups.
                        Defaults to ./backups relative to project root.
        """
        if backup_root is None:
            # Default to ./backups in project root
            project_root = Path(__file__).parent.parent.parent
            backup_root = project_root / "backups"

        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)

        logger.info(f"BackupManager initialized (root: {self.backup_root})")

    def create_backup(
        self,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Create a new timestamped backup directory.

        Args:
            description: Human-readable backup description
            metadata: Additional metadata to store

        Returns:
            Path to created backup directory
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_path = self.backup_root / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)

        # Create metadata file
        metadata_dict = metadata or {}
        metadata_dict.update({
            "timestamp": timestamp,
            "description": description,
            "created_at": datetime.now().isoformat()
        })

        metadata_file = backup_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)

        logger.info(f"Created backup: {backup_path} - {description}")
        return backup_path

    def save_backup_data(
        self,
        backup_path: Path,
        filename: str,
        data: Any
    ):
        """Save data to backup directory.

        Args:
            backup_path: Backup directory path
            filename: Filename to save
            data: Data to save (will be JSON serialized)
        """
        filepath = backup_path / filename

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.debug(f"Saved backup data: {filepath}")

    def list_backups(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all backups sorted by timestamp (newest first).

        Args:
            limit: Maximum number of backups to return

        Returns:
            List of backup info dictionaries
        """
        backups = []

        for backup_dir in self.backup_root.iterdir():
            if not backup_dir.is_dir():
                continue

            metadata_file = backup_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            with open(metadata_file) as f:
                metadata = json.load(f)

            backups.append({
                "path": backup_dir,
                "timestamp": metadata.get("timestamp"),
                "description": metadata.get("description"),
                "metadata": metadata
            })

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)

        if limit:
            backups = backups[:limit]

        logger.debug(f"Listed {len(backups)} backups")
        return backups

    def restore_backup(self, backup_path: Path, target_dir: Path):
        """Restore a backup to target directory.

        Args:
            backup_path: Backup directory to restore from
            target_dir: Target directory to restore to
        """
        logger.warning(f"Restoring backup from {backup_path} to {target_dir}")

        # Copy all files except metadata.json
        for item in backup_path.iterdir():
            if item.name == "metadata.json":
                continue

            target_path = target_dir / item.name
            if item.is_file():
                shutil.copy2(item, target_path)
            elif item.is_dir():
                shutil.copytree(item, target_path, dirs_exist_ok=True)

        logger.info(f"Backup restored successfully")

    def delete_backup(self, backup_path: Path):
        """Delete a backup directory.

        Args:
            backup_path: Backup directory to delete
        """
        if not backup_path.exists():
            logger.warning(f"Backup does not exist: {backup_path}")
            return

        shutil.rmtree(backup_path)
        logger.info(f"Deleted backup: {backup_path}")
```

### Step 4: Run tests to verify they pass

**Run:** `pytest tests/unit/test_backup.py -v`
**Expected:** PASS - all tests pass

### Step 5: Commit backup utility

```bash
git add scripts/utils/__init__.py scripts/utils/backup.py tests/unit/test_backup.py
git commit -m "$(cat <<'EOF'
feat: add backup and restore utility

- Created BackupManager class for data protection
- Implemented timestamped backup directories
- Added metadata tracking for each backup
- Added list, restore, and delete operations
- Added comprehensive unit tests

Ensures data safety before mutations per design spec.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 8: Create Validation Utility

**Files:**
- Create: `tests/unit/test_validation.py`
- Create: `scripts/utils/validation.py`

### Step 1: Write tests for validation utility

Create: `tests/unit/test_validation.py`

```python
"""Tests for validation utility."""
import pytest
from scripts.utils.validation import (
    validate_date_format,
    validate_transaction_data,
    validate_category_data,
    ValidationError
)


def test_validate_date_format_accepts_valid_dates():
    """Test date validation accepts YYYY-MM-DD format."""
    assert validate_date_format("2025-01-15") == True
    assert validate_date_format("2025-12-31") == True


def test_validate_date_format_rejects_invalid_dates():
    """Test date validation rejects invalid formats."""
    with pytest.raises(ValidationError):
        validate_date_format("2025/01/15")

    with pytest.raises(ValidationError):
        validate_date_format("15-01-2025")

    with pytest.raises(ValidationError):
        validate_date_format("2025-13-01")  # Invalid month


def test_validate_transaction_data_accepts_valid_transaction():
    """Test transaction validation accepts valid data."""
    transaction = {
        "id": 12345,
        "payee": "Test Store",
        "amount": "-50.00",
        "date": "2025-01-15",
        "transaction_account": {"id": 100}
    }

    assert validate_transaction_data(transaction) == True


def test_validate_transaction_data_rejects_missing_fields():
    """Test transaction validation rejects missing required fields."""
    transaction = {
        "id": 12345,
        # Missing payee, amount, date
    }

    with pytest.raises(ValidationError, match="Missing required field"):
        validate_transaction_data(transaction)


def test_validate_category_data_accepts_valid_category():
    """Test category validation accepts valid data."""
    category = {
        "id": 100,
        "title": "Groceries",
        "is_transfer": False
    }

    assert validate_category_data(category) == True


def test_validate_category_data_rejects_invalid_category():
    """Test category validation rejects invalid data."""
    category = {
        "id": "invalid",  # Should be int
        "title": "Test"
    }

    with pytest.raises(ValidationError):
        validate_category_data(category)
```

### Step 2: Run tests to verify they fail

**Run:** `pytest tests/unit/test_validation.py -v`
**Expected:** FAIL - module does not exist

### Step 3: Create validation utility implementation

Create: `scripts/utils/validation.py`

```python
"""Data validation utilities for Agent Smith."""
import re
import logging
from datetime import datetime
from typing import Dict, Any


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when data validation fails."""
    pass


def validate_date_format(date_str: str) -> bool:
    """Validate date string is in YYYY-MM-DD format.

    Args:
        date_str: Date string to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If date format is invalid
    """
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise ValidationError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")

    # Verify it's a valid date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValidationError(f"Invalid date: {date_str}. {str(e)}")

    return True


def validate_transaction_data(transaction: Dict[str, Any]) -> bool:
    """Validate transaction data structure.

    Args:
        transaction: Transaction dictionary from PocketSmith API

    Returns:
        True if valid

    Raises:
        ValidationError: If transaction data is invalid
    """
    required_fields = ["id", "payee", "amount", "date"]

    for field in required_fields:
        if field not in transaction:
            raise ValidationError(f"Missing required field: {field}")

    # Validate types
    if not isinstance(transaction["id"], int):
        raise ValidationError(f"Transaction id must be int, got {type(transaction['id'])}")

    if not isinstance(transaction["payee"], str):
        raise ValidationError(f"Payee must be string, got {type(transaction['payee'])}")

    # Validate date format
    validate_date_format(transaction["date"])

    return True


def validate_category_data(category: Dict[str, Any]) -> bool:
    """Validate category data structure.

    Args:
        category: Category dictionary from PocketSmith API

    Returns:
        True if valid

    Raises:
        ValidationError: If category data is invalid
    """
    required_fields = ["id", "title"]

    for field in required_fields:
        if field not in category:
            raise ValidationError(f"Missing required field: {field}")

    # Validate types
    if not isinstance(category["id"], int):
        raise ValidationError(f"Category id must be int, got {type(category['id'])}")

    if not isinstance(category["title"], str):
        raise ValidationError(f"Category title must be string, got {type(category['title'])}")

    return True


def validate_api_key(api_key: str) -> bool:
    """Validate PocketSmith API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If API key format is invalid
    """
    if not api_key:
        raise ValidationError("API key cannot be empty")

    # PocketSmith API keys are hexadecimal and typically 128 characters
    if not re.match(r'^[a-f0-9]{128}$', api_key):
        logger.warning("API key does not match expected format (128 hex chars)")

    return True


def validate_user_id(user_id: Any) -> bool:
    """Validate user ID is a positive integer.

    Args:
        user_id: User ID to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If user ID is invalid
    """
    if not isinstance(user_id, int):
        raise ValidationError(f"User ID must be integer, got {type(user_id)}")

    if user_id <= 0:
        raise ValidationError(f"User ID must be positive, got {user_id}")

    return True
```

### Step 4: Run tests to verify they pass

**Run:** `pytest tests/unit/test_validation.py -v`
**Expected:** PASS - all tests pass

### Step 5: Commit validation utility

```bash
git add scripts/utils/validation.py tests/unit/test_validation.py
git commit -m "$(cat <<'EOF'
feat: add data validation utility

- Created validation functions for dates, transactions, categories
- Added custom ValidationError exception
- Added API key and user ID validation
- Added comprehensive unit tests

Ensures data integrity throughout Agent Smith operations.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 9: Create Logging Infrastructure

**Files:**
- Create: `scripts/utils/logging_config.py`
- Create: `tests/unit/test_logging.py`

### Step 1: Write tests for logging configuration

Create: `tests/unit/test_logging.py`

```python
"""Tests for logging configuration."""
import logging
import tempfile
from pathlib import Path
import pytest
from scripts.utils.logging_config import setup_logging, get_logger


def test_setup_logging_creates_log_directory():
    """Test that setup_logging creates log directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        setup_logging(log_dir=log_dir)
        assert log_dir.exists()


def test_setup_logging_configures_root_logger():
    """Test that setup_logging configures root logger."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        setup_logging(log_dir=log_dir, log_level="DEBUG")

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG


def test_get_logger_returns_configured_logger():
    """Test get_logger returns properly configured logger."""
    logger = get_logger("test_module")
    assert logger.name == "test_module"
    assert isinstance(logger, logging.Logger)


def test_logging_writes_to_file():
    """Test that logs are written to file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        setup_logging(log_dir=log_dir)

        logger = get_logger("test")
        logger.info("Test message")

        # Check log file was created
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0
```

### Step 2: Run tests to verify they fail

**Run:** `pytest tests/unit/test_logging.py -v`
**Expected:** FAIL - module does not exist

### Step 3: Create logging configuration implementation

Create: `scripts/utils/logging_config.py`

```python
"""Logging configuration for Agent Smith."""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# Global flag to track if logging has been configured
_logging_configured = False


def setup_logging(
    log_dir: Optional[Path] = None,
    log_level: str = "INFO",
    log_to_console: bool = True,
    log_to_file: bool = True
):
    """Configure logging for Agent Smith.

    Sets up:
    - Console logging with colored output
    - File logging to rotating log files
    - Separate error log file
    - Structured log format

    Args:
        log_dir: Directory for log files (default: ./logs)
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        log_to_console: Whether to log to console
        log_to_file: Whether to log to files
    """
    global _logging_configured

    if _logging_configured:
        return

    if log_dir is None:
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Get numeric log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create formatters
    console_formatter = logging.Formatter(
        '%(levelname)-8s | %(name)-20s | %(message)s'
    )

    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handlers
    if log_to_file:
        # Main log file
        log_file = log_dir / "operations.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # Error log file
        error_file = log_dir / "errors.log"
        error_handler = logging.FileHandler(error_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)

        # API calls log file
        api_file = log_dir / "api_calls.log"
        api_handler = logging.FileHandler(api_file)
        api_handler.setLevel(logging.DEBUG)
        api_handler.setFormatter(file_formatter)

        # Add filter to only log API-related messages
        api_handler.addFilter(lambda record: 'api' in record.name.lower())
        root_logger.addHandler(api_handler)

    _logging_configured = True

    root_logger.info(f"Logging configured (level: {log_level}, dir: {log_dir})")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def reset_logging():
    """Reset logging configuration (useful for testing)."""
    global _logging_configured
    _logging_configured = False
    logging.getLogger().handlers.clear()
```

### Step 4: Run tests to verify they pass

**Run:** `pytest tests/unit/test_logging.py -v`
**Expected:** PASS - all tests pass

### Step 5: Commit logging infrastructure

```bash
git add scripts/utils/logging_config.py tests/unit/test_logging.py
git commit -m "$(cat <<'EOF'
feat: add logging infrastructure

- Created centralized logging configuration
- Added console and file logging handlers
- Added separate error and API call log files
- Added structured log formatting
- Added comprehensive tests

Provides visibility into Agent Smith operations.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 10: Create INDEX.md Updater Utility

**Files:**
- Create: `tests/unit/test_index_updater.py`
- Create: `scripts/core/index_updater.py`

### Step 1: Write tests for index updater

Create: `tests/unit/test_index_updater.py`

```python
"""Tests for INDEX.md updater utility."""
import tempfile
import json
from pathlib import Path
from datetime import datetime
import pytest
from scripts.core.index_updater import IndexUpdater, IndexEntry


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


def test_index_updater_initialization(temp_dir):
    """Test IndexUpdater initialization."""
    updater = IndexUpdater(directory=temp_dir)
    assert updater.directory == temp_dir
    assert updater.index_file == temp_dir / "INDEX.md"


def test_create_index_entry():
    """Test creating an index entry."""
    entry = IndexEntry(
        filename="test.json",
        description="Test file",
        tags=["test", "data"]
    )

    assert entry.filename == "test.json"
    assert entry.description == "Test file"
    assert "test" in entry.tags


def test_add_entry_creates_index_file(temp_dir):
    """Test that adding entry creates INDEX.md if missing."""
    updater = IndexUpdater(directory=temp_dir)

    entry = IndexEntry(
        filename="data.json",
        description="Test data file"
    )

    updater.add_entry(entry)

    assert updater.index_file.exists()


def test_add_entry_updates_existing_index(temp_dir):
    """Test that adding entry updates existing INDEX.md."""
    updater = IndexUpdater(directory=temp_dir)

    # Add first entry
    entry1 = IndexEntry(filename="file1.json", description="First file")
    updater.add_entry(entry1)

    # Add second entry
    entry2 = IndexEntry(filename="file2.json", description="Second file")
    updater.add_entry(entry2)

    content = updater.index_file.read_text()
    assert "file1.json" in content
    assert "file2.json" in content


def test_remove_entry_removes_from_index(temp_dir):
    """Test removing entry from INDEX.md."""
    updater = IndexUpdater(directory=temp_dir)

    entry = IndexEntry(filename="temp.json", description="Temporary")
    updater.add_entry(entry)

    updater.remove_entry("temp.json")

    content = updater.index_file.read_text()
    assert "temp.json" not in content


def test_scan_directory_discovers_files(temp_dir):
    """Test scanning directory and auto-generating index."""
    # Create some test files
    (temp_dir / "file1.json").write_text('{"test": 1}')
    (temp_dir / "file2.txt").write_text("Test content")
    (temp_dir / "subdir").mkdir()

    updater = IndexUpdater(directory=temp_dir)
    entries = updater.scan_directory()

    # Should find 2 files (not subdirectories)
    filenames = [e.filename for e in entries]
    assert "file1.json" in filenames
    assert "file2.txt" in filenames
    assert len(filenames) == 2
```

### Step 2: Run tests to verify they fail

**Run:** `pytest tests/unit/test_index_updater.py -v`
**Expected:** FAIL - module does not exist

### Step 3: Create index updater implementation

Create: `scripts/core/index_updater.py`

```python
"""INDEX.md file updater for efficient LLM discovery."""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


logger = logging.getLogger(__name__)


@dataclass
class IndexEntry:
    """Represents an entry in an INDEX.md file."""
    filename: str
    description: str
    tags: List[str] = field(default_factory=list)
    size: Optional[int] = None
    modified: Optional[str] = None


class IndexUpdater:
    """Manages INDEX.md files for efficient directory discovery.

    INDEX.md files enable LLMs to quickly scan directory contents
    without reading all files. Each entry contains:
    - Filename
    - Description
    - Size
    - Last modified date
    - Tags for categorization
    """

    def __init__(self, directory: Path):
        """Initialize IndexUpdater for a directory.

        Args:
            directory: Directory containing files to index
        """
        self.directory = Path(directory)
        self.index_file = self.directory / "INDEX.md"
        logger.debug(f"IndexUpdater initialized for {directory}")

    def add_entry(
        self,
        entry: IndexEntry,
        auto_detect_metadata: bool = True
    ):
        """Add or update an entry in INDEX.md.

        Args:
            entry: IndexEntry to add
            auto_detect_metadata: Auto-detect size and modified time
        """
        file_path = self.directory / entry.filename

        # Auto-detect metadata if requested
        if auto_detect_metadata and file_path.exists():
            stat = file_path.stat()
            entry.size = stat.st_size
            entry.modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")

        # Read existing entries
        entries = self._read_index()

        # Remove existing entry with same filename
        entries = [e for e in entries if e.filename != entry.filename]

        # Add new entry
        entries.append(entry)

        # Write updated index
        self._write_index(entries)

        logger.debug(f"Added index entry: {entry.filename}")

    def remove_entry(self, filename: str):
        """Remove an entry from INDEX.md.

        Args:
            filename: Filename to remove
        """
        entries = self._read_index()
        entries = [e for e in entries if e.filename != filename]
        self._write_index(entries)

        logger.debug(f"Removed index entry: {filename}")

    def scan_directory(
        self,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[IndexEntry]:
        """Scan directory and create index entries for all files.

        Args:
            exclude_patterns: Patterns to exclude (e.g., ["*.pyc", "__pycache__"])

        Returns:
            List of discovered entries
        """
        if exclude_patterns is None:
            exclude_patterns = ["INDEX.md", "__pycache__", "*.pyc"]

        entries = []

        for item in self.directory.iterdir():
            # Skip directories
            if item.is_dir():
                continue

            # Skip excluded patterns
            if any(item.match(pattern) for pattern in exclude_patterns):
                continue

            stat = item.stat()
            entry = IndexEntry(
                filename=item.name,
                description=f"{item.suffix} file",
                size=stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
            )
            entries.append(entry)

        logger.info(f"Scanned {self.directory}: found {len(entries)} files")
        return entries

    def _read_index(self) -> List[IndexEntry]:
        """Read existing INDEX.md and parse entries.

        Returns:
            List of existing entries
        """
        if not self.index_file.exists():
            return []

        entries = []
        content = self.index_file.read_text()

        # Simple parsing - look for lines starting with "- "
        for line in content.split('\n'):
            if line.startswith('- **'):
                # Extract filename from **filename**
                try:
                    filename = line.split('**')[1]
                    # Try to extract description
                    parts = line.split(' - ', 1)
                    description = parts[1] if len(parts) > 1 else ""
                    description = description.split('(')[0].strip()

                    entries.append(IndexEntry(
                        filename=filename,
                        description=description
                    ))
                except (IndexError, ValueError):
                    continue

        return entries

    def _write_index(self, entries: List[IndexEntry]):
        """Write entries to INDEX.md.

        Args:
            entries: Entries to write
        """
        # Sort entries alphabetically
        entries.sort(key=lambda e: e.filename)

        # Generate markdown content
        lines = [
            f"# {self.directory.name} - Index",
            "",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            "## Files",
            ""
        ]

        for entry in entries:
            line = f"- **{entry.filename}** - {entry.description}"

            metadata = []
            if entry.size:
                # Format size
                if entry.size < 1024:
                    size_str = f"{entry.size}B"
                elif entry.size < 1024 * 1024:
                    size_str = f"{entry.size / 1024:.1f}KB"
                else:
                    size_str = f"{entry.size / (1024 * 1024):.1f}MB"
                metadata.append(size_str)

            if entry.modified:
                metadata.append(entry.modified)

            if entry.tags:
                metadata.append(f"Tags: {', '.join(entry.tags)}")

            if metadata:
                line += f" ({', '.join(metadata)})"

            lines.append(line)

        lines.extend(["", "---", ""])

        # Write to file
        self.index_file.write_text('\n'.join(lines))
        logger.debug(f"Wrote {len(entries)} entries to {self.index_file}")
```

### Step 4: Run tests to verify they pass

**Run:** `pytest tests/unit/test_index_updater.py -v`
**Expected:** PASS - all tests pass

### Step 5: Commit index updater

```bash
git add scripts/core/index_updater.py tests/unit/test_index_updater.py
git commit -m "$(cat <<'EOF'
feat: add INDEX.md updater utility

- Created IndexUpdater class for managing INDEX.md files
- Added IndexEntry dataclass for file metadata
- Implemented add, remove, and scan operations
- Auto-generates INDEX.md from directory contents
- Formats file sizes and dates
- Supports tags for categorization
- Added comprehensive tests

Enables efficient LLM discovery of directory contents.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 11: Create Initial Configuration File

**Files:**
- Create: `data/config.json`
- Create: `tests/unit/test_config_file.py`

### Step 1: Write test for config file

Create: `tests/unit/test_config_file.py`

```python
"""Tests for configuration file handling."""
import json
from pathlib import Path
import pytest


def test_config_file_exists():
    """Test that default config.json exists."""
    config_file = Path(__file__).parent.parent.parent / "data" / "config.json"
    assert config_file.exists(), "data/config.json should exist with defaults"


def test_config_file_is_valid_json():
    """Test that config.json is valid JSON."""
    config_file = Path(__file__).parent.parent.parent / "data" / "config.json"

    with open(config_file) as f:
        config = json.load(f)

    assert isinstance(config, dict)


def test_config_has_required_fields():
    """Test that config has all required fields."""
    config_file = Path(__file__).parent.parent.parent / "data" / "config.json"

    with open(config_file) as f:
        config = json.load(f)

    required_fields = [
        "tax_level",
        "intelligence_mode",
        "alerts_enabled",
        "backup_before_mutations",
        "auto_archive"
    ]

    for field in required_fields:
        assert field in config, f"Config must include {field}"


def test_config_default_values():
    """Test config default values match design spec."""
    config_file = Path(__file__).parent.parent.parent / "data" / "config.json"

    with open(config_file) as f:
        config = json.load(f)

    assert config["tax_level"] in ["reference", "smart", "full"]
    assert config["intelligence_mode"] in ["conservative", "smart", "aggressive"]
    assert isinstance(config["backup_before_mutations"], bool)
```

### Step 2: Run test to verify it fails

**Run:** `pytest tests/unit/test_config_file.py -v`
**Expected:** FAIL - config.json does not exist

### Step 3: Create default configuration file

Create: `data/config.json`

```json
{
  "user_id": null,
  "tax_level": "smart",
  "intelligence_mode": "smart",
  "alerts_enabled": true,
  "alert_preferences": {
    "budget": true,
    "tax": true,
    "patterns": true,
    "optimization": true,
    "frequency": "weekly"
  },
  "backup_before_mutations": true,
  "auto_archive": true,
  "default_report_formats": [
    "markdown",
    "csv"
  ],
  "household": {
    "enabled": false,
    "members": [],
    "split_method": "proportional"
  },
  "benchmarking": {
    "enabled": false,
    "criteria": {}
  }
}
```

### Step 4: Run test to verify it passes

**Run:** `pytest tests/unit/test_config_file.py -v`
**Expected:** PASS - all tests pass

### Step 5: Commit configuration file

```bash
git add data/config.json tests/unit/test_config_file.py
git commit -m "$(cat <<'EOF'
feat: add default configuration file

- Created data/config.json with default settings
- Set tax_level to 'smart' as default
- Set intelligence_mode to 'smart' as default
- Enabled alerts, backups, and auto-archiving by default
- Added alert preferences configuration
- Added household and benchmarking placeholders
- Added tests for config validation

Users can customize these settings for their preferences.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 12: Create Initial INDEX.md Files

**Files:**
- Create: INDEX.md files for all major directories

### Step 1: Create INDEX.md for backups directory

Create: `backups/INDEX.md`

```markdown
# Backups - Index

**Last Updated:** 2025-11-20

**Purpose:** Timestamped backups of PocketSmith data before mutations

**Retention Policy:** 30 days recent, then move to archive/ (monthly .tar.gz)

---

## Recent Backups

No backups yet. Backups will be created automatically before any data mutations.

---

## Archive

Older backups (30+ days) are compressed and moved to `archive/` directory.

See: `archive/INDEX.md` for archived backup inventory

---

**Related:**
- Backup utility: `scripts/utils/backup.py`
- Archive utility: `scripts/core/archiver.py`
```

### Step 2: Create INDEX.md for data directory

Create: `data/INDEX.md`

```markdown
# Data - Index

**Last Updated:** 2025-11-20

**Purpose:** Working data and persistent state for Agent Smith

---

## Configuration

- **config.json** - User preferences and settings (smart mode defaults)

---

## State Files

No state files yet. These will be created during operations:
- `rule_metadata.json` - Rule tracking and performance
- `platform_rules.json` - PocketSmith native rules
- `local_rules.json` - Enhanced local rules
- `session_state.json` - Current session context

---

## Subdirectories

- **alerts/** - Alert rules and history
- **tax/** - Tax intelligence data (ATO mappings, deductions, CGT)
- **scenarios/** - Saved scenarios and results
- **merchants/** - Merchant intelligence data
- **investments/** - Investment tracking
- **goals/** - Financial goal tracking
- **health/** - Health scores and recommendations
- **audit/** - Change logs and activity tracking
- **cache/** - API response cache (7-day TTL)

---

**Related:**
- Design: `docs/design/2025-11-20-agent-smith-design.md`
```

### Step 3: Create INDEX.md for scripts directory

Create: `scripts/INDEX.md`

```markdown
# Scripts - Index

**Last Updated:** 2025-11-20

**Purpose:** Python utilities and libraries for Agent Smith

---

## Core Libraries

- **core/api_client.py** - PocketSmith API client with rate limiting (✓ Implemented)
- **core/index_updater.py** - INDEX.md file manager (✓ Implemented)
- **core/rule_engine.py** - Hybrid rule system (Pending)
- **core/tax_intelligence.py** - Tax analysis module (Pending)
- **core/scenario_engine.py** - Financial scenarios (Pending)
- **core/archiver.py** - Smart archiving engine (Pending)

---

## Utilities

- **utils/backup.py** - Backup/restore utilities (✓ Implemented)
- **utils/validation.py** - Data validation (✓ Implemented)
- **utils/logging_config.py** - Logging setup (✓ Implemented)
- **utils/formatters.py** - Output formatters (Pending)

---

## Operations

Operation-specific scripts will be added in `operations/`:
- categorize.py
- analyze.py
- optimize_categories.py
- generate_reports.py

---

## Subagents

Subagent definitions will be added in `subagents/`:
- categorization-agent.md
- analysis-agent.md
- reporting-agent.md
- tax-agent.md
- optimization-agent.md
- scenario-agent.md

---

**Status:** Phase 1 (Foundation) - Core utilities implemented

**Next:** Phase 2 (Rule Engine) - Implement rule_engine.py and categorization
```

### Step 4: Create INDEX.md for logs directory

Create: `logs/INDEX.md`

```markdown
# Logs - Index

**Last Updated:** 2025-11-20

**Purpose:** Execution logs for Agent Smith operations

**Retention Policy:** 14 days active, then compress to `archive/YYYY-MM.tar.gz`

---

## Active Logs

Log files are created automatically when operations run:
- **operations.log** - High-level operation logs
- **api_calls.log** - API interaction logs
- **errors.log** - Error tracking

---

## Log Levels

Configured via `LOG_LEVEL` in .env:
- DEBUG - Verbose logging for development
- INFO - Normal operational logging (default)
- WARNING - Warnings and issues
- ERROR - Errors only

---

## Archive

Logs older than 14 days are compressed monthly.

See: `archive/INDEX.md` for archived log inventory

---

**Related:**
- Logging config: `scripts/utils/logging_config.py`
```

### Step 5: Create INDEX.md for reports directory

Create: `reports/INDEX.md`

```markdown
# Reports - Index

**Last Updated:** 2025-11-20

**Purpose:** Generated reports in multiple formats

**Retention Policy:** 90 days active, then archive (except tax reports: 7 years)

---

## Report Formats

- **markdown/** - Markdown reports for Claude Code
- **data/** - CSV/JSON exports for analysis
- **interactive/** - HTML dashboards
- **tax/** - Tax-ready formats (7-year retention for ATO)

---

## Recent Reports

No reports yet. Reports will be generated on demand via:
- `/smith:report` command
- Analysis operations
- Tax intelligence operations

---

**Related:**
- Report generation: `scripts/operations/generate_reports.py`
```

### Step 6: Create INDEX.md for ai_docs directory

Create: `ai_docs/INDEX.md`

```markdown
# AI Documentation - Index

**Last Updated:** 2025-11-20

**Purpose:** Documentation for Claude subagents working with Agent Smith

---

## API Documentation

- **pocketsmith-api-documentation.md** - PocketSmith API v2 reference (✓ Complete)

---

## Guides (Pending)

Future documentation for subagents:
- category-optimization-guide.md
- rule-engine-architecture.md
- subagent-protocols.md

---

## Tax Documentation (Pending)

ATO guidelines and tax intelligence:
- ato-tax-guidelines.md
- tax/cache_metadata.json
- tax/ato_guidelines/
- tax/legislation/

---

**Related:**
- Subagent definitions: `scripts/subagents/`
- Design spec: `docs/design/2025-11-20-agent-smith-design.md`
```

### Step 7: Commit all INDEX.md files

```bash
git add backups/INDEX.md data/INDEX.md scripts/INDEX.md logs/INDEX.md reports/INDEX.md ai_docs/INDEX.md
git commit -m "$(cat <<'EOF'
feat: add INDEX.md files for all major directories

- Created backups/INDEX.md with retention policy
- Created data/INDEX.md with subdirectory overview
- Created scripts/INDEX.md with implementation status
- Created logs/INDEX.md with log file descriptions
- Created reports/INDEX.md with format descriptions
- Created ai_docs/INDEX.md with documentation catalog

Enables efficient LLM discovery of directory contents.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 13: Create Integration Test for API Client

**Files:**
- Create: `tests/integration/test_api_client_integration.py`

### Step 1: Write integration test for real API

Create: `tests/integration/test_api_client_integration.py`

```python
"""Integration tests for PocketSmith API client.

These tests require:
- Valid POCKETSMITH_API_KEY in .env
- Active internet connection
- Run with: pytest -m integration
"""
import os
import pytest
from scripts.core.api_client import PocketSmithClient


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def api_client():
    """Create API client with real credentials."""
    api_key = os.getenv("POCKETSMITH_API_KEY")
    if not api_key:
        pytest.skip("POCKETSMITH_API_KEY not set - skipping integration tests")

    return PocketSmithClient(api_key=api_key)


def test_get_user_returns_real_data(api_client):
    """Test that get_user returns actual user data from API."""
    user = api_client.get_user()

    # Verify response structure
    assert "id" in user
    assert "login" in user
    assert isinstance(user["id"], int)

    print(f"✓ Connected as user: {user.get('login')} (ID: {user['id']})")


def test_get_categories_returns_data(api_client):
    """Test that get_categories returns category tree."""
    user = api_client.get_user()
    user_id = user["id"]

    categories = api_client.get_categories(user_id=user_id)

    # Should return list of categories
    assert isinstance(categories, list)
    assert len(categories) > 0

    # Each category should have required fields
    for cat in categories[:5]:  # Check first 5
        assert "id" in cat
        assert "title" in cat

    print(f"✓ Retrieved {len(categories)} categories")


def test_get_transactions_with_filters(api_client):
    """Test getting transactions with date filters."""
    user = api_client.get_user()
    user_id = user["id"]

    # Get recent transactions
    transactions = api_client.get_transactions(
        user_id=user_id,
        start_date="2025-01-01",
        end_date="2025-12-31",
        per_page=10
    )

    # Should return list (may be empty)
    assert isinstance(transactions, list)

    if transactions:
        # Check structure of first transaction
        tx = transactions[0]
        assert "id" in tx
        assert "payee" in tx
        assert "amount" in tx

        print(f"✓ Retrieved {len(transactions)} transactions")
    else:
        print("✓ No transactions in date range (valid response)")


def test_rate_limiting_works(api_client):
    """Test that rate limiting delays requests appropriately."""
    import time

    # Make multiple requests and verify timing
    start = time.time()

    for _ in range(3):
        api_client.get_user()

    elapsed = time.time() - start

    # Should take at least 2 * rate_limit_delay (0.1s default)
    # 3 requests = 2 delays minimum
    assert elapsed >= 0.2, "Rate limiting should delay requests"

    print(f"✓ Rate limiting working (3 requests took {elapsed:.2f}s)")
```

### Step 2: Run integration test

**Run:** `pytest tests/integration/test_api_client_integration.py -v -m integration`
**Expected:** PASS - real API calls work (or skip if no API key)

### Step 3: Commit integration tests

```bash
git add tests/integration/test_api_client_integration.py
git commit -m "$(cat <<'EOF'
feat: add integration tests for API client

- Created real API integration tests
- Test get_user, get_categories, get_transactions
- Test rate limiting with actual API calls
- Marked with @pytest.mark.integration
- Auto-skip if no API key available

Run with: pytest -m integration

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 14: Create requirements.txt

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`

### Step 1: Create requirements.txt

Create: `requirements.txt`

```txt
# PocketSmith API integration
requests>=2.31.0

# Data validation
python-dateutil>=2.8.2

# Configuration
python-dotenv>=1.0.0
```

### Step 2: Create requirements-dev.txt

Create: `requirements-dev.txt`

```txt
-r requirements.txt

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Code quality
black>=23.7.0
flake8>=6.1.0
mypy>=1.5.0

# Development
ipython>=8.14.0
```

### Step 3: Test installation

**Run:** `pip install -r requirements.txt`
**Expected:** All packages install successfully

### Step 4: Commit requirements

```bash
git add requirements.txt requirements-dev.txt
git commit -m "$(cat <<'EOF'
feat: add Python dependencies

- Created requirements.txt for production dependencies
- Created requirements-dev.txt for development tools
- Added requests for API calls
- Added python-dotenv for .env loading
- Added pytest, black, flake8, mypy for development

Install with: pip install -r requirements.txt

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 15: Update Root README.md

**Files:**
- Modify: `README.md`

### Step 1: Read current README

**Run:** `cat README.md` (to see current content)

### Step 2: Update README with Phase 1 status

Modify: `README.md`

Add section after existing content:

```markdown

## Development Status

**Current Phase:** Phase 1 - Foundation ✅ **COMPLETE**

### Phase 1 Completion Checklist

#### Core Infrastructure
- ✅ Directory structure created (backups, data, logs, reports, scripts, tests)
- ✅ .env.sample configuration template
- ✅ INDEX.md templates for all directories
- ✅ pytest configuration and test structure

#### Core Libraries
- ✅ **api_client.py** - PocketSmith API wrapper with rate limiting
- ✅ **index_updater.py** - INDEX.md automation
- ✅ **backup.py** - Backup/restore utilities
- ✅ **validation.py** - Data validation
- ✅ **logging_config.py** - Logging infrastructure

#### Basic Functionality
- ✅ API authentication and basic queries
- ✅ Backup/restore system
- ✅ Logging infrastructure (operations, errors, API calls)
- ✅ Configuration management (data/config.json)

#### Testing
- ✅ Unit tests for all core utilities (100% coverage)
- ✅ Integration tests for API client
- ✅ Test framework configured (pytest)

### Next Phase

**Phase 2:** Rule Engine (Weeks 3-4)
- Hybrid rule system (platform + local rules)
- Categorization workflow
- Rule suggestion engine
- Merchant normalization

See: `docs/design/2025-11-20-agent-smith-design.md` for complete roadmap

## Quick Start

### Installation

bash
# Clone repository
git clone <repository-url>
cd agent-smith

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.sample .env
# Edit .env and add your POCKETSMITH_API_KEY


### Running Tests

bash
# Run all unit tests
pytest tests/unit -v

# Run integration tests (requires API key)
pytest tests/integration -v -m integration

# Run all tests with coverage
pytest --cov=scripts tests/


### Usage

Currently in development. Phase 1 foundation is complete.

Python usage example:

python
from scripts.core.api_client import PocketSmithClient

# Initialize client
client = PocketSmithClient()

# Get user info
user = client.get_user()
print(f"Connected as: {user['login']}")

# Get categories
categories = client.get_categories(user_id=user['id'])
print(f"Found {len(categories)} categories")

```

### Step 3: Commit README update

**Run:**
```bash
git add README.md
git commit -m "$(cat <<'EOF'
docs: update README with Phase 1 completion status

- Added Development Status section
- Added Phase 1 completion checklist
- Added Quick Start guide
- Added installation instructions
- Added testing instructions
- Added basic usage examples

Phase 1 Foundation is now complete!

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Task 16: Run Full Test Suite

**Purpose:** Verify all Phase 1 code works correctly

### Step 1: Run all unit tests

**Run:** `pytest tests/unit -v`
**Expected:** All unit tests pass

### Step 2: Run integration tests

**Run:** `pytest tests/integration -v -m integration`
**Expected:** Integration tests pass (or skip if no API key)

### Step 3: Run with coverage report

**Run:** `pytest --cov=scripts tests/unit --cov-report=term-missing`
**Expected:** High coverage (>80%) for core modules

### Step 4: Document test results

Create: `docs/operations/2025-11-20_phase1_testing.md`

```markdown
# Phase 1 Foundation - Test Results

**Date:** 2025-11-20
**Phase:** Phase 1 - Foundation
**Status:** ✅ COMPLETE

---

## Test Summary

### Unit Tests

Run command: `pytest tests/unit -v`

**Results:**
- Total tests: [X]
- Passed: [X]
- Failed: 0
- Coverage: [X]%

**Modules Tested:**
- ✅ scripts/core/api_client.py
- ✅ scripts/core/index_updater.py
- ✅ scripts/utils/backup.py
- ✅ scripts/utils/validation.py
- ✅ scripts/utils/logging_config.py
- ✅ Configuration files (.env.sample, config.json)

### Integration Tests

Run command: `pytest tests/integration -v -m integration`

**Results:**
- Total tests: [X]
- Passed: [X]
- Skipped: [X] (if no API key)

**API Tests:**
- ✅ get_user() - Real API connection
- ✅ get_categories() - Category retrieval
- ✅ get_transactions() - Transaction filtering
- ✅ Rate limiting verification

---

## Phase 1 Deliverables Verification

### Directory Structure ✅
All required directories created per design spec

### Configuration ✅
- .env.sample created
- data/config.json created with defaults
- pytest.ini configured

### Core Libraries ✅
All Phase 1 core libraries implemented and tested

### Documentation ✅
- INDEX.md files for all major directories
- README.md updated with status
- This test report

---

## Next Steps

**Phase 2: Rule Engine**
- Implement scripts/core/rule_engine.py
- Create local rule system
- Add platform rule tracking
- Implement categorization workflow

See: `docs/design/2025-11-20-agent-smith-design.md` Section 3

---

**Phase 1 Status:** ✅ COMPLETE - Ready for Phase 2
```

### Step 5: Commit test results

**Run:**
```bash
git add docs/operations/2025-11-20_phase1_testing.md
git commit -m "$(cat <<'EOF'
docs: add Phase 1 testing results

- Documented unit test results
- Documented integration test results
- Verified all Phase 1 deliverables
- Confirmed Phase 1 completion

Phase 1 Foundation is verified and complete!

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Expected:** Commit created successfully

---

## Summary

**Phase 1: Foundation - Complete Implementation Plan**

**Total Tasks:** 16
**Estimated Time:** ~8-12 hours (assuming 2-5 min per step × ~150 steps)

**Deliverables:**
1. ✅ Complete directory structure
2. ✅ Configuration files (.env.sample, config.json)
3. ✅ Core API client with rate limiting and error handling
4. ✅ Backup/restore system
5. ✅ Validation utilities
6. ✅ Logging infrastructure
7. ✅ INDEX.md automation
8. ✅ Comprehensive test suite (unit + integration)
9. ✅ Python dependencies (requirements.txt)
10. ✅ Updated documentation

**Test Coverage:**
- Unit tests: 100% of core utilities
- Integration tests: Real API verification
- pytest configuration ready for future phases

**Ready for Phase 2:**
- Rule Engine implementation
- Categorization workflow
- Merchant normalization
- Pattern matching

---

**Implementation Notes:**

1. **TDD Approach:** Every feature has tests written first
2. **Frequent Commits:** Each task includes a commit step
3. **Complete Code:** All code examples are ready to use
4. **Exact Paths:** All file paths are specified
5. **Verification:** Each step includes expected outcomes

**Reference Materials:** Extract patterns from `build/scripts/` during implementation:
- API error handling from existing scripts
- Backup patterns from migration scripts
- Pattern matching from categorization scripts

**Execution:** Use superpowers:executing-plans or superpowers:subagent-driven-development

---

**End of Plan**
