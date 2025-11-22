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
                category_rule = self._parse_category_rule(rule_dict)
                self.category_rules.append(category_rule)
            elif rule_type == "label":
                label_rule = self._parse_label_rule(rule_dict)
                self.label_rules.append(label_rule)

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
