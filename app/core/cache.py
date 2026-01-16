import json
import redis
from typing import Optional, Any
from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception:
        return None


def set_cache(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set value in cache with TTL (default 1 hour)"""
    try:
        redis_client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception:
        return False


def delete_cache(key: str) -> bool:
    """Delete a key from cache"""
    try:
        redis_client.delete(key)
        return True
    except Exception:
        return False


def delete_cache_pattern(pattern: str) -> bool:
    """Delete all keys matching a pattern"""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception:
        return False
