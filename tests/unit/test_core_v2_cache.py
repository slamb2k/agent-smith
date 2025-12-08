"""Unit tests for core_v2 caching layer."""

import tempfile
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from scripts.core_v2.cache import (
    CacheEntry,
    CacheKey,
    CachePolicy,
    CacheStats,
    PocketSmithCache,
)


class TestCacheKey:
    """Tests for CacheKey generation."""

    def test_for_user(self):
        """Test user cache key."""
        key = CacheKey.for_user(12345)
        assert str(key) == "pocketsmith:user:12345"

    def test_for_user_me(self):
        """Test user cache key without ID."""
        key = CacheKey.for_user()
        assert str(key) == "pocketsmith:user:me"

    def test_for_categories(self):
        """Test categories cache key."""
        key = CacheKey.for_categories(123, flatten=True)
        assert str(key) == "pocketsmith:categories:123:flat=True"

        key_no_flatten = CacheKey.for_categories(123, flatten=False)
        assert str(key_no_flatten) == "pocketsmith:categories:123:flat=False"

    def test_for_accounts(self):
        """Test accounts cache key."""
        key = CacheKey.for_accounts(123)
        assert str(key) == "pocketsmith:accounts:123"

    def test_for_transaction_accounts(self):
        """Test transaction accounts cache key."""
        key = CacheKey.for_transaction_accounts(123)
        assert str(key) == "pocketsmith:transaction_accounts:123"

    def test_for_transactions(self):
        """Test transactions cache key with params."""
        key = CacheKey.for_transactions(
            user_id=123,
            start_date="2024-01-01",
            end_date="2024-01-31",
            page=1,
        )
        # Key includes hash of params
        assert str(key).startswith("pocketsmith:transactions:123:")

    def test_for_transactions_different_params_different_keys(self):
        """Test that different params produce different keys."""
        key1 = CacheKey.for_transactions(
            user_id=123,
            start_date="2024-01-01",
            page=1,
        )
        key2 = CacheKey.for_transactions(
            user_id=123,
            start_date="2024-02-01",
            page=1,
        )

        assert str(key1) != str(key2)

    def test_for_transaction_single(self):
        """Test single transaction cache key."""
        key = CacheKey.for_transaction(12345)
        assert str(key) == "pocketsmith:transaction:12345"

    def test_cache_key_is_hashable(self):
        """Test that CacheKey is hashable (can be used in sets/dicts)."""
        key1 = CacheKey.for_user(123)
        key2 = CacheKey.for_user(123)
        key3 = CacheKey.for_user(456)

        key_set = {key1, key2, key3}
        assert len(key_set) == 2  # key1 and key2 are equal


class TestCachePolicy:
    """Tests for CachePolicy TTL configuration."""

    def test_policy_values(self):
        """Test that policy values are reasonable."""
        assert CachePolicy.TRANSACTIONS_RECENT.value == 300  # 5 min
        assert CachePolicy.TRANSACTIONS_HISTORICAL.value == 86400  # 24 hr
        assert CachePolicy.CATEGORIES.value == 1800  # 30 min
        assert CachePolicy.USER.value == 3600  # 1 hr

    def test_for_transactions_recent(self):
        """Test TTL for recent transactions (within 30 days)."""
        recent_date = date.today() - timedelta(days=7)
        ttl = CachePolicy.for_transactions(recent_date)
        assert ttl == CachePolicy.TRANSACTIONS_RECENT.value

    def test_for_transactions_historical(self):
        """Test TTL for historical transactions (older than 30 days)."""
        old_date = date.today() - timedelta(days=60)
        ttl = CachePolicy.for_transactions(old_date)
        assert ttl == CachePolicy.TRANSACTIONS_HISTORICAL.value

    def test_for_transactions_no_date(self):
        """Test TTL defaults to recent when no date provided."""
        ttl = CachePolicy.for_transactions(None)
        assert ttl == CachePolicy.TRANSACTIONS_RECENT.value


class TestCacheEntry:
    """Tests for CacheEntry."""

    def test_entry_creation(self):
        """Test creating a cache entry."""
        entry = CacheEntry(
            data={"test": "data"},
            created_at=datetime.now(),
            ttl_seconds=300,
        )

        assert entry.data == {"test": "data"}
        assert entry.ttl_seconds == 300
        assert entry.hit_count == 0

    def test_is_expired_false(self):
        """Test entry is not expired within TTL."""
        entry = CacheEntry(
            data="test",
            created_at=datetime.now(),
            ttl_seconds=300,
        )

        assert entry.is_expired is False

    def test_is_expired_true(self):
        """Test entry is expired after TTL."""
        entry = CacheEntry(
            data="test",
            created_at=datetime.now() - timedelta(seconds=400),
            ttl_seconds=300,
        )

        assert entry.is_expired is True

    def test_expires_at(self):
        """Test expires_at calculation."""
        now = datetime.now()
        entry = CacheEntry(
            data="test",
            created_at=now,
            ttl_seconds=300,
        )

        expected = now + timedelta(seconds=300)
        assert entry.expires_at == expected

    def test_age_seconds(self):
        """Test age calculation."""
        entry = CacheEntry(
            data="test",
            created_at=datetime.now() - timedelta(seconds=100),
            ttl_seconds=300,
        )

        # Age should be approximately 100 seconds
        assert 99 <= entry.age_seconds <= 102

    def test_to_dict_and_from_dict(self):
        """Test serialization round-trip."""
        original = CacheEntry(
            data={"key": "value", "list": [1, 2, 3]},
            created_at=datetime.now(),
            ttl_seconds=600,
            hit_count=5,
        )

        serialized = original.to_dict()
        restored = CacheEntry.from_dict(serialized)

        assert restored.data == original.data
        assert restored.ttl_seconds == original.ttl_seconds
        assert restored.hit_count == original.hit_count


class TestCacheStats:
    """Tests for CacheStats."""

    def test_initial_stats(self):
        """Test initial statistics."""
        stats = CacheStats()

        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0
        assert stats.hit_rate == 0.0

    def test_record_hit(self):
        """Test recording hits."""
        stats = CacheStats()
        stats.record_hit()
        stats.record_hit()

        assert stats.hits == 2

    def test_record_miss(self):
        """Test recording misses."""
        stats = CacheStats()
        stats.record_miss()

        assert stats.misses == 1

    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        stats = CacheStats()
        stats.hits = 80
        stats.misses = 20

        assert stats.hit_rate == 0.8

    def test_hit_rate_no_requests(self):
        """Test hit rate with no requests."""
        stats = CacheStats()
        assert stats.hit_rate == 0.0


class TestPocketSmithCache:
    """Tests for PocketSmithCache."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def cache(self, temp_cache_dir):
        """Create cache instance for testing."""
        return PocketSmithCache(cache_dir=temp_cache_dir, default_ttl=60)

    def test_set_and_get(self, cache):
        """Test basic set and get."""
        key = CacheKey.for_user(123)
        cache.set(key, {"name": "Test User"})

        result = cache.get(key)
        assert result == {"name": "Test User"}

    def test_get_nonexistent(self, cache):
        """Test getting nonexistent key."""
        key = CacheKey.for_user(999)
        result = cache.get(key)

        assert result is None

    def test_get_with_default(self, cache):
        """Test getting nonexistent key with default."""
        key = CacheKey.for_user(999)
        result = cache.get(key, default="default_value")

        assert result == "default_value"

    def test_delete(self, cache):
        """Test deleting a key."""
        key = CacheKey.for_user(123)
        cache.set(key, "test")

        assert cache.get(key) == "test"

        deleted = cache.delete(key)
        assert deleted is True
        assert cache.get(key) is None

    def test_delete_nonexistent(self, cache):
        """Test deleting nonexistent key."""
        key = CacheKey.for_user(999)
        deleted = cache.delete(key)

        assert deleted is False

    def test_stats_tracking(self, cache):
        """Test that stats are tracked."""
        key1 = CacheKey.for_user(1)
        key2 = CacheKey.for_user(2)

        # Miss
        cache.get(key1)
        assert cache.stats.misses == 1

        # Set and hit
        cache.set(key1, "test")
        cache.get(key1)
        assert cache.stats.hits == 1

        # Another miss
        cache.get(key2)
        assert cache.stats.misses == 2

    def test_invalidate_transactions(self, cache):
        """Test invalidating all transactions for a user."""
        user_id = 123

        # Set multiple transaction cache entries
        for page in range(1, 4):
            key = CacheKey.for_transactions(user_id, page=page)
            cache.set(key, [{"id": page}])

        # Verify they're cached
        key1 = CacheKey.for_transactions(user_id, page=1)
        assert cache.get(key1) is not None

        # Invalidate all
        count = cache.invalidate_transactions(user_id)

        # Verify they're gone
        assert cache.get(key1) is None
        assert count >= 1

    def test_invalidate_transaction(self, cache):
        """Test invalidating single transaction."""
        key = CacheKey.for_transaction(12345)
        cache.set(key, {"id": 12345})

        assert cache.get(key) is not None

        result = cache.invalidate_transaction(12345)
        assert result is True
        assert cache.get(key) is None

    def test_clear(self, cache):
        """Test clearing entire cache."""
        cache.set(CacheKey.for_user(1), "user1")
        cache.set(CacheKey.for_user(2), "user2")

        cache.clear()

        assert cache.get(CacheKey.for_user(1)) is None
        assert cache.get(CacheKey.for_user(2)) is None

    def test_cache_disabled(self, temp_cache_dir):
        """Test cache when disabled."""
        cache = PocketSmithCache(cache_dir=temp_cache_dir, enabled=False)

        key = CacheKey.for_user(123)
        cache.set(key, "test")

        # Should return None even after set
        assert cache.get(key) is None

    def test_custom_ttl(self, cache):
        """Test setting custom TTL."""
        key = CacheKey.for_user(123)
        cache.set(key, "test", ttl=1)  # 1 second TTL

        # Should be available immediately
        assert cache.get(key) == "test"

        # Wait for expiration
        time.sleep(1.5)

        # Should be expired
        assert cache.get(key) is None

    def test_complex_data_types(self, cache):
        """Test caching complex data structures."""
        key = CacheKey.for_transactions(user_id=1, page=1)
        data = [
            {"id": 1, "amount": -50.00, "labels": ["Tax", "Business"]},
            {"id": 2, "amount": 100.00, "nested": {"key": "value"}},
        ]

        cache.set(key, data)
        result = cache.get(key)

        assert result == data
        assert result[0]["labels"] == ["Tax", "Business"]
        assert result[1]["nested"]["key"] == "value"


class TestCacheIntegration:
    """Integration tests for cache with realistic scenarios."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_transaction_workflow(self, temp_cache_dir):
        """Test typical transaction caching workflow."""
        cache = PocketSmithCache(cache_dir=temp_cache_dir)
        user_id = 123

        # 1. Cache categories (long TTL)
        cat_key = CacheKey.for_categories(user_id, flatten=True)
        categories = [{"id": 1, "title": "Food"}, {"id": 2, "title": "Transport"}]
        cache.set(cat_key, categories, ttl=CachePolicy.CATEGORIES.value)

        # 2. Cache transactions (short TTL for recent)
        txn_key = CacheKey.for_transactions(user_id, start_date="2024-01-01")
        transactions = [{"id": 100, "amount": -50}]
        cache.set(txn_key, transactions, ttl=CachePolicy.TRANSACTIONS_RECENT.value)

        # 3. Verify both are cached
        assert cache.get(cat_key) == categories
        assert cache.get(txn_key) == transactions

        # 4. Simulate transaction update - invalidate
        cache.invalidate_transactions(user_id)

        # 5. Transactions should be gone, categories should remain
        assert cache.get(txn_key) is None
        assert cache.get(cat_key) == categories

    def test_hit_rate_improves_with_use(self, temp_cache_dir):
        """Test that hit rate improves as cache is used."""
        cache = PocketSmithCache(cache_dir=temp_cache_dir)
        key = CacheKey.for_user(1)

        # First access - miss
        cache.get(key)
        assert cache.stats.hit_rate == 0.0

        # Cache the data
        cache.set(key, {"id": 1})

        # Subsequent accesses - hits
        for _ in range(9):
            cache.get(key)

        # 9 hits, 1 miss = 90% hit rate
        assert cache.stats.hit_rate == 0.9
