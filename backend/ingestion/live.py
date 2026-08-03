"""
Minimal in-memory TTL cache for live external API calls.

This is intentionally simple: a per-process dict, not Redis-backed. That's
fine for a single backend replica (which is what the shipped docker-compose
files run) - it just avoids hammering Yahoo/FRED on every dashboard refresh
within the same short window. If this is ever scaled to multiple backend
replicas, this cache should move to the Redis instance already provisioned
in the stack (REDIS_URL is set but currently unused anywhere in the app).
"""

import time
from typing import Callable, TypeVar

T = TypeVar("T")

_cache: dict[str, tuple[float, object]] = {}


def cached(key: str, ttl_seconds: float, fetch: Callable[[], T]) -> T:
    now = time.time()
    hit = _cache.get(key)
    if hit is not None and now - hit[0] < ttl_seconds:
        return hit[1]  # type: ignore[return-value]
    value = fetch()
    _cache[key] = (now, value)
    return value


def clear() -> None:
    """Mainly for tests."""
    _cache.clear()
