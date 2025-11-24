"""PocketSmith API client with rate limiting and error handling."""

import os
import time
import logging
from typing import Optional, Dict, Any, List, cast
import requests


logger = logging.getLogger(__name__)


class PocketSmithClient:
    """Client for interacting with PocketSmith API v2.

    Features:
    - API authentication via Developer Key
    - Rate limiting
    - Request/response logging
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_delay: float = 0.1,
        base_url: str = "https://api.pocketsmith.com/v2",
    ):
        """Initialize PocketSmith API client.

        Args:
            api_key: PocketSmith Developer API key. If None, reads from env.
            rate_limit_delay: Delay between API calls in seconds (default: 0.1)
            base_url: API base URL (default: production API)

        Raises:
            ValueError: If no API key provided
        """
        self.api_key = api_key or os.getenv("POCKETSMITH_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide via parameter or POCKETSMITH_API_KEY env var."
            )

        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0

        logger.info(f"Initialized PocketSmith API client (base_url: {base_url})")

    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        assert self.api_key is not None  # Validated in __init__
        return {
            "X-Developer-Key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make GET request to API.

        Args:
            endpoint: API endpoint (e.g., "/me" or "/users/123/transactions")
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            requests.HTTPError: If request fails
        """
        self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET {url} (params: {params})")

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        logger.debug(f"GET {url} - {response.status_code}")
        return response.json()

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make POST request to API.

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            Parsed JSON response

        Raises:
            requests.HTTPError: If request fails
        """
        self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"POST {url}")

        response = requests.post(url, headers=self.headers, json=data)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            import sys

            print(f"\n{'='*70}", file=sys.stderr)
            print(f"API ERROR: POST {url} failed: {response.status_code}", file=sys.stderr)
            print(f"Request payload: {data}", file=sys.stderr)
            print(f"Response body: {response.text}", file=sys.stderr)
            print(f"{'='*70}\n", file=sys.stderr)
            # HTTPError already has 'response' attribute with .text property
            raise

        logger.debug(f"POST {url} - {response.status_code}")
        return response.json()

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make PUT request to API.

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            Parsed JSON response

        Raises:
            requests.HTTPError: If request fails
        """
        self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"PUT {url}")

        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()

        logger.debug(f"PUT {url} - {response.status_code}")
        return response.json()

    def delete(self, endpoint: str) -> Any:
        """Make DELETE request to API.

        Args:
            endpoint: API endpoint

        Returns:
            Parsed JSON response or None

        Raises:
            requests.HTTPError: If request fails
        """
        self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"DELETE {url}")

        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()

        logger.debug(f"DELETE {url} - {response.status_code}")

        # DELETE may return empty response
        if response.text:
            return response.json()
        return None

    # High-level API methods

    def get_user(self) -> Dict[str, Any]:
        """Get authorized user information.

        Returns:
            User object with id, login, name, email, etc.
        """
        logger.info("Fetching authorized user")
        return cast(Dict[str, Any], self.get("/me"))

    def get_transactions(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        uncategorised: Optional[bool] = None,
        account_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 100,
    ) -> list:
        """Get transactions for a user.

        Args:
            user_id: PocketSmith user ID
            start_date: Filter start date (YYYY-MM-DD)
            end_date: Filter end date (YYYY-MM-DD)
            uncategorised: Filter for uncategorized transactions only
            account_id: Filter by specific account
            page: Page number (1-indexed)
            per_page: Results per page (max 100)

        Returns:
            List of transaction objects
        """
        params: Dict[str, Any] = {"page": page, "per_page": per_page}

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if uncategorised is not None:
            params["uncategorised"] = 1 if uncategorised else 0
        if account_id:
            params["account_id"] = account_id

        logger.info(f"Fetching transactions for user {user_id} (page {page})")
        return cast(List[Any], self.get(f"/users/{user_id}/transactions", params=params))

    def get_categories(self, user_id: int) -> list:
        """Get all categories for a user.

        Args:
            user_id: PocketSmith user ID

        Returns:
            List of category objects with full hierarchy
        """
        logger.info(f"Fetching categories for user {user_id}")
        return cast(List[Any], self.get(f"/users/{user_id}/categories"))

    def update_transaction(
        self, transaction_id: int, category_id: Optional[int] = None, note: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a transaction.

        Args:
            transaction_id: Transaction ID to update
            category_id: New category ID
            note: Transaction note/memo

        Returns:
            Updated transaction object
        """
        data: Dict[str, Any] = {}
        if category_id is not None:
            data["category_id"] = category_id
        if note is not None:
            data["note"] = note

        logger.info(f"Updating transaction {transaction_id}")
        return cast(Dict[str, Any], self.put(f"/transactions/{transaction_id}", data=data))

    def get_category_rules(self, category_id: int) -> List[Dict[str, Any]]:
        """Get all category rules for a specific category.

        Args:
            category_id: Category ID to fetch rules for

        Returns:
            List of category rule objects
        """
        logger.info(f"Fetching category rules for category {category_id}")
        return cast(List[Dict[str, Any]], self.get(f"/categories/{category_id}/category_rules"))

    def create_category_rule(self, category_id: int, payee_matches: str) -> Dict[str, Any]:
        """Create a category rule (platform rule).

        Note: PocketSmith API only supports simple keyword matching.
        For advanced rules, use local rule engine.

        Args:
            category_id: Category to assign
            payee_matches: Keyword to match in payee name

        Returns:
            Created category rule object
        """
        data = {"payee_matches": payee_matches, "apply_to_all": True}

        logger.info(f"Creating category rule for category {category_id}: '{payee_matches}'")
        return cast(
            Dict[str, Any], self.post(f"/categories/{category_id}/category_rules", data=data)
        )

    def get_transaction_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all transaction accounts for a user.

        Transaction accounts are the specific accounts where transactions are recorded.

        Args:
            user_id: PocketSmith user ID

        Returns:
            List of transaction account objects with name, id, type, current_balance, etc.
        """
        logger.info(f"Fetching transaction accounts for user {user_id}")
        return cast(List[Dict[str, Any]], self.get(f"/users/{user_id}/transaction_accounts"))
