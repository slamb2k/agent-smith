"""Health data collection from PocketSmith API."""

from typing import Dict, List, Any, Optional
from datetime import datetime
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

        total_applied = sum(r.get("applied", 0) for r in local_rules)
        total_overrides = sum(r.get("user_overrides", 0) for r in local_rules)

        # Get transactions for coverage calculation
        transactions = self.api_client.get_transactions()
        total_txn = len(transactions)
        auto_categorized = sum(1 for t in transactions if t.get("auto_categorized", False))

        coverage = auto_categorized / total_txn if total_txn > 0 else 0
        accuracy = (
            total_applied / (total_applied + total_overrides)
            if (total_applied + total_overrides) > 0
            else 1.0
        )

        # Count conflicts and stale rules
        conflicts = rule_metadata.get("conflicts", 0)
        stale_days = 90
        stale = sum(1 for r in local_rules if self._days_since(r.get("last_used")) > stale_days)

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
        budgets = self.api_client.get_budgets() if hasattr(self.api_client, "get_budgets") else []

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
