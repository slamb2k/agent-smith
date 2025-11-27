"""Discovery analyzer for PocketSmith account structure."""

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass
class AccountClassification:
    """Classification of an account type."""

    account_id: int
    account_name: str
    institution: str
    account_type: str  # "household_shared", "parenting_shared", "individual"
    confidence: float  # 0.0-1.0
    indicators: List[str]  # Keywords/patterns that triggered classification


@dataclass
class NameSuggestion:
    """Suggested names for a shared context."""

    context: str  # "household_shared" or "parenting_shared"
    person_1: Optional[str]
    person_2: Optional[str]
    confidence: float  # 0.0-1.0
    source: str  # "account_name", "category_names", "transaction_notes"


@dataclass
class TemplateRecommendation:
    """Recommended template combination for composable template system."""

    primary: str  # E.g., "payg-employee" or "sole-trader"
    living: str  # E.g., "single", "shared-hybrid", "separated-parents"
    additional: List[str]  # E.g., ["property-investor", "share-investor"]
    name_suggestions: Dict[str, NameSuggestion] = field(default_factory=dict)  # Context -> names


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
    account_classifications: List[AccountClassification] = field(default_factory=list)


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

        Uses efficient API calls:
        - Total count from X-Total-Count header (1 API call with minimal data)
        - Uncategorized count from X-Total-Count header with filter (1 API call)
        - Date range from first/last transactions (2 API calls)
        - Per-account counts from account transaction counts

        Args:
            user_id: PocketSmith user ID

        Returns:
            TransactionSummary object

        Raises:
            ValueError: If client is not configured
        """
        if self.client is None:
            raise ValueError("Client must be configured to fetch transactions")

        # Get total count efficiently from header
        total_count = self.client.get_transaction_count(user_id)

        # Get uncategorized count efficiently from header
        uncategorized_count = self.client.get_transaction_count(user_id, uncategorised=True)

        # Get date range from first and last transactions (minimal fetch)
        date_range_start = None
        date_range_end = None

        if total_count > 0:
            # Get newest transaction (first page, sorted by date descending - default)
            # Note: PocketSmith default sort is newest first, so page 1 = newest
            # API requires per_page >= 10
            newest_txns = self.client.get_transactions(user_id, page=1, per_page=10)
            if newest_txns and newest_txns[0].get("date"):
                date_range_end = datetime.fromisoformat(
                    newest_txns[0]["date"].replace("Z", "+00:00")
                ).date()

            # Calculate last page to get oldest transactions
            last_page = (total_count + 99) // 100  # Ceiling division
            oldest_txns = self.client.get_transactions(user_id, page=last_page, per_page=100)
            if oldest_txns:
                # Last item on last page is oldest
                oldest_txn = oldest_txns[-1]
                if oldest_txn.get("date"):
                    date_range_start = datetime.fromisoformat(
                        oldest_txn["date"].replace("Z", "+00:00")
                    ).date()

        # Per-account counts - will be populated from account data if available
        by_account: Dict[int, int] = {}

        return TransactionSummary(
            total_count=total_count,
            uncategorized_count=uncategorized_count,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            by_account=by_account,
        )

    def _parse_names_from_text(self, text: str) -> List[str]:
        """Extract person names from text using regex patterns.

        Args:
            text: Text to parse for names

        Returns:
            List of extracted names (maximum 2)
        """
        # Pattern 1: "Name1 & Name2" or "Name1 and Name2"
        pattern1 = r"([A-Z][a-z]+)\s+(?:&|and)\s+([A-Z][a-z]+)"
        match = re.search(pattern1, text)
        if match:
            return [match.group(1), match.group(2)]

        # Pattern 2: "Name1's" possessive form
        pattern2 = r"([A-Z][a-z]+)'s"
        matches = re.findall(pattern2, text)
        if matches:
            return list(set(matches))[:2]

        # Pattern 3: Capitalized words (less confident)
        pattern3 = r"\b([A-Z][a-z]{2,})\b"
        matches = re.findall(pattern3, text)
        # Filter out common account/category words
        common_words = {
            "Account",
            "Bills",
            "Shared",
            "Joint",
            "Kids",
            "Children",
            "Bank",
            "Card",
            "Savings",
            "Checking",
            "Credit",
            "Debit",
        }
        names = [m for m in matches if m not in common_words]

        return names[:2]

    def _extract_names_from_account(
        self,
        account: AccountSummary,
        transactions: List[Dict[str, Any]],
        categories: List[CategorySummary],
    ) -> Optional[NameSuggestion]:
        """Extract names from account-specific data.

        Args:
            account: Account to analyze
            transactions: All transactions (will filter to this account)
            categories: All categories

        Returns:
            NameSuggestion or None if no names found
        """
        # Strategy 1: Try account name first
        names_from_account = self._parse_names_from_text(account.name)
        if len(names_from_account) == 2:
            return NameSuggestion(
                context="",  # Will be set by caller
                person_1=names_from_account[0],
                person_2=names_from_account[1],
                confidence=0.9,
                source="account_name",
            )
        elif len(names_from_account) == 1:
            return NameSuggestion(
                context="",
                person_1=names_from_account[0],
                person_2=None,
                confidence=0.7,
                source="account_name",
            )

        # Strategy 2: Try category names used in this account
        account_txns = [
            t for t in transactions if t.get("transaction_account", {}).get("id") == account.id
        ]

        account_category_ids = {
            t.get("category", {}).get("id") for t in account_txns if t.get("category")
        }

        account_categories = [cat for cat in categories if cat.id in account_category_ids]

        for cat in account_categories:
            names_from_category = self._parse_names_from_text(cat.title)
            if len(names_from_category) >= 1:
                return NameSuggestion(
                    context="",
                    person_1=names_from_category[0],
                    person_2=names_from_category[1] if len(names_from_category) > 1 else None,
                    confidence=0.6,
                    source="category_names",
                )

        # Strategy 3: Try transaction notes (if available)
        # Note: This is optional and depends on transactions having notes
        for txn in account_txns[:50]:  # Check first 50 transactions
            if "note" in txn and txn["note"]:
                names_from_note = self._parse_names_from_text(txn["note"])
                if len(names_from_note) >= 1:
                    return NameSuggestion(
                        context="",
                        person_1=names_from_note[0],
                        person_2=names_from_note[1] if len(names_from_note) > 1 else None,
                        confidence=0.4,
                        source="transaction_notes",
                    )

        return None

    def _classify_accounts(
        self,
        accounts: List[AccountSummary],
        transactions: List[Dict[str, Any]],
        categories: List[CategorySummary],
    ) -> List[AccountClassification]:
        """Classify each account as household-shared, parenting-shared, or individual.

        Args:
            accounts: List of account summaries
            transactions: All transactions
            categories: All categories

        Returns:
            List of AccountClassification objects
        """
        classifications = []

        for account in accounts:
            account_name_lower = account.name.lower()

            # Get transactions for THIS account only
            account_txns = [
                t for t in transactions if t.get("transaction_account", {}).get("id") == account.id
            ]

            # Extract categories used in THIS account
            account_category_ids = {
                t.get("category", {}).get("id") for t in account_txns if t.get("category")
            }

            account_category_titles = {
                cat.title.lower() for cat in categories if cat.id in account_category_ids
            }

            # Classification logic
            household_indicators = {"shared", "joint", "household", "bills", "house"}
            parenting_indicators = {
                "kids",
                "children",
                "child",
                "custody",
                "child support",
                "parenting",
                "school",
            }

            # Check account name
            household_score = sum(1.0 for ind in household_indicators if ind in account_name_lower)
            parenting_score = sum(1.0 for ind in parenting_indicators if ind in account_name_lower)

            # Check categories (with lower weight)
            household_score += (
                sum(
                    1.0
                    for ind in household_indicators
                    if any(ind in cat for cat in account_category_titles)
                )
                * 0.5
            )
            parenting_score += (
                sum(
                    1.0
                    for ind in parenting_indicators
                    if any(ind in cat for cat in account_category_titles)
                )
                * 0.5
            )

            # Determine account type
            indicators_found = []
            if household_score > parenting_score and household_score > 0:
                account_type = "household_shared"
                confidence = min(household_score / 3.0, 1.0)
                indicators_found = [
                    ind for ind in household_indicators if ind in account_name_lower
                ]
            elif parenting_score > 0:
                account_type = "parenting_shared"
                confidence = min(parenting_score / 3.0, 1.0)
                indicators_found = [
                    ind for ind in parenting_indicators if ind in account_name_lower
                ]
            else:
                account_type = "individual"
                confidence = 0.8
                indicators_found = ["no shared indicators"]

            classifications.append(
                AccountClassification(
                    account_id=account.id,
                    account_name=account.name,
                    institution=account.institution,
                    account_type=account_type,
                    confidence=confidence,
                    indicators=indicators_found,
                )
            )

        return classifications

    def _recommend_template(
        self,
        accounts: List[AccountSummary],
        categories: List[CategorySummary],
        transactions: List[Dict[str, Any]],
        account_classifications: List[AccountClassification],
    ) -> TemplateRecommendation:
        """Recommend templates based on account and category structure.

        Uses the composable template system with three layers:
        - Primary: Income structure (payg-employee, sole-trader, small-business)
        - Living: Living arrangement (single, shared-hybrid, separated-parents)
        - Additional: Extra income sources (property-investor, share-investor)

        Args:
            accounts: List of account summaries
            categories: List of category summaries
            transactions: All transactions
            account_classifications: Account classification results

        Returns:
            TemplateRecommendation with primary, living, additional, and name_suggestions
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

        # Extract names from classified accounts
        name_suggestions: Dict[str, NameSuggestion] = {}

        # Try to find household shared account with names
        household_accounts = [
            acc for acc in account_classifications if acc.account_type == "household_shared"
        ]
        if household_accounts:
            # Sort by confidence and try highest confidence first
            household_accounts.sort(key=lambda x: x.confidence, reverse=True)
            for classified_acc in household_accounts:
                # Find the AccountSummary object
                account_summary = next(
                    (a for a in accounts if a.id == classified_acc.account_id), None
                )
                if account_summary:
                    suggestion = self._extract_names_from_account(
                        account_summary, transactions, categories
                    )
                    if suggestion:
                        suggestion.context = "household_shared"
                        name_suggestions["household_shared"] = suggestion
                        break

        # Try to find parenting shared account with names
        parenting_accounts = [
            acc for acc in account_classifications if acc.account_type == "parenting_shared"
        ]
        if parenting_accounts:
            # Sort by confidence and try highest confidence first
            parenting_accounts.sort(key=lambda x: x.confidence, reverse=True)
            for classified_acc in parenting_accounts:
                # Find the AccountSummary object
                account_summary = next(
                    (a for a in accounts if a.id == classified_acc.account_id), None
                )
                if account_summary:
                    suggestion = self._extract_names_from_account(
                        account_summary, transactions, categories
                    )
                    if suggestion:
                        suggestion.context = "parenting_shared"
                        name_suggestions["parenting_shared"] = suggestion
                        break

        return TemplateRecommendation(
            primary=primary,
            living=living,
            additional=additional,
            name_suggestions=name_suggestions,
        )

    def analyze(self, include_health_check: bool = False) -> DiscoveryReport:
        """Run complete discovery analysis.

        Uses efficient API calls to minimize data transfer:
        - Transaction counts from headers (not full fetches)
        - Sample transactions for pattern analysis (200 max)
        - Per-account counts via efficient count endpoint

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
        transaction_summary = self._fetch_transaction_summary(user_id)

        # Fetch sample of recent transactions for pattern analysis (max 200)
        # This is sufficient for classification and name detection
        sample_transactions: List[Dict[str, Any]] = []
        sample_transactions.extend(self.client.get_transactions(user_id, page=1, per_page=100))
        if transaction_summary.total_count > 100:
            sample_transactions.extend(self.client.get_transactions(user_id, page=2, per_page=100))

        # Estimate per-account transaction counts from sample data
        # Note: PocketSmith API doesn't support per-account counts via headers
        # so we use the sample transactions to estimate distribution
        for account in accounts:
            account.transaction_count = sum(
                1
                for txn in sample_transactions
                if txn.get("transaction_account", {}).get("id") == account.id
            )

        # Classify accounts using sample transactions
        account_classifications = self._classify_accounts(accounts, sample_transactions, categories)

        # Get template recommendation
        recommendation = self._recommend_template(
            accounts, categories, sample_transactions, account_classifications
        )

        # Optional: Run baseline health check
        baseline_health_score = None
        if include_health_check:
            from scripts.onboarding.baseline_health import BaselineHealthChecker

            checker = BaselineHealthChecker(client=self.client, user_id=user_id)
            baseline_health_score = checker.run_baseline_check()

        return DiscoveryReport(
            user_id=user_id,
            user_email=user_email,
            accounts=accounts,
            categories=categories,
            transactions=transaction_summary,
            baseline_health_score=baseline_health_score,
            recommendation=recommendation,
            account_classifications=account_classifications,
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

        # Account Classifications
        if report.account_classifications:
            household_accounts = [
                acc
                for acc in report.account_classifications
                if acc.account_type == "household_shared"
            ]
            parenting_accounts = [
                acc
                for acc in report.account_classifications
                if acc.account_type == "parenting_shared"
            ]

            if household_accounts or parenting_accounts:
                print("Account Classifications:")
                print()

            if household_accounts:
                print("  Household Shared Accounts:")
                sorted_household = sorted(
                    household_accounts, key=lambda x: x.confidence, reverse=True
                )
                classified_acc: AccountClassification
                for classified_acc in sorted_household:
                    print(f"    • {classified_acc.account_name} ({classified_acc.institution})")
                    print(f"      Confidence: {classified_acc.confidence * 100:.0f}%")
                    print(f"      Indicators: {', '.join(classified_acc.indicators)}")
                print()

            if parenting_accounts:
                print("  Parenting Shared Accounts:")
                sorted_parenting = sorted(
                    parenting_accounts, key=lambda x: x.confidence, reverse=True
                )
                acc_p: AccountClassification
                for acc_p in sorted_parenting:
                    print(f"    • {acc_p.account_name} ({acc_p.institution})")
                    print(f"      Confidence: {acc_p.confidence * 100:.0f}%")
                    print(f"      Indicators: {', '.join(acc_p.indicators)}")
                print()

        # Name Suggestions
        if report.recommendation.name_suggestions:
            print("Name Suggestions:")
            for context, suggestion in report.recommendation.name_suggestions.items():
                context_label = "Household" if context == "household_shared" else "Parenting"
                names: str
                if suggestion.person_2:
                    names = f"{suggestion.person_1} and {suggestion.person_2}"
                else:
                    names = suggestion.person_1 or "Unknown"
                print(f"  {context_label}: {names}")
                confidence_pct = f"{suggestion.confidence * 100:.0f}%"
                print(f"    Source: {suggestion.source} (confidence: {confidence_pct})")
            print()

        print("Recommended Template:")
        print(f"  Primary: {report.recommendation.primary}")
        print(f"  Living: {report.recommendation.living}")
        if report.recommendation.additional:
            print(f"  Additional: {', '.join(report.recommendation.additional)}")
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
