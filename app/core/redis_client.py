import redis.asyncio as redis
import json
from typing import Any, Optional
from .config import settings

class RedisClient:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            await self.redis.ping()
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self.redis = None
    
    async def get(self, key: str) -> Optional[dict]:
        """Get data from Redis cache"""
        if not self.redis:
            return None
        
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set data in Redis cache with TTL"""
        if not self.redis:
            return False
        
        try:
            await self.redis.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            print(f"Redis set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self.redis:
            return False
        
        try:
            return bool(await self.redis.exists(key))
        except:
            return False

# Global Redis client instance
redis_client = RedisClient()
