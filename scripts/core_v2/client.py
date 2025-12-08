"""Pydantic-validated PocketSmith API client with caching.

This module provides a type-safe API client that:
- Returns Pydantic models instead of raw dictionaries
- Automatically caches responses with appropriate TTLs
- Validates API responses at runtime
- Invalidates cache on mutations
- Handles rate limiting

Usage:
    from scripts.core_v2.client import PocketSmithClientV2

    client = PocketSmithClientV2()
    user = client.get_user()  # Returns User model
    transactions = client.get_transactions(user.id)  # Returns list[Transaction]
"""

import logging
import os
import time
from datetime import date
from typing import Any, Optional

import requests

from .cache import (
    CacheKey,
    CachePolicy,
    PocketSmithCache,
    get_global_cache,
)
from .models import (
    Account,
    Category,
    CategoryRule,
    Transaction,
    TransactionAccount,
    TransactionListParams,
    TransactionUpdate,
    User,
)

logger = logging.getLogger(__name__)


class PocketSmithClientV2:
    """Type-safe PocketSmith API client with caching.

    All methods return Pydantic models with full validation.
    Caching is automatic based on data type and age.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_delay: float = 0.1,
        base_url: str = "https://api.pocketsmith.com/v2",
        cache: Optional[PocketSmithCache] = None,
        enable_cache: bool = True,
    ):
        """Initialize API client.

        Args:
            api_key: PocketSmith Developer API key. Reads from env if not provided.
            rate_limit_delay: Delay between API calls in seconds
            base_url: API base URL
            cache: Cache instance. Uses global cache if not provided.
            enable_cache: Whether to use caching
        """
        self.api_key = api_key or os.getenv("POCKETSMITH_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Provide via parameter or POCKETSMITH_API_KEY env var."
            )

        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0

        # Cache setup
        self._cache = cache if cache is not None else get_global_cache()
        self._enable_cache = enable_cache

        logger.info(f"Initialized PocketSmithClientV2 (cache: {enable_cache})")

    @property
    def headers(self) -> dict[str, str]:
        """HTTP headers for API requests."""
        return {
            "X-Developer-Key": self.api_key,  # type: ignore
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _get(
        self, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> Any:
        """Make GET request."""
        self._rate_limit()
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET {url} (params: {params})")

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def _get_with_headers(
        self, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> tuple[Any, dict[str, str]]:
        """Make GET request and return headers."""
        self._rate_limit()
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET {url} (params: {params})")

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json(), dict(response.headers)

    def _post(
        self, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> Any:
        """Make POST request."""
        self._rate_limit()
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"POST {url}")

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()

        return response.json()

    def _put(
        self, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> Any:
        """Make PUT request."""
        self._rate_limit()
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"PUT {url}")

        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()

        return response.json()

    def _delete(self, endpoint: str) -> Optional[Any]:
        """Make DELETE request."""
        self._rate_limit()
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"DELETE {url}")

        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()

        if response.text:
            return response.json()
        return None

    # =========================================================================
    # User Methods
    # =========================================================================

    def get_user(self, bypass_cache: bool = False) -> User:
        """Get authenticated user.

        Args:
            bypass_cache: Skip cache and fetch fresh data

        Returns:
            User model with all fields validated
        """
        cache_key = CacheKey.for_user()

        if self._enable_cache and not bypass_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return User.model_validate(cached)

        data = self._get("/me")
        user = User.model_validate(data)

        if self._enable_cache:
            self._cache.set(
                cache_key,
                data,
                ttl=CachePolicy.USER.value,
            )

        return user

    # =========================================================================
    # Category Methods
    # =========================================================================

    def get_categories(
        self,
        user_id: int,
        flatten: bool = True,
        bypass_cache: bool = False,
    ) -> list[Category]:
        """Get all categories for a user.

        Args:
            user_id: PocketSmith user ID
            flatten: If True, returns flat list including children.
                    If False, returns hierarchical structure.
            bypass_cache: Skip cache

        Returns:
            List of Category models
        """
        cache_key = CacheKey.for_categories(user_id, flatten)

        if self._enable_cache and not bypass_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return [Category.model_validate(c) for c in cached]

        data = self._get(f"/users/{user_id}/categories")

        if flatten:
            data = self._flatten_categories(data)

        categories = [Category.model_validate(c) for c in data]

        if self._enable_cache:
            self._cache.set(
                cache_key,
                data,
                ttl=CachePolicy.CATEGORIES.value,
            )

        return categories

    def get_category(self, category_id: int) -> Category:
        """Get a specific category.

        Args:
            category_id: Category ID

        Returns:
            Category model
        """
        data = self._get(f"/categories/{category_id}")
        return Category.model_validate(data)

    @staticmethod
    def _flatten_categories(
        categories: list[dict[str, Any]], level: int = 0
    ) -> list[dict[str, Any]]:
        """Flatten hierarchical categories into a single list."""
        result = []
        for category in categories:
            cat_copy = category.copy()
            cat_copy["hierarchy_level"] = level
            result.append(cat_copy)

            if category.get("children"):
                result.extend(
                    PocketSmithClientV2._flatten_categories(
                        category["children"], level=level + 1
                    )
                )
        return result

    # =========================================================================
    # Account Methods
    # =========================================================================

    def get_accounts(
        self,
        user_id: int,
        bypass_cache: bool = False,
    ) -> list[Account]:
        """Get all accounts for a user.

        Args:
            user_id: PocketSmith user ID
            bypass_cache: Skip cache

        Returns:
            List of Account models
        """
        cache_key = CacheKey.for_accounts(user_id)

        if self._enable_cache and not bypass_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return [Account.model_validate(a) for a in cached]

        data = self._get(f"/users/{user_id}/accounts")
        accounts = [Account.model_validate(a) for a in data]

        if self._enable_cache:
            self._cache.set(
                cache_key,
                data,
                ttl=CachePolicy.ACCOUNTS.value,
            )

        return accounts

    def get_transaction_accounts(
        self,
        user_id: int,
        bypass_cache: bool = False,
    ) -> list[TransactionAccount]:
        """Get all transaction accounts for a user.

        Args:
            user_id: PocketSmith user ID
            bypass_cache: Skip cache

        Returns:
            List of TransactionAccount models
        """
        cache_key = CacheKey.for_transaction_accounts(user_id)

        if self._enable_cache and not bypass_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return [TransactionAccount.model_validate(a) for a in cached]

        data = self._get(f"/users/{user_id}/transaction_accounts")
        accounts = [TransactionAccount.model_validate(a) for a in data]

        if self._enable_cache:
            self._cache.set(
                cache_key,
                data,
                ttl=CachePolicy.TRANSACTION_ACCOUNTS.value,
            )

        return accounts

    # =========================================================================
    # Transaction Methods
    # =========================================================================

    def get_transactions(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        uncategorised: Optional[bool] = None,
        account_id: Optional[int] = None,
        needs_review: Optional[bool] = None,
        page: int = 1,
        per_page: int = 100,
        bypass_cache: bool = False,
    ) -> list[Transaction]:
        """Get transactions for a user.

        Args:
            user_id: PocketSmith user ID
            start_date: Filter start date
            end_date: Filter end date
            uncategorised: Filter for uncategorized only
            account_id: Filter by account
            needs_review: Filter by needs_review flag
            page: Page number (1-indexed)
            per_page: Results per page (max 100)
            bypass_cache: Skip cache

        Returns:
            List of Transaction models
        """
        # Build validated params
        params = TransactionListParams(
            start_date=start_date,
            end_date=end_date,
            uncategorised=uncategorised,
            needs_review=needs_review,
            account_id=account_id,
            page=page,
            per_page=per_page,
        )

        # Build cache key
        cache_key = CacheKey.for_transactions(
            user_id=user_id,
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
            uncategorised=uncategorised,
            account_id=account_id,
            page=page,
        )

        if self._enable_cache and not bypass_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return [Transaction.model_validate(t) for t in cached]

        # Fetch from API
        data = self._get(
            f"/users/{user_id}/transactions",
            params=params.to_api_params(),
        )

        transactions = [Transaction.model_validate(t) for t in data]

        # Cache with TTL based on transaction age
        if self._enable_cache:
            # Use short TTL if recent data, long TTL if historical
            ttl = CachePolicy.for_transactions(start_date)
            self._cache.set(cache_key, data, ttl=ttl)

        return transactions

    def get_all_transactions(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        uncategorised: Optional[bool] = None,
        account_id: Optional[int] = None,
        bypass_cache: bool = False,
        progress_callback: Optional[callable] = None,
    ) -> list[Transaction]:
        """Get ALL transactions with automatic pagination.

        Args:
            user_id: PocketSmith user ID
            start_date: Filter start date
            end_date: Filter end date
            uncategorised: Filter for uncategorized only
            account_id: Filter by account
            bypass_cache: Skip cache
            progress_callback: Optional callback(page, total_fetched)

        Returns:
            Complete list of Transaction models
        """
        all_transactions: list[Transaction] = []
        page = 1
        per_page = 100

        while True:
            batch = self.get_transactions(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                uncategorised=uncategorised,
                account_id=account_id,
                page=page,
                per_page=per_page,
                bypass_cache=bypass_cache,
            )

            if not batch:
                break

            all_transactions.extend(batch)

            if progress_callback:
                progress_callback(page, len(all_transactions))

            if len(batch) < per_page:
                break

            page += 1

        logger.info(f"Fetched {len(all_transactions)} total transactions")
        return all_transactions

    def get_transaction(
        self, transaction_id: int, bypass_cache: bool = False
    ) -> Transaction:
        """Get a specific transaction.

        Args:
            transaction_id: Transaction ID
            bypass_cache: Skip cache

        Returns:
            Transaction model
        """
        cache_key = CacheKey.for_transaction(transaction_id)

        if self._enable_cache and not bypass_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return Transaction.model_validate(cached)

        data = self._get(f"/transactions/{transaction_id}")
        transaction = Transaction.model_validate(data)

        if self._enable_cache:
            ttl = CachePolicy.for_transactions(transaction.date)
            self._cache.set(cache_key, data, ttl=ttl)

        return transaction

    def get_transaction_count(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        uncategorised: Optional[bool] = None,
        account_id: Optional[int] = None,
    ) -> int:
        """Get transaction count from API headers.

        More efficient than fetching all transactions when only count is needed.

        Returns:
            Total transaction count
        """
        params = TransactionListParams(
            start_date=start_date,
            end_date=end_date,
            uncategorised=uncategorised,
            account_id=account_id,
            page=1,
            per_page=10,  # Minimum fetch
        )

        _, headers = self._get_with_headers(
            f"/users/{user_id}/transactions",
            params=params.to_api_params(),
        )

        total = headers.get("Total", headers.get("total", "0"))
        return int(total)

    # =========================================================================
    # Transaction Mutation Methods (with cache invalidation)
    # =========================================================================

    def update_transaction(
        self,
        transaction_id: int,
        update: TransactionUpdate,
    ) -> Transaction:
        """Update a transaction.

        Automatically invalidates relevant caches.

        Args:
            transaction_id: Transaction ID
            update: Update model with fields to change

        Returns:
            Updated Transaction model
        """
        data = self._put(
            f"/transactions/{transaction_id}",
            data=update.to_api_dict(),
        )

        transaction = Transaction.model_validate(data)

        # Invalidate caches
        if self._enable_cache:
            self._cache.invalidate_transaction(transaction_id)
            # Also invalidate transaction lists (we don't know which user)
            # In practice, caller should invalidate user's transaction cache

        logger.info(f"Updated transaction {transaction_id}")
        return transaction

    def update_transaction_simple(
        self,
        transaction_id: int,
        category_id: Optional[int] = None,
        note: Optional[str] = None,
        labels: Optional[list[str]] = None,
        needs_review: Optional[bool] = None,
    ) -> Transaction:
        """Simplified transaction update with individual parameters.

        Args:
            transaction_id: Transaction ID
            category_id: New category ID
            note: New note
            labels: New labels
            needs_review: New needs_review flag

        Returns:
            Updated Transaction model
        """
        update = TransactionUpdate(
            category_id=category_id,
            note=note,
            labels=labels,
            needs_review=needs_review,
        )
        return self.update_transaction(transaction_id, update)

    # =========================================================================
    # Category Rule Methods
    # =========================================================================

    def get_category_rules(self, category_id: int) -> list[CategoryRule]:
        """Get rules for a category.

        Args:
            category_id: Category ID

        Returns:
            List of CategoryRule models
        """
        data = self._get(f"/categories/{category_id}/category_rules")
        return [CategoryRule.model_validate(r) for r in data]

    def create_category_rule(
        self,
        category_id: int,
        payee_matches: str,
        apply_to_all: bool = True,
    ) -> CategoryRule:
        """Create a category rule.

        Args:
            category_id: Category to assign
            payee_matches: Keyword to match in payee
            apply_to_all: Apply to existing uncategorized transactions

        Returns:
            Created CategoryRule model
        """
        data = self._post(
            f"/categories/{category_id}/category_rules",
            data={"payee_matches": payee_matches, "apply_to_all": apply_to_all},
        )

        if self._enable_cache:
            # Invalidate categories cache (rules may affect category display)
            # Note: We'd need user_id here, which we don't have
            pass

        return CategoryRule.model_validate(data)

    # =========================================================================
    # Cache Management
    # =========================================================================

    def invalidate_user_caches(self, user_id: int) -> None:
        """Invalidate all caches for a user.

        Call this after bulk operations.

        Args:
            user_id: User ID
        """
        if self._enable_cache:
            self._cache.invalidate_transactions(user_id)
            self._cache.invalidate_categories(user_id)
            self._cache.delete(CacheKey.for_accounts(user_id))
            self._cache.delete(CacheKey.for_transaction_accounts(user_id))
            logger.info(f"Invalidated all caches for user {user_id}")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with hit rate, size, etc.
        """
        stats = self._cache.get_stats()
        return {
            "hits": stats.hits,
            "misses": stats.misses,
            "hit_rate": f"{stats.hit_rate:.1%}",
            "evictions": stats.evictions,
            "size": stats.size,
        }
