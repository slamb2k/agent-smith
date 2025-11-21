"""Health score definitions and base classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


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
            score: Health score (0-100). Values outside range are clamped.

        Returns:
            Corresponding HealthStatus
        """
        # Clamp score to valid range
        score = max(0, min(100, score))
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
            recommendations.append("Run /agent-smith-categorize to categorize transactions")

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
            issues.append(
                f"{root_count} root-level categories (ideal: {self.IDEAL_ROOT_CATEGORIES})"
            )
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
            issues.append(
                f"Rule accuracy at {accuracy*100:.0f}% ({override_rate:.0f}% override rate)"
            )
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
            issues.append(
                f"{missing} deductible transactions lack substantiation ({(1-sub_rate)*100:.0f}%)"
            )
            if days_to_eofy <= 60:
                recommendations.append(
                    "URGENT: Gather receipts for deductible expenses before EOFY"
                )
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
            recommendations.insert(
                0, f"Only {days_to_eofy} days to EOFY - prioritize tax preparation"
            )

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
        features_enabled: float = 0
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


# Placeholder exports for __init__.py imports
# These will be implemented in subsequent tasks
BudgetAlignmentScorer = None
