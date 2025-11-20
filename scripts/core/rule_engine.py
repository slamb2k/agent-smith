"""Hybrid rule engine for transaction categorization."""

import uuid
import re
import logging
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Rule type enum."""

    LOCAL = "local"
    PLATFORM = "platform"
    SESSION = "session"


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

        if self.rules_file.exists():
            self.load_rules()

    def load_rules(self) -> None:
        """Load rules from JSON file."""
        # Stub implementation - will be implemented in Task 2
        pass
