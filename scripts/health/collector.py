"""Health data collection from PocketSmith API.

This module collects health metrics from PocketSmith API data.
Follows PocketSmith API v2 OpenAPI specification for field names:
- Transaction: category (object), payee, amount, date, needs_review, status, labels, etc.
- Category: id, title, colour, children, parent_id, is_transfer, is_bill, roll_up, etc.
- Note: Category does NOT have transaction_count - must be calculated from transactions
- Note: Transaction does NOT have auto_categorized - must be tracked locally
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import Counter
import json
from pathlib import Path


class HealthDataCollector:
    """Collects data for health check scoring from various sources."""

    def __init__(self, api_client: Any, user_id: int, data_dir: Optional[Path] = None) -> None:
        """Initialize collector.

        Args:
            api_client: PocketSmith API client instance
            user_id: PocketSmith user ID
            data_dir: Path to data directory (default: data/)
        """
        self.api_client = api_client
        self.user_id = user_id
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
        transactions = self.api_client.get_transactions(self.user_id)

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

        Note: PocketSmith API Category objects do NOT have a transaction_count field.
        We must calculate category usage by counting transactions per category.

        Returns:
            Dict with category structure metrics
        """
        # Fetch with flatten=True to include all child categories
        categories = self.api_client.get_categories(self.user_id, flatten=True)

        # Build set of category IDs that have transactions
        # API spec: Transaction.category is an object with 'id' field, not category_id
        transactions = self.api_client.get_transactions(self.user_id)
        categories_with_txns = self._get_categories_with_transactions(transactions)

        total = len(categories)
        with_transactions = sum(1 for c in categories if c.get("id") in categories_with_txns)
        root_count = sum(1 for c in categories if c.get("parent_id") is None)
        empty = total - with_transactions

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

    def _get_categories_with_transactions(self, transactions: List[Dict]) -> Set[int]:
        """Extract set of category IDs that have at least one transaction.

        API spec: Transaction.category is a nested Category object (not category_id).
        The category object has 'id', 'title', 'colour', 'parent_id', etc.

        Args:
            transactions: List of transaction objects from API

        Returns:
            Set of category IDs that have transactions
        """
        category_ids: Set[int] = set()
        for t in transactions:
            # API returns 'category' as nested object, not 'category_id'
            category = t.get("category")
            if category and isinstance(category, dict):
                cat_id = category.get("id")
                if cat_id:
                    category_ids.add(cat_id)
        return category_ids

    def collect_rule_engine(self) -> Dict[str, Any]:
        """Collect rule engine metrics.

        Note: PocketSmith API Transaction objects do NOT have an 'auto_categorized' field.
        Auto-categorization tracking must be done locally via rule metadata.

        Returns:
            Dict with rule engine metrics
        """
        # Load local category and label rules (we only use local rules now)
        category_rules = self._load_json("category_rules.json", [])
        label_rules = self._load_json("label_rules.json", [])

        total_rules = len(category_rules) + len(label_rules)
        active_cat_rules = sum(1 for r in category_rules if r.get("active", True))
        active_label_rules = sum(1 for r in label_rules if r.get("active", True))
        active_rules = active_cat_rules + active_label_rules

        # Calculate metrics from rule metadata
        rule_metadata = self._load_json("rule_metadata.json", {})

        total_applied = sum(r.get("applied", 0) for r in category_rules + label_rules)
        total_overrides = sum(r.get("user_overrides", 0) for r in category_rules + label_rules)

        # Get transactions for coverage calculation
        # API spec: Transaction does NOT have 'auto_categorized' field
        # Instead, we calculate coverage from local rule application stats
        transactions = self.api_client.get_transactions(self.user_id)
        total_txn = len(transactions)

        # Calculate coverage from locally tracked rule applications
        # If no rule metadata, estimate from categorized transactions
        auto_categorized = rule_metadata.get("total_auto_categorized", 0)
        if auto_categorized == 0 and total_rules > 0:
            # Fallback: estimate from rule application counts
            auto_categorized = total_applied

        coverage = auto_categorized / total_txn if total_txn > 0 else 0
        # Cap coverage at 1.0 (can't be more than 100%)
        coverage = min(1.0, coverage)

        accuracy = (
            total_applied / (total_applied + total_overrides)
            if (total_applied + total_overrides) > 0
            else 1.0
        )

        # Count conflicts and stale rules
        conflicts = rule_metadata.get("conflicts", 0)
        stale_days = 90
        all_rules = category_rules + label_rules
        stale = sum(1 for r in all_rules if self._days_since(r.get("last_used")) > stale_days)

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
        transactions = self.api_client.get_transactions(self.user_id)
        deductible = sum(1 for t in transactions if self._is_deductible(t))
        substantiated = substantiation.get("substantiated_count", 0)

        # ATO coverage (flatten to include all child categories)
        # API spec: Category does NOT have transaction_count - calculate from transactions
        categories = self.api_client.get_categories(self.user_id, flatten=True)
        categories_with_txns = self._get_categories_with_transactions(transactions)
        cats_used = sum(1 for c in categories if c.get("id") in categories_with_txns)
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

        # Rule auto-apply rate (category and label rules)
        category_rules = self._load_json("category_rules.json", [])
        label_rules = self._load_json("label_rules.json", [])
        all_rules = category_rules + label_rules
        auto_apply_rules = sum(1 for r in all_rules if not r.get("requires_approval", True))
        total_rules = len(all_rules)
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
        """Check if transaction is potentially deductible.

        API spec: Category uses 'title' field (not 'name').
        """
        category = transaction.get("category", {})
        if not category:
            return False
        # Simplified check - in real implementation, use ATO mappings
        # API spec: Category field is 'title', not 'name'
        cat_title = category.get("title", "").lower()
        deductible_keywords = [
            "work",
            "business",
            "office",
            "professional",
            "education",
        ]
        return any(kw in cat_title for kw in deductible_keywords)

    def _days_since(self, date_str: Optional[str]) -> int:
        """Calculate days since a date string."""
        if not date_str:
            return 999
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return (datetime.now(date.tzinfo) - date).days
        except (ValueError, TypeError):
            return 999
