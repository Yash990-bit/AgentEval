# backend/app/utils/redis_cache.py
import os
import json
import redis
from typing import Optional, Any

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisCache:
    def __init__(self):
        try:
            self.client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        if not self.client:
            return False
        try:
            self.client.set(key, json.dumps(value), ex=expire_seconds)
            return True
        except Exception as e:
            print(f"Redis set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        if not self.client:
            return False
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error for key {key}: {e}")
            return False

redis_cache = RedisCache()
