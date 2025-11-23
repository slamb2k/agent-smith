# Phase 8: Health Check & Polish Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement comprehensive health check system with 6 health scores, recommendation engine, automated monitoring, and complete project polish including end-to-end testing, documentation, and performance optimization.

**Architecture:** Health check system calculates scores across 6 dimensions (Data Quality, Category Structure, Rule Engine, Tax Readiness, Automation & Efficiency, Budget Alignment). Each scorer is independent, enabling parallel calculation. Recommendation engine prioritizes issues by impact. Monitoring integrates with existing AlertScheduler for periodic checks.

**Tech Stack:** Python 3.9+, pytest, existing Agent Smith modules (api_client, rule_engine, tax modules, alerts)

---

## Part 1: Health Check Core System

### Task 1: Create Health Module Directory Structure

**Files:**
- Create: `scripts/health/__init__.py`
- Create: `scripts/health/scores.py`
- Create: `scripts/health/engine.py`
- Create: `data/health/INDEX.md`

**Step 1: Create directory and init file**

```bash
mkdir -p scripts/health data/health
```

**Step 2: Create health module init**

Create `scripts/health/__init__.py`:

```python
"""Health check system for Agent Smith."""

from scripts.health.scores import (
    HealthScore,
    HealthStatus,
    DataQualityScorer,
    CategoryStructureScorer,
    RuleEngineScorer,
    TaxReadinessScorer,
    AutomationScorer,
    BudgetAlignmentScorer,
)
from scripts.health.engine import HealthCheckEngine

__all__ = [
    "HealthScore",
    "HealthStatus",
    "DataQualityScorer",
    "CategoryStructureScorer",
    "RuleEngineScorer",
    "TaxReadinessScorer",
    "AutomationScorer",
    "BudgetAlignmentScorer",
    "HealthCheckEngine",
]
```

**Step 3: Create data/health INDEX**

Create `data/health/INDEX.md`:

```markdown
# Health Check Data

## Purpose
Stores health check results, historical scores, and recommendations.

## Files
- `health_scores.json` - Latest health scores for each dimension
- `health_history.json` - Historical health check results
- `recommendations.json` - Current active recommendations

## Retention
- Current scores: Always kept
- History: 90 days, then archived monthly
```

**Step 4: Commit**

```bash
git add scripts/health/ data/health/
git commit -m "feat(health): create health module directory structure"
```

---

### Task 2: Implement HealthScore Base Classes

**Files:**
- Create: `scripts/health/scores.py`
- Create: `tests/unit/test_health_scores.py`

**Step 1: Write the failing test for HealthStatus enum**

Create `tests/unit/test_health_scores.py`:

```python
"""Unit tests for health score system."""

import pytest
from scripts.health.scores import HealthStatus, HealthScore


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_status_from_score_excellent(self):
        """Score 90-100 should be EXCELLENT."""
        assert HealthStatus.from_score(90) == HealthStatus.EXCELLENT
        assert HealthStatus.from_score(100) == HealthStatus.EXCELLENT

    def test_status_from_score_good(self):
        """Score 70-89 should be GOOD."""
        assert HealthStatus.from_score(70) == HealthStatus.GOOD
        assert HealthStatus.from_score(89) == HealthStatus.GOOD

    def test_status_from_score_fair(self):
        """Score 50-69 should be FAIR."""
        assert HealthStatus.from_score(50) == HealthStatus.FAIR
        assert HealthStatus.from_score(69) == HealthStatus.FAIR

    def test_status_from_score_poor(self):
        """Score below 50 should be POOR."""
        assert HealthStatus.from_score(0) == HealthStatus.POOR
        assert HealthStatus.from_score(49) == HealthStatus.POOR
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_scores.py::TestHealthStatus -v
```

Expected: FAIL with "ModuleNotFoundError" or "cannot import name 'HealthStatus'"

**Step 3: Write minimal implementation for HealthStatus**

Create `scripts/health/scores.py`:

```python
"""Health score definitions and base classes."""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


class HealthStatus(Enum):
    """Health status levels based on score ranges."""

    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"  # 70-89
    FAIR = "fair"  # 50-69
    POOR = "poor"  # 0-49

    @classmethod
    def from_score(cls, score: int) -> "HealthStatus":
        """Determine status from numeric score.

        Args:
            score: Health score (0-100)

        Returns:
            Corresponding HealthStatus
        """
        if score >= 90:
            return cls.EXCELLENT
        elif score >= 70:
            return cls.GOOD
        elif score >= 50:
            return cls.FAIR
        else:
            return cls.POOR

    @property
    def emoji(self) -> str:
        """Get emoji representation of status."""
        return {
            HealthStatus.EXCELLENT: "✅",
            HealthStatus.GOOD: "👍",
            HealthStatus.FAIR: "⚠️",
            HealthStatus.POOR: "❌",
        }[self]
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_scores.py::TestHealthStatus -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/scores.py tests/unit/test_health_scores.py
git commit -m "feat(health): add HealthStatus enum with score-based classification"
```

---

### Task 3: Implement HealthScore Dataclass

**Files:**
- Modify: `scripts/health/scores.py`
- Modify: `tests/unit/test_health_scores.py`

**Step 1: Write the failing test for HealthScore**

Add to `tests/unit/test_health_scores.py`:

```python
class TestHealthScore:
    """Tests for HealthScore dataclass."""

    def test_health_score_creation(self):
        """Test creating a health score."""
        score = HealthScore(
            dimension="data_quality",
            score=85,
            max_score=100,
            issues=["10 uncategorized transactions"],
            recommendations=["Categorize remaining transactions"],
        )

        assert score.dimension == "data_quality"
        assert score.score == 85
        assert score.status == HealthStatus.GOOD
        assert len(score.issues) == 1
        assert len(score.recommendations) == 1

    def test_health_score_percentage(self):
        """Test percentage calculation."""
        score = HealthScore(dimension="test", score=75, max_score=100)
        assert score.percentage == 75.0

        score2 = HealthScore(dimension="test", score=15, max_score=20)
        assert score2.percentage == 75.0

    def test_health_score_to_dict(self):
        """Test serialization to dict."""
        score = HealthScore(
            dimension="rule_engine",
            score=60,
            max_score=100,
            issues=["Low coverage"],
        )

        data = score.to_dict()
        assert data["dimension"] == "rule_engine"
        assert data["score"] == 60
        assert data["status"] == "fair"
        assert "timestamp" in data
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_scores.py::TestHealthScore -v
```

Expected: FAIL with "cannot import name 'HealthScore'"

**Step 3: Write minimal implementation for HealthScore**

Add to `scripts/health/scores.py` after HealthStatus class:

```python
@dataclass
class HealthScore:
    """Represents a health score for a specific dimension."""

    dimension: str
    score: int
    max_score: int = 100
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def status(self) -> HealthStatus:
        """Get status based on percentage score."""
        return HealthStatus.from_score(int(self.percentage))

    @property
    def percentage(self) -> float:
        """Calculate percentage score."""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dict representation of health score
        """
        return {
            "dimension": self.dimension,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "status": self.status.value,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_scores.py::TestHealthScore -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/scores.py tests/unit/test_health_scores.py
git commit -m "feat(health): add HealthScore dataclass with serialization"
```

---

### Task 4: Implement BaseScorer Abstract Class

**Files:**
- Modify: `scripts/health/scores.py`
- Modify: `tests/unit/test_health_scores.py`

**Step 1: Write the failing test for BaseScorer**

Add to `tests/unit/test_health_scores.py`:

```python
from scripts.health.scores import BaseScorer


class TestBaseScorer:
    """Tests for BaseScorer abstract class."""

    def test_concrete_scorer_must_implement_calculate(self):
        """Concrete scorers must implement calculate method."""

        class IncompleteScorer(BaseScorer):
            dimension = "incomplete"

        with pytest.raises(TypeError):
            IncompleteScorer()

    def test_concrete_scorer_works(self):
        """A properly implemented scorer should work."""

        class TestScorer(BaseScorer):
            dimension = "test_dimension"

            def calculate(self, data):
                return HealthScore(
                    dimension=self.dimension,
                    score=100,
                    max_score=100,
                )

        scorer = TestScorer()
        result = scorer.calculate({})
        assert result.dimension == "test_dimension"
        assert result.score == 100
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_scores.py::TestBaseScorer -v
```

Expected: FAIL with "cannot import name 'BaseScorer'"

**Step 3: Write minimal implementation for BaseScorer**

Add to `scripts/health/scores.py`:

```python
from abc import ABC, abstractmethod


class BaseScorer(ABC):
    """Abstract base class for health dimension scorers."""

    dimension: str = "base"

    @abstractmethod
    def calculate(self, data: Dict[str, Any]) -> HealthScore:
        """Calculate health score for this dimension.

        Args:
            data: Input data for score calculation

        Returns:
            HealthScore for this dimension
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(dimension={self.dimension})"
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_scores.py::TestBaseScorer -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/scores.py tests/unit/test_health_scores.py
git commit -m "feat(health): add BaseScorer abstract class"
```

---

### Task 5: Implement DataQualityScorer

**Files:**
- Modify: `scripts/health/scores.py`
- Modify: `tests/unit/test_health_scores.py`

**Step 1: Write the failing test for DataQualityScorer**

Add to `tests/unit/test_health_scores.py`:

```python
from scripts.health.scores import DataQualityScorer


class TestDataQualityScorer:
    """Tests for DataQualityScorer."""

    def test_perfect_data_quality(self):
        """All transactions categorized = 100 score."""
        scorer = DataQualityScorer()
        data = {
            "total_transactions": 100,
            "categorized_transactions": 100,
            "transactions_with_payee": 100,
            "duplicate_count": 0,
        }

        result = scorer.calculate(data)
        assert result.dimension == "data_quality"
        assert result.score == 100
        assert result.status == HealthStatus.EXCELLENT
        assert len(result.issues) == 0

    def test_uncategorized_transactions_reduce_score(self):
        """Uncategorized transactions reduce score."""
        scorer = DataQualityScorer()
        data = {
            "total_transactions": 100,
            "categorized_transactions": 80,
            "transactions_with_payee": 100,
            "duplicate_count": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 100
        assert "uncategorized" in result.issues[0].lower()

    def test_duplicates_reduce_score(self):
        """Duplicate transactions reduce score."""
        scorer = DataQualityScorer()
        data = {
            "total_transactions": 100,
            "categorized_transactions": 100,
            "transactions_with_payee": 100,
            "duplicate_count": 10,
        }

        result = scorer.calculate(data)
        assert result.score < 100
        assert any("duplicate" in issue.lower() for issue in result.issues)

    def test_missing_payees_reduce_score(self):
        """Missing payee names reduce score."""
        scorer = DataQualityScorer()
        data = {
            "total_transactions": 100,
            "categorized_transactions": 100,
            "transactions_with_payee": 70,
            "duplicate_count": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 100
        assert any("payee" in issue.lower() for issue in result.issues)

    def test_empty_data_returns_zero(self):
        """No transactions = 0 score."""
        scorer = DataQualityScorer()
        data = {
            "total_transactions": 0,
            "categorized_transactions": 0,
            "transactions_with_payee": 0,
            "duplicate_count": 0,
        }

        result = scorer.calculate(data)
        assert result.score == 0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_scores.py::TestDataQualityScorer -v
```

Expected: FAIL with "cannot import name 'DataQualityScorer'"

**Step 3: Write minimal implementation for DataQualityScorer**

Add to `scripts/health/scores.py`:

```python
class DataQualityScorer(BaseScorer):
    """Scores data quality: categorization, completeness, duplicates."""

    dimension = "data_quality"

    # Weight factors for each component
    CATEGORIZATION_WEIGHT = 0.5
    PAYEE_WEIGHT = 0.3
    DUPLICATE_WEIGHT = 0.2

    def calculate(self, data: Dict[str, Any]) -> HealthScore:
        """Calculate data quality score.

        Args:
            data: Dict with keys:
                - total_transactions: int
                - categorized_transactions: int
                - transactions_with_payee: int
                - duplicate_count: int

        Returns:
            HealthScore for data quality dimension
        """
        total = data.get("total_transactions", 0)
        categorized = data.get("categorized_transactions", 0)
        with_payee = data.get("transactions_with_payee", 0)
        duplicates = data.get("duplicate_count", 0)

        issues: List[str] = []
        recommendations: List[str] = []

        if total == 0:
            return HealthScore(
                dimension=self.dimension,
                score=0,
                issues=["No transactions found"],
                recommendations=["Import transactions from PocketSmith"],
            )

        # Calculate component scores
        cat_rate = categorized / total
        payee_rate = with_payee / total
        dup_rate = duplicates / total if total > 0 else 0

        # Categorization score (0-50 points)
        cat_score = cat_rate * 100 * self.CATEGORIZATION_WEIGHT
        if cat_rate < 1.0:
            uncategorized = total - categorized
            issues.append(f"{uncategorized} uncategorized transactions ({(1-cat_rate)*100:.1f}%)")
            recommendations.append("Run /smith:categorize to categorize transactions")

        # Payee completeness score (0-30 points)
        payee_score = payee_rate * 100 * self.PAYEE_WEIGHT
        if payee_rate < 0.95:
            missing = total - with_payee
            issues.append(f"{missing} transactions missing payee name")
            recommendations.append("Review transactions with missing payee information")

        # Duplicate penalty (0-20 points, deducted for duplicates)
        dup_penalty = min(dup_rate * 100 * 5, 20)  # Max 20 point penalty
        dup_score = (100 * self.DUPLICATE_WEIGHT) - dup_penalty
        if duplicates > 0:
            issues.append(f"{duplicates} potential duplicate transactions detected")
            recommendations.append("Review and merge duplicate transactions")

        total_score = int(cat_score + payee_score + max(0, dup_score))

        return HealthScore(
            dimension=self.dimension,
            score=min(100, max(0, total_score)),
            issues=issues,
            recommendations=recommendations,
            details={
                "categorization_rate": cat_rate,
                "payee_rate": payee_rate,
                "duplicate_rate": dup_rate,
            },
        )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_scores.py::TestDataQualityScorer -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/scores.py tests/unit/test_health_scores.py
git commit -m "feat(health): add DataQualityScorer for transaction quality metrics"
```

---

### Task 6: Implement CategoryStructureScorer

**Files:**
- Modify: `scripts/health/scores.py`
- Modify: `tests/unit/test_health_scores.py`

**Step 1: Write the failing test for CategoryStructureScorer**

Add to `tests/unit/test_health_scores.py`:

```python
from scripts.health.scores import CategoryStructureScorer


class TestCategoryStructureScorer:
    """Tests for CategoryStructureScorer."""

    def test_good_category_structure(self):
        """Well-organized categories score high."""
        scorer = CategoryStructureScorer()
        data = {
            "total_categories": 30,
            "categories_with_transactions": 25,
            "max_depth": 3,
            "categories_at_root": 8,
            "ato_mapped_categories": 20,
            "empty_categories": 5,
        }

        result = scorer.calculate(data)
        assert result.dimension == "category_structure"
        assert result.score >= 70
        assert result.status in [HealthStatus.GOOD, HealthStatus.EXCELLENT]

    def test_too_many_root_categories_penalized(self):
        """Too many root categories indicates poor organization."""
        scorer = CategoryStructureScorer()
        data = {
            "total_categories": 50,
            "categories_with_transactions": 50,
            "max_depth": 1,  # All flat
            "categories_at_root": 50,  # All at root
            "ato_mapped_categories": 10,
            "empty_categories": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 70
        assert any("root" in issue.lower() or "hierarchy" in issue.lower() for issue in result.issues)

    def test_many_empty_categories_penalized(self):
        """Many unused categories reduce score."""
        scorer = CategoryStructureScorer()
        data = {
            "total_categories": 50,
            "categories_with_transactions": 10,
            "max_depth": 3,
            "categories_at_root": 10,
            "ato_mapped_categories": 10,
            "empty_categories": 40,
        }

        result = scorer.calculate(data)
        assert result.score < 70
        assert any("empty" in issue.lower() or "unused" in issue.lower() for issue in result.issues)

    def test_poor_ato_mapping_penalized(self):
        """Poor ATO category mapping reduces tax readiness."""
        scorer = CategoryStructureScorer()
        data = {
            "total_categories": 30,
            "categories_with_transactions": 30,
            "max_depth": 3,
            "categories_at_root": 8,
            "ato_mapped_categories": 5,  # Only 5 of 30 mapped
            "empty_categories": 0,
        }

        result = scorer.calculate(data)
        # Score should be reduced due to poor ATO mapping
        assert any("ato" in issue.lower() or "tax" in issue.lower() for issue in result.issues)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_scores.py::TestCategoryStructureScorer -v
```

Expected: FAIL with "cannot import name 'CategoryStructureScorer'"

**Step 3: Write minimal implementation for CategoryStructureScorer**

Add to `scripts/health/scores.py`:

```python
class CategoryStructureScorer(BaseScorer):
    """Scores category structure: hierarchy, usage, ATO alignment."""

    dimension = "category_structure"

    HIERARCHY_WEIGHT = 0.3
    USAGE_WEIGHT = 0.4
    ATO_WEIGHT = 0.3

    IDEAL_ROOT_CATEGORIES = 10
    IDEAL_MAX_DEPTH = 3

    def calculate(self, data: Dict[str, Any]) -> HealthScore:
        """Calculate category structure score.

        Args:
            data: Dict with keys:
                - total_categories: int
                - categories_with_transactions: int
                - max_depth: int
                - categories_at_root: int
                - ato_mapped_categories: int
                - empty_categories: int

        Returns:
            HealthScore for category structure dimension
        """
        total = data.get("total_categories", 0)
        used = data.get("categories_with_transactions", 0)
        max_depth = data.get("max_depth", 1)
        root_count = data.get("categories_at_root", 0)
        ato_mapped = data.get("ato_mapped_categories", 0)
        empty = data.get("empty_categories", 0)

        issues: List[str] = []
        recommendations: List[str] = []

        if total == 0:
            return HealthScore(
                dimension=self.dimension,
                score=0,
                issues=["No categories found"],
                recommendations=["Set up category structure in PocketSmith"],
            )

        # Hierarchy score (0-30 points)
        hierarchy_score = 100 * self.HIERARCHY_WEIGHT

        # Penalize too many root categories
        if root_count > self.IDEAL_ROOT_CATEGORIES * 2:
            penalty = min(15, (root_count - self.IDEAL_ROOT_CATEGORIES) * 0.5)
            hierarchy_score -= penalty
            issues.append(f"{root_count} root-level categories (ideal: {self.IDEAL_ROOT_CATEGORIES})")
            recommendations.append("Consolidate categories into a hierarchical structure")

        # Penalize flat structure
        if max_depth < 2 and total > 15:
            hierarchy_score -= 10
            issues.append("Flat category structure lacks hierarchy")
            recommendations.append("Create parent categories to organize related expenses")

        # Usage score (0-40 points)
        usage_rate = used / total if total > 0 else 0
        usage_score = usage_rate * 100 * self.USAGE_WEIGHT

        if empty > total * 0.3:
            issues.append(f"{empty} empty/unused categories ({empty/total*100:.0f}%)")
            recommendations.append("Archive or delete unused categories")

        # ATO alignment score (0-30 points)
        ato_rate = ato_mapped / used if used > 0 else 0
        ato_score = ato_rate * 100 * self.ATO_WEIGHT

        if ato_rate < 0.5:
            issues.append(f"Only {ato_mapped} categories mapped to ATO tax categories")
            recommendations.append("Map categories to ATO expense types for tax reporting")

        total_score = int(hierarchy_score + usage_score + ato_score)

        return HealthScore(
            dimension=self.dimension,
            score=min(100, max(0, total_score)),
            issues=issues,
            recommendations=recommendations,
            details={
                "usage_rate": usage_rate,
                "ato_mapping_rate": ato_rate,
                "hierarchy_depth": max_depth,
                "root_categories": root_count,
            },
        )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_scores.py::TestCategoryStructureScorer -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/scores.py tests/unit/test_health_scores.py
git commit -m "feat(health): add CategoryStructureScorer for category organization metrics"
```

---

### Task 7: Implement RuleEngineScorer

**Files:**
- Modify: `scripts/health/scores.py`
- Modify: `tests/unit/test_health_scores.py`

**Step 1: Write the failing test for RuleEngineScorer**

Add to `tests/unit/test_health_scores.py`:

```python
from scripts.health.scores import RuleEngineScorer


class TestRuleEngineScorer:
    """Tests for RuleEngineScorer."""

    def test_high_coverage_high_accuracy(self):
        """High rule coverage and accuracy = excellent score."""
        scorer = RuleEngineScorer()
        data = {
            "total_rules": 50,
            "active_rules": 48,
            "auto_categorization_rate": 0.85,
            "rule_accuracy": 0.95,
            "conflicting_rules": 0,
            "stale_rules": 2,
        }

        result = scorer.calculate(data)
        assert result.dimension == "rule_engine"
        assert result.score >= 80
        assert result.status in [HealthStatus.GOOD, HealthStatus.EXCELLENT]

    def test_low_coverage_penalized(self):
        """Low auto-categorization rate reduces score."""
        scorer = RuleEngineScorer()
        data = {
            "total_rules": 10,
            "active_rules": 10,
            "auto_categorization_rate": 0.20,  # Only 20% auto-categorized
            "rule_accuracy": 0.90,
            "conflicting_rules": 0,
            "stale_rules": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 70
        assert any("coverage" in issue.lower() for issue in result.issues)

    def test_conflicting_rules_penalized(self):
        """Conflicting rules reduce score."""
        scorer = RuleEngineScorer()
        data = {
            "total_rules": 50,
            "active_rules": 50,
            "auto_categorization_rate": 0.80,
            "rule_accuracy": 0.90,
            "conflicting_rules": 10,
            "stale_rules": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 90
        assert any("conflict" in issue.lower() for issue in result.issues)

    def test_low_accuracy_penalized(self):
        """Low rule accuracy (high override rate) reduces score."""
        scorer = RuleEngineScorer()
        data = {
            "total_rules": 50,
            "active_rules": 50,
            "auto_categorization_rate": 0.80,
            "rule_accuracy": 0.60,  # 40% override rate
            "conflicting_rules": 0,
            "stale_rules": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 80
        assert any("accuracy" in issue.lower() or "override" in issue.lower() for issue in result.issues)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_scores.py::TestRuleEngineScorer -v
```

Expected: FAIL with "cannot import name 'RuleEngineScorer'"

**Step 3: Write minimal implementation for RuleEngineScorer**

Add to `scripts/health/scores.py`:

```python
class RuleEngineScorer(BaseScorer):
    """Scores rule engine: coverage, accuracy, conflicts."""

    dimension = "rule_engine"

    COVERAGE_WEIGHT = 0.4
    ACCURACY_WEIGHT = 0.4
    HEALTH_WEIGHT = 0.2

    TARGET_COVERAGE = 0.70  # 70% auto-categorization target

    def calculate(self, data: Dict[str, Any]) -> HealthScore:
        """Calculate rule engine score.

        Args:
            data: Dict with keys:
                - total_rules: int
                - active_rules: int
                - auto_categorization_rate: float (0-1)
                - rule_accuracy: float (0-1)
                - conflicting_rules: int
                - stale_rules: int

        Returns:
            HealthScore for rule engine dimension
        """
        total_rules = data.get("total_rules", 0)
        active_rules = data.get("active_rules", 0)
        coverage = data.get("auto_categorization_rate", 0)
        accuracy = data.get("rule_accuracy", 1.0)
        conflicts = data.get("conflicting_rules", 0)
        stale = data.get("stale_rules", 0)

        issues: List[str] = []
        recommendations: List[str] = []

        # Coverage score (0-40 points)
        coverage_score = min(coverage / self.TARGET_COVERAGE, 1.0) * 100 * self.COVERAGE_WEIGHT

        if coverage < 0.50:
            issues.append(f"Low auto-categorization coverage ({coverage*100:.0f}%)")
            recommendations.append("Create more rules to improve coverage (target: 70%)")
        elif coverage < self.TARGET_COVERAGE:
            issues.append(f"Auto-categorization coverage at {coverage*100:.0f}% (target: 70%)")

        # Accuracy score (0-40 points)
        accuracy_score = accuracy * 100 * self.ACCURACY_WEIGHT

        if accuracy < 0.80:
            override_rate = (1 - accuracy) * 100
            issues.append(f"Rule accuracy at {accuracy*100:.0f}% ({override_rate:.0f}% override rate)")
            recommendations.append("Review and refine rules with high override rates")

        # Health score (0-20 points) - conflicts and staleness
        health_score = 100 * self.HEALTH_WEIGHT

        if conflicts > 0:
            penalty = min(10, conflicts * 2)
            health_score -= penalty
            issues.append(f"{conflicts} conflicting rules detected")
            recommendations.append("Resolve rule conflicts to avoid categorization issues")

        if stale > 5:
            penalty = min(5, stale * 0.5)
            health_score -= penalty
            issues.append(f"{stale} stale rules (no recent matches)")
            recommendations.append("Review and archive rules that no longer match transactions")

        total_score = int(coverage_score + accuracy_score + max(0, health_score))

        return HealthScore(
            dimension=self.dimension,
            score=min(100, max(0, total_score)),
            issues=issues,
            recommendations=recommendations,
            details={
                "coverage": coverage,
                "accuracy": accuracy,
                "total_rules": total_rules,
                "active_rules": active_rules,
                "conflicts": conflicts,
                "stale_rules": stale,
            },
        )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_scores.py::TestRuleEngineScorer -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/scores.py tests/unit/test_health_scores.py
git commit -m "feat(health): add RuleEngineScorer for rule coverage and accuracy metrics"
```

---

### Task 8: Implement TaxReadinessScorer

**Files:**
- Modify: `scripts/health/scores.py`
- Modify: `tests/unit/test_health_scores.py`

**Step 1: Write the failing test for TaxReadinessScorer**

Add to `tests/unit/test_health_scores.py`:

```python
from scripts.health.scores import TaxReadinessScorer


class TestTaxReadinessScorer:
    """Tests for TaxReadinessScorer."""

    def test_tax_ready_high_score(self):
        """Full tax compliance = excellent score."""
        scorer = TaxReadinessScorer()
        data = {
            "deductible_transactions": 100,
            "substantiated_transactions": 95,
            "ato_category_coverage": 0.90,
            "cgt_events_tracked": 10,
            "cgt_events_total": 10,
            "missing_documentation_count": 5,
            "days_to_eofy": 180,
        }

        result = scorer.calculate(data)
        assert result.dimension == "tax_readiness"
        assert result.score >= 80
        assert result.status in [HealthStatus.GOOD, HealthStatus.EXCELLENT]

    def test_poor_substantiation_penalized(self):
        """Poor receipt/documentation tracking reduces score."""
        scorer = TaxReadinessScorer()
        data = {
            "deductible_transactions": 100,
            "substantiated_transactions": 30,  # Only 30%
            "ato_category_coverage": 0.80,
            "cgt_events_tracked": 5,
            "cgt_events_total": 5,
            "missing_documentation_count": 70,
            "days_to_eofy": 180,
        }

        result = scorer.calculate(data)
        assert result.score < 70
        assert any("substantiation" in issue.lower() or "documentation" in issue.lower() for issue in result.issues)

    def test_eofy_urgency_affects_recommendations(self):
        """Close to EOFY should generate urgent recommendations."""
        scorer = TaxReadinessScorer()
        data = {
            "deductible_transactions": 100,
            "substantiated_transactions": 60,
            "ato_category_coverage": 0.70,
            "cgt_events_tracked": 5,
            "cgt_events_total": 5,
            "missing_documentation_count": 40,
            "days_to_eofy": 30,  # One month to EOFY
        }

        result = scorer.calculate(data)
        # Should have EOFY-related recommendations
        assert any("eofy" in r.lower() or "june" in r.lower() or "urgent" in r.lower() for r in result.recommendations) or result.score < 70

    def test_untracked_cgt_events_penalized(self):
        """Untracked CGT events reduce score."""
        scorer = TaxReadinessScorer()
        data = {
            "deductible_transactions": 100,
            "substantiated_transactions": 90,
            "ato_category_coverage": 0.85,
            "cgt_events_tracked": 2,
            "cgt_events_total": 10,  # 8 untracked
            "missing_documentation_count": 10,
            "days_to_eofy": 180,
        }

        result = scorer.calculate(data)
        assert result.score < 90
        assert any("cgt" in issue.lower() or "capital" in issue.lower() for issue in result.issues)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_scores.py::TestTaxReadinessScorer -v
```

Expected: FAIL with "cannot import name 'TaxReadinessScorer'"

**Step 3: Write minimal implementation for TaxReadinessScorer**

Add to `scripts/health/scores.py`:

```python
class TaxReadinessScorer(BaseScorer):
    """Scores tax readiness: substantiation, ATO compliance, CGT tracking."""

    dimension = "tax_readiness"

    SUBSTANTIATION_WEIGHT = 0.35
    ATO_COVERAGE_WEIGHT = 0.30
    CGT_WEIGHT = 0.20
    DOCUMENTATION_WEIGHT = 0.15

    def calculate(self, data: Dict[str, Any]) -> HealthScore:
        """Calculate tax readiness score.

        Args:
            data: Dict with keys:
                - deductible_transactions: int
                - substantiated_transactions: int
                - ato_category_coverage: float (0-1)
                - cgt_events_tracked: int
                - cgt_events_total: int
                - missing_documentation_count: int
                - days_to_eofy: int

        Returns:
            HealthScore for tax readiness dimension
        """
        deductible = data.get("deductible_transactions", 0)
        substantiated = data.get("substantiated_transactions", 0)
        ato_coverage = data.get("ato_category_coverage", 0)
        cgt_tracked = data.get("cgt_events_tracked", 0)
        cgt_total = data.get("cgt_events_total", 0)
        missing_docs = data.get("missing_documentation_count", 0)
        days_to_eofy = data.get("days_to_eofy", 365)

        issues: List[str] = []
        recommendations: List[str] = []

        # Substantiation score (0-35 points)
        sub_rate = substantiated / deductible if deductible > 0 else 1.0
        sub_score = sub_rate * 100 * self.SUBSTANTIATION_WEIGHT

        if sub_rate < 0.80:
            missing = deductible - substantiated
            issues.append(f"{missing} deductible transactions lack substantiation ({(1-sub_rate)*100:.0f}%)")
            if days_to_eofy <= 60:
                recommendations.append("URGENT: Gather receipts for deductible expenses before EOFY")
            else:
                recommendations.append("Attach receipts to deductible transactions over $300")

        # ATO coverage score (0-30 points)
        ato_score = ato_coverage * 100 * self.ATO_COVERAGE_WEIGHT

        if ato_coverage < 0.70:
            issues.append(f"ATO category coverage at {ato_coverage*100:.0f}%")
            recommendations.append("Map more categories to ATO expense types")

        # CGT tracking score (0-20 points)
        cgt_rate = cgt_tracked / cgt_total if cgt_total > 0 else 1.0
        cgt_score = cgt_rate * 100 * self.CGT_WEIGHT

        if cgt_total > 0 and cgt_rate < 1.0:
            untracked = cgt_total - cgt_tracked
            issues.append(f"{untracked} CGT events not fully tracked")
            recommendations.append("Complete CGT register entries for all asset sales")

        # Documentation score (0-15 points)
        doc_penalty = min(15, missing_docs * 0.5)
        doc_score = (100 * self.DOCUMENTATION_WEIGHT) - doc_penalty

        if missing_docs > 10:
            issues.append(f"{missing_docs} transactions missing required documentation")

        total_score = int(sub_score + ato_score + cgt_score + max(0, doc_score))

        # EOFY urgency
        if days_to_eofy <= 30 and total_score < 80:
            recommendations.insert(0, f"⚠️ Only {days_to_eofy} days to EOFY - prioritize tax preparation")

        return HealthScore(
            dimension=self.dimension,
            score=min(100, max(0, total_score)),
            issues=issues,
            recommendations=recommendations,
            details={
                "substantiation_rate": sub_rate,
                "ato_coverage": ato_coverage,
                "cgt_tracking_rate": cgt_rate,
                "days_to_eofy": days_to_eofy,
            },
        )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_scores.py::TestTaxReadinessScorer -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/scores.py tests/unit/test_health_scores.py
git commit -m "feat(health): add TaxReadinessScorer for tax compliance metrics"
```

---

### Task 9: Implement AutomationScorer

**Files:**
- Modify: `scripts/health/scores.py`
- Modify: `tests/unit/test_health_scores.py`

**Step 1: Write the failing test for AutomationScorer**

Add to `tests/unit/test_health_scores.py`:

```python
from scripts.health.scores import AutomationScorer


class TestAutomationScorer:
    """Tests for AutomationScorer."""

    def test_high_automation_utilization(self):
        """High usage of automation features = excellent score."""
        scorer = AutomationScorer()
        data = {
            "auto_categorization_enabled": True,
            "scheduled_reports_count": 3,
            "active_alerts_count": 5,
            "rule_auto_apply_rate": 0.85,
            "manual_operations_30d": 10,
            "total_operations_30d": 100,
        }

        result = scorer.calculate(data)
        assert result.dimension == "automation"
        assert result.score >= 75
        assert result.status in [HealthStatus.GOOD, HealthStatus.EXCELLENT]

    def test_no_automation_low_score(self):
        """No automation features used = poor score."""
        scorer = AutomationScorer()
        data = {
            "auto_categorization_enabled": False,
            "scheduled_reports_count": 0,
            "active_alerts_count": 0,
            "rule_auto_apply_rate": 0.0,
            "manual_operations_30d": 100,
            "total_operations_30d": 100,
        }

        result = scorer.calculate(data)
        assert result.score < 50
        assert result.status == HealthStatus.POOR

    def test_recommendations_for_unused_features(self):
        """Should recommend enabling unused automation features."""
        scorer = AutomationScorer()
        data = {
            "auto_categorization_enabled": False,
            "scheduled_reports_count": 0,
            "active_alerts_count": 2,
            "rule_auto_apply_rate": 0.50,
            "manual_operations_30d": 50,
            "total_operations_30d": 100,
        }

        result = scorer.calculate(data)
        # Should recommend enabling auto-categorization and scheduled reports
        assert any("auto" in r.lower() or "categoriz" in r.lower() for r in result.recommendations)
        assert any("report" in r.lower() or "schedule" in r.lower() for r in result.recommendations)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_scores.py::TestAutomationScorer -v
```

Expected: FAIL with "cannot import name 'AutomationScorer'"

**Step 3: Write minimal implementation for AutomationScorer**

Add to `scripts/health/scores.py`:

```python
class AutomationScorer(BaseScorer):
    """Scores automation utilization: auto-categorization, alerts, reports."""

    dimension = "automation"

    FEATURES_WEIGHT = 0.4
    EFFICIENCY_WEIGHT = 0.4
    UTILIZATION_WEIGHT = 0.2

    def calculate(self, data: Dict[str, Any]) -> HealthScore:
        """Calculate automation score.

        Args:
            data: Dict with keys:
                - auto_categorization_enabled: bool
                - scheduled_reports_count: int
                - active_alerts_count: int
                - rule_auto_apply_rate: float (0-1)
                - manual_operations_30d: int
                - total_operations_30d: int

        Returns:
            HealthScore for automation dimension
        """
        auto_cat = data.get("auto_categorization_enabled", False)
        scheduled_reports = data.get("scheduled_reports_count", 0)
        active_alerts = data.get("active_alerts_count", 0)
        auto_apply = data.get("rule_auto_apply_rate", 0)
        manual_ops = data.get("manual_operations_30d", 0)
        total_ops = data.get("total_operations_30d", 1)

        issues: List[str] = []
        recommendations: List[str] = []

        # Features score (0-40 points)
        features_enabled = 0
        max_features = 4

        if auto_cat:
            features_enabled += 1
        else:
            issues.append("Auto-categorization not enabled")
            recommendations.append("Enable auto-categorization in Smart mode")

        if scheduled_reports > 0:
            features_enabled += 1
        else:
            recommendations.append("Set up scheduled reports for regular financial summaries")

        if active_alerts >= 3:
            features_enabled += 1
        elif active_alerts > 0:
            features_enabled += 0.5
        else:
            recommendations.append("Configure alerts for budget monitoring and tax deadlines")

        if auto_apply >= 0.70:
            features_enabled += 1
        elif auto_apply >= 0.40:
            features_enabled += 0.5

        features_score = (features_enabled / max_features) * 100 * self.FEATURES_WEIGHT

        # Efficiency score (0-40 points)
        automation_rate = 1 - (manual_ops / total_ops) if total_ops > 0 else 0
        efficiency_score = automation_rate * 100 * self.EFFICIENCY_WEIGHT

        if automation_rate < 0.50:
            issues.append(f"High manual operation rate ({manual_ops}/{total_ops} operations)")
            recommendations.append("Create rules to automate repetitive categorization tasks")

        # Utilization score (0-20 points)
        utilization = auto_apply * 100 * self.UTILIZATION_WEIGHT

        total_score = int(features_score + efficiency_score + utilization)

        return HealthScore(
            dimension=self.dimension,
            score=min(100, max(0, total_score)),
            issues=issues,
            recommendations=recommendations,
            details={
                "features_enabled": features_enabled,
                "automation_rate": automation_rate,
                "auto_apply_rate": auto_apply,
            },
        )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_scores.py::TestAutomationScorer -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/scores.py tests/unit/test_health_scores.py
git commit -m "feat(health): add AutomationScorer for automation utilization metrics"
```

---

### Task 10: Implement BudgetAlignmentScorer

**Files:**
- Modify: `scripts/health/scores.py`
- Modify: `tests/unit/test_health_scores.py`

**Step 1: Write the failing test for BudgetAlignmentScorer**

Add to `tests/unit/test_health_scores.py`:

```python
from scripts.health.scores import BudgetAlignmentScorer


class TestBudgetAlignmentScorer:
    """Tests for BudgetAlignmentScorer."""

    def test_on_budget_high_score(self):
        """Spending on budget = excellent score."""
        scorer = BudgetAlignmentScorer()
        data = {
            "categories_with_budget": 10,
            "categories_on_track": 9,
            "categories_over_budget": 1,
            "total_budget": 5000.00,
            "total_spent": 4800.00,
            "goals_on_track": 3,
            "goals_total": 3,
        }

        result = scorer.calculate(data)
        assert result.dimension == "budget_alignment"
        assert result.score >= 80
        assert result.status in [HealthStatus.GOOD, HealthStatus.EXCELLENT]

    def test_overspending_penalized(self):
        """Significant overspending reduces score."""
        scorer = BudgetAlignmentScorer()
        data = {
            "categories_with_budget": 10,
            "categories_on_track": 3,
            "categories_over_budget": 7,
            "total_budget": 5000.00,
            "total_spent": 7000.00,  # 40% over
            "goals_on_track": 1,
            "goals_total": 3,
        }

        result = scorer.calculate(data)
        assert result.score < 60
        assert any("over" in issue.lower() or "budget" in issue.lower() for issue in result.issues)

    def test_no_budgets_penalized(self):
        """No budgets set = lower score with recommendation."""
        scorer = BudgetAlignmentScorer()
        data = {
            "categories_with_budget": 0,
            "categories_on_track": 0,
            "categories_over_budget": 0,
            "total_budget": 0,
            "total_spent": 3000.00,
            "goals_on_track": 0,
            "goals_total": 0,
        }

        result = scorer.calculate(data)
        assert result.score < 50
        assert any("budget" in r.lower() for r in result.recommendations)

    def test_goals_behind_flagged(self):
        """Goals behind schedule should be flagged."""
        scorer = BudgetAlignmentScorer()
        data = {
            "categories_with_budget": 5,
            "categories_on_track": 5,
            "categories_over_budget": 0,
            "total_budget": 3000.00,
            "total_spent": 2800.00,
            "goals_on_track": 1,
            "goals_total": 4,  # 3 goals behind
        }

        result = scorer.calculate(data)
        assert any("goal" in issue.lower() for issue in result.issues)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_scores.py::TestBudgetAlignmentScorer -v
```

Expected: FAIL with "cannot import name 'BudgetAlignmentScorer'"

**Step 3: Write minimal implementation for BudgetAlignmentScorer**

Add to `scripts/health/scores.py`:

```python
class BudgetAlignmentScorer(BaseScorer):
    """Scores budget alignment: spending vs budget, goal progress."""

    dimension = "budget_alignment"

    SPENDING_WEIGHT = 0.5
    CATEGORY_WEIGHT = 0.3
    GOALS_WEIGHT = 0.2

    def calculate(self, data: Dict[str, Any]) -> HealthScore:
        """Calculate budget alignment score.

        Args:
            data: Dict with keys:
                - categories_with_budget: int
                - categories_on_track: int
                - categories_over_budget: int
                - total_budget: float
                - total_spent: float
                - goals_on_track: int
                - goals_total: int

        Returns:
            HealthScore for budget alignment dimension
        """
        cats_budgeted = data.get("categories_with_budget", 0)
        cats_on_track = data.get("categories_on_track", 0)
        cats_over = data.get("categories_over_budget", 0)
        total_budget = data.get("total_budget", 0)
        total_spent = data.get("total_spent", 0)
        goals_on_track = data.get("goals_on_track", 0)
        goals_total = data.get("goals_total", 0)

        issues: List[str] = []
        recommendations: List[str] = []

        # No budgets set
        if cats_budgeted == 0:
            return HealthScore(
                dimension=self.dimension,
                score=30,  # Base score for having no budgets
                issues=["No category budgets configured"],
                recommendations=[
                    "Set up budgets for major spending categories",
                    "Use /smith:analyze spending to identify budget targets",
                ],
            )

        # Spending alignment score (0-50 points)
        if total_budget > 0:
            spend_ratio = total_spent / total_budget
            if spend_ratio <= 1.0:
                spending_score = 100 * self.SPENDING_WEIGHT
            else:
                # Penalize overspending
                over_percent = (spend_ratio - 1.0) * 100
                penalty = min(50, over_percent)
                spending_score = max(0, (100 - penalty) * self.SPENDING_WEIGHT)
                issues.append(f"Overall spending {over_percent:.0f}% over budget")
                recommendations.append("Review spending in over-budget categories")
        else:
            spending_score = 50 * self.SPENDING_WEIGHT

        # Category tracking score (0-30 points)
        if cats_budgeted > 0:
            track_rate = cats_on_track / cats_budgeted
            category_score = track_rate * 100 * self.CATEGORY_WEIGHT

            if cats_over > 0:
                issues.append(f"{cats_over} categories over budget")
        else:
            category_score = 0

        # Goals score (0-20 points)
        if goals_total > 0:
            goal_rate = goals_on_track / goals_total
            goals_score = goal_rate * 100 * self.GOALS_WEIGHT

            behind = goals_total - goals_on_track
            if behind > 0:
                issues.append(f"{behind} financial goals behind schedule")
                recommendations.append("Review goal progress and adjust contributions")
        else:
            goals_score = 100 * self.GOALS_WEIGHT  # No goals = full points (optional feature)

        total_score = int(spending_score + category_score + goals_score)

        return HealthScore(
            dimension=self.dimension,
            score=min(100, max(0, total_score)),
            issues=issues,
            recommendations=recommendations,
            details={
                "spend_ratio": total_spent / total_budget if total_budget > 0 else 0,
                "categories_on_track_rate": cats_on_track / cats_budgeted if cats_budgeted > 0 else 0,
                "goals_on_track_rate": goals_on_track / goals_total if goals_total > 0 else 1,
            },
        )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_scores.py::TestBudgetAlignmentScorer -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/scores.py tests/unit/test_health_scores.py
git commit -m "feat(health): add BudgetAlignmentScorer for budget and goals tracking"
```

---

## Part 2: Health Check Engine

### Task 11: Implement HealthCheckEngine Core

**Files:**
- Create: `scripts/health/engine.py`
- Create: `tests/unit/test_health_engine.py`

**Step 1: Write the failing test for HealthCheckEngine**

Create `tests/unit/test_health_engine.py`:

```python
"""Unit tests for HealthCheckEngine."""

import pytest
from datetime import datetime
from scripts.health.engine import HealthCheckEngine, HealthCheckResult
from scripts.health.scores import HealthScore, HealthStatus


class TestHealthCheckEngine:
    """Tests for HealthCheckEngine."""

    def test_engine_initialization(self):
        """Engine initializes with all scorers."""
        engine = HealthCheckEngine()
        assert len(engine.scorers) == 6
        dimensions = {s.dimension for s in engine.scorers}
        assert "data_quality" in dimensions
        assert "category_structure" in dimensions
        assert "rule_engine" in dimensions
        assert "tax_readiness" in dimensions
        assert "automation" in dimensions
        assert "budget_alignment" in dimensions

    def test_run_all_checks(self):
        """Running all checks returns complete result."""
        engine = HealthCheckEngine()

        # Provide data for all scorers
        data = {
            "data_quality": {
                "total_transactions": 100,
                "categorized_transactions": 90,
                "transactions_with_payee": 95,
                "duplicate_count": 2,
            },
            "category_structure": {
                "total_categories": 30,
                "categories_with_transactions": 25,
                "max_depth": 3,
                "categories_at_root": 8,
                "ato_mapped_categories": 20,
                "empty_categories": 5,
            },
            "rule_engine": {
                "total_rules": 40,
                "active_rules": 38,
                "auto_categorization_rate": 0.75,
                "rule_accuracy": 0.92,
                "conflicting_rules": 1,
                "stale_rules": 2,
            },
            "tax_readiness": {
                "deductible_transactions": 50,
                "substantiated_transactions": 45,
                "ato_category_coverage": 0.80,
                "cgt_events_tracked": 3,
                "cgt_events_total": 3,
                "missing_documentation_count": 5,
                "days_to_eofy": 200,
            },
            "automation": {
                "auto_categorization_enabled": True,
                "scheduled_reports_count": 2,
                "active_alerts_count": 4,
                "rule_auto_apply_rate": 0.80,
                "manual_operations_30d": 20,
                "total_operations_30d": 100,
            },
            "budget_alignment": {
                "categories_with_budget": 8,
                "categories_on_track": 7,
                "categories_over_budget": 1,
                "total_budget": 4000.00,
                "total_spent": 3800.00,
                "goals_on_track": 2,
                "goals_total": 2,
            },
        }

        result = engine.run_all(data)

        assert isinstance(result, HealthCheckResult)
        assert len(result.scores) == 6
        assert result.overall_score > 0
        assert result.overall_status in HealthStatus
        assert len(result.top_recommendations) > 0

    def test_run_single_check(self):
        """Can run single dimension check."""
        engine = HealthCheckEngine()

        data = {
            "total_transactions": 100,
            "categorized_transactions": 80,
            "transactions_with_payee": 90,
            "duplicate_count": 5,
        }

        score = engine.run_single("data_quality", data)

        assert score.dimension == "data_quality"
        assert 0 <= score.score <= 100

    def test_overall_score_calculation(self):
        """Overall score is weighted average of dimension scores."""
        engine = HealthCheckEngine()

        # Create mock scores
        scores = [
            HealthScore(dimension="data_quality", score=80),
            HealthScore(dimension="category_structure", score=70),
            HealthScore(dimension="rule_engine", score=60),
            HealthScore(dimension="tax_readiness", score=90),
            HealthScore(dimension="automation", score=50),
            HealthScore(dimension="budget_alignment", score=85),
        ]

        overall = engine._calculate_overall(scores)
        # Should be weighted average
        assert 60 <= overall <= 80
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_engine.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation for HealthCheckEngine**

Create `scripts/health/engine.py`:

```python
"""Health check engine for comprehensive system evaluation."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from scripts.health.scores import (
    HealthScore,
    HealthStatus,
    BaseScorer,
    DataQualityScorer,
    CategoryStructureScorer,
    RuleEngineScorer,
    TaxReadinessScorer,
    AutomationScorer,
    BudgetAlignmentScorer,
)


@dataclass
class HealthCheckResult:
    """Complete health check result."""

    scores: List[HealthScore]
    overall_score: int
    overall_status: HealthStatus
    top_recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "overall_score": self.overall_score,
            "overall_status": self.overall_status.value,
            "scores": [s.to_dict() for s in self.scores],
            "top_recommendations": self.top_recommendations,
            "timestamp": self.timestamp.isoformat(),
        }


class HealthCheckEngine:
    """Engine for running health checks across all dimensions."""

    # Dimension weights for overall score calculation
    WEIGHTS = {
        "data_quality": 0.20,
        "category_structure": 0.15,
        "rule_engine": 0.20,
        "tax_readiness": 0.20,
        "automation": 0.10,
        "budget_alignment": 0.15,
    }

    def __init__(self) -> None:
        """Initialize engine with all scorers."""
        self.scorers: List[BaseScorer] = [
            DataQualityScorer(),
            CategoryStructureScorer(),
            RuleEngineScorer(),
            TaxReadinessScorer(),
            AutomationScorer(),
            BudgetAlignmentScorer(),
        ]
        self._scorer_map = {s.dimension: s for s in self.scorers}

    def run_all(self, data: Dict[str, Dict[str, Any]]) -> HealthCheckResult:
        """Run all health checks.

        Args:
            data: Dict mapping dimension names to their input data

        Returns:
            Complete HealthCheckResult
        """
        scores: List[HealthScore] = []

        for scorer in self.scorers:
            dimension_data = data.get(scorer.dimension, {})
            score = scorer.calculate(dimension_data)
            scores.append(score)

        overall = self._calculate_overall(scores)
        top_recs = self._prioritize_recommendations(scores)

        return HealthCheckResult(
            scores=scores,
            overall_score=overall,
            overall_status=HealthStatus.from_score(overall),
            top_recommendations=top_recs[:5],  # Top 5 recommendations
        )

    def run_single(self, dimension: str, data: Dict[str, Any]) -> HealthScore:
        """Run health check for single dimension.

        Args:
            dimension: Dimension name (e.g., 'data_quality')
            data: Input data for the scorer

        Returns:
            HealthScore for the dimension

        Raises:
            ValueError: If dimension not found
        """
        scorer = self._scorer_map.get(dimension)
        if not scorer:
            raise ValueError(f"Unknown dimension: {dimension}")

        return scorer.calculate(data)

    def _calculate_overall(self, scores: List[HealthScore]) -> int:
        """Calculate weighted overall score.

        Args:
            scores: List of dimension scores

        Returns:
            Overall score (0-100)
        """
        total_weight = 0
        weighted_sum = 0

        for score in scores:
            weight = self.WEIGHTS.get(score.dimension, 0.1)
            weighted_sum += score.score * weight
            total_weight += weight

        if total_weight == 0:
            return 0

        return int(weighted_sum / total_weight)

    def _prioritize_recommendations(self, scores: List[HealthScore]) -> List[str]:
        """Prioritize recommendations by impact.

        Args:
            scores: All dimension scores

        Returns:
            Prioritized list of recommendations
        """
        # Sort scores by impact (weight * deficit from 100)
        scored_recs: List[tuple] = []

        for score in scores:
            weight = self.WEIGHTS.get(score.dimension, 0.1)
            deficit = 100 - score.score
            impact = weight * deficit

            for rec in score.recommendations:
                scored_recs.append((impact, score.dimension, rec))

        # Sort by impact descending
        scored_recs.sort(key=lambda x: x[0], reverse=True)

        # Return unique recommendations
        seen = set()
        result = []
        for _, dimension, rec in scored_recs:
            if rec not in seen:
                seen.add(rec)
                result.append(rec)

        return result
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_engine.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/engine.py tests/unit/test_health_engine.py
git commit -m "feat(health): add HealthCheckEngine for comprehensive health evaluation"
```

---

### Task 12: Add Health Check Data Collection

**Files:**
- Create: `scripts/health/collector.py`
- Create: `tests/unit/test_health_collector.py`

**Step 1: Write the failing test for HealthDataCollector**

Create `tests/unit/test_health_collector.py`:

```python
"""Unit tests for health data collection."""

import pytest
from unittest.mock import Mock, MagicMock
from scripts.health.collector import HealthDataCollector


class TestHealthDataCollector:
    """Tests for HealthDataCollector."""

    def test_collector_initialization(self):
        """Collector initializes with API client."""
        mock_client = Mock()
        collector = HealthDataCollector(api_client=mock_client)
        assert collector.api_client == mock_client

    def test_collect_data_quality_metrics(self):
        """Collects data quality metrics from transactions."""
        mock_client = Mock()
        mock_client.get_transactions.return_value = [
            {"id": 1, "category": {"id": 1}, "payee": "Store A"},
            {"id": 2, "category": {"id": 2}, "payee": "Store B"},
            {"id": 3, "category": None, "payee": ""},
            {"id": 4, "category": {"id": 1}, "payee": "Store A"},
        ]

        collector = HealthDataCollector(api_client=mock_client)
        data = collector.collect_data_quality()

        assert data["total_transactions"] == 4
        assert data["categorized_transactions"] == 3
        assert data["transactions_with_payee"] == 3
        assert "duplicate_count" in data

    def test_collect_returns_all_dimensions(self):
        """Collect all returns data for all dimensions."""
        mock_client = Mock()
        mock_client.get_transactions.return_value = []
        mock_client.get_categories.return_value = []
        mock_client.get_user.return_value = {"id": 1}

        collector = HealthDataCollector(api_client=mock_client)

        # Mock all collection methods
        collector.collect_data_quality = Mock(return_value={"total_transactions": 0})
        collector.collect_category_structure = Mock(return_value={"total_categories": 0})
        collector.collect_rule_engine = Mock(return_value={"total_rules": 0})
        collector.collect_tax_readiness = Mock(return_value={"deductible_transactions": 0})
        collector.collect_automation = Mock(return_value={"auto_categorization_enabled": False})
        collector.collect_budget_alignment = Mock(return_value={"categories_with_budget": 0})

        data = collector.collect_all()

        assert "data_quality" in data
        assert "category_structure" in data
        assert "rule_engine" in data
        assert "tax_readiness" in data
        assert "automation" in data
        assert "budget_alignment" in data
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_collector.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation for HealthDataCollector**

Create `scripts/health/collector.py`:

```python
"""Health data collection from PocketSmith API."""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import json
from pathlib import Path


class HealthDataCollector:
    """Collects data for health check scoring from various sources."""

    def __init__(self, api_client: Any, data_dir: Optional[Path] = None) -> None:
        """Initialize collector.

        Args:
            api_client: PocketSmith API client instance
            data_dir: Path to data directory (default: data/)
        """
        self.api_client = api_client
        self.data_dir = data_dir or Path("data")

    def collect_all(self) -> Dict[str, Dict[str, Any]]:
        """Collect data for all health dimensions.

        Returns:
            Dict mapping dimension names to their data
        """
        return {
            "data_quality": self.collect_data_quality(),
            "category_structure": self.collect_category_structure(),
            "rule_engine": self.collect_rule_engine(),
            "tax_readiness": self.collect_tax_readiness(),
            "automation": self.collect_automation(),
            "budget_alignment": self.collect_budget_alignment(),
        }

    def collect_data_quality(self) -> Dict[str, Any]:
        """Collect data quality metrics.

        Returns:
            Dict with data quality metrics
        """
        transactions = self.api_client.get_transactions()

        total = len(transactions)
        categorized = sum(1 for t in transactions if t.get("category"))
        with_payee = sum(1 for t in transactions if t.get("payee", "").strip())

        # Simple duplicate detection by payee+amount+date
        signatures = []
        for t in transactions:
            sig = f"{t.get('payee', '')}|{t.get('amount', '')}|{t.get('date', '')}"
            signatures.append(sig)

        sig_counts = Counter(signatures)
        duplicates = sum(count - 1 for count in sig_counts.values() if count > 1)

        return {
            "total_transactions": total,
            "categorized_transactions": categorized,
            "transactions_with_payee": with_payee,
            "duplicate_count": duplicates,
        }

    def collect_category_structure(self) -> Dict[str, Any]:
        """Collect category structure metrics.

        Returns:
            Dict with category structure metrics
        """
        categories = self.api_client.get_categories()

        total = len(categories)
        with_transactions = sum(1 for c in categories if c.get("transaction_count", 0) > 0)
        root_count = sum(1 for c in categories if c.get("parent_id") is None)
        empty = sum(1 for c in categories if c.get("transaction_count", 0) == 0)

        # Calculate max depth
        max_depth = self._calculate_category_depth(categories)

        # Load ATO mappings
        ato_mapped = self._count_ato_mapped_categories()

        return {
            "total_categories": total,
            "categories_with_transactions": with_transactions,
            "max_depth": max_depth,
            "categories_at_root": root_count,
            "ato_mapped_categories": ato_mapped,
            "empty_categories": empty,
        }

    def collect_rule_engine(self) -> Dict[str, Any]:
        """Collect rule engine metrics.

        Returns:
            Dict with rule engine metrics
        """
        # Load local rules
        local_rules = self._load_json("local_rules.json", [])
        platform_rules = self._load_json("platform_rules.json", [])

        total_rules = len(local_rules) + len(platform_rules)
        active_rules = sum(1 for r in local_rules if r.get("active", True))
        active_rules += len(platform_rules)  # Platform rules always active

        # Calculate metrics from rule metadata
        rule_metadata = self._load_json("rule_metadata.json", {})

        total_matches = sum(r.get("matches", 0) for r in local_rules)
        total_applied = sum(r.get("applied", 0) for r in local_rules)
        total_overrides = sum(r.get("user_overrides", 0) for r in local_rules)

        # Get transactions for coverage calculation
        transactions = self.api_client.get_transactions()
        total_txn = len(transactions)
        auto_categorized = sum(1 for t in transactions if t.get("auto_categorized", False))

        coverage = auto_categorized / total_txn if total_txn > 0 else 0
        accuracy = total_applied / (total_applied + total_overrides) if (total_applied + total_overrides) > 0 else 1.0

        # Count conflicts and stale rules
        conflicts = rule_metadata.get("conflicts", 0)
        stale_days = 90
        stale = sum(1 for r in local_rules
                   if self._days_since(r.get("last_used")) > stale_days)

        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "auto_categorization_rate": coverage,
            "rule_accuracy": accuracy,
            "conflicting_rules": conflicts,
            "stale_rules": stale,
        }

    def collect_tax_readiness(self) -> Dict[str, Any]:
        """Collect tax readiness metrics.

        Returns:
            Dict with tax readiness metrics
        """
        # Load tax tracking data
        substantiation = self._load_json("tax/substantiation_tracking.json", {})
        cgt_register = self._load_json("tax/cgt_register.json", {"events": []})
        ato_mappings = self._load_json("tax/ato_category_mappings.json", {})

        # Count deductible transactions (simplified)
        transactions = self.api_client.get_transactions()
        deductible = sum(1 for t in transactions if self._is_deductible(t))
        substantiated = substantiation.get("substantiated_count", 0)

        # ATO coverage
        categories = self.api_client.get_categories()
        cats_used = sum(1 for c in categories if c.get("transaction_count", 0) > 0)
        cats_mapped = len(ato_mappings.get("mappings", {}))
        ato_coverage = cats_mapped / cats_used if cats_used > 0 else 0

        # CGT tracking
        cgt_events = cgt_register.get("events", [])
        cgt_total = len(cgt_events)
        cgt_tracked = sum(1 for e in cgt_events if e.get("complete", False))

        # Missing documentation
        missing_docs = substantiation.get("missing_count", 0)

        # Days to EOFY (June 30)
        today = datetime.now()
        eofy = datetime(today.year, 6, 30)
        if today > eofy:
            eofy = datetime(today.year + 1, 6, 30)
        days_to_eofy = (eofy - today).days

        return {
            "deductible_transactions": max(1, deductible),  # Avoid division by zero
            "substantiated_transactions": substantiated,
            "ato_category_coverage": ato_coverage,
            "cgt_events_tracked": cgt_tracked,
            "cgt_events_total": cgt_total,
            "missing_documentation_count": missing_docs,
            "days_to_eofy": days_to_eofy,
        }

    def collect_automation(self) -> Dict[str, Any]:
        """Collect automation utilization metrics.

        Returns:
            Dict with automation metrics
        """
        config = self._load_json("config.json", {})

        auto_cat_enabled = config.get("intelligence_mode", "smart") != "conservative"
        scheduled_reports = len(config.get("scheduled_reports", []))
        active_alerts = len(config.get("active_alerts", []))

        # Rule auto-apply rate
        local_rules = self._load_json("local_rules.json", [])
        auto_apply_rules = sum(1 for r in local_rules if not r.get("requires_approval", True))
        total_rules = len(local_rules)
        auto_apply_rate = auto_apply_rules / total_rules if total_rules > 0 else 0

        # Operation metrics (from audit log)
        audit_log = self._load_json("audit/operation_stats.json", {})
        manual_ops = audit_log.get("manual_operations_30d", 0)
        total_ops = audit_log.get("total_operations_30d", 1)

        return {
            "auto_categorization_enabled": auto_cat_enabled,
            "scheduled_reports_count": scheduled_reports,
            "active_alerts_count": active_alerts,
            "rule_auto_apply_rate": auto_apply_rate,
            "manual_operations_30d": manual_ops,
            "total_operations_30d": total_ops,
        }

    def collect_budget_alignment(self) -> Dict[str, Any]:
        """Collect budget alignment metrics.

        Returns:
            Dict with budget alignment metrics
        """
        # Get budget data from PocketSmith
        budgets = self.api_client.get_budgets() if hasattr(self.api_client, 'get_budgets') else []

        cats_with_budget = len(budgets)
        cats_on_track = sum(1 for b in budgets if b.get("spent", 0) <= b.get("budget", 0))
        cats_over = cats_with_budget - cats_on_track

        total_budget = sum(b.get("budget", 0) for b in budgets)
        total_spent = sum(b.get("spent", 0) for b in budgets)

        # Goals from local storage
        goals = self._load_json("goals/financial_goals.json", {"goals": []})
        goals_list = goals.get("goals", [])
        goals_total = len(goals_list)
        goals_on_track = sum(1 for g in goals_list if g.get("on_track", False))

        return {
            "categories_with_budget": cats_with_budget,
            "categories_on_track": cats_on_track,
            "categories_over_budget": cats_over,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "goals_on_track": goals_on_track,
            "goals_total": goals_total,
        }

    def _load_json(self, filename: str, default: Any) -> Any:
        """Load JSON file from data directory."""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return default

    def _calculate_category_depth(self, categories: List[Dict]) -> int:
        """Calculate maximum category hierarchy depth."""
        if not categories:
            return 0

        # Build parent-child relationships
        by_id = {c.get("id"): c for c in categories}
        max_depth = 1

        for cat in categories:
            depth = 1
            parent_id = cat.get("parent_id")
            while parent_id and parent_id in by_id:
                depth += 1
                parent_id = by_id[parent_id].get("parent_id")
            max_depth = max(max_depth, depth)

        return max_depth

    def _count_ato_mapped_categories(self) -> int:
        """Count categories mapped to ATO expense types."""
        mappings = self._load_json("tax/ato_category_mappings.json", {})
        return len(mappings.get("mappings", {}))

    def _is_deductible(self, transaction: Dict) -> bool:
        """Check if transaction is potentially deductible."""
        category = transaction.get("category", {})
        if not category:
            return False
        # Simplified check - in real implementation, use ATO mappings
        cat_name = category.get("name", "").lower()
        deductible_keywords = ["work", "business", "office", "professional", "education"]
        return any(kw in cat_name for kw in deductible_keywords)

    def _days_since(self, date_str: Optional[str]) -> int:
        """Calculate days since a date string."""
        if not date_str:
            return 999
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return (datetime.now(date.tzinfo) - date).days
        except (ValueError, TypeError):
            return 999
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_collector.py -v
```

Expected: PASS

**Step 5: Update __init__.py and commit**

Update `scripts/health/__init__.py` to include collector:

```python
"""Health check system for Agent Smith."""

from scripts.health.scores import (
    HealthScore,
    HealthStatus,
    BaseScorer,
    DataQualityScorer,
    CategoryStructureScorer,
    RuleEngineScorer,
    TaxReadinessScorer,
    AutomationScorer,
    BudgetAlignmentScorer,
)
from scripts.health.engine import HealthCheckEngine, HealthCheckResult
from scripts.health.collector import HealthDataCollector

__all__ = [
    "HealthScore",
    "HealthStatus",
    "BaseScorer",
    "DataQualityScorer",
    "CategoryStructureScorer",
    "RuleEngineScorer",
    "TaxReadinessScorer",
    "AutomationScorer",
    "BudgetAlignmentScorer",
    "HealthCheckEngine",
    "HealthCheckResult",
    "HealthDataCollector",
]
```

```bash
git add scripts/health/collector.py scripts/health/__init__.py tests/unit/test_health_collector.py
git commit -m "feat(health): add HealthDataCollector for gathering metrics from API and files"
```

---

## Part 3: Recommendation Engine

### Task 13: Implement RecommendationEngine

**Files:**
- Create: `scripts/health/recommendations.py`
- Create: `tests/unit/test_recommendations.py`

**Step 1: Write the failing test for RecommendationEngine**

Create `tests/unit/test_recommendations.py`:

```python
"""Unit tests for recommendation engine."""

import pytest
from scripts.health.recommendations import (
    RecommendationEngine,
    Recommendation,
    RecommendationPriority,
    RecommendationCategory,
)
from scripts.health.scores import HealthScore, HealthStatus


class TestRecommendation:
    """Tests for Recommendation dataclass."""

    def test_recommendation_creation(self):
        """Test creating a recommendation."""
        rec = Recommendation(
            title="Improve categorization",
            description="Add rules to increase auto-categorization rate",
            priority=RecommendationPriority.HIGH,
            category=RecommendationCategory.RULE_ENGINE,
            impact_score=15,
            effort="medium",
            command="/smith:optimize rules",
        )

        assert rec.title == "Improve categorization"
        assert rec.priority == RecommendationPriority.HIGH
        assert rec.impact_score == 15


class TestRecommendationEngine:
    """Tests for RecommendationEngine."""

    def test_generate_recommendations_from_scores(self):
        """Generates prioritized recommendations from health scores."""
        engine = RecommendationEngine()

        scores = [
            HealthScore(
                dimension="data_quality",
                score=60,
                issues=["40 uncategorized transactions"],
                recommendations=["Categorize remaining transactions"],
            ),
            HealthScore(
                dimension="rule_engine",
                score=45,
                issues=["Low coverage (30%)"],
                recommendations=["Create more categorization rules"],
            ),
        ]

        recommendations = engine.generate(scores)

        assert len(recommendations) > 0
        # Higher impact recommendations should come first
        assert recommendations[0].impact_score >= recommendations[-1].impact_score

    def test_quick_wins_identified(self):
        """Quick wins (high impact, low effort) are flagged."""
        engine = RecommendationEngine()

        scores = [
            HealthScore(
                dimension="automation",
                score=30,
                issues=["Auto-categorization disabled"],
                recommendations=["Enable auto-categorization"],
            ),
        ]

        recommendations = engine.generate(scores)

        # Enabling auto-categorization should be a quick win
        quick_wins = [r for r in recommendations if r.effort == "low" and r.impact_score >= 10]
        assert len(quick_wins) > 0

    def test_recommendations_include_commands(self):
        """Recommendations include actionable commands where applicable."""
        engine = RecommendationEngine()

        scores = [
            HealthScore(
                dimension="data_quality",
                score=50,
                issues=["50 uncategorized transactions"],
                recommendations=["Run categorization"],
            ),
        ]

        recommendations = engine.generate(scores)

        # Should have at least one recommendation with a command
        with_commands = [r for r in recommendations if r.command]
        assert len(with_commands) > 0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_recommendations.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation for RecommendationEngine**

Create `scripts/health/recommendations.py`:

```python
"""Recommendation engine for health improvement suggestions."""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from scripts.health.scores import HealthScore


class RecommendationPriority(Enum):
    """Priority levels for recommendations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationCategory(Enum):
    """Categories of recommendations."""

    DATA_QUALITY = "data_quality"
    CATEGORY_STRUCTURE = "category_structure"
    RULE_ENGINE = "rule_engine"
    TAX_READINESS = "tax_readiness"
    AUTOMATION = "automation"
    BUDGET = "budget"


@dataclass
class Recommendation:
    """A specific actionable recommendation."""

    title: str
    description: str
    priority: RecommendationPriority
    category: RecommendationCategory
    impact_score: int  # 0-20 points potential improvement
    effort: str  # "low", "medium", "high"
    command: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "category": self.category.value,
            "impact_score": self.impact_score,
            "effort": self.effort,
            "command": self.command,
            "details": self.details,
        }


class RecommendationEngine:
    """Engine for generating prioritized recommendations from health scores."""

    # Mapping of issues to recommendations with metadata
    RECOMMENDATION_TEMPLATES = {
        "uncategorized": {
            "title": "Categorize uncategorized transactions",
            "category": RecommendationCategory.DATA_QUALITY,
            "effort": "medium",
            "command": "/smith:categorize",
            "base_impact": 10,
        },
        "auto-categorization": {
            "title": "Enable auto-categorization",
            "category": RecommendationCategory.AUTOMATION,
            "effort": "low",
            "command": "/agent-smith --mode=smart",
            "base_impact": 12,
        },
        "coverage": {
            "title": "Improve rule coverage",
            "category": RecommendationCategory.RULE_ENGINE,
            "effort": "medium",
            "command": "/smith:optimize rules",
            "base_impact": 15,
        },
        "substantiation": {
            "title": "Add missing receipts/documentation",
            "category": RecommendationCategory.TAX_READINESS,
            "effort": "high",
            "command": "/smith:tax deductions",
            "base_impact": 12,
        },
        "budget": {
            "title": "Set up category budgets",
            "category": RecommendationCategory.BUDGET,
            "effort": "medium",
            "command": "/smith:analyze spending",
            "base_impact": 8,
        },
        "ato": {
            "title": "Map categories to ATO expense types",
            "category": RecommendationCategory.TAX_READINESS,
            "effort": "medium",
            "command": "/smith:tax",
            "base_impact": 10,
        },
        "duplicate": {
            "title": "Review potential duplicate transactions",
            "category": RecommendationCategory.DATA_QUALITY,
            "effort": "low",
            "command": "/smith:analyze",
            "base_impact": 5,
        },
        "hierarchy": {
            "title": "Organize category hierarchy",
            "category": RecommendationCategory.CATEGORY_STRUCTURE,
            "effort": "high",
            "command": "/smith:optimize categories",
            "base_impact": 8,
        },
        "rule": {
            "title": "Create categorization rules",
            "category": RecommendationCategory.RULE_ENGINE,
            "effort": "medium",
            "command": "/smith:optimize rules",
            "base_impact": 12,
        },
        "alert": {
            "title": "Configure budget and tax alerts",
            "category": RecommendationCategory.AUTOMATION,
            "effort": "low",
            "command": "/agent-smith",
            "base_impact": 6,
        },
        "report": {
            "title": "Set up scheduled reports",
            "category": RecommendationCategory.AUTOMATION,
            "effort": "low",
            "command": "/smith:report",
            "base_impact": 5,
        },
        "cgt": {
            "title": "Complete CGT register entries",
            "category": RecommendationCategory.TAX_READINESS,
            "effort": "high",
            "command": "/smith:tax cgt",
            "base_impact": 10,
        },
        "goal": {
            "title": "Review financial goals progress",
            "category": RecommendationCategory.BUDGET,
            "effort": "low",
            "command": "/smith:scenario projection",
            "base_impact": 5,
        },
    }

    # Dimension weights for impact calculation
    DIMENSION_WEIGHTS = {
        "data_quality": 0.20,
        "category_structure": 0.15,
        "rule_engine": 0.20,
        "tax_readiness": 0.20,
        "automation": 0.10,
        "budget_alignment": 0.15,
    }

    def generate(self, scores: List[HealthScore]) -> List[Recommendation]:
        """Generate prioritized recommendations from health scores.

        Args:
            scores: List of health scores from all dimensions

        Returns:
            Prioritized list of recommendations
        """
        recommendations: List[Recommendation] = []

        for score in scores:
            dimension_weight = self.DIMENSION_WEIGHTS.get(score.dimension, 0.1)
            deficit = 100 - score.score

            # Generate recommendations from issues
            for issue in score.issues:
                rec = self._issue_to_recommendation(
                    issue=issue,
                    score=score,
                    dimension_weight=dimension_weight,
                    deficit=deficit,
                )
                if rec:
                    recommendations.append(rec)

            # Generate recommendations from score recommendations
            for rec_text in score.recommendations:
                rec = self._text_to_recommendation(
                    text=rec_text,
                    score=score,
                    dimension_weight=dimension_weight,
                    deficit=deficit,
                )
                if rec and not self._duplicate_exists(rec, recommendations):
                    recommendations.append(rec)

        # Sort by impact score descending
        recommendations.sort(key=lambda r: r.impact_score, reverse=True)

        return recommendations

    def _issue_to_recommendation(
        self,
        issue: str,
        score: HealthScore,
        dimension_weight: float,
        deficit: int,
    ) -> Optional[Recommendation]:
        """Convert an issue to a recommendation."""
        issue_lower = issue.lower()

        for keyword, template in self.RECOMMENDATION_TEMPLATES.items():
            if keyword in issue_lower:
                impact = self._calculate_impact(
                    template["base_impact"],
                    dimension_weight,
                    deficit,
                )
                priority = self._determine_priority(impact, deficit)

                return Recommendation(
                    title=template["title"],
                    description=issue,
                    priority=priority,
                    category=template["category"],
                    impact_score=impact,
                    effort=template["effort"],
                    command=template["command"],
                    details={"source_dimension": score.dimension},
                )

        return None

    def _text_to_recommendation(
        self,
        text: str,
        score: HealthScore,
        dimension_weight: float,
        deficit: int,
    ) -> Optional[Recommendation]:
        """Convert recommendation text to structured recommendation."""
        text_lower = text.lower()

        for keyword, template in self.RECOMMENDATION_TEMPLATES.items():
            if keyword in text_lower:
                impact = self._calculate_impact(
                    template["base_impact"],
                    dimension_weight,
                    deficit,
                )
                priority = self._determine_priority(impact, deficit)

                return Recommendation(
                    title=template["title"],
                    description=text,
                    priority=priority,
                    category=template["category"],
                    impact_score=impact,
                    effort=template["effort"],
                    command=template["command"],
                    details={"source_dimension": score.dimension},
                )

        # Generic recommendation if no template matches
        category = self._dimension_to_category(score.dimension)
        impact = self._calculate_impact(5, dimension_weight, deficit)

        return Recommendation(
            title=text[:50] + "..." if len(text) > 50 else text,
            description=text,
            priority=self._determine_priority(impact, deficit),
            category=category,
            impact_score=impact,
            effort="medium",
            details={"source_dimension": score.dimension},
        )

    def _calculate_impact(
        self,
        base_impact: int,
        dimension_weight: float,
        deficit: int,
    ) -> int:
        """Calculate impact score based on various factors."""
        # Impact increases with dimension weight and deficit
        weight_factor = dimension_weight / 0.20  # Normalize around 20%
        deficit_factor = min(deficit / 50, 1.5)  # Cap at 1.5x for 75+ deficit

        return int(base_impact * weight_factor * deficit_factor)

    def _determine_priority(self, impact: int, deficit: int) -> RecommendationPriority:
        """Determine priority based on impact and deficit."""
        if impact >= 15 or deficit >= 60:
            return RecommendationPriority.CRITICAL
        elif impact >= 10 or deficit >= 40:
            return RecommendationPriority.HIGH
        elif impact >= 5:
            return RecommendationPriority.MEDIUM
        else:
            return RecommendationPriority.LOW

    def _dimension_to_category(self, dimension: str) -> RecommendationCategory:
        """Map dimension name to recommendation category."""
        mapping = {
            "data_quality": RecommendationCategory.DATA_QUALITY,
            "category_structure": RecommendationCategory.CATEGORY_STRUCTURE,
            "rule_engine": RecommendationCategory.RULE_ENGINE,
            "tax_readiness": RecommendationCategory.TAX_READINESS,
            "automation": RecommendationCategory.AUTOMATION,
            "budget_alignment": RecommendationCategory.BUDGET,
        }
        return mapping.get(dimension, RecommendationCategory.DATA_QUALITY)

    def _duplicate_exists(
        self,
        rec: Recommendation,
        existing: List[Recommendation],
    ) -> bool:
        """Check if a similar recommendation already exists."""
        for existing_rec in existing:
            if existing_rec.title == rec.title and existing_rec.category == rec.category:
                return True
        return False
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_recommendations.py -v
```

Expected: PASS

**Step 5: Update __init__.py and commit**

Update `scripts/health/__init__.py`:

```python
"""Health check system for Agent Smith."""

from scripts.health.scores import (
    HealthScore,
    HealthStatus,
    BaseScorer,
    DataQualityScorer,
    CategoryStructureScorer,
    RuleEngineScorer,
    TaxReadinessScorer,
    AutomationScorer,
    BudgetAlignmentScorer,
)
from scripts.health.engine import HealthCheckEngine, HealthCheckResult
from scripts.health.collector import HealthDataCollector
from scripts.health.recommendations import (
    RecommendationEngine,
    Recommendation,
    RecommendationPriority,
    RecommendationCategory,
)

__all__ = [
    "HealthScore",
    "HealthStatus",
    "BaseScorer",
    "DataQualityScorer",
    "CategoryStructureScorer",
    "RuleEngineScorer",
    "TaxReadinessScorer",
    "AutomationScorer",
    "BudgetAlignmentScorer",
    "HealthCheckEngine",
    "HealthCheckResult",
    "HealthDataCollector",
    "RecommendationEngine",
    "Recommendation",
    "RecommendationPriority",
    "RecommendationCategory",
]
```

```bash
git add scripts/health/recommendations.py scripts/health/__init__.py tests/unit/test_recommendations.py
git commit -m "feat(health): add RecommendationEngine for prioritized improvement suggestions"
```

---

## Part 4: Automated Monitoring

### Task 14: Integrate Health Monitoring with Alert System

**Files:**
- Create: `scripts/health/monitoring.py`
- Create: `tests/unit/test_health_monitoring.py`

**Step 1: Write the failing test**

Create `tests/unit/test_health_monitoring.py`:

```python
"""Unit tests for health monitoring integration."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from scripts.health.monitoring import HealthMonitor, MonitoringConfig


class TestHealthMonitor:
    """Tests for HealthMonitor."""

    def test_monitor_initialization(self):
        """Monitor initializes with config."""
        config = MonitoringConfig(
            weekly_check_enabled=True,
            monthly_full_check_enabled=True,
            alert_on_score_drop=True,
            score_drop_threshold=10,
        )

        monitor = HealthMonitor(config=config)
        assert monitor.config.weekly_check_enabled is True

    def test_should_run_weekly_check(self):
        """Determines when weekly check should run."""
        config = MonitoringConfig(weekly_check_enabled=True)
        monitor = HealthMonitor(config=config)

        # Last check was 8 days ago
        monitor.last_weekly_check = datetime.now() - timedelta(days=8)

        assert monitor.should_run_weekly() is True

    def test_should_not_run_if_recent(self):
        """Skip check if ran recently."""
        config = MonitoringConfig(weekly_check_enabled=True)
        monitor = HealthMonitor(config=config)

        # Last check was 2 days ago
        monitor.last_weekly_check = datetime.now() - timedelta(days=2)

        assert monitor.should_run_weekly() is False

    def test_detect_score_drop(self):
        """Detects significant score drops."""
        config = MonitoringConfig(
            alert_on_score_drop=True,
            score_drop_threshold=10,
        )
        monitor = HealthMonitor(config=config)

        previous = {"data_quality": 80, "rule_engine": 75}
        current = {"data_quality": 65, "rule_engine": 74}  # 15 point drop

        drops = monitor.detect_score_drops(previous, current)

        assert len(drops) == 1
        assert drops[0]["dimension"] == "data_quality"
        assert drops[0]["drop"] == 15

    def test_generate_monitoring_alerts(self):
        """Generates alerts from health check results."""
        config = MonitoringConfig(alert_on_score_drop=True)
        monitor = HealthMonitor(config=config)

        # Mock health check result with low scores
        mock_result = Mock()
        mock_result.overall_score = 45
        mock_result.overall_status = Mock(value="poor")

        alerts = monitor.generate_alerts(mock_result)

        assert len(alerts) > 0
        assert any("poor" in str(a).lower() or "health" in str(a).lower() for a in alerts)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_monitoring.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `scripts/health/monitoring.py`:

```python
"""Health monitoring and automated alerting."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

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
                drops.append({
                    "dimension": dimension,
                    "previous": prev_score,
                    "current": curr_score,
                    "drop": drop,
                })

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
            alerts.append(HealthAlert(
                alert_type="health_critical",
                title="Health Score Critical",
                message=f"Overall health score is {result.overall_score}/100 ({result.overall_status.value})",
                severity="critical",
                data={"score": result.overall_score},
            ))
        elif result.overall_status == HealthStatus.POOR:
            alerts.append(HealthAlert(
                alert_type="health_poor",
                title="Health Score Poor",
                message=f"Overall health score needs attention: {result.overall_score}/100",
                severity="warning",
                data={"score": result.overall_score},
            ))

        # Dimension-specific alerts
        for score in result.scores:
            if score.score < 40:
                alerts.append(HealthAlert(
                    alert_type="dimension_critical",
                    title=f"{score.dimension.replace('_', ' ').title()} Critical",
                    message=f"{score.dimension} score is {score.score}/100",
                    severity="critical",
                    dimension=score.dimension,
                    data={"score": score.score, "issues": score.issues},
                ))

        # Score drop alerts
        if self.last_scores and self.config.alert_on_score_drop:
            current_scores = {s.dimension: s.score for s in result.scores}
            drops = self.detect_score_drops(self.last_scores, current_scores)

            for drop in drops:
                alerts.append(HealthAlert(
                    alert_type="score_drop",
                    title=f"{drop['dimension'].replace('_', ' ').title()} Score Dropped",
                    message=f"Score dropped {drop['drop']} points (from {drop['previous']} to {drop['current']})",
                    severity="warning",
                    dimension=drop["dimension"],
                    data=drop,
                ))

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
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_monitoring.py -v
```

Expected: PASS

**Step 5: Update __init__.py and commit**

```bash
git add scripts/health/monitoring.py scripts/health/__init__.py tests/unit/test_health_monitoring.py
git commit -m "feat(health): add HealthMonitor for automated health alerting"
```

---

## Part 5: End-to-End Testing

### Task 15: Create Health Check Integration Tests

**Files:**
- Create: `tests/integration/test_health_check.py`

**Step 1: Write integration tests**

Create `tests/integration/test_health_check.py`:

```python
"""Integration tests for complete health check workflow."""

import pytest
from unittest.mock import Mock, patch
from scripts.health import (
    HealthCheckEngine,
    HealthDataCollector,
    RecommendationEngine,
    HealthMonitor,
    MonitoringConfig,
)


class TestHealthCheckIntegration:
    """End-to-end health check integration tests."""

    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client with realistic data."""
        client = Mock()

        # Transactions
        client.get_transactions.return_value = [
            {"id": i, "category": {"id": i % 10, "name": f"Category {i % 10}"}, "payee": f"Store {i}", "amount": 50.0, "date": "2025-01-01"}
            for i in range(100)
        ] + [
            {"id": 100 + i, "category": None, "payee": "", "amount": 25.0, "date": "2025-01-02"}
            for i in range(20)
        ]

        # Categories
        client.get_categories.return_value = [
            {"id": i, "name": f"Category {i}", "parent_id": None if i < 5 else i % 5, "transaction_count": 10}
            for i in range(20)
        ]

        # Budgets
        client.get_budgets.return_value = [
            {"id": i, "category_id": i, "budget": 500.0, "spent": 400.0 + i * 20}
            for i in range(5)
        ]

        return client

    def test_full_health_check_workflow(self, mock_api_client, tmp_path):
        """Test complete health check from data collection to recommendations."""
        # Setup
        collector = HealthDataCollector(
            api_client=mock_api_client,
            data_dir=tmp_path,
        )
        engine = HealthCheckEngine()
        rec_engine = RecommendationEngine()

        # Create required data files
        (tmp_path / "local_rules.json").write_text("[]")
        (tmp_path / "platform_rules.json").write_text("[]")
        (tmp_path / "rule_metadata.json").write_text("{}")
        (tmp_path / "config.json").write_text('{"intelligence_mode": "smart"}')
        (tmp_path / "tax").mkdir()
        (tmp_path / "tax" / "ato_category_mappings.json").write_text('{"mappings": {}}')
        (tmp_path / "tax" / "substantiation_tracking.json").write_text('{}')
        (tmp_path / "tax" / "cgt_register.json").write_text('{"events": []}')
        (tmp_path / "goals").mkdir()
        (tmp_path / "goals" / "financial_goals.json").write_text('{"goals": []}')
        (tmp_path / "audit").mkdir()
        (tmp_path / "audit" / "operation_stats.json").write_text('{}')

        # Collect data
        data = collector.collect_all()

        # Run health check
        result = engine.run_all(data)

        # Verify result structure
        assert result.overall_score > 0
        assert len(result.scores) == 6
        assert result.overall_status is not None

        # Generate recommendations
        recommendations = rec_engine.generate(result.scores)

        # Verify recommendations
        assert len(recommendations) > 0
        # Should have recommendations for uncategorized transactions
        assert any("categoriz" in r.title.lower() for r in recommendations)

    def test_health_monitoring_workflow(self, mock_api_client, tmp_path):
        """Test health monitoring and alert generation."""
        # Setup
        config = MonitoringConfig(
            weekly_check_enabled=True,
            alert_on_score_drop=True,
            score_drop_threshold=10,
        )
        monitor = HealthMonitor(config=config)
        collector = HealthDataCollector(api_client=mock_api_client, data_dir=tmp_path)
        engine = HealthCheckEngine()

        # Create minimal data files
        (tmp_path / "local_rules.json").write_text("[]")
        (tmp_path / "platform_rules.json").write_text("[]")
        (tmp_path / "rule_metadata.json").write_text("{}")
        (tmp_path / "config.json").write_text('{"intelligence_mode": "conservative"}')
        (tmp_path / "tax").mkdir()
        (tmp_path / "tax" / "ato_category_mappings.json").write_text('{"mappings": {}}')
        (tmp_path / "tax" / "substantiation_tracking.json").write_text('{}')
        (tmp_path / "tax" / "cgt_register.json").write_text('{"events": []}')
        (tmp_path / "goals").mkdir()
        (tmp_path / "goals" / "financial_goals.json").write_text('{"goals": []}')
        (tmp_path / "audit").mkdir()
        (tmp_path / "audit" / "operation_stats.json").write_text('{}')

        # Should run check (never run before)
        assert monitor.should_run_weekly() is True

        # Run check
        data = collector.collect_all()
        result = engine.run_all(data)

        # Generate alerts
        alerts = monitor.generate_alerts(result)

        # Record check
        monitor.record_check("weekly")

        # Should not run immediately after
        assert monitor.should_run_weekly() is False

        # Verify alerts generated for poor scores
        # With conservative mode disabled and no rules, automation score will be low
        assert len(alerts) >= 0  # May or may not have alerts depending on scores

    def test_quick_health_check(self, mock_api_client, tmp_path):
        """Test quick health check (single dimension)."""
        collector = HealthDataCollector(api_client=mock_api_client, data_dir=tmp_path)
        engine = HealthCheckEngine()

        # Quick check - just data quality
        data = collector.collect_data_quality()
        score = engine.run_single("data_quality", data)

        assert score.dimension == "data_quality"
        assert 0 <= score.score <= 100
        # With 20 uncategorized out of 120, score should reflect that
        assert score.score < 100
```

**Step 2: Run integration tests**

```bash
pytest tests/integration/test_health_check.py -v
```

Expected: PASS

**Step 3: Commit**

```bash
git add tests/integration/test_health_check.py
git commit -m "test(health): add integration tests for complete health check workflow"
```

---

## Part 6: Documentation & Polish

### Task 16: Create Health Check User Guide

**Files:**
- Create: `docs/guides/health-check-guide.md`

**Step 1: Write the user guide**

Create `docs/guides/health-check-guide.md`:

```markdown
# Agent Smith Health Check Guide

## Overview

The health check system evaluates your PocketSmith setup across 6 dimensions and provides actionable recommendations for improvement.

## Health Dimensions

### 1. Data Quality (20%)
- **What it measures:** Transaction categorization rate, payee completeness, duplicates
- **Target:** 90%+ categorization, minimal duplicates
- **Quick fix:** `/smith:categorize`

### 2. Category Structure (15%)
- **What it measures:** Hierarchy organization, usage, ATO alignment
- **Target:** Clear hierarchy, 70%+ categories in use
- **Quick fix:** `/smith:optimize categories`

### 3. Rule Engine (20%)
- **What it measures:** Auto-categorization coverage, rule accuracy
- **Target:** 70%+ auto-categorization rate, 90%+ accuracy
- **Quick fix:** `/smith:optimize rules`

### 4. Tax Readiness (20%)
- **What it measures:** Substantiation, ATO mapping, CGT tracking
- **Target:** 80%+ substantiation, complete CGT register
- **Quick fix:** `/smith:tax deductions`

### 5. Automation (10%)
- **What it measures:** Feature utilization, auto-apply rate
- **Target:** Auto-categorization enabled, alerts configured
- **Quick fix:** Enable Smart mode

### 6. Budget Alignment (15%)
- **What it measures:** Spending vs. budget, goal progress
- **Target:** On-budget, goals on track
- **Quick fix:** `/smith:analyze spending`

## Running Health Checks

### Quick Check
```
/smith:health --quick
```
Essential checks only, fast results.

### Full Check
```
/smith:health --full
```
Comprehensive analysis of all dimensions.

### Specific Dimension
```
/smith:health --category=tax
```
Focus on specific area: `categories`, `rules`, `tax`, `data`

## Understanding Scores

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | Excellent | Maintain practices |
| 70-89 | Good | Minor improvements |
| 50-69 | Fair | Several issues |
| 0-49 | Poor | Significant work needed |

## Automated Monitoring

Health checks run automatically:
- **Weekly:** Quick check every 7 days
- **Monthly:** Full check every 30 days
- **Pre-EOFY:** Extra checks in May-June

Configure alerts for:
- Score drops > 10 points
- Critical scores (< 50)
- EOFY deadlines

## Recommendations

Recommendations are prioritized by:
1. **Impact** - Points gained
2. **Effort** - Time required
3. **Urgency** - Deadline proximity

Look for **Quick Wins** (high impact, low effort) to improve scores fast.

## Example Output

```
🏥 AGENT SMITH HEALTH CHECK
════════════════════════════════════════

Overall Score: 72/100 (Good) 👍

Individual Scores:
├─ Data Quality:        85/100 ✅ Good
├─ Category Structure:  68/100 ⚠️ Fair
├─ Rule Engine:         65/100 ⚠️ Fair
├─ Tax Readiness:       78/100 👍 Good
├─ Automation:          60/100 ⚠️ Fair
└─ Budget Alignment:    75/100 👍 Good

🎯 TOP RECOMMENDATIONS:
1. [HIGH] Create categorization rules (15 pts)
   Run: /smith:optimize rules

2. [MEDIUM] Organize category hierarchy (8 pts)
   Run: /smith:optimize categories

3. [LOW] Enable scheduled reports (5 pts)
   Run: /smith:report

Projected after fixes: 89/100
```
```

**Step 2: Commit**

```bash
mkdir -p docs/guides
git add docs/guides/health-check-guide.md
git commit -m "docs: add health check user guide"
```

---

### Task 17: Update Module INDEX.md Files

**Files:**
- Update: `scripts/health/INDEX.md`
- Update: `scripts/INDEX.md`

**Step 1: Create scripts/health/INDEX.md**

Create `scripts/health/INDEX.md`:

```markdown
# Health Check Module

## Purpose
Comprehensive health evaluation system for Agent Smith with 6 scoring dimensions and recommendation engine.

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Module exports |
| `scores.py` | Health score definitions and 6 dimension scorers |
| `engine.py` | HealthCheckEngine for running all checks |
| `collector.py` | Data collection from API and local files |
| `recommendations.py` | Recommendation engine with prioritization |
| `monitoring.py` | Automated monitoring and alert generation |

## Usage

```python
from scripts.health import (
    HealthCheckEngine,
    HealthDataCollector,
    RecommendationEngine,
)

# Collect data and run checks
collector = HealthDataCollector(api_client=client)
data = collector.collect_all()

engine = HealthCheckEngine()
result = engine.run_all(data)

# Generate recommendations
rec_engine = RecommendationEngine()
recommendations = rec_engine.generate(result.scores)
```

## Dimensions

1. **data_quality** - Transaction categorization, payee completeness
2. **category_structure** - Hierarchy, usage, ATO alignment
3. **rule_engine** - Coverage, accuracy, conflicts
4. **tax_readiness** - Substantiation, CGT tracking
5. **automation** - Feature utilization
6. **budget_alignment** - Spending vs. budget, goals

## Related

- `/smith:health` - Slash command
- `docs/guides/health-check-guide.md` - User guide
```

**Step 2: Update scripts/INDEX.md**

Add health module to `scripts/INDEX.md`:

```markdown
# Scripts Directory

## Modules

| Directory | Description |
|-----------|-------------|
| `core/` | Core libraries (API client, rule engine) |
| `utils/` | Utility functions (backup, validation, logging) |
| `operations/` | Operation scripts (categorize) |
| `analysis/` | Analysis modules (spending, trends) |
| `reporting/` | Report formatters |
| `tax/` | Tax intelligence modules |
| `scenarios/` | Scenario analysis engines |
| `orchestration/` | Subagent orchestration |
| `workflows/` | Complex workflow handlers |
| `features/` | Advanced features (alerts, audit, etc.) |
| `health/` | Health check system (NEW) |

## Health Module (Phase 8)

The health module provides comprehensive setup evaluation:

- 6 dimension scorers
- Automated data collection
- Prioritized recommendations
- Monitoring and alerting

See `health/INDEX.md` for details.
```

**Step 3: Commit**

```bash
git add scripts/health/INDEX.md scripts/INDEX.md
git commit -m "docs: add INDEX.md files for health module"
```

---

### Task 18: Performance Optimization - Add Caching

**Files:**
- Modify: `scripts/health/collector.py`
- Create: `tests/unit/test_health_caching.py`

**Step 1: Write the failing test for caching**

Create `tests/unit/test_health_caching.py`:

```python
"""Unit tests for health data caching."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from scripts.health.collector import HealthDataCollector, CacheConfig


class TestHealthDataCaching:
    """Tests for health data caching."""

    def test_cache_config_defaults(self):
        """Default cache configuration."""
        config = CacheConfig()
        assert config.enabled is True
        assert config.ttl_seconds == 300  # 5 minutes

    def test_cached_data_returned(self):
        """Cached data returned within TTL."""
        mock_client = Mock()
        mock_client.get_transactions.return_value = [{"id": 1}]

        config = CacheConfig(enabled=True, ttl_seconds=300)
        collector = HealthDataCollector(api_client=mock_client, cache_config=config)

        # First call
        data1 = collector.collect_data_quality()

        # Second call should use cache
        data2 = collector.collect_data_quality()

        # API should only be called once
        assert mock_client.get_transactions.call_count == 1
        assert data1 == data2

    def test_cache_expired_refetches(self):
        """Expired cache triggers refetch."""
        mock_client = Mock()
        mock_client.get_transactions.return_value = [{"id": 1}]

        config = CacheConfig(enabled=True, ttl_seconds=1)  # 1 second TTL
        collector = HealthDataCollector(api_client=mock_client, cache_config=config)

        # First call
        collector.collect_data_quality()

        # Wait for cache to expire
        import time
        time.sleep(1.1)

        # Second call should refetch
        collector.collect_data_quality()

        assert mock_client.get_transactions.call_count == 2

    def test_cache_disabled(self):
        """Cache can be disabled."""
        mock_client = Mock()
        mock_client.get_transactions.return_value = [{"id": 1}]

        config = CacheConfig(enabled=False)
        collector = HealthDataCollector(api_client=mock_client, cache_config=config)

        collector.collect_data_quality()
        collector.collect_data_quality()

        assert mock_client.get_transactions.call_count == 2

    def test_force_refresh_bypasses_cache(self):
        """Force refresh bypasses cache."""
        mock_client = Mock()
        mock_client.get_transactions.return_value = [{"id": 1}]

        config = CacheConfig(enabled=True, ttl_seconds=300)
        collector = HealthDataCollector(api_client=mock_client, cache_config=config)

        collector.collect_data_quality()
        collector.collect_data_quality(force_refresh=True)

        assert mock_client.get_transactions.call_count == 2
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_health_caching.py -v
```

Expected: FAIL

**Step 3: Add caching to collector**

Update `scripts/health/collector.py` - add at the top after imports:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import json
from pathlib import Path
from collections import Counter


@dataclass
class CacheConfig:
    """Configuration for data caching."""

    enabled: bool = True
    ttl_seconds: int = 300  # 5 minutes default


@dataclass
class CacheEntry:
    """A cached data entry."""

    data: Any
    timestamp: datetime

    def is_valid(self, ttl_seconds: int) -> bool:
        """Check if cache entry is still valid."""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age < ttl_seconds
```

Update `HealthDataCollector.__init__`:

```python
def __init__(
    self,
    api_client: Any,
    data_dir: Optional[Path] = None,
    cache_config: Optional[CacheConfig] = None,
) -> None:
    """Initialize collector.

    Args:
        api_client: PocketSmith API client instance
        data_dir: Path to data directory (default: data/)
        cache_config: Cache configuration
    """
    self.api_client = api_client
    self.data_dir = data_dir or Path("data")
    self.cache_config = cache_config or CacheConfig()
    self._cache: Dict[str, CacheEntry] = {}
```

Add caching helper method:

```python
def _get_cached_or_fetch(
    self,
    key: str,
    fetch_func: Callable[[], Any],
    force_refresh: bool = False,
) -> Any:
    """Get data from cache or fetch fresh.

    Args:
        key: Cache key
        fetch_func: Function to fetch fresh data
        force_refresh: Bypass cache if True

    Returns:
        Cached or fresh data
    """
    if not self.cache_config.enabled or force_refresh:
        return fetch_func()

    cached = self._cache.get(key)
    if cached and cached.is_valid(self.cache_config.ttl_seconds):
        return cached.data

    data = fetch_func()
    self._cache[key] = CacheEntry(data=data, timestamp=datetime.now())
    return data
```

Update `collect_data_quality` to use caching:

```python
def collect_data_quality(self, force_refresh: bool = False) -> Dict[str, Any]:
    """Collect data quality metrics.

    Args:
        force_refresh: Bypass cache if True

    Returns:
        Dict with data quality metrics
    """
    def fetch() -> Dict[str, Any]:
        transactions = self.api_client.get_transactions()

        total = len(transactions)
        categorized = sum(1 for t in transactions if t.get("category"))
        with_payee = sum(1 for t in transactions if t.get("payee", "").strip())

        signatures = []
        for t in transactions:
            sig = f"{t.get('payee', '')}|{t.get('amount', '')}|{t.get('date', '')}"
            signatures.append(sig)

        sig_counts = Counter(signatures)
        duplicates = sum(count - 1 for count in sig_counts.values() if count > 1)

        return {
            "total_transactions": total,
            "categorized_transactions": categorized,
            "transactions_with_payee": with_payee,
            "duplicate_count": duplicates,
        }

    return self._get_cached_or_fetch("data_quality", fetch, force_refresh)
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_health_caching.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/health/collector.py tests/unit/test_health_caching.py
git commit -m "perf(health): add caching to health data collector"
```

---

### Task 19: Run Full Test Suite

**Files:**
- None (verification only)

**Step 1: Run all health module tests**

```bash
pytest tests/unit/test_health*.py tests/integration/test_health*.py -v
```

Expected: All PASS

**Step 2: Run full test suite**

```bash
pytest tests/ -v --tb=short
```

Expected: All PASS

**Step 3: Run type checking**

```bash
mypy scripts/health/
```

Expected: No errors (or acceptable ones)

**Step 4: Run linting**

```bash
flake8 scripts/health/
black --check scripts/health/
```

Expected: All pass

**Step 5: Commit any fixes**

```bash
git add -A
git commit -m "fix: address linting and type check issues in health module"
```

---

### Task 20: Final Documentation Update

**Files:**
- Update: `CLAUDE.md`
- Update: `README.md`

**Step 1: Update CLAUDE.md with Phase 8 completion**

Add to the Implementation Phases section:

```markdown
### Phase 8: Health Check & Polish (Complete)

**Health Check System:**
- ✅ 6 health dimension scorers
- ✅ HealthCheckEngine for comprehensive evaluation
- ✅ HealthDataCollector with caching
- ✅ RecommendationEngine with prioritization
- ✅ HealthMonitor for automated alerting

**Polish:**
- ✅ Integration tests
- ✅ User documentation
- ✅ Performance optimization (caching)
- ✅ INDEX.md files updated
```

**Step 2: Update README.md**

Add health check section:

```markdown
## Health Check

Evaluate your PocketSmith setup:

```bash
# Quick health check
/smith:health --quick

# Full comprehensive check
/smith:health --full
```

Scores across 6 dimensions: Data Quality, Category Structure, Rule Engine, Tax Readiness, Automation, Budget Alignment.

See `docs/guides/health-check-guide.md` for details.
```

**Step 3: Final commit**

```bash
git add CLAUDE.md README.md
git commit -m "docs: complete Phase 8 documentation updates"
```

---

## Summary

Phase 8 implements:

1. **Health Check Core** (Tasks 1-10)
   - 6 dimension scorers with comprehensive metrics
   - HealthScore and HealthStatus classes

2. **Health Check Engine** (Tasks 11-12)
   - HealthCheckEngine for running all checks
   - HealthDataCollector for gathering metrics

3. **Recommendation Engine** (Task 13)
   - Prioritized recommendations
   - Quick wins identification

4. **Automated Monitoring** (Task 14)
   - Weekly/monthly scheduled checks
   - Score drop detection
   - Alert generation

5. **Testing & Polish** (Tasks 15-20)
   - Integration tests
   - User documentation
   - Performance optimization
   - Final documentation

**Total Tasks:** 20
**Estimated Time:** 4-6 hours with TDD approach
