"""Discovery analyzer for PocketSmith account structure."""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass
class TemplateRecommendation:
    """Recommended template combination for composable template system."""

    primary: str  # E.g., "payg-employee" or "sole-trader"
    living: str  # E.g., "single", "shared-hybrid", "separated-parents"
    additional: List[str]  # E.g., ["property-investor", "share-investor"]


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
    recommendation: TemplateRecommendation


class DiscoveryAnalyzer:
    """Analyzer for PocketSmith account discovery."""

    def __init__(self, client: Optional[Any] = None) -> None:
        """Initialize with optional PocketSmith client.

        Args:
            client: PocketSmithClient instance (or None for testing)
        """
        self.client = client

    def _fetch_accounts(self, user_id: int) -> List[AccountSummary]:
        """Fetch account summaries from PocketSmith.

        Args:
            user_id: PocketSmith user ID

        Returns:
            List of AccountSummary objects

        Raises:
            ValueError: If client is not configured
        """
        if self.client is None:
            raise ValueError("Client must be configured to fetch accounts")

        accounts_data = self.client.get_transaction_accounts(user_id)
        summaries = []

        for acc in accounts_data:
            # Transaction accounts have 'name' not 'title'
            # And they may have an 'institution' object or just be standalone
            institution_name = "Unknown"
            if "institution" in acc and acc["institution"]:
                institution_name = acc["institution"].get("title", "Unknown")

            summary = AccountSummary(
                id=acc["id"],
                name=acc.get("name", "Unknown"),
                institution=institution_name,
                transaction_count=0,  # Will be populated by transaction fetch
                uncategorized_count=0,
            )
            summaries.append(summary)

        return summaries

    def _fetch_categories(self, user_id: int) -> List[CategorySummary]:
        """Fetch category summaries from PocketSmith.

        Args:
            user_id: PocketSmith user ID

        Returns:
            List of CategorySummary objects

        Raises:
            ValueError: If client is not configured
        """
        if self.client is None:
            raise ValueError("Client must be configured to fetch categories")

        categories_data = self.client.get_categories(user_id)
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

    def _fetch_transaction_summary(self, user_id: int) -> TransactionSummary:
        """Fetch transaction summary statistics.

        Args:
            user_id: PocketSmith user ID

        Returns:
            TransactionSummary object

        Raises:
            ValueError: If client is not configured
        """
        if self.client is None:
            raise ValueError("Client must be configured to fetch transactions")

        transactions = self.client.get_transactions(user_id)

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

    def _recommend_template(
        self,
        accounts: List[AccountSummary],
        categories: List[CategorySummary],
    ) -> TemplateRecommendation:
        """Recommend templates based on account and category structure.

        Uses the composable template system with three layers:
        - Primary: Income structure (payg-employee, sole-trader, small-business)
        - Living: Living arrangement (single, shared-hybrid, separated-parents)
        - Additional: Extra income sources (property-investor, share-investor)

        Args:
            accounts: List of account summaries
            categories: List of category summaries

        Returns:
            TemplateRecommendation with primary, living, and additional templates
        """
        # Extract category titles for pattern matching
        category_titles = {cat.title.lower() for cat in categories}
        account_names = {acc.name.lower() for acc in accounts}

        # Determine PRIMARY template (income structure)
        business_indicators = {"business expenses", "abn", "gst", "bas"}
        has_business = any(
            indicator in title for title in category_titles for indicator in business_indicators
        )
        business_accounts = any("business" in name for name in account_names)

        if has_business or business_accounts:
            primary = "sole-trader"  # Default to sole trader for business income
        else:
            primary = "payg-employee"  # Default to PAYG employee for salary/wages

        # Determine LIVING template (household arrangement)
        separated_indicators = {
            "child support",
            "kids activities",
            "kids",
            "children",
            "child care",
            "school fees",
            "custody",
        }
        has_separated = any(
            indicator in title for title in category_titles for indicator in separated_indicators
        )

        shared_indicators = {"shared", "joint", "household", "split"}
        has_shared = any(
            indicator in title for title in category_titles for indicator in shared_indicators
        )
        joint_accounts = any("joint" in name or "shared" in name for name in account_names)

        if has_separated:
            living = "separated-parents"
        elif has_shared or (joint_accounts and len(accounts) > 1):
            living = "shared-hybrid"
        else:
            living = "single"

        # Determine ADDITIONAL templates (extra income sources)
        additional = []

        # Check for property investment
        property_indicators = {"rental income", "property expenses", "council rates"}
        has_property = any(
            indicator in title for title in category_titles for indicator in property_indicators
        )
        if has_property:
            additional.append("property-investor")

        # Check for share/ETF investment
        investment_indicators = {
            "investment",
            "dividends",
            "capital gains",
            "cgt",
            "shares",
            "etf",
            "crypto",
        }
        has_investments = any(
            indicator in title for title in category_titles for indicator in investment_indicators
        )
        if has_investments:
            additional.append("share-investor")

        return TemplateRecommendation(primary=primary, living=living, additional=additional)

    def analyze(self, include_health_check: bool = False) -> DiscoveryReport:
        """Run complete discovery analysis.

        Args:
            include_health_check: Whether to run baseline health check

        Returns:
            DiscoveryReport with all analysis results

        Raises:
            ValueError: If client is not configured
        """
        if self.client is None:
            raise ValueError("Client must be configured to run analysis")

        # Fetch user info
        user_data = self.client.get_user()
        user_id = user_data["id"]
        user_email = user_data.get("login", "unknown")

        # Fetch all data
        accounts = self._fetch_accounts(user_id)
        categories = self._fetch_categories(user_id)
        transactions = self._fetch_transaction_summary(user_id)

        # Update account transaction counts
        for account in accounts:
            account.transaction_count = transactions.by_account.get(account.id, 0)
            # Uncategorized count would need separate query - simplified for now

        # Update category transaction counts
        # (Would need to count from transactions - simplified for now)

        # Get template recommendation
        recommendation = self._recommend_template(accounts, categories)

        # Optional: Run baseline health check
        baseline_health_score = None
        if include_health_check:
            from scripts.onboarding.baseline_health import BaselineHealthChecker

            checker = BaselineHealthChecker(client=self.client)
            baseline_health_score = checker.run_baseline_check()

        return DiscoveryReport(
            user_id=user_id,
            user_email=user_email,
            accounts=accounts,
            categories=categories,
            transactions=transactions,
            baseline_health_score=baseline_health_score,
            recommendation=recommendation,
        )


def main() -> None:
    """CLI entry point for discovery analysis."""
    import sys
    import os
    from pathlib import Path
    from scripts.core.api_client import PocketSmithClient

    # Load .env file (plugin-aware)
    # When run as a plugin, USER_CWD environment variable should point to user's directory
    try:
        from dotenv import load_dotenv

        user_dir = os.getenv("USER_CWD", os.getcwd())
        env_path = Path(user_dir) / ".env"

        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded configuration from: {env_path}")
        else:
            # Fallback to searching from current directory
            load_dotenv()
    except ImportError:
        # python-dotenv not available - rely on environment variables
        pass

    print("=" * 70)
    print("Agent Smith - PocketSmith Discovery Analysis")
    print("=" * 70)
    print()

    try:
        client = PocketSmithClient()
        analyzer = DiscoveryAnalyzer(client=client)

        print("Analyzing your PocketSmith account...")
        print()

        report = analyzer.analyze(include_health_check=False)

        # Print report
        print(f"Connected as: {report.user_email}")
        print(f"User ID: {report.user_id}")
        print()

        print(f"Accounts ({len(report.accounts)}):")
        for acc in report.accounts:
            print(f"  - {acc.name} ({acc.institution})")
            print(f"    Transactions: {acc.transaction_count}")
        print()

        print(f"Categories ({len(report.categories)}):")
        # Show top 10 by title
        for cat in sorted(report.categories, key=lambda c: c.title)[:10]:
            parent_info = f" (under {cat.parent_title})" if cat.parent_title else ""
            print(f"  - {cat.title}{parent_info}")
        if len(report.categories) > 10:
            print(f"  ... and {len(report.categories) - 10} more")
        print()

        print("Transactions:")
        print(f"  Total: {report.transactions.total_count}")
        if report.transactions.total_count > 0:
            uncategorized_pct = (
                report.transactions.uncategorized_count / report.transactions.total_count * 100
            )
            uncategorized_msg = (
                f"  Uncategorized: {report.transactions.uncategorized_count} "
                f"({uncategorized_pct:.1f}%)"
            )
            print(uncategorized_msg)
        else:
            print(f"  Uncategorized: {report.transactions.uncategorized_count}")
        if report.transactions.date_range_start:
            date_msg = (
                f"  Date Range: {report.transactions.date_range_start} to "
                f"{report.transactions.date_range_end}"
            )
            print(date_msg)
        print()

        print(f"Recommended Template: {report.recommendation}")
        print()

        print("=" * 70)
        print("Discovery complete!")
        print()
        print("Next steps:")
        print("1. Run: uv run python scripts/setup/template_selector.py")
        print(f"2. Select template: {report.recommendation}")
        print("3. Customize data/rules.yaml for your needs")

    except Exception as e:
        print(f"Error during discovery: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
