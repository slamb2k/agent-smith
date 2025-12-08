"""Multi-tier caching layer for PocketSmith API responses.

This module provides intelligent caching with TTL policies based on data type:
- Recent transactions: Short TTL (5 minutes) - may be updated/categorized
- Historical transactions: Long TTL (24 hours) - immutable after reconciliation
- Categories: Medium TTL (30 minutes) - rarely change
- Accounts: Medium TTL (30 minutes) - rarely change
- User: Long TTL (1 hour) - rarely changes

Features:
- Disk-based persistence (survives restarts)
- Automatic TTL expiration
- Cache invalidation on mutations
- Thread-safe operations
- Memory + disk hybrid for performance
"""

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Generic

try:
    import diskcache
except ImportError:
    diskcache = None  # type: ignore

logger = logging.getLogger(__name__)


# =============================================================================
# Cache Policy Configuration
# =============================================================================


class CachePolicy(Enum):
    """Cache TTL policies for different data types."""

    # Transactions
    TRANSACTIONS_RECENT = 300  # 5 minutes for recent (may be edited)
    TRANSACTIONS_HISTORICAL = 86400  # 24 hours for historical (immutable)

    # Reference data
    CATEGORIES = 1800  # 30 minutes
    ACCOUNTS = 1800  # 30 minutes
    TRANSACTION_ACCOUNTS = 1800  # 30 minutes
    USER = 3600  # 1 hour

    # Computed/derived data
    RULES = 900  # 15 minutes (rules may be edited)
    HEALTH_SCORES = 3600  # 1 hour

    # Short-lived
    SEARCH_RESULTS = 60  # 1 minute

    @classmethod
    def for_transactions(cls, transaction_date: Optional[date] = None) -> int:
        """Get TTL for transactions based on date.

        Args:
            transaction_date: Date of the transaction. If within last 30 days,
                             uses short TTL. Otherwise uses long TTL.

        Returns:
            TTL in seconds
        """
        if transaction_date is None:
            return cls.TRANSACTIONS_RECENT.value

        days_ago = (date.today() - transaction_date).days
        if days_ago <= 30:
            return cls.TRANSACTIONS_RECENT.value
        return cls.TRANSACTIONS_HISTORICAL.value


# =============================================================================
# Cache Key Generation
# =============================================================================


@dataclass(frozen=True)
class CacheKey:
    """Structured cache key with namespace and parameters."""

    namespace: str
    resource_type: str
    resource_id: Optional[str] = None
    params_hash: Optional[str] = None

    def __str__(self) -> str:
        """Generate string key for cache storage."""
        parts = [self.namespace, self.resource_type]
        if self.resource_id:
            parts.append(str(self.resource_id))
        if self.params_hash:
            parts.append(self.params_hash)
        return ":".join(parts)

    @classmethod
    def for_user(cls, user_id: Optional[int] = None) -> "CacheKey":
        """Create key for user data."""
        return cls(
            namespace="pocketsmith",
            resource_type="user",
            resource_id=str(user_id) if user_id else "me",
        )

    @classmethod
    def for_categories(cls, user_id: int, flatten: bool = False) -> "CacheKey":
        """Create key for categories."""
        return cls(
            namespace="pocketsmith",
            resource_type="categories",
            resource_id=str(user_id),
            params_hash=f"flat={flatten}",
        )

    @classmethod
    def for_accounts(cls, user_id: int) -> "CacheKey":
        """Create key for accounts."""
        return cls(
            namespace="pocketsmith",
            resource_type="accounts",
            resource_id=str(user_id),
        )

    @classmethod
    def for_transaction_accounts(cls, user_id: int) -> "CacheKey":
        """Create key for transaction accounts."""
        return cls(
            namespace="pocketsmith",
            resource_type="transaction_accounts",
            resource_id=str(user_id),
        )

    @classmethod
    def for_transactions(
        cls,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        uncategorised: Optional[bool] = None,
        account_id: Optional[int] = None,
        page: int = 1,
    ) -> "CacheKey":
        """Create key for transaction list."""
        params = {
            "start": start_date,
            "end": end_date,
            "uncat": uncategorised,
            "acct": account_id,
            "page": page,
        }
        # Filter out None values and create hash
        filtered = {k: v for k, v in params.items() if v is not None}
        params_str = json.dumps(filtered, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]

        return cls(
            namespace="pocketsmith",
            resource_type="transactions",
            resource_id=str(user_id),
            params_hash=params_hash,
        )

    @classmethod
    def for_transaction(cls, transaction_id: int) -> "CacheKey":
        """Create key for single transaction."""
        return cls(
            namespace="pocketsmith",
            resource_type="transaction",
            resource_id=str(transaction_id),
        )


# =============================================================================
# Cache Entry
# =============================================================================


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    data: Any
    created_at: datetime
    ttl_seconds: int
    hit_count: int = 0

    @property
    def expires_at(self) -> datetime:
        """Calculate expiration time."""
        return self.created_at + timedelta(seconds=self.ttl_seconds)

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.now() > self.expires_at

    @property
    def age_seconds(self) -> float:
        """Get entry age in seconds."""
        return (datetime.now() - self.created_at).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for storage."""
        return {
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "ttl_seconds": self.ttl_seconds,
            "hit_count": self.hit_count,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CacheEntry":
        """Deserialize from dictionary."""
        return cls(
            data=d["data"],
            created_at=datetime.fromisoformat(d["created_at"]),
            ttl_seconds=d["ttl_seconds"],
            hit_count=d.get("hit_count", 0),
        )


# =============================================================================
# Cache Statistics
# =============================================================================


@dataclass
class CacheStats:
    """Cache performance statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate (0.0 - 1.0)."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1

    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1

    def record_eviction(self) -> None:
        """Record a cache eviction."""
        self.evictions += 1


# =============================================================================
# Main Cache Implementation
# =============================================================================

T = TypeVar("T")


class PocketSmithCache:
    """Multi-tier cache for PocketSmith API responses.

    Uses diskcache for persistent storage with automatic TTL expiration.
    Falls back to in-memory cache if diskcache is not available.
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        default_ttl: int = 300,
        enabled: bool = True,
    ):
        """Initialize cache.

        Args:
            cache_dir: Directory for disk cache. Defaults to data/cache/
            default_ttl: Default TTL in seconds
            enabled: Whether caching is enabled
        """
        self.enabled = enabled
        self.default_ttl = default_ttl
        self.stats = CacheStats()

        # Set up cache directory
        if cache_dir is None:
            project_root = Path(__file__).parent.parent.parent
            cache_dir = project_root / "data" / "cache"

        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize disk cache if available
        self._disk_cache: Optional[Any] = None
        self._memory_cache: dict[str, CacheEntry] = {}

        if diskcache is not None and enabled:
            try:
                self._disk_cache = diskcache.Cache(
                    str(self.cache_dir),
                    size_limit=100 * 1024 * 1024,  # 100 MB
                    cull_limit=10,  # Remove 10% when full
                    statistics=True,
                )
                logger.info(f"Initialized disk cache at {self.cache_dir}")
            except Exception as e:
                logger.warning(f"Failed to initialize disk cache: {e}, using memory only")
                self._disk_cache = None
        else:
            if not enabled:
                logger.info("Cache disabled")
            elif diskcache is None:
                logger.warning("diskcache not installed, using memory cache only")

    def get(self, key: CacheKey, default: Optional[T] = None) -> Optional[T]:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if not found

        Returns:
            Cached value or default
        """
        if not self.enabled:
            return default

        str_key = str(key)

        # Try disk cache first
        if self._disk_cache is not None:
            try:
                entry_dict = self._disk_cache.get(str_key)
                if entry_dict is not None:
                    entry = CacheEntry.from_dict(entry_dict)
                    if not entry.is_expired:
                        entry.hit_count += 1
                        self.stats.record_hit()
                        logger.debug(f"Cache HIT: {str_key} (age: {entry.age_seconds:.1f}s)")
                        return entry.data
                    else:
                        # Expired, remove it
                        self._disk_cache.delete(str_key)
                        self.stats.record_eviction()
            except Exception as e:
                logger.warning(f"Disk cache get failed: {e}")

        # Try memory cache
        if str_key in self._memory_cache:
            entry = self._memory_cache[str_key]
            if not entry.is_expired:
                entry.hit_count += 1
                self.stats.record_hit()
                logger.debug(f"Memory cache HIT: {str_key}")
                return entry.data
            else:
                del self._memory_cache[str_key]
                self.stats.record_eviction()

        self.stats.record_miss()
        logger.debug(f"Cache MISS: {str_key}")
        return default

    def set(
        self,
        key: CacheKey,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (uses default if not specified)
        """
        if not self.enabled:
            return

        str_key = str(key)
        ttl = ttl or self.default_ttl

        entry = CacheEntry(
            data=value,
            created_at=datetime.now(),
            ttl_seconds=ttl,
        )

        # Store in disk cache if available
        if self._disk_cache is not None:
            try:
                self._disk_cache.set(str_key, entry.to_dict(), expire=ttl)
                logger.debug(f"Cache SET (disk): {str_key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"Disk cache set failed: {e}")
                # Fall back to memory
                self._memory_cache[str_key] = entry
        else:
            self._memory_cache[str_key] = entry
            logger.debug(f"Cache SET (memory): {str_key} (TTL: {ttl}s)")

        self.stats.size = len(self._memory_cache)
        if self._disk_cache:
            self.stats.size += len(self._disk_cache)

    def delete(self, key: CacheKey) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if value was deleted
        """
        str_key = str(key)
        deleted = False

        if self._disk_cache is not None:
            try:
                deleted = self._disk_cache.delete(str_key)
            except Exception as e:
                logger.warning(f"Disk cache delete failed: {e}")

        if str_key in self._memory_cache:
            del self._memory_cache[str_key]
            deleted = True

        if deleted:
            logger.debug(f"Cache DELETE: {str_key}")

        return deleted

    def invalidate_transactions(self, user_id: int) -> int:
        """Invalidate all cached transactions for a user.

        Call this after mutating transactions.

        Args:
            user_id: User ID

        Returns:
            Number of entries invalidated
        """
        pattern = f"pocketsmith:transactions:{user_id}"
        return self._invalidate_pattern(pattern)

    def invalidate_transaction(self, transaction_id: int) -> bool:
        """Invalidate a specific transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            True if invalidated
        """
        key = CacheKey.for_transaction(transaction_id)
        return self.delete(key)

    def invalidate_categories(self, user_id: int) -> int:
        """Invalidate cached categories for a user.

        Args:
            user_id: User ID

        Returns:
            Number of entries invalidated
        """
        pattern = f"pocketsmith:categories:{user_id}"
        return self._invalidate_pattern(pattern)

    def _invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern.

        Args:
            pattern: Key prefix pattern

        Returns:
            Number of entries invalidated
        """
        count = 0

        # Invalidate memory cache
        keys_to_delete = [k for k in self._memory_cache if k.startswith(pattern)]
        for key in keys_to_delete:
            del self._memory_cache[key]
            count += 1

        # Invalidate disk cache (if available)
        if self._disk_cache is not None:
            try:
                # diskcache doesn't support pattern matching, iterate all keys
                for key in list(self._disk_cache):
                    if key.startswith(pattern):
                        self._disk_cache.delete(key)
                        count += 1
            except Exception as e:
                logger.warning(f"Disk cache pattern invalidation failed: {e}")

        if count > 0:
            logger.info(f"Invalidated {count} cache entries matching '{pattern}'")

        return count

    def clear(self) -> None:
        """Clear all cached data."""
        self._memory_cache.clear()
        if self._disk_cache is not None:
            try:
                self._disk_cache.clear()
            except Exception as e:
                logger.warning(f"Disk cache clear failed: {e}")

        self.stats = CacheStats()
        logger.info("Cache cleared")

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.stats

    def close(self) -> None:
        """Close cache connections."""
        if self._disk_cache is not None:
            try:
                self._disk_cache.close()
            except Exception:
                pass


# =============================================================================
# Cache Decorator
# =============================================================================


def cached(
    key_func: Callable[..., CacheKey],
    ttl: Optional[int] = None,
    cache: Optional[PocketSmithCache] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for caching function results.

    Args:
        key_func: Function to generate cache key from arguments
        ttl: TTL in seconds
        cache: Cache instance (uses global cache if not provided)

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            nonlocal cache
            if cache is None:
                cache = get_global_cache()

            key = key_func(*args, **kwargs)
            result = cache.get(key)

            if result is not None:
                return result

            result = func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)
            return result

        return wrapper

    return decorator


# =============================================================================
# Global Cache Instance
# =============================================================================

_global_cache: Optional[PocketSmithCache] = None


def get_global_cache() -> PocketSmithCache:
    """Get or create global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = PocketSmithCache()
    return _global_cache


def set_global_cache(cache: PocketSmithCache) -> None:
    """Set global cache instance."""
    global _global_cache
    _global_cache = cache
