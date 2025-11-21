"""Cache system for health check results."""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class CacheEntry:
    """Single cache entry with expiration."""

    data: dict[str, Any]
    timestamp: float
    ttl_seconds: int = 3600  # 1 hour default

    @property
    def is_expired(self) -> bool:
        return time.time() > self.timestamp + self.ttl_seconds


class HealthCheckCache:
    """Cache for health check results."""

    def __init__(self, cache_path: Optional[Path] = None, default_ttl: int = 3600):
        self.cache_path = cache_path or Path("data/health/cache.json")
        self.default_ttl = default_ttl
        self._cache: dict[str, CacheEntry] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cache from disk."""
        if self.cache_path.exists():
            try:
                data = json.loads(self.cache_path.read_text())
                for key, entry_data in data.items():
                    entry = CacheEntry(
                        data=entry_data["data"],
                        timestamp=entry_data["timestamp"],
                        ttl_seconds=entry_data.get("ttl_seconds", self.default_ttl),
                    )
                    if not entry.is_expired:
                        self._cache[key] = entry
            except (json.JSONDecodeError, KeyError):
                self._cache = {}

    def _save_cache(self) -> None:
        """Persist cache to disk."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            key: {
                "data": entry.data,
                "timestamp": entry.timestamp,
                "ttl_seconds": entry.ttl_seconds,
            }
            for key, entry in self._cache.items()
            if not entry.is_expired
        }
        self.cache_path.write_text(json.dumps(data, indent=2))

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value if not expired."""
        entry = self._cache.get(key)
        if entry and not entry.is_expired:
            return entry.data
        elif entry:
            del self._cache[key]
        return None

    def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Cache a value with TTL."""
        self._cache[key] = CacheEntry(
            data=data,
            timestamp=time.time(),
            ttl_seconds=ttl or self.default_ttl,
        )
        self._save_cache()

    def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry."""
        if key in self._cache:
            del self._cache[key]
            self._save_cache()

    def invalidate_all(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
        self._save_cache()

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        valid = sum(1 for e in self._cache.values() if not e.is_expired)
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid,
            "expired_entries": len(self._cache) - valid,
        }
