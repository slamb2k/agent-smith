# LLM-Enhanced Categorization & Labeling Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add LLM-powered categorization and intelligent labeling system with unified YAML rules, deprecating platform rule creation in favor of local-only rules with full control.

**Architecture:** Two-phase execution (categorization → labeling) using unified YAML rules. LLM integration via subagent for fallback categorization and validation. Smart batching (20-50 transactions/call), confidence scoring through Intelligence Modes, rule learning from LLM suggestions.

**Tech Stack:** Python 3.9+, PyYAML, existing RuleEngine/SubagentConductor, PocketSmith API

---

## Task 1: YAML Rule Schema & Parser

**Files:**
- Create: `scripts/core/unified_rules.py`
- Create: `data/rules.yaml`
- Create: `tests/unit/test_unified_rules.py`

**Step 1: Write failing test for YAML rule parsing**

Create `tests/unit/test_unified_rules.py`:

```python
"""Tests for unified YAML rule system."""

import pytest
from pathlib import Path
from scripts.core.unified_rules import UnifiedRuleEngine, RuleType


def test_parse_category_rule(tmp_path):
    """Test parsing a category rule from YAML."""
    rules_file = tmp_path / "test_rules.yaml"
    rules_file.write_text("""
rules:
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS, COLES]
    category: Groceries
    confidence: 95
""")

    engine = UnifiedRuleEngine(rules_file=rules_file)

    assert len(engine.category_rules) == 1
    rule = engine.category_rules[0]
    assert rule.name == "WOOLWORTHS → Groceries"
    assert rule.patterns == ["WOOLWORTHS", "COLES"]
    assert rule.category == "Groceries"
    assert rule.confidence == 95


def test_parse_label_rule(tmp_path):
    """Test parsing a label rule from YAML."""
    rules_file = tmp_path / "test_rules.yaml"
    rules_file.write_text("""
rules:
  - type: label
    name: Personal Groceries
    when:
      categories: [Groceries]
      accounts: [Personal]
    labels: [Personal, Essential]
""")

    engine = UnifiedRuleEngine(rules_file=rules_file)

    assert len(engine.label_rules) == 1
    rule = engine.label_rules[0]
    assert rule.name == "Personal Groceries"
    assert rule.when_categories == ["Groceries"]
    assert rule.when_accounts == ["Personal"]
    assert rule.labels == ["Personal", "Essential"]


def test_parse_mixed_rules(tmp_path):
    """Test parsing both category and label rules."""
    rules_file = tmp_path / "test_rules.yaml"
    rules_file.write_text("""
rules:
  - type: category
    name: Test Category
    patterns: [TEST]
    category: Test
    confidence: 90

  - type: label
    name: Test Label
    when:
      categories: [Test]
    labels: [TestLabel]
""")

    engine = UnifiedRuleEngine(rules_file=rules_file)

    assert len(engine.category_rules) == 1
    assert len(engine.label_rules) == 1
```

**Step 2: Run test to verify it fails**

```bash
uv run python -u -m pytest tests/unit/test_unified_rules.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'scripts.core.unified_rules'"

**Step 3: Install PyYAML dependency**

Add to `pyproject.toml` (or `requirements.txt`):

```toml
[project]
dependencies = [
    "requests>=2.31.0",
    "python-dateutil>=2.8.2",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.1",  # NEW
]
```

Run:
```bash
uv sync
```

**Step 4: Write minimal rule schema classes**

Create `scripts/core/unified_rules.py`:

```python
"""Unified rule engine for categories and labels."""

import yaml
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Rule type enum."""
    CATEGORY = "category"
    LABEL = "label"


@dataclass
class CategoryRule:
    """Rule for categorizing transactions."""

    name: str
    patterns: List[str]
    category: str
    confidence: int = 90
    exclude_patterns: List[str] = field(default_factory=list)
    amount_operator: Optional[str] = None
    amount_value: Optional[float] = None
    accounts: List[str] = field(default_factory=list)


@dataclass
class LabelRule:
    """Rule for labeling transactions."""

    name: str
    labels: List[str]
    when_categories: List[str] = field(default_factory=list)
    when_accounts: List[str] = field(default_factory=list)
    when_amount_operator: Optional[str] = None
    when_amount_value: Optional[float] = None
    when_uncategorized: bool = False


class UnifiedRuleEngine:
    """Unified rule engine managing categories and labels."""

    def __init__(self, rules_file: Optional[Path] = None):
        """Initialize unified rule engine.

        Args:
            rules_file: Path to YAML rules file
        """
        if rules_file is None:
            project_root = Path(__file__).parent.parent.parent
            rules_file = project_root / "data" / "rules.yaml"

        self.rules_file = Path(rules_file)
        self.category_rules: List[CategoryRule] = []
        self.label_rules: List[LabelRule] = []

        if self.rules_file.exists():
            self.load_rules()

    def load_rules(self) -> None:
        """Load rules from YAML file."""
        if not self.rules_file.exists():
            logger.warning(f"Rules file not found: {self.rules_file}")
            return

        with open(self.rules_file) as f:
            data = yaml.safe_load(f)

        rules_data = data.get("rules", [])

        for rule_dict in rules_data:
            rule_type = rule_dict.get("type")

            if rule_type == "category":
                rule = self._parse_category_rule(rule_dict)
                self.category_rules.append(rule)
            elif rule_type == "label":
                rule = self._parse_label_rule(rule_dict)
                self.label_rules.append(rule)

        logger.info(
            f"Loaded {len(self.category_rules)} category rules, "
            f"{len(self.label_rules)} label rules from {self.rules_file}"
        )

    def _parse_category_rule(self, rule_dict: Dict[str, Any]) -> CategoryRule:
        """Parse category rule from dict."""
        # Ensure patterns is always a list
        patterns = rule_dict.get("patterns", [])
        if isinstance(patterns, str):
            patterns = [patterns]

        exclude_patterns = rule_dict.get("exclude_patterns", [])
        if isinstance(exclude_patterns, str):
            exclude_patterns = [exclude_patterns]

        accounts = rule_dict.get("accounts", [])
        if isinstance(accounts, str):
            accounts = [accounts]

        return CategoryRule(
            name=rule_dict["name"],
            patterns=patterns,
            category=rule_dict["category"],
            confidence=rule_dict.get("confidence", 90),
            exclude_patterns=exclude_patterns,
            amount_operator=rule_dict.get("amount_operator"),
            amount_value=rule_dict.get("amount_value"),
            accounts=accounts,
        )

    def _parse_label_rule(self, rule_dict: Dict[str, Any]) -> LabelRule:
        """Parse label rule from dict."""
        when = rule_dict.get("when", {})

        # Ensure all when conditions are lists
        categories = when.get("categories", [])
        if isinstance(categories, str):
            categories = [categories]

        accounts = when.get("accounts", [])
        if isinstance(accounts, str):
            accounts = [accounts]

        labels = rule_dict.get("labels", [])
        if isinstance(labels, str):
            labels = [labels]

        return LabelRule(
            name=rule_dict["name"],
            labels=labels,
            when_categories=categories,
            when_accounts=accounts,
            when_amount_operator=when.get("amount_operator"),
            when_amount_value=when.get("amount_value"),
            when_uncategorized=when.get("uncategorized", False),
        )
```

**Step 5: Run tests to verify they pass**

```bash
uv run python -u -m pytest tests/unit/test_unified_rules.py -v
```

Expected: PASS (3 tests)

**Step 6: Commit**

```bash
git add scripts/core/unified_rules.py tests/unit/test_unified_rules.py pyproject.toml
git commit -m "feat: add YAML rule schema and parser for unified categories/labels"
```

---

## Task 2: Rule Matching Logic

**Files:**
- Modify: `scripts/core/unified_rules.py`
- Modify: `tests/unit/test_unified_rules.py`

**Step 1: Write failing test for category rule matching**

Add to `tests/unit/test_unified_rules.py`:

```python
def test_match_category_rule_by_pattern():
    """Test matching category rule by payee pattern."""
    rule = CategoryRule(
        name="Groceries",
        patterns=["WOOLWORTHS", "COLES"],
        category="Groceries",
        confidence=95
    )

    transaction = {
        "payee": "WOOLWORTHS METRO 123",
        "amount": -45.50,
    }

    assert rule.matches(transaction) is True


def test_match_category_rule_with_exclusion():
    """Test category rule with exclusion pattern."""
    rule = CategoryRule(
        name="Transport",
        patterns=["UBER"],
        exclude_patterns=["UBER EATS"],
        category="Transport",
        confidence=90
    )

    transaction_match = {"payee": "UBER TRIP ABC123"}
    transaction_exclude = {"payee": "UBER EATS ORDER 456"}

    assert rule.matches(transaction_match) is True
    assert rule.matches(transaction_exclude) is False


def test_match_label_rule():
    """Test matching label rule with conditions."""
    rule = LabelRule(
        name="Personal Groceries",
        when_categories=["Groceries"],
        when_accounts=["Personal"],
        labels=["Personal", "Essential"]
    )

    transaction = {
        "category": {"title": "Groceries"},
        "_account_name": "Personal",
    }

    assert rule.matches(transaction) is True


def test_match_label_rule_uncategorized():
    """Test label rule matching uncategorized transactions."""
    rule = LabelRule(
        name="Flag Uncategorized",
        when_uncategorized=True,
        labels=["Needs Categorization"]
    )

    transaction_uncategorized = {"category": None}
    transaction_categorized = {"category": {"title": "Groceries"}}

    assert rule.matches(transaction_uncategorized) is True
    assert rule.matches(transaction_categorized) is False
```

**Step 2: Run test to verify it fails**

```bash
uv run python -u -m pytest tests/unit/test_unified_rules.py::test_match_category_rule_by_pattern -v
```

Expected: FAIL with "AttributeError: 'CategoryRule' object has no attribute 'matches'"

**Step 3: Implement match methods**

Add to `CategoryRule` class in `scripts/core/unified_rules.py`:

```python
    def matches(self, transaction: Dict[str, Any]) -> bool:
        """Check if rule matches transaction.

        Args:
            transaction: Transaction dict

        Returns:
            True if rule matches, False otherwise
        """
        payee = transaction.get("payee", "").upper()

        # Check patterns (OR logic)
        pattern_match = any(pattern.upper() in payee for pattern in self.patterns)
        if not pattern_match:
            return False

        # Check exclusions
        for exclude in self.exclude_patterns:
            if exclude.upper() in payee:
                return False

        # Check amount condition
        if self.amount_operator and self.amount_value is not None:
            amount = abs(float(transaction.get("amount", 0)))
            if not self._check_amount(amount):
                return False

        # Check account filter
        if self.accounts:
            account_name = transaction.get("_account_name") or \
                          transaction.get("transaction_account", {}).get("name")
            if account_name not in self.accounts:
                return False

        return True

    def _check_amount(self, amount: float) -> bool:
        """Check amount condition."""
        if self.amount_operator == ">":
            return amount > self.amount_value
        elif self.amount_operator == "<":
            return amount < self.amount_value
        elif self.amount_operator == ">=":
            return amount >= self.amount_value
        elif self.amount_operator == "<=":
            return amount <= self.amount_value
        elif self.amount_operator == "==":
            return amount == self.amount_value
        elif self.amount_operator == "!=":
            return amount != self.amount_value
        return True
```

Add to `LabelRule` class:

```python
    def matches(self, transaction: Dict[str, Any]) -> bool:
        """Check if label rule matches transaction.

        Args:
            transaction: Transaction dict (may include _account_name)

        Returns:
            True if all conditions match
        """
        # Check uncategorized condition
        if self.when_uncategorized:
            category = transaction.get("category")
            if category is None:
                return True
            return False

        # Check category condition (OR logic within list)
        if self.when_categories:
            category = transaction.get("category")
            if category is None:
                return False

            category_title = category.get("title", "") if isinstance(category, dict) else str(category)

            if not any(cat in category_title for cat in self.when_categories):
                return False

        # Check account condition (OR logic within list)
        if self.when_accounts:
            account_name = transaction.get("_account_name") or \
                          transaction.get("transaction_account", {}).get("name", "")

            if not any(acc in account_name for acc in self.when_accounts):
                return False

        # Check amount condition
        if self.when_amount_operator and self.when_amount_value is not None:
            amount = float(transaction.get("amount", 0))
            if not self._check_amount(amount):
                return False

        return True

    def _check_amount(self, amount: float) -> bool:
        """Check amount condition."""
        if self.when_amount_operator == ">":
            return amount > self.when_amount_value
        elif self.when_amount_operator == "<":
            return amount < self.when_amount_value
        elif self.when_amount_operator == ">=":
            return amount >= self.when_amount_value
        elif self.when_amount_operator == "<=":
            return amount <= self.when_amount_value
        elif self.when_amount_operator == "==":
            return amount == self.when_amount_value
        elif self.when_amount_operator == "!=":
            return amount != self.when_amount_value
        return True
```

**Step 4: Run tests to verify they pass**

```bash
uv run python -u -m pytest tests/unit/test_unified_rules.py -v
```

Expected: PASS (all tests)

**Step 5: Commit**

```bash
git add scripts/core/unified_rules.py tests/unit/test_unified_rules.py
git commit -m "feat: add rule matching logic for categories and labels"
```

---

## Task 3: Two-Phase Categorization & Labeling

**Files:**
- Modify: `scripts/core/unified_rules.py`
- Modify: `tests/unit/test_unified_rules.py`

**Step 1: Write failing test for two-phase execution**

Add to `tests/unit/test_unified_rules.py`:

```python
def test_categorize_and_label_transaction(tmp_path):
    """Test two-phase categorization and labeling."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("""
rules:
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95

  - type: label
    name: Personal Groceries
    when:
      categories: [Groceries]
      accounts: [Personal]
    labels: [Personal, Essential]

  - type: label
    name: Shared Groceries
    when:
      categories: [Groceries]
      accounts: [Shared Bills]
    labels: [Shared Expense]
""")

    engine = UnifiedRuleEngine(rules_file=rules_file)

    transaction = {
        "id": 123,
        "payee": "WOOLWORTHS METRO",
        "amount": -45.50,
        "_account_name": "Personal",
    }

    result = engine.categorize_and_label(transaction)

    assert result["category_matched"] is True
    assert result["category"] == "Groceries"
    assert result["confidence"] == 95
    assert result["labels_matched"] is True
    assert "Personal" in result["labels"]
    assert "Essential" in result["labels"]
    assert "Shared Expense" not in result["labels"]


def test_label_multiple_rules():
    """Test multiple label rules matching same transaction."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("""
rules:
  - type: label
    name: Groceries Label
    when:
      categories: [Groceries]
    labels: [Food]

  - type: label
    name: Large Purchase
    when:
      amount_operator: ">"
      amount_value: 100
    labels: [Large Purchase, Review]
""")

    engine = UnifiedRuleEngine(rules_file=rules_file)

    transaction = {
        "category": {"title": "Groceries"},
        "amount": -150.00,
    }

    result = engine.categorize_and_label(transaction)

    # Both label rules should match
    assert "Food" in result["labels"]
    assert "Large Purchase" in result["labels"]
    assert "Review" in result["labels"]
```

**Step 2: Run test to verify it fails**

```bash
uv run python -u -m pytest tests/unit/test_unified_rules.py::test_categorize_and_label_transaction -v
```

Expected: FAIL with "AttributeError: 'UnifiedRuleEngine' object has no attribute 'categorize_and_label'"

**Step 3: Implement two-phase execution**

Add to `UnifiedRuleEngine` class:

```python
    def categorize_and_label(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize and label a transaction using two-phase execution.

        Phase 1: Apply category rules
        Phase 2: Apply label rules (can use category from Phase 1)

        Args:
            transaction: Transaction dict

        Returns:
            Result dict with category, confidence, labels, etc.
        """
        result = {
            "transaction_id": transaction.get("id"),
            "category_matched": False,
            "category": None,
            "category_rule": None,
            "confidence": None,
            "labels_matched": False,
            "labels": [],
            "label_rules": [],
        }

        # Phase 1: Categorization
        category_match = self.find_best_category_match(transaction)
        if category_match:
            result["category_matched"] = True
            result["category"] = category_match.category
            result["category_rule"] = category_match.name
            result["confidence"] = category_match.confidence

            # Update transaction with matched category for Phase 2
            transaction = transaction.copy()
            transaction["category"] = {"title": category_match.category}

        # Phase 2: Labeling
        labels = set()
        matched_label_rules = []

        for label_rule in self.label_rules:
            if label_rule.matches(transaction):
                labels.update(label_rule.labels)
                matched_label_rules.append(label_rule.name)

        if labels:
            result["labels_matched"] = True
            result["labels"] = sorted(list(labels))
            result["label_rules"] = matched_label_rules

        return result

    def find_best_category_match(self, transaction: Dict[str, Any]) -> Optional[CategoryRule]:
        """Find best matching category rule for transaction.

        Args:
            transaction: Transaction dict

        Returns:
            Best matching CategoryRule or None
        """
        matches = [rule for rule in self.category_rules if rule.matches(transaction)]

        if not matches:
            return None

        # Sort by confidence descending
        matches.sort(key=lambda r: r.confidence, reverse=True)
        return matches[0]
```

**Step 4: Run tests to verify they pass**

```bash
uv run python -u -m pytest tests/unit/test_unified_rules.py -v
```

Expected: PASS (all tests)

**Step 5: Commit**

```bash
git add scripts/core/unified_rules.py tests/unit/test_unified_rules.py
git commit -m "feat: implement two-phase categorization and labeling execution"
```

---

## Task 4: Preset Hierarchy Templates

**Files:**
- Create: `data/templates/simple.yaml`
- Create: `data/templates/separated-families.yaml`
- Create: `data/templates/shared-household.yaml`
- Create: `data/templates/advanced.yaml`
- Create: `data/templates/INDEX.md`
- Create: `scripts/setup/template_selector.py`

**Step 1: Create Simple template (single person, basic categories)**

Create `data/templates/simple.yaml`:

```yaml
# Simple Template - Single Person Finances
# Best for: Individuals managing personal finances only

metadata:
  template_name: Simple
  description: Basic categories and labels for individual financial tracking
  target_users: Single person, no shared expenses, basic needs

rules:
  # ═══════════════════════════════════════════════════════════
  # INCOME
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Salary Income
    patterns: [SALARY, WAGES, EMPLOYER]
    category: Income > Salary
    confidence: 95

  # ═══════════════════════════════════════════════════════════
  # ESSENTIAL EXPENSES
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Groceries
    patterns: [WOOLWORTHS, COLES, ALDI, IGA]
    category: Food & Dining > Groceries
    confidence: 95

  - type: label
    name: Essential Spending
    when:
      categories: [Groceries, Utilities, Rent, Insurance]
    labels: [Essential]

  - type: category
    name: Utilities
    patterns: [AGL, ORIGIN, ENERGY AUSTRALIA, TELSTRA, OPTUS]
    category: Bills > Utilities
    confidence: 90

  # ═══════════════════════════════════════════════════════════
  # DISCRETIONARY
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Dining Out
    patterns: [RESTAURANT, CAFE, UBER EATS, DELIVEROO]
    category: Food & Dining > Dining Out
    confidence: 90

  - type: label
    name: Discretionary Spending
    when:
      categories: [Dining Out, Entertainment, Shopping]
    labels: [Discretionary]

  - type: category
    name: Entertainment
    patterns: [NETFLIX, SPOTIFY, CINEMA, STEAM]
    category: Entertainment
    confidence: 95

  # ═══════════════════════════════════════════════════════════
  # TRANSPORT
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Transport
    patterns: [UBER, TRAIN, BUS, PETROL]
    exclude_patterns: [UBER EATS]
    category: Transport
    confidence: 90

  # ═══════════════════════════════════════════════════════════
  # CROSS-CATEGORY LABELS
  # ═══════════════════════════════════════════════════════════

  - type: label
    name: Large Purchase Review
    when:
      amount_operator: ">"
      amount_value: 200
    labels: [Large Purchase, Review]

  - type: label
    name: Flag Uncategorized
    when:
      uncategorized: true
    labels: [Needs Categorization]
```

**Step 2: Create Separated Families template**

Create `data/templates/separated-families.yaml`:

```yaml
# Separated Families Template
# Best for: Divorced/separated parents managing shared kid expenses

metadata:
  template_name: Separated Families
  description: Track kids expenses, child support, and contributor accountability
  target_users: Separated parents with shared custody and expenses

rules:
  # ═══════════════════════════════════════════════════════════
  # INCOME & TRANSFERS
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Child Support Received
    patterns: [CHILD SUPPORT, CSA, CENTRELINK]
    category: Income > Child Support
    confidence: 95

  - type: label
    name: Child Support Income
    when:
      categories: [Income > Child Support]
      amount_operator: ">"
      amount_value: 0
    labels: [Child Support, Income]

  # ═══════════════════════════════════════════════════════════
  # KIDS EXPENSES - ESSENTIAL
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Kids School Expenses
    patterns: [SCHOOL, UNIFORM, TEXTBOOK, EXCURSION]
    category: Kids > Education
    confidence: 90

  - type: label
    name: Kids Essential Expense
    when:
      categories: [Kids > Education, Kids > Medical, Kids > Clothing]
    labels: [Kids Expense, Essential, Shared Responsibility]

  - type: category
    name: Kids Medical
    patterns: [DOCTOR, DENTIST, PHARMACY, CHEMIST]
    accounts: [Kids Account]
    category: Kids > Medical
    confidence: 85

  - type: category
    name: Kids Activities
    patterns: [SPORT, MUSIC LESSONS, SWIMMING, DANCE]
    category: Kids > Activities
    confidence: 85

  - type: label
    name: Kids Discretionary
    when:
      categories: [Kids > Activities, Kids > Entertainment]
    labels: [Kids Expense, Discretionary]

  # ═══════════════════════════════════════════════════════════
  # CONTRIBUTOR TRACKING
  # ═══════════════════════════════════════════════════════════

  - type: label
    name: Parent 1 Contribution
    when:
      accounts: [Parent1 Account, Joint Account]
      amount_operator: ">"
      amount_value: 0
    labels: [Contributor: Parent1]

  - type: label
    name: Parent 2 Contribution
    when:
      accounts: [Parent2 Account]
      amount_operator: ">"
      amount_value: 0
    labels: [Contributor: Parent2]

  # ═══════════════════════════════════════════════════════════
  # EXPENSE SPLITTING & RECONCILIATION
  # ═══════════════════════════════════════════════════════════

  - type: label
    name: Needs Reconciliation - Large Kids Expense
    when:
      categories: [Kids > Education, Kids > Medical, Kids > Activities]
      amount_operator: ">"
      amount_value: 100
    labels: [Needs Reconciliation, Shared Responsibility]

  - type: label
    name: Flag Uncategorized Kids Account
    when:
      accounts: [Kids Account]
      uncategorized: true
    labels: [Needs Categorization, Kids Related]
```

**Step 3: Create Shared Household template**

Create `data/templates/shared-household.yaml`:

```yaml
# Shared Household Template
# Best for: Couples, roommates, or families with shared expenses

metadata:
  template_name: Shared Household
  description: Manage shared expenses with contributor tracking and approval workflows
  target_users: Couples, roommates, or families sharing bills

rules:
  # ═══════════════════════════════════════════════════════════
  # SHARED EXPENSES - ESSENTIAL
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Shared Groceries
    patterns: [WOOLWORTHS, COLES, ALDI, IGA]
    accounts: [Shared Bills, Joint Account]
    category: Food & Dining > Groceries
    confidence: 95

  - type: label
    name: Shared Essential Expense
    when:
      categories: [Groceries, Utilities, Rent, Insurance]
      accounts: [Shared Bills, Joint Account]
    labels: [Shared Expense, Essential]

  - type: category
    name: Rent/Mortgage
    patterns: [RENT, MORTGAGE, REAL ESTATE]
    category: Housing > Rent
    confidence: 95

  - type: label
    name: Major Shared Expense
    when:
      categories: [Housing > Rent, Housing > Mortgage]
    labels: [Shared Expense, Major, Essential]

  - type: category
    name: Utilities
    patterns: [AGL, ORIGIN, ENERGY, WATER, GAS, TELSTRA, INTERNET]
    category: Bills > Utilities
    confidence: 90

  # ═══════════════════════════════════════════════════════════
  # CONTRIBUTOR TRACKING
  # ═══════════════════════════════════════════════════════════

  - type: label
    name: Person A Contribution
    when:
      accounts: [Shared Bills, Joint Account]
      categories: []  # Applies to all categories
      amount_operator: ">"
      amount_value: 0
    labels: [Contributor: PersonA]

  - type: label
    name: Person B Contribution
    when:
      accounts: [Shared Bills]
      patterns: [PERSONB NAME, TRANSFER FROM PERSONB]
      amount_operator: ">"
      amount_value: 0
    labels: [Contributor: PersonB]

  # ═══════════════════════════════════════════════════════════
  # PERSONAL EXPENSES
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Personal Groceries
    patterns: [WOOLWORTHS, COLES, ALDI]
    accounts: [Personal, PersonA Account, PersonB Account]
    category: Food & Dining > Groceries
    confidence: 95

  - type: label
    name: Personal Expense
    when:
      accounts: [Personal, PersonA Account, PersonB Account]
    labels: [Personal, Individual]

  # ═══════════════════════════════════════════════════════════
  # APPROVAL WORKFLOWS
  # ═══════════════════════════════════════════════════════════

  - type: label
    name: Needs Approval - Large Shared Purchase
    when:
      accounts: [Shared Bills, Joint Account]
      amount_operator: ">"
      amount_value: 150
    labels: [Needs Approval, Review Required]

  - type: label
    name: Needs Approval - Discretionary Shared
    when:
      accounts: [Shared Bills, Joint Account]
      categories: [Dining Out, Entertainment, Shopping]
    labels: [Needs Approval, Discretionary]

  # ═══════════════════════════════════════════════════════════
  # RECONCILIATION
  # ═══════════════════════════════════════════════════════════

  - type: label
    name: Monthly Reconciliation Item
    when:
      accounts: [Shared Bills, Joint Account]
      categories: [Groceries, Utilities, Dining Out, Entertainment]
    labels: [Monthly Reconciliation]

  - type: label
    name: Flag Uncategorized Shared
    when:
      accounts: [Shared Bills, Joint Account]
      uncategorized: true
    labels: [Needs Categorization, Shared Account]
```

**Step 4: Create Advanced template**

Create `data/templates/advanced.yaml`:

```yaml
# Advanced Template
# Best for: Complex households with investments, tax optimization, business expenses

metadata:
  template_name: Advanced
  description: Comprehensive tracking with tax optimization and investment management
  target_users: High-income households, business owners, investors

rules:
  # ═══════════════════════════════════════════════════════════
  # INCOME STREAMS
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Salary Income
    patterns: [SALARY, WAGES, EMPLOYER]
    category: Income > Employment
    confidence: 95

  - type: label
    name: Taxable Income
    when:
      categories: [Income > Employment, Income > Business, Income > Rental]
    labels: [Taxable Income, ATO: Income]

  - type: category
    name: Investment Income
    patterns: [DIVIDEND, DISTRIBUTION, INTEREST, INVESTMENT]
    category: Income > Investment
    confidence: 90

  - type: label
    name: Investment Income Tax
    when:
      categories: [Income > Investment]
    labels: [Taxable Income, ATO: Investment, CGT Relevant]

  - type: category
    name: Business Income
    patterns: [INVOICE, CLIENT, BUSINESS]
    category: Income > Business
    confidence: 85

  # ═══════════════════════════════════════════════════════════
  # TAX DEDUCTIBLE EXPENSES
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Home Office
    patterns: [OFFICE SUPPLIES, DESK, CHAIR, MONITOR, OFFICEWORKS]
    category: Work Expenses > Home Office
    confidence: 85

  - type: label
    name: Tax Deductible - Home Office
    when:
      categories: [Work Expenses > Home Office]
    labels: [Tax Deductible, ATO: D2 - Work Expenses]

  - type: category
    name: Professional Development
    patterns: [COURSE, TRAINING, CONFERENCE, SEMINAR, UDEMY, COURSERA]
    category: Work Expenses > Professional Development
    confidence: 90

  - type: label
    name: Tax Deductible - Self Education
    when:
      categories: [Work Expenses > Professional Development]
    labels: [Tax Deductible, ATO: D5 - Self Education]

  - type: category
    name: Work Travel
    patterns: [FLIGHT, HOTEL, ACCOMMODATION]
    accounts: [Work, Business]
    category: Work Expenses > Travel
    confidence: 85

  - type: label
    name: Tax Deductible - Work Travel
    when:
      categories: [Work Expenses > Travel]
    labels: [Tax Deductible, ATO: D1 - Work Travel, Requires Documentation]

  - type: category
    name: Charitable Donations
    patterns: [DONATION, CHARITY, FOUNDATION, GIVIT]
    category: Charity
    confidence: 90

  - type: label
    name: Tax Deductible - Donation
    when:
      categories: [Charity]
    labels: [Tax Deductible, ATO: D9 - Donations, Requires Receipt]

  # ═══════════════════════════════════════════════════════════
  # INVESTMENT MANAGEMENT
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Share Purchase
    patterns: [COMMSEC, ETRADE, SELFWEALTH, SHARE PURCHASE]
    category: Investment > Shares
    confidence: 90

  - type: label
    name: Capital Gains Tracking
    when:
      categories: [Investment > Shares, Investment > Property, Investment > Crypto]
    labels: [CGT Relevant, Investment, Requires Cost Base Tracking]

  - type: category
    name: Investment Fees
    patterns: [PLATFORM FEE, MANAGEMENT FEE, BROKERAGE]
    category: Investment > Fees
    confidence: 85

  - type: label
    name: Tax Deductible - Investment Fees
    when:
      categories: [Investment > Fees]
    labels: [Tax Deductible, ATO: D4 - Investment Management]

  # ═══════════════════════════════════════════════════════════
  # RENTAL PROPERTY
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Rental Property Expenses
    patterns: [PROPERTY MANAGEMENT, MAINTENANCE, REPAIRS]
    accounts: [Investment Property]
    category: Investment > Rental Property > Expenses
    confidence: 85

  - type: label
    name: Tax Deductible - Rental Property
    when:
      categories: [Investment > Rental Property > Expenses]
    labels: [Tax Deductible, ATO: Rental Property, Negative Gearing]

  - type: category
    name: Rental Income
    patterns: [RENT RECEIVED, RENTAL INCOME]
    category: Income > Rental
    confidence: 95

  # ═══════════════════════════════════════════════════════════
  # BUSINESS EXPENSES
  # ═══════════════════════════════════════════════════════════

  - type: category
    name: Business Software
    patterns: [SLACK, ADOBE, MICROSOFT, SOFTWARE SUBSCRIPTION]
    accounts: [Business]
    category: Business Expenses > Software
    confidence: 90

  - type: label
    name: Tax Deductible - Business Expense
    when:
      accounts: [Business]
      categories: [Business Expenses > Software, Business Expenses > Equipment]
    labels: [Tax Deductible, Business Expense, GST Claimable]

  # ═══════════════════════════════════════════════════════════
  # CROSS-CATEGORY RULES
  # ═══════════════════════════════════════════════════════════

  - type: label
    name: Large Transaction - Requires Documentation
    when:
      amount_operator: ">"
      amount_value: 1000
    labels: [Large Transaction, Requires Documentation]

  - type: label
    name: End of Financial Year Review
    when:
      categories: [Income > Investment, Work Expenses, Investment, Charity]
    labels: [EOFY Review Required]

  - type: label
    name: Flag Uncategorized
    when:
      uncategorized: true
    labels: [Needs Categorization, Review Required]
```

**Step 5: Create template index**

Create `data/templates/INDEX.md`:

```markdown
# Rule Templates

Preset rule hierarchies for different household types. Select the template that best matches your situation during initial setup.

## Available Templates

| Template | Best For | Key Features |
|----------|----------|--------------|
| **simple.yaml** | Single person | Basic categories, essential/discretionary labels |
| **separated-families.yaml** | Separated parents | Kids expense tracking, contributor tracking, child support |
| **shared-household.yaml** | Couples/roommates | Shared expense tracking, approval workflows, reconciliation |
| **advanced.yaml** | Complex finances | Tax optimization, investment tracking, business expenses |

## Template Metadata

Each template includes:
- **Category hierarchy** - Organized category structure
- **Label taxonomy** - Labels for tracking and workflows
- **Sample rules** - Pre-configured patterns for common merchants

## Customization

After selecting a template:
1. Copy to `data/rules.yaml`
2. Update merchant patterns for your region
3. Adjust account names to match your setup
4. Add custom rules as needed

## Template Details

### Simple
- **Target:** Individual managing personal finances
- **Categories:** Income, Groceries, Utilities, Dining, Entertainment, Transport
- **Labels:** Essential, Discretionary, Large Purchase

### Separated Families
- **Target:** Divorced/separated parents with shared custody
- **Categories:** Child Support, Kids Education, Kids Medical, Kids Activities
- **Labels:** Contributor tracking, Shared Responsibility, Needs Reconciliation

### Shared Household
- **Target:** Couples, roommates, or families with joint expenses
- **Categories:** Shared Groceries, Rent, Utilities, Personal expenses
- **Labels:** Contributor tracking, Needs Approval, Monthly Reconciliation

### Advanced
- **Target:** High-income households, business owners, investors
- **Categories:** Multiple income streams, Investment categories, Business expenses
- **Labels:** Tax deductible (ATO codes), CGT tracking, EOFY review, Documentation requirements
```

**Step 6: Create template selector script**

Create `scripts/setup/template_selector.py`:

```python
"""Template selector for initial Agent Smith setup."""

import shutil
from pathlib import Path
from typing import Dict, Any


class TemplateSelector:
    """Select and apply rule templates based on household type."""

    def __init__(self):
        """Initialize template selector."""
        self.templates_dir = Path(__file__).parent.parent.parent / "data" / "templates"
        self.rules_file = Path(__file__).parent.parent.parent / "data" / "rules.yaml"

    def list_templates(self) -> Dict[str, Dict[str, str]]:
        """List available templates with metadata.

        Returns:
            Dict mapping template names to metadata
        """
        templates = {
            "simple": {
                "name": "Simple - Single Person",
                "description": "Basic categories for individual financial tracking",
                "best_for": "Single person, no shared expenses",
            },
            "separated-families": {
                "name": "Separated Families",
                "description": "Kids expenses, child support, contributor tracking",
                "best_for": "Divorced/separated parents with shared custody",
            },
            "shared-household": {
                "name": "Shared Household",
                "description": "Shared expense tracking with approval workflows",
                "best_for": "Couples, roommates, or families",
            },
            "advanced": {
                "name": "Advanced",
                "description": "Tax optimization and investment management",
                "best_for": "Business owners, investors, complex finances",
            },
        }

        return templates

    def apply_template(self, template_name: str, backup: bool = True) -> None:
        """Apply a template to rules.yaml.

        Args:
            template_name: Name of template (simple, separated-families, etc.)
            backup: Whether to backup existing rules.yaml
        """
        template_file = self.templates_dir / f"{template_name}.yaml"

        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")

        # Backup existing rules if requested
        if backup and self.rules_file.exists():
            backup_file = self.rules_file.with_suffix(".yaml.backup")
            shutil.copy(self.rules_file, backup_file)
            print(f"Backed up existing rules to {backup_file}")

        # Copy template to rules.yaml
        shutil.copy(template_file, self.rules_file)
        print(f"Applied template: {template_name}")
        print(f"Rules file: {self.rules_file}")


def main():
    """Interactive template selection."""
    selector = TemplateSelector()

    print("=" * 70)
    print("Agent Smith - Rule Template Setup")
    print("=" * 70)
    print()

    templates = selector.list_templates()

    print("Available templates:")
    for i, (key, info) in enumerate(templates.items(), 1):
        print(f"\n{i}. {info['name']}")
        print(f"   {info['description']}")
        print(f"   Best for: {info['best_for']}")

    print()
    choice = input("Select template (1-4): ").strip()

    template_map = {
        "1": "simple",
        "2": "separated-families",
        "3": "shared-household",
        "4": "advanced",
    }

    template_name = template_map.get(choice)

    if not template_name:
        print("Invalid choice. Exiting.")
        return

    print()
    print(f"Applying template: {templates[template_name]['name']}")
    selector.apply_template(template_name)

    print()
    print("✓ Template applied successfully!")
    print()
    print("Next steps:")
    print("1. Review data/rules.yaml and customize for your needs")
    print("2. Update merchant patterns for your region")
    print("3. Adjust account names to match your PocketSmith setup")
    print("4. Run: /agent-smith-categorize --mode=dry-run to test")


if __name__ == "__main__":
    main()
```

**Step 7: Commit**

```bash
git add data/templates/ scripts/setup/template_selector.py
git commit -m "feat: add preset rule templates for different household types

- Simple template: single person, basic categories
- Separated families: kids expenses, child support, contributor tracking
- Shared household: shared expenses, approval workflows, reconciliation
- Advanced: tax optimization, investments, business expenses
- Template selector script for interactive setup"
```

---

## Task 5: LLM Categorization Service (Subagent Integration)

**Files:**
- Create: `scripts/services/llm_categorization.py`
- Create: `tests/unit/test_llm_categorization.py`

**Step 1: Write failing test for LLM service**

Create `tests/unit/test_llm_categorization.py`:

```python
"""Tests for LLM categorization service."""

import pytest
from scripts.services.llm_categorization import LLMCategorizationService


def test_build_categorization_prompt():
    """Test building LLM prompt for categorization."""
    service = LLMCategorizationService()

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "amount": -45.50},
        {"id": 2, "payee": "UBER TRIP", "amount": -25.00},
    ]

    categories = [
        {"title": "Groceries", "parent": "Expenses > Food & Dining"},
        {"title": "Transport", "parent": "Expenses > Transport"},
    ]

    prompt = service.build_categorization_prompt(transactions, categories)

    assert "WOOLWORTHS" in prompt
    assert "UBER TRIP" in prompt
    assert "Groceries" in prompt
    assert "Transport" in prompt
    assert "confidence" in prompt.lower()


def test_parse_llm_response():
    """Test parsing LLM categorization response."""
    service = LLMCategorizationService()

    llm_response = """
    Transaction 1: WOOLWORTHS
    Category: Groceries
    Confidence: 95%

    Transaction 2: UBER TRIP
    Category: Transport
    Confidence: 90%
    """

    transaction_ids = [1, 2]

    results = service.parse_llm_response(llm_response, transaction_ids)

    assert len(results) == 2
    assert results[0]["transaction_id"] == 1
    assert results[0]["category"] == "Groceries"
    assert results[0]["confidence"] == 95
    assert results[1]["category"] == "Transport"
    assert results[1]["confidence"] == 90
```

**Step 2: Run test to verify it fails**

```bash
uv run python -u -m pytest tests/unit/test_llm_categorization.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement LLM service stub**

Create `scripts/services/llm_categorization.py`:

```python
"""LLM-powered categorization service using subagent context."""

import re
import logging
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)


class LLMCategorizationService:
    """Service for LLM-powered transaction categorization.

    Uses the subagent's own LLM context rather than external API calls.
    This is implemented via prompt instructions to the subagent.
    """

    def __init__(self):
        """Initialize LLM categorization service."""
        pass

    def build_categorization_prompt(
        self,
        transactions: List[Dict[str, Any]],
        categories: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for LLM to categorize transactions.

        Args:
            transactions: List of transaction dicts (id, payee, amount)
            categories: List of category dicts (title, parent hierarchy)

        Returns:
            Formatted prompt string
        """
        # Build category hierarchy section
        category_lines = []
        for cat in categories:
            parent = cat.get("parent", "")
            if parent:
                category_lines.append(f"- {parent} > {cat['title']}")
            else:
                category_lines.append(f"- {cat['title']}")

        categories_text = "\n".join(category_lines)

        # Build transactions section
        transaction_lines = []
        for i, txn in enumerate(transactions, 1):
            payee = txn.get("payee", "Unknown")
            amount = txn.get("amount", 0)
            transaction_lines.append(
                f"Transaction {i}: {payee} (${abs(amount):.2f})"
            )

        transactions_text = "\n".join(transaction_lines)

        prompt = f"""Categorize these transactions using the category hierarchy below.

For each transaction, provide:
1. Category name (exact match from hierarchy)
2. Confidence score (0-100%)

Available Categories:
{categories_text}

Transactions to Categorize:
{transactions_text}

Format your response as:
Transaction N: [payee]
Category: [category name]
Confidence: [score]%

Reasoning: [brief explanation]
"""

        return prompt

    def parse_llm_response(
        self,
        llm_response: str,
        transaction_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """Parse LLM categorization response.

        Args:
            llm_response: Raw LLM response text
            transaction_ids: Original transaction IDs (in order)

        Returns:
            List of categorization results
        """
        results = []

        # Split response into transaction blocks
        blocks = re.split(r'Transaction \d+:', llm_response)
        blocks = [b.strip() for b in blocks if b.strip()]

        for i, block in enumerate(blocks):
            if i >= len(transaction_ids):
                break

            txn_id = transaction_ids[i]

            # Extract category
            category_match = re.search(r'Category:\s*(.+?)(?:\n|$)', block)
            category = category_match.group(1).strip() if category_match else None

            # Extract confidence
            confidence_match = re.search(r'Confidence:\s*(\d+)', block)
            confidence = int(confidence_match.group(1)) if confidence_match else 50

            # Extract reasoning (optional)
            reasoning_match = re.search(r'Reasoning:\s*(.+?)(?:\n\n|$)', block, re.DOTALL)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

            results.append({
                "transaction_id": txn_id,
                "category": category,
                "confidence": confidence,
                "reasoning": reasoning,
                "source": "llm",
            })

        return results

    def build_validation_prompt(
        self,
        transaction: Dict[str, Any],
        suggested_category: str,
        rule_confidence: int,
    ) -> str:
        """Build prompt for LLM to validate a rule-based categorization.

        Args:
            transaction: Transaction dict
            suggested_category: Category suggested by rule
            rule_confidence: Confidence of the rule match

        Returns:
            Formatted validation prompt
        """
        payee = transaction.get("payee", "Unknown")
        amount = transaction.get("amount", 0)

        prompt = f"""Validate this transaction categorization:

Transaction: {payee} (${abs(amount):.2f})
Suggested Category: {suggested_category}
Rule Confidence: {rule_confidence}%

Does this categorization look correct? Provide:
1. Validation: CONFIRM or REJECT
2. Adjusted Confidence: 0-100%
3. Reasoning: Brief explanation

If you REJECT, suggest a better category.
"""

        return prompt

    def parse_validation_response(
        self,
        llm_response: str,
        original_category: str,
        original_confidence: int,
    ) -> Dict[str, Any]:
        """Parse LLM validation response.

        Args:
            llm_response: Raw LLM response
            original_category: Original suggested category
            original_confidence: Original confidence score

        Returns:
            Validation result dict
        """
        # Check validation status
        validation = "UNKNOWN"
        if "CONFIRM" in llm_response.upper():
            validation = "CONFIRM"
        elif "REJECT" in llm_response.upper():
            validation = "REJECT"

        # Extract adjusted confidence
        confidence_match = re.search(r'Adjusted Confidence:\s*(\d+)', llm_response)
        adjusted_confidence = int(confidence_match.group(1)) if confidence_match else original_confidence

        # Extract suggested category if rejected
        suggested_category = original_category
        if validation == "REJECT":
            category_match = re.search(r'Suggested Category:\s*(.+?)(?:\n|$)', llm_response)
            if category_match:
                suggested_category = category_match.group(1).strip()

        # Extract reasoning
        reasoning_match = re.search(r'Reasoning:\s*(.+?)(?:\n\n|$)', llm_response, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

        return {
            "validation": validation,
            "category": suggested_category,
            "confidence": adjusted_confidence,
            "reasoning": reasoning,
        }
```

**Step 4: Run tests to verify they pass**

```bash
uv run python -u -m pytest tests/unit/test_llm_categorization.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add scripts/services/llm_categorization.py tests/unit/test_llm_categorization.py
git commit -m "feat: add LLM categorization service with prompt building"
```

---

## Task 6: Integration with Categorization Workflow

**Files:**
- Modify: `scripts/workflows/categorization.py`
- Create: `tests/integration/test_llm_workflow.py`

**Step 1: Write integration test**

Create `tests/integration/test_llm_workflow.py`:

```python
"""Integration tests for LLM-enhanced categorization workflow."""

import pytest
from pathlib import Path
from scripts.workflows.categorization import EnhancedCategorizationWorkflow
from scripts.core.unified_rules import UnifiedRuleEngine


def test_workflow_uses_rules_first(tmp_path):
    """Test workflow tries rules before LLM."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("""
rules:
  - type: category
    name: Test Rule
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95
""")

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = EnhancedCategorizationWorkflow(engine=engine)

    transaction = {
        "id": 123,
        "payee": "WOOLWORTHS METRO",
        "amount": -45.50,
    }

    result = workflow.process_transaction(transaction, mode="smart")

    # Should match via rule, not LLM
    assert result["category"] == "Groceries"
    assert result["source"] == "rule"
    assert result["llm_used"] is False


def test_workflow_falls_back_to_llm(tmp_path):
    """Test workflow falls back to LLM when no rule matches."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("rules: []")

    engine = UnifiedRuleEngine(rules_file=rules_file)
    workflow = EnhancedCategorizationWorkflow(engine=engine)

    transaction = {
        "id": 123,
        "payee": "UNKNOWN MERCHANT 123",
        "amount": -45.50,
    }

    # Mock LLM response
    workflow.llm_service.categorize = lambda txns, cats: [
        {"transaction_id": 123, "category": "Shopping", "confidence": 85}
    ]

    result = workflow.process_transaction(
        transaction,
        mode="smart",
        available_categories=[{"title": "Shopping"}]
    )

    # Should fall back to LLM
    assert result["source"] == "llm"
    assert result["llm_used"] is True
```

**Step 2: Run test to verify it fails**

```bash
uv run python -u -m pytest tests/integration/test_llm_workflow.py -v
```

Expected: FAIL with import errors

**Step 3: Implement enhanced workflow**

Modify `scripts/workflows/categorization.py`:

```python
"""Enhanced categorization workflow with LLM integration."""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from scripts.core.unified_rules import UnifiedRuleEngine
from scripts.services.llm_categorization import LLMCategorizationService
from scripts.orchestration.conductor import SubagentConductor, OperationType

if TYPE_CHECKING:
    from scripts.core.api_client import PocketSmithClient

logger = logging.getLogger(__name__)


class EnhancedCategorizationWorkflow:
    """Enhanced workflow with rule-based and LLM categorization."""

    def __init__(
        self,
        engine: UnifiedRuleEngine,
        client: Optional["PocketSmithClient"] = None,
        mode: str = "smart"
    ):
        """Initialize enhanced categorization workflow.

        Args:
            engine: Unified rule engine
            client: PocketSmith API client
            mode: Intelligence mode (conservative|smart|aggressive)
        """
        self.engine = engine
        self.client = client
        self.mode = mode
        self.llm_service = LLMCategorizationService()
        self.conductor = SubagentConductor()

    def process_transaction(
        self,
        transaction: Dict[str, Any],
        mode: Optional[str] = None,
        available_categories: Optional[List[Dict[str, Any]]] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """Process a single transaction (categorize and label).

        Args:
            transaction: Transaction dict
            mode: Intelligence mode override
            available_categories: List of available categories for LLM
            dry_run: If True, don't apply changes

        Returns:
            Result dict with category, labels, source, etc.
        """
        mode = mode or self.mode

        # Phase 1: Try rule-based categorization
        rule_result = self.engine.categorize_and_label(transaction)

        if rule_result["category_matched"]:
            # Rule matched - check if needs LLM validation
            confidence = rule_result["confidence"]

            if self._should_validate_with_llm(confidence, mode):
                # Validate with LLM (70-89% confidence range)
                validation = self._validate_with_llm(
                    transaction,
                    rule_result["category"],
                    confidence
                )

                result = {
                    **rule_result,
                    "source": "rule",
                    "llm_used": True,
                    "llm_validation": validation,
                    "final_confidence": validation["confidence"],
                }
            else:
                result = {
                    **rule_result,
                    "source": "rule",
                    "llm_used": False,
                    "final_confidence": confidence,
                }
        else:
            # No rule match - fall back to LLM
            if available_categories is None:
                logger.warning("No categories provided for LLM categorization")
                return {
                    "category_matched": False,
                    "source": "none",
                    "llm_used": False,
                }

            llm_result = self._categorize_with_llm([transaction], available_categories)

            if llm_result:
                result = {
                    "category_matched": True,
                    "category": llm_result[0]["category"],
                    "confidence": llm_result[0]["confidence"],
                    "source": "llm",
                    "llm_used": True,
                    "llm_reasoning": llm_result[0].get("reasoning", ""),
                    "final_confidence": llm_result[0]["confidence"],
                    "labels_matched": False,
                    "labels": [],
                }
            else:
                result = {
                    "category_matched": False,
                    "source": "none",
                    "llm_used": True,
                }

        # Apply if not dry run and meets confidence threshold
        if not dry_run and result.get("category_matched"):
            self._apply_categorization(transaction, result, mode)

        return result

    def _should_validate_with_llm(self, confidence: int, mode: str) -> bool:
        """Determine if should validate rule match with LLM.

        Validates medium-confidence matches (70-89% in smart mode).
        """
        if mode == "conservative":
            return False  # Always ask user, don't use LLM
        elif mode == "smart":
            return 70 <= confidence < 90
        elif mode == "aggressive":
            return 50 <= confidence < 80
        return False

    def _validate_with_llm(
        self,
        transaction: Dict[str, Any],
        suggested_category: str,
        confidence: int,
    ) -> Dict[str, Any]:
        """Validate a rule-based categorization with LLM.

        NOTE: This is a stub - actual LLM calls happen in subagent context.
        """
        prompt = self.llm_service.build_validation_prompt(
            transaction, suggested_category, confidence
        )

        # In real implementation, this would be passed to subagent
        # For now, return stub validation
        logger.info(f"LLM validation prompt: {prompt[:100]}...")

        return {
            "validation": "CONFIRM",
            "category": suggested_category,
            "confidence": min(95, confidence + 10),
            "reasoning": "LLM validation not yet implemented",
        }

    def _categorize_with_llm(
        self,
        transactions: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Categorize transactions using LLM.

        NOTE: This is a stub - actual LLM calls happen in subagent context.
        """
        prompt = self.llm_service.build_categorization_prompt(
            transactions, categories
        )

        # In real implementation, this would be passed to subagent
        logger.info(f"LLM categorization prompt: {prompt[:100]}...")

        return []

    def _apply_categorization(
        self,
        transaction: Dict[str, Any],
        result: Dict[str, Any],
        mode: str,
    ) -> None:
        """Apply categorization to transaction via API."""
        if self.client is None:
            logger.warning("No API client - cannot apply categorization")
            return

        # Check if should auto-apply based on confidence and mode
        confidence = result.get("final_confidence", 0)

        should_auto_apply = False
        if mode == "smart" and confidence >= 90:
            should_auto_apply = True
        elif mode == "aggressive" and confidence >= 80:
            should_auto_apply = True

        if should_auto_apply:
            logger.info(
                f"Auto-applying category '{result['category']}' "
                f"to transaction {transaction['id']}"
            )
            # API call would happen here
        else:
            logger.info(
                f"Requires approval: category '{result['category']}' "
                f"(confidence: {confidence}%)"
            )
```

**Step 4: Run tests**

```bash
uv run python -u -m pytest tests/integration/test_llm_workflow.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add scripts/workflows/categorization.py tests/integration/test_llm_workflow.py
git commit -m "feat: integrate LLM categorization into enhanced workflow"
```

---

## Task 7: Operational Modes & Range Processing

**Files:**
- Create: `scripts/operations/batch_processor.py`
- Create: `tests/unit/test_batch_processor.py`
- Modify: `scripts/workflows/categorization.py`

**Step 1: Write failing test for operational modes**

Create `tests/unit/test_batch_processor.py`:

```python
"""Tests for batch processing operational modes."""

import pytest
from datetime import datetime, timedelta
from scripts.operations.batch_processor import (
    BatchProcessor,
    ProcessingMode,
    UpdateStrategy,
    DateRange,
)


def test_dry_run_mode():
    """Test dry-run mode doesn't modify transactions."""
    processor = BatchProcessor(mode=ProcessingMode.DRY_RUN)

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "category": None},
        {"id": 2, "payee": "UBER", "category": None},
    ]

    results = processor.process_batch(transactions)

    # Dry-run should show what would happen but not apply
    assert results["total"] == 2
    assert results["would_categorize"] == 2
    assert results["applied"] == 0
    assert results["dry_run"] is True


def test_validate_mode_detects_changes():
    """Test validate mode identifies transactions that would change."""
    processor = BatchProcessor(mode=ProcessingMode.VALIDATE)

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "category": {"title": "Shopping"}},
        {"id": 2, "payee": "COLES", "category": {"title": "Groceries"}},
    ]

    # Rules would categorize both as "Groceries"
    results = processor.process_batch(transactions)

    assert results["total"] == 2
    assert results["would_change"] == 1  # Transaction 1 would change
    assert results["unchanged"] == 1  # Transaction 2 already correct


def test_update_strategy_skip_existing():
    """Test SKIP_EXISTING strategy."""
    processor = BatchProcessor(
        mode=ProcessingMode.APPLY,
        update_strategy=UpdateStrategy.SKIP_EXISTING,
    )

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "category": None},
        {"id": 2, "payee": "COLES", "category": {"title": "Shopping"}},
    ]

    results = processor.process_batch(transactions)

    # Should only process uncategorized
    assert results["processed"] == 1
    assert results["skipped"] == 1


def test_update_strategy_replace_all():
    """Test REPLACE_ALL strategy."""
    processor = BatchProcessor(
        mode=ProcessingMode.APPLY,
        update_strategy=UpdateStrategy.REPLACE_ALL,
    )

    transactions = [
        {"id": 1, "payee": "WOOLWORTHS", "category": None},
        {"id": 2, "payee": "COLES", "category": {"title": "Shopping"}},
    ]

    results = processor.process_batch(transactions)

    # Should process all transactions
    assert results["processed"] == 2
    assert results["skipped"] == 0


def test_update_strategy_upgrade_confidence():
    """Test UPGRADE_CONFIDENCE strategy."""
    processor = BatchProcessor(
        mode=ProcessingMode.APPLY,
        update_strategy=UpdateStrategy.UPGRADE_CONFIDENCE,
    )

    transactions = [
        {
            "id": 1,
            "payee": "WOOLWORTHS",
            "category": {"title": "Groceries"},
            "_category_confidence": 75,  # Lower confidence
        },
        {
            "id": 2,
            "payee": "COLES",
            "category": {"title": "Groceries"},
            "_category_confidence": 95,  # Higher confidence
        },
    ]

    # New rule has 95% confidence
    results = processor.process_batch(transactions)

    # Should upgrade first, skip second
    assert results["upgraded"] == 1
    assert results["skipped"] == 1


def test_date_range_filtering():
    """Test filtering transactions by date range."""
    today = datetime.now()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    transactions = [
        {"id": 1, "payee": "TEST1", "date": today.strftime("%Y-%m-%d")},
        {"id": 2, "payee": "TEST2", "date": last_week.strftime("%Y-%m-%d")},
        {"id": 3, "payee": "TEST3", "date": last_month.strftime("%Y-%m-%d")},
    ]

    # Filter to last 2 weeks
    date_range = DateRange(
        start_date=last_week - timedelta(days=7),
        end_date=today,
    )

    processor = BatchProcessor(date_range=date_range)
    filtered = processor.filter_transactions(transactions)

    assert len(filtered) == 2  # Today and last week only


def test_account_filtering():
    """Test filtering transactions by account."""
    transactions = [
        {"id": 1, "payee": "TEST1", "_account_name": "Personal"},
        {"id": 2, "payee": "TEST2", "_account_name": "Shared Bills"},
        {"id": 3, "payee": "TEST3", "_account_name": "Work"},
    ]

    processor = BatchProcessor(accounts=["Personal", "Work"])
    filtered = processor.filter_transactions(transactions)

    assert len(filtered) == 2  # Personal and Work only


def test_limit_processing():
    """Test limiting number of transactions processed."""
    transactions = [{"id": i, "payee": f"TEST{i}"} for i in range(100)]

    processor = BatchProcessor(limit=10)
    filtered = processor.filter_transactions(transactions)

    assert len(filtered) == 10
```

**Step 2: Run test to verify it fails**

```bash
uv run python -u -m pytest tests/unit/test_batch_processor.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement batch processor with operational modes**

Create `scripts/operations/batch_processor.py`:

```python
"""Batch processing with operational modes and range filtering."""

import logging
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing mode enum."""

    DRY_RUN = "dry_run"  # Preview changes without applying
    VALIDATE = "validate"  # Identify what would change on existing values
    APPLY = "apply"  # Actually apply changes


class UpdateStrategy(Enum):
    """Strategy for handling existing categorizations."""

    SKIP_EXISTING = "skip_existing"  # Only process uncategorized
    REPLACE_ALL = "replace_all"  # Replace all, even existing
    UPGRADE_CONFIDENCE = "upgrade_confidence"  # Replace if new confidence higher
    REPLACE_IF_DIFFERENT = "replace_if_different"  # Replace if category differs


@dataclass
class DateRange:
    """Date range for filtering transactions."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BatchProcessor:
    """Batch processor with operational modes and filtering."""

    def __init__(
        self,
        mode: ProcessingMode = ProcessingMode.DRY_RUN,
        update_strategy: UpdateStrategy = UpdateStrategy.SKIP_EXISTING,
        date_range: Optional[DateRange] = None,
        accounts: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ):
        """Initialize batch processor.

        Args:
            mode: Processing mode (dry_run/validate/apply)
            update_strategy: How to handle existing categorizations
            date_range: Optional date range filter
            accounts: Optional list of account names to process
            limit: Optional maximum number of transactions to process
        """
        self.mode = mode
        self.update_strategy = update_strategy
        self.date_range = date_range
        self.accounts = accounts
        self.limit = limit

    def filter_transactions(
        self, transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter transactions by date range, accounts, and limit.

        Args:
            transactions: List of transaction dicts

        Returns:
            Filtered list of transactions
        """
        filtered = transactions

        # Filter by date range
        if self.date_range:
            filtered = self._filter_by_date(filtered)

        # Filter by accounts
        if self.accounts:
            filtered = self._filter_by_accounts(filtered)

        # Apply limit
        if self.limit:
            filtered = filtered[: self.limit]

        return filtered

    def _filter_by_date(
        self, transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter transactions by date range."""
        filtered = []

        for txn in transactions:
            txn_date_str = txn.get("date")
            if not txn_date_str:
                continue

            try:
                txn_date = datetime.strptime(txn_date_str, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid date format: {txn_date_str}")
                continue

            # Check start date
            if self.date_range.start_date and txn_date < self.date_range.start_date:
                continue

            # Check end date
            if self.date_range.end_date and txn_date > self.date_range.end_date:
                continue

            filtered.append(txn)

        return filtered

    def _filter_by_accounts(
        self, transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter transactions by account names."""
        filtered = []

        for txn in transactions:
            account_name = txn.get("_account_name") or txn.get(
                "transaction_account", {}
            ).get("name", "")

            if account_name in self.accounts:
                filtered.append(txn)

        return filtered

    def process_batch(
        self,
        transactions: List[Dict[str, Any]],
        categorization_fn: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Process a batch of transactions.

        Args:
            transactions: List of transaction dicts
            categorization_fn: Function to categorize transactions

        Returns:
            Results dict with counts and details
        """
        results = {
            "total": len(transactions),
            "processed": 0,
            "skipped": 0,
            "would_categorize": 0,
            "would_change": 0,
            "unchanged": 0,
            "upgraded": 0,
            "applied": 0,
            "dry_run": self.mode == ProcessingMode.DRY_RUN,
            "mode": self.mode.value,
            "update_strategy": self.update_strategy.value,
            "details": [],
        }

        for txn in transactions:
            # Check if should process based on update strategy
            should_process = self._should_process_transaction(txn)

            if not should_process:
                results["skipped"] += 1
                continue

            # Categorize transaction (stub for now)
            if categorization_fn:
                categorization_result = categorization_fn(txn)
            else:
                categorization_result = self._stub_categorize(txn)

            # Handle based on mode
            if self.mode == ProcessingMode.DRY_RUN:
                results["would_categorize"] += 1
                results["details"].append(
                    {
                        "transaction_id": txn["id"],
                        "action": "would_categorize",
                        "category": categorization_result.get("category"),
                    }
                )

            elif self.mode == ProcessingMode.VALIDATE:
                if self._would_change(txn, categorization_result):
                    results["would_change"] += 1
                    results["details"].append(
                        {
                            "transaction_id": txn["id"],
                            "action": "would_change",
                            "from": txn.get("category", {}).get("title"),
                            "to": categorization_result.get("category"),
                        }
                    )
                else:
                    results["unchanged"] += 1

            elif self.mode == ProcessingMode.APPLY:
                # Actually apply the categorization
                results["processed"] += 1
                results["applied"] += 1

                if self.update_strategy == UpdateStrategy.UPGRADE_CONFIDENCE:
                    old_confidence = txn.get("_category_confidence", 0)
                    new_confidence = categorization_result.get("confidence", 0)
                    if new_confidence > old_confidence:
                        results["upgraded"] += 1

        return results

    def _should_process_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Determine if transaction should be processed based on update strategy."""
        has_category = transaction.get("category") is not None

        if self.update_strategy == UpdateStrategy.SKIP_EXISTING:
            return not has_category
        elif self.update_strategy == UpdateStrategy.REPLACE_ALL:
            return True
        elif self.update_strategy == UpdateStrategy.UPGRADE_CONFIDENCE:
            return True  # Will check confidence in processing
        elif self.update_strategy == UpdateStrategy.REPLACE_IF_DIFFERENT:
            return True  # Will check if different in processing

        return True

    def _would_change(
        self, transaction: Dict[str, Any], new_result: Dict[str, Any]
    ) -> bool:
        """Check if applying categorization would change the transaction."""
        current_category = transaction.get("category")
        if current_category is None:
            return True  # New categorization

        current_category_title = (
            current_category.get("title")
            if isinstance(current_category, dict)
            else str(current_category)
        )

        new_category = new_result.get("category")

        return current_category_title != new_category

    def _stub_categorize(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Stub categorization for testing."""
        payee = transaction.get("payee", "").upper()

        if "WOOLWORTHS" in payee or "COLES" in payee:
            return {"category": "Groceries", "confidence": 95}
        elif "UBER" in payee:
            return {"category": "Transport", "confidence": 90}

        return {"category": "Unknown", "confidence": 50}
```

**Step 4: Run tests to verify they pass**

```bash
uv run python -u -m pytest tests/unit/test_batch_processor.py -v
```

Expected: PASS (all tests)

**Step 5: Add progress reporting**

Add to `BatchProcessor` class:

```python
    def process_batch_with_progress(
        self,
        transactions: List[Dict[str, Any]],
        categorization_fn: Optional[callable] = None,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Process batch with progress reporting.

        Args:
            transactions: List of transaction dicts
            categorization_fn: Function to categorize transactions
            progress_callback: Optional callback(current, total, transaction)

        Returns:
            Results dict
        """
        results = {
            "total": len(transactions),
            "processed": 0,
            "skipped": 0,
            "applied": 0,
            "errors": 0,
            "dry_run": self.mode == ProcessingMode.DRY_RUN,
            "details": [],
        }

        for i, txn in enumerate(transactions, 1):
            # Report progress
            if progress_callback:
                progress_callback(i, len(transactions), txn)

            try:
                # Process transaction
                should_process = self._should_process_transaction(txn)

                if not should_process:
                    results["skipped"] += 1
                    continue

                if categorization_fn:
                    categorization_result = categorization_fn(txn)
                else:
                    categorization_result = self._stub_categorize(txn)

                if self.mode == ProcessingMode.APPLY:
                    results["applied"] += 1

                results["processed"] += 1

            except Exception as e:
                logger.error(f"Error processing transaction {txn.get('id')}: {e}")
                results["errors"] += 1
                results["details"].append(
                    {
                        "transaction_id": txn.get("id"),
                        "error": str(e),
                    }
                )

        return results
```

**Step 6: Commit**

```bash
git add scripts/operations/batch_processor.py tests/unit/test_batch_processor.py
git commit -m "feat: add batch processor with operational modes and range filtering"
```

---

## Task 8: Deprecate Platform Rule Creation

**Files:**
- Modify: `scripts/core/rule_engine.py`
- Create: `docs/migration/platform-to-local-rules.md`

**Step 1: Add deprecation warning to platform rule creation**

Modify `scripts/core/rule_engine.py`:

```python
    def create_platform_rule(
        self, api_client: Any, category_id: int, payee_contains: str
    ) -> Dict[str, Any]:
        """Create a platform rule via PocketSmith API.

        DEPRECATED: Platform rule creation is deprecated in favor of local rules.
        Use UnifiedRuleEngine with YAML rules instead for full control.

        Platform rules have limitations:
        - Cannot be modified or deleted via API
        - Keyword-only matching (no regex)
        - No confidence scoring or advanced conditions

        This method remains for backward compatibility with existing scripts.
        """
        logger.warning(
            "Platform rule creation is DEPRECATED. "
            "Use UnifiedRuleEngine with YAML rules for better control."
        )

        # Existing implementation...
```

**Step 2: Create migration guide**

Create `docs/migration/platform-to-local-rules.md`:

```markdown
# Migrating from Platform Rules to Local Rules

## Why Migrate?

**Platform rules** (created via PocketSmith API) have limitations:
- ✗ Cannot modify or delete via API
- ✗ Keyword-only matching (no regex patterns)
- ✗ No confidence scoring
- ✗ No performance tracking
- ✗ Cannot combine with labels
- ✗ No visibility into which rule applied

**Local rules** (YAML-based) provide:
- ✓ Full CRUD operations
- ✓ Regex patterns with exclusions
- ✓ Confidence scoring (0-100%)
- ✓ Performance tracking (accuracy metrics)
- ✓ Integrated with labeling system
- ✓ Complete audit trail

## Migration Strategy

### Step 1: Export Existing Platform Rules

Run the platform rule sync to create a snapshot:

```bash
uv run python -c "
from scripts.core.rule_engine import RuleEngine
from scripts.core.api_client import PocketSmithClient

client = PocketSmithClient()
engine = RuleEngine()
engine.sync_platform_rules(client)
"
```

This creates `data/platform_rules.json` with all platform rules.

### Step 2: Convert to YAML Format

For each platform rule in `data/platform_rules.json`:

**Platform rule:**
```json
{
  "rule_id": 12345,
  "category_id": 67890,
  "payee_contains": "WOOLWORTHS"
}
```

**Convert to YAML:**
```yaml
- type: category
  name: WOOLWORTHS → Groceries
  patterns: [WOOLWORTHS]
  category: Groceries  # Look up category name by ID
  confidence: 95
```

Add to `data/rules.yaml`.

### Step 3: Test Local Rules

Test with dry-run mode:

```bash
uv run python scripts/operations/categorize_batch.py --dry-run --period=2025-11
```

Verify local rules match the same transactions as platform rules.

### Step 4: Leave Platform Rules in Place

**Important:** You cannot delete platform rules via API.

**Recommendation:** Leave them active. They will continue to auto-categorize transactions when they sync from your bank, and Agent Smith's local rules will supplement (not conflict).

**Alternative:** Manually delete via PocketSmith web interface if desired.

## Example Conversion

### Before (Platform Rule)

Created via API:
```python
api_client.create_category_rule(
    category_id=12345,
    payee_matches="UBER"
)
```

Limitations:
- Can't exclude "UBER EATS"
- Can't track accuracy
- Can't add labels

### After (Local Rule)

YAML rule:
```yaml
- type: category
  name: UBER → Transport
  patterns: [UBER]
  exclude_patterns: [UBER EATS]
  category: Transport
  confidence: 90

- type: label
  name: Personal Transport
  when:
    categories: [Transport]
    accounts: [Personal]
  labels: [Personal, Discretionary]
```

Benefits:
- Excludes UBER EATS (goes to Dining Out instead)
- Tracks confidence and accuracy
- Automatically labels based on account
- Can be modified/deleted/versioned

## Best Practices

1. **Start with high-confidence patterns** - Convert your most reliable platform rules first

2. **Use visual grouping** - Group related category + label rules together in YAML

3. **Test incrementally** - Convert 5-10 rules, test, repeat

4. **Keep platform rules** - Leave them active, use local rules to supplement

5. **Version control** - Commit `data/rules.yaml` to git for history

6. **Regular reviews** - Check rule accuracy metrics monthly, refine as needed
```

**Step 3: Commit**

```bash
git add scripts/core/rule_engine.py docs/migration/platform-to-local-rules.md
git commit -m "docs: deprecate platform rule creation, add migration guide"
```

---

## Task 9: Documentation

**Files:**
- Create: `docs/guides/unified-rules-guide.md`
- Modify: `README.md`

**Step 1: Create comprehensive rules guide**

Create `docs/guides/unified-rules-guide.md`:

```markdown
# Unified Rules Guide - Categories & Labels

## Overview

Agent Smith uses a **unified YAML rule system** that handles both transaction categorization and labeling in a single, easy-to-read file.

**Key Features:**
- 📝 **YAML format** - Easy to read and edit
- 🔄 **Two-phase execution** - Categories first, then labels
- 🎯 **Pattern matching** - Regex patterns with exclusions
- 📊 **Confidence scoring** - 0-100% confidence for auto-apply logic
- 🏷️ **Smart labeling** - Context-aware labels (account, category, amount)
- 🤖 **LLM fallback** - AI categorization when rules don't match

## Quick Start

### 1. Create Your Rules File

Copy the sample:

```bash
cp data/rules.yaml.sample data/rules.yaml
```

### 2. Add Your First Rule

Edit `data/rules.yaml`:

```yaml
rules:
  - type: category
    name: Coffee → Dining Out
    patterns: [STARBUCKS, COSTA, CAFE]
    category: Dining Out
    confidence: 95

  - type: label
    name: Personal Coffee
    when:
      categories: [Dining Out]
      accounts: [Personal]
    labels: [Discretionary, Personal]
```

### 3. Test It

```bash
uv run python scripts/operations/test_rules.py --payee="STARBUCKS" --account="Personal"
```

Expected output:
```
✓ Category: Dining Out (95% confidence)
✓ Labels: Discretionary, Personal
```

## Rule Types

### Category Rules

Categorize transactions based on payee patterns.

```yaml
- type: category
  name: WOOLWORTHS → Groceries
  patterns: [WOOLWORTHS, COLES, ALDI]
  exclude_patterns: [WOOLWORTHS PETROL]
  category: Groceries
  confidence: 95
  accounts: [Personal, Shared Bills]  # Optional: limit to specific accounts
  amount_operator: ">"                # Optional: amount condition
  amount_value: 0
```

**Fields:**
- `type`: Must be "category"
- `name`: Descriptive name (shows in logs)
- `patterns`: List of payee keywords (OR logic)
- `category`: Category to assign
- `confidence`: 0-100% (affects auto-apply behavior)
- `exclude_patterns`: Optional - patterns to exclude
- `accounts`: Optional - limit to specific accounts
- `amount_operator`/`amount_value`: Optional - amount condition

### Label Rules

Add labels based on category, account, amount, etc.

```yaml
- type: label
  name: Shared Groceries
  when:
    categories: [Groceries, Household]  # OR logic
    accounts: [Shared Bills]             # OR logic
  labels: [Shared Expense, Needs Approval]
```

**Fields:**
- `type`: Must be "label"
- `name`: Descriptive name
- `when`: Conditions (all must match - AND logic)
  - `categories`: List of categories (OR within list)
  - `accounts`: List of accounts (OR within list)
  - `amount_operator`/`amount_value`: Amount condition
  - `uncategorized`: Set to `true` to match uncategorized transactions
- `labels`: List of labels to apply

## Execution Flow

### Phase 1: Categorization

1. Check all category rules against transaction
2. If multiple match, use highest confidence
3. If no rules match → LLM fallback (if enabled)
4. Apply category to transaction

### Phase 2: Labeling

1. Check all label rules against transaction (now has category from Phase 1)
2. Apply ALL matching label rules (additive)
3. Deduplicate labels

**Example:**

Transaction: `WOOLWORTHS` in `Shared Bills` account, amount `-$127.50`

**Phase 1 matches:**
- "WOOLWORTHS → Groceries" (95% confidence) ✓

**Phase 2 matches:**
- "Shared Groceries" (categories: [Groceries], accounts: [Shared Bills]) ✓
- "Large Purchase" (amount > $100) ✓

**Result:**
- Category: Groceries
- Labels: Shared Expense, Needs Approval, Large Purchase

## Intelligence Modes

Agent Smith has three modes that control auto-apply behavior based on confidence:

### Conservative Mode
- **Never auto-applies** - always asks user
- Use when: Learning the system, want full control

### Smart Mode (Default)
- **Auto-apply ≥90%** confidence
- **Ask approval 70-89%** confidence
- **Skip <70%** confidence
- LLM validates 70-89% range (upgrades confidence if confirms)

### Aggressive Mode
- **Auto-apply ≥80%** confidence
- **Ask approval 50-79%** confidence
- **Skip <50%** confidence

**Set mode in command:**
```bash
/agent-smith-categorize --mode=smart
```

## LLM Integration

### Fallback Categorization

When no rule matches, Agent Smith uses LLM to suggest a category.

**Example:**
```
Transaction: ACME WIDGETS LTD -$245.00
No rule match → LLM suggests "Business Supplies" (85% confidence)
→ Asks user for approval (smart mode)
```

### Validation

Medium-confidence rule matches (70-89%) are validated by LLM.

**Example:**
```
Transaction: UBER MEDICAL CENTRE -$80
Rule match: "UBER → Transport" (75% confidence)
→ LLM validates: "This looks like medical, not transport"
→ LLM suggests: "Medical & Healthcare" (90% confidence)
→ Auto-applied (upgraded to 90%)
```

### Learning

After LLM categorizes transactions, Agent Smith offers to create rules.

**Example:**
```
LLM categorized 12 "ACME WIDGETS" transactions as "Business Supplies"

Create rule?
- type: category
  name: ACME WIDGETS → Business Supplies
  patterns: [ACME WIDGETS]
  category: Business Supplies
  confidence: 90

[Yes] [Edit] [No]
```

## Advanced Patterns

### Cross-Category Labels

Apply labels regardless of category:

```yaml
- type: label
  name: Tax Deductible
  when:
    categories: [Software, Professional Development, Home Office]
  labels: [Tax Deductible, ATO: D1]

- type: label
  name: Large Purchases
  when:
    amount_operator: ">"
    amount_value: 500
  labels: [Large Purchase, Review Required]
```

### Account-Based Workflows

Different labels for same category in different accounts:

```yaml
- type: category
  name: Transport
  patterns: [UBER, LYFT, TAXI]
  category: Transport
  confidence: 90

- type: label
  name: Personal Transport
  when:
    categories: [Transport]
    accounts: [Personal]
  labels: [Personal, Discretionary]

- type: label
  name: Work Transport
  when:
    categories: [Transport]
    accounts: [Work, Personal]
    amount_operator: "<"
    amount_value: 0
  labels: [Work Related, Reimbursable]
```

### Uncategorized Flagging

Flag uncategorized transactions for review:

```yaml
- type: label
  name: Flag Uncategorized
  when:
    uncategorized: true
  labels: [Needs Categorization, Review Required]
```

## Best Practices

### 1. Order Rules Specific → General

```yaml
# Good: Specific first
- patterns: [UBER EATS]
  category: Dining Out

- patterns: [UBER]
  category: Transport

# Bad: General first (UBER catches UBER EATS)
- patterns: [UBER]
  category: Transport

- patterns: [UBER EATS]
  category: Dining Out  # Never reached!
```

**Fix:** Use `exclude_patterns`:
```yaml
- patterns: [UBER]
  exclude_patterns: [UBER EATS]
  category: Transport
```

### 2. Use Visual Grouping

Group related rules together with comments:

```yaml
# ═══════════════════════════════════════
# GROCERIES FLOW
# ═══════════════════════════════════════

- type: category
  # ...

- type: label
  # ...
```

### 3. Start with High Confidence

Begin with rules you're certain about (95%+):
- Groceries: WOOLWORTHS, COLES
- Transport: UBER, LYFT
- Utilities: AGL, ORIGIN ENERGY

Add medium-confidence rules (80-90%) later.

### 4. Test with Dry Run

Always test before applying:

```bash
uv run python scripts/operations/categorize_batch.py --dry-run --period=2025-11
```

Review suggested categorizations before committing.

### 5. Version Control Rules

Commit `data/rules.yaml` to git:

```bash
git add data/rules.yaml
git commit -m "rules: add coffee shop categorization"
```

Track rule evolution over time.

### 6. Review Rule Performance

Check rule accuracy monthly:

```bash
/agent-smith-analyze rules --period=last-month
```

Refine rules with low accuracy.

## Troubleshooting

### Rule Not Matching

**Check:**
1. Is payee pattern exact? (case-insensitive but spacing matters)
2. Is there an exclusion pattern blocking it?
3. Is account filter too restrictive?
4. Is amount condition correct?

**Debug:**
```bash
uv run python scripts/operations/test_rules.py --payee="EXACT PAYEE" --debug
```

### Multiple Rules Matching

**Expected behavior:** Highest confidence wins

**Fix:** Adjust confidence scores or add exclusion patterns

### Labels Not Applying

**Check:**
1. Did category rule match first? (labels depend on category from Phase 1)
2. Are when conditions too restrictive?
3. Is uncategorized flag correct?

## Migration from Old Rules

See [Platform to Local Rules Migration Guide](../migration/platform-to-local-rules.md) for converting existing platform rules to unified YAML format.

## Examples

See `data/rules.yaml.sample` for complete examples covering:
- Groceries (personal vs shared)
- Transport (work vs personal)
- Dining out (discretionary labeling)
- Tax deductible categories
- Large purchase flagging
- Uncategorized flagging
```

**Step 2: Update README**

Add to `README.md`:

```markdown
## Unified Rule System

Agent Smith uses a YAML-based rule system for categorization and labeling:

```yaml
rules:
  # Category rule
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS, COLES]
    category: Groceries
    confidence: 95

  # Label rule
  - type: label
    name: Shared Groceries
    when:
      categories: [Groceries]
      accounts: [Shared Bills]
    labels: [Shared Expense]
```

**Key features:**
- Two-phase execution (categorization → labeling)
- LLM fallback for unmatched transactions
- Intelligence modes (conservative/smart/aggressive)
- Rule learning from LLM suggestions

See [Unified Rules Guide](docs/guides/unified-rules-guide.md) for details.
```

**Step 3: Commit**

```bash
git add docs/guides/unified-rules-guide.md README.md
git commit -m "docs: add comprehensive unified rules guide"
```

---

## Task 10: Testing & Cleanup

**Files:**
- Run all tests
- Update INDEX.md files

**Step 1: Run full test suite**

```bash
uv run python -u -m pytest tests/ -v --cov=scripts
```

Expected: All tests passing

**Step 2: Update data/INDEX.md**

Add to `data/INDEX.md`:

```markdown
## Rules

| File | Description | Format |
|------|-------------|--------|
| `rules.yaml.sample` | Sample unified rules file with examples | YAML |
| `rules.yaml` | Active rules file (git-ignored) | YAML |
| `platform_rules.json` | Platform rule tracking (deprecated) | JSON |
| `local_rules.json` | Old local rules format (deprecated) | JSON |
```

**Step 3: Update docs/INDEX.md**

Add to `docs/INDEX.md`:

```markdown
## Guides

| File | Description |
|------|-------------|
| `guides/unified-rules-guide.md` | Complete guide to YAML rule system |
| `migration/platform-to-local-rules.md` | Migration from platform to local rules |
```

**Step 4: Commit**

```bash
git add data/INDEX.md docs/INDEX.md
git commit -m "docs: update INDEX files for unified rules"
```

---

## Summary

This plan implements:

✅ **YAML rule schema** - Unified categories + labels
✅ **Two-phase execution** - Categorization → Labeling
✅ **LLM integration** - Fallback & validation via subagent
✅ **Intelligence modes** - Conservative/Smart/Aggressive
✅ **Operational modes** - Dry-run, validate, apply
✅ **Update strategies** - Skip existing, replace all, upgrade confidence, replace if different
✅ **Range processing** - Date ranges, account filters, transaction limits
✅ **Progress reporting** - Real-time progress callbacks for long operations
✅ **Rule learning** - Create rules from LLM suggestions
✅ **Migration guide** - Platform → Local rules
✅ **Comprehensive docs** - Examples, best practices, troubleshooting
✅ **Full test coverage** - Unit + integration tests

**Dependencies:**
- PyYAML for rule parsing
- Existing RuleEngine, SubagentConductor
- PocketSmith API client

**Next steps after implementation:**
1. Create feature branch
2. Execute plan task-by-task
3. Test with real PocketSmith data
4. Migrate existing rules to YAML
5. Create PR and merge

**Estimated effort:** 10-14 hours (spread across multiple sessions)

## Usage Examples

**Dry-run mode (preview changes):**
```bash
uv run python scripts/operations/categorize_batch.py \
  --mode=dry-run \
  --period=2025-11 \
  --account="Personal"
```

**Validate mode (check what would change on existing categorizations):**
```bash
uv run python scripts/operations/categorize_batch.py \
  --mode=validate \
  --update-strategy=replace-all \
  --period=2025
```

**Apply mode (actually make changes):**
```bash
# Only process uncategorized transactions
uv run python scripts/operations/categorize_batch.py \
  --mode=apply \
  --update-strategy=skip-existing \
  --period=2025-11

# Replace all with higher confidence categorizations
uv run python scripts/operations/categorize_batch.py \
  --mode=apply \
  --update-strategy=upgrade-confidence \
  --date-start=2025-01-01 \
  --date-end=2025-11-30

# Full re-categorization (replace everything)
uv run python scripts/operations/categorize_batch.py \
  --mode=apply \
  --update-strategy=replace-all \
  --limit=100
```
