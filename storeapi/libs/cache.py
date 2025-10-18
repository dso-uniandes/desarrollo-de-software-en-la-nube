import json
from functools import lru_cache
from typing import Any, Optional

from storeapi.config import config

try:
    import redis
except Exception:  # pragma: no cover
    redis = None  # type: ignore


@lru_cache()
def _get_client() -> Optional["redis.Redis[bytes]"]:
    if not config.REDIS_URL or redis is None:
        return None
    return redis.from_url(config.REDIS_URL, decode_responses=False)


async def cache_get(key: str) -> Optional[Any]:
    client = _get_client()
    if client is None:
        return None
    data = client.get(key)
    if data is None:
        return None
    try:
        return json.loads(data)
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
    client = _get_client()
    if client is None:
        return
    payload = json.dumps(value, default=str)
    if ttl_seconds and ttl_seconds > 0:
        client.setex(key, ttl_seconds, payload)
    else:
        client.set(key, payload)


async def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys that match the given pattern"""
    client = _get_client()
    if client is None:
        return
    try:
        # Find all keys that match the pattern
        keys = client.keys(pattern)
        if keys:
            # Delete all found keys
            client.delete(*keys)
    except Exception:
        # If there's any error, just continue
        pass

