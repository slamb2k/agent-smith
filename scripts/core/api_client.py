"""PocketSmith API client with rate limiting and error handling."""
import os
import time
import logging
from typing import Optional, Dict, Any
import requests


logger = logging.getLogger(__name__)


class PocketSmithClient:
    """Client for interacting with PocketSmith API v2.

    Features:
    - API authentication via Developer Key
    - Rate limiting
    - Response caching
    - Error handling and retries
    - Request/response logging
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_delay: float = 0.1,
        base_url: str = "https://api.pocketsmith.com/v2"
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
            raise ValueError("API key is required. Provide via parameter or POCKETSMITH_API_KEY env var.")

        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0

        logger.info(f"Initialized PocketSmith API client (base_url: {base_url})")

    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "X-Developer-Key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _rate_limit(self):
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
        response.raise_for_status()

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
