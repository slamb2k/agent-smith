"""Hybrid rule engine for transaction categorization."""

import uuid
import re
import json
import logging
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Rule type enum."""

    LOCAL = "local"
    PLATFORM = "platform"
    SESSION = "session"


class IntelligenceMode(Enum):
    """Intelligence mode for rule application."""

    CONSERVATIVE = "conservative"
    SMART = "smart"
    AGGRESSIVE = "aggressive"


@dataclass
class Rule:
    """Represents a categorization rule."""

    name: str
    payee_regex: str
    category_id: int
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_type: RuleType = RuleType.LOCAL
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    account_ids: List[int] = field(default_factory=list)
    excludes: List[str] = field(default_factory=list)
    confidence: int = 100
    priority: int = 100
    requires_approval: bool = False
    tags: List[str] = field(default_factory=list)

    # Metadata
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "user"
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())

    # Performance tracking
    matches: int = 0
    applied: int = 0
    user_overrides: int = 0
    last_used: Optional[str] = None

    def match_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Check if rule matches transaction.

        Args:
            transaction: Transaction dict with payee, amount, etc.

        Returns:
            True if rule matches, False otherwise
        """
        payee = transaction.get("payee", "")

        # Check payee regex
        if not re.match(self.payee_regex, payee):
            return False

        # Check exclusions
        for exclude_pattern in self.excludes:
            if re.match(exclude_pattern, payee):
                return False

        # Check amount range
        if self.amount_min is not None or self.amount_max is not None:
            amount_str = transaction.get("amount", "0")
            amount = abs(float(amount_str))

            if self.amount_min is not None and amount < self.amount_min:
                return False
            if self.amount_max is not None and amount > self.amount_max:
                return False

        # Check account filter
        if self.account_ids:
            account_id = transaction.get("transaction_account", {}).get("id")
            if account_id not in self.account_ids:
                return False

        return True


class RuleEngine:
    """Hybrid rule engine managing local and platform rules."""

    def __init__(self, rules_file: Optional[Path] = None):
        """Initialize rule engine.

        Args:
            rules_file: Path to local rules JSON file
        """
        if rules_file is None:
            project_root = Path(__file__).parent.parent.parent
            rules_file = project_root / "data" / "local_rules.json"

        self.rules_file = Path(rules_file)
        self.rules: List[Rule] = []
        self.intelligence_mode = IntelligenceMode.SMART

        if self.rules_file.exists():
            self.load_rules()

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the engine.

        Args:
            rule: Rule to add
        """
        self.rules.append(rule)
        logger.info(f"Added rule: {rule.name} (ID: {rule.rule_id})")

    def save_rules(self) -> None:
        """Save rules to JSON file."""
        self.rules_file.parent.mkdir(parents=True, exist_ok=True)

        rules_data = []
        for rule in self.rules:
            rule_dict = asdict(rule)
            # Convert RuleType enum to string
            rule_dict["rule_type"] = rule.rule_type.value
            rules_data.append(rule_dict)

        with open(self.rules_file, "w") as f:
            json.dump(rules_data, f, indent=2)

        logger.info(f"Saved {len(self.rules)} rules to {self.rules_file}")

    def load_rules(self) -> None:
        """Load rules from JSON file."""
        if not self.rules_file.exists():
            logger.debug(f"Rules file not found: {self.rules_file}")
            return

        with open(self.rules_file) as f:
            rules_data = json.load(f)

        self.rules = []
        for rule_dict in rules_data:
            # Convert rule_type string back to enum
            rule_dict["rule_type"] = RuleType(rule_dict["rule_type"])
            rule = Rule(**rule_dict)
            self.rules.append(rule)

        logger.info(f"Loaded {len(self.rules)} rules from {self.rules_file}")

    def should_auto_apply(self, rule: Rule) -> bool:
        """Determine if rule should be auto-applied based on intelligence mode.

        Args:
            rule: Rule to check

        Returns:
            True if should auto-apply, False otherwise
        """
        if rule.requires_approval:
            return False

        if self.intelligence_mode == IntelligenceMode.CONSERVATIVE:
            return False
        elif self.intelligence_mode == IntelligenceMode.SMART:
            return rule.confidence >= 90
        else:  # AGGRESSIVE
            return rule.confidence >= 80

    def should_ask_approval(self, rule: Rule) -> bool:
        """Determine if should ask for approval based on intelligence mode.

        Args:
            rule: Rule to check

        Returns:
            True if should ask for approval, False if should skip
        """
        if self.intelligence_mode == IntelligenceMode.CONSERVATIVE:
            return True
        elif self.intelligence_mode == IntelligenceMode.SMART:
            return 70 <= rule.confidence < 90
        else:  # AGGRESSIVE
            return 50 <= rule.confidence < 80

    def find_matching_rules(self, transaction: Dict[str, Any]) -> List[Rule]:
        """Find all rules that match a transaction.

        Args:
            transaction: Transaction dict to match against

        Returns:
            List of matching rules sorted by priority (highest first)
        """
        matches = [rule for rule in self.rules if rule.match_transaction(transaction)]
        # Sort by priority descending
        matches.sort(key=lambda r: r.priority, reverse=True)
        return matches

    def find_best_match(self, transaction: Dict[str, Any]) -> Optional[Rule]:
        """Find the best matching rule for a transaction.

        Args:
            transaction: Transaction dict to match against

        Returns:
            Best matching rule (highest priority) or None
        """
        matches = self.find_matching_rules(transaction)
        return matches[0] if matches else None
