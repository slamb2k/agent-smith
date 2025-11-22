"""Discovery analyzer for PocketSmith account structure."""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional


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

    def __init__(self, client: Optional[Any] = None) -> None:
        """Initialize with optional PocketSmith client.

        Args:
            client: PocketSmithClient instance (or None for testing)
        """
        self.client = client

    def _fetch_accounts(self) -> List[AccountSummary]:
        """Fetch account summaries from PocketSmith.

        Returns:
            List of AccountSummary objects

        Raises:
            ValueError: If client is not configured
        """
        if self.client is None:
            raise ValueError("Client must be configured to fetch accounts")

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

        Raises:
            ValueError: If client is not configured
        """
        if self.client is None:
            raise ValueError("Client must be configured to fetch categories")

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

        Raises:
            ValueError: If client is not configured
        """
        if self.client is None:
            raise ValueError("Client must be configured to fetch transactions")

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
