"""Tests for health check cache system."""

import pytest
import time
from pathlib import Path
from scripts.health.cache import HealthCheckCache, CacheEntry


class TestCacheEntry:
    def test_cache_entry_not_expired(self):
        entry = CacheEntry(data={"score": 85}, timestamp=time.time(), ttl_seconds=3600)
        assert not entry.is_expired

    def test_cache_entry_expired(self):
        entry = CacheEntry(data={"score": 85}, timestamp=time.time() - 7200, ttl_seconds=3600)
        assert entry.is_expired


class TestHealthCheckCache:
    def test_set_and_get(self, tmp_path):
        cache = HealthCheckCache(cache_path=tmp_path / "cache.json")
        cache.set("test_key", {"value": 42})
        assert cache.get("test_key") == {"value": 42}

    def test_get_expired_returns_none(self, tmp_path):
        cache = HealthCheckCache(cache_path=tmp_path / "cache.json", default_ttl=1)
        cache.set("test_key", {"value": 42})
        time.sleep(1.1)
        assert cache.get("test_key") is None

    def test_invalidate(self, tmp_path):
        cache = HealthCheckCache(cache_path=tmp_path / "cache.json")
        cache.set("test_key", {"value": 42})
        cache.invalidate("test_key")
        assert cache.get("test_key") is None

    def test_invalidate_all(self, tmp_path):
        cache = HealthCheckCache(cache_path=tmp_path / "cache.json")
        cache.set("key1", {"value": 1})
        cache.set("key2", {"value": 2})
        cache.invalidate_all()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_persistence(self, tmp_path):
        cache_path = tmp_path / "cache.json"
        cache1 = HealthCheckCache(cache_path=cache_path)
        cache1.set("test_key", {"value": 42})

        # Create new instance to test loading
        cache2 = HealthCheckCache(cache_path=cache_path)
        assert cache2.get("test_key") == {"value": 42}

    def test_get_stats(self, tmp_path):
        cache = HealthCheckCache(cache_path=tmp_path / "cache.json")
        cache.set("key1", {"value": 1})
        cache.set("key2", {"value": 2})
        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["valid_entries"] == 2
