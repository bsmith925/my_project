from typing import Optional
import redis.asyncio as redis
from redis_om import get_redis_connection

from app.config.settings import settings


class RedisClient:
    """Redis client for the application."""
    
    _instance: Optional[redis.Redis] = None
    _om_instance: Optional[redis.Redis] = None
    
    @classmethod
    async def get_instance(cls) -> redis.Redis:
        """Get Redis client instance."""
        if cls._instance is None:
            # Use REDIS_URL if provided, otherwise construct from host, port, etc.
            if settings.REDIS_URL:
                cls._instance = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
            else:
                cls._instance = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True
                )
            
            # Test connection
            try:
                await cls._instance.ping()
            except redis.ConnectionError as e:
                raise ConnectionError(f"Failed to connect to Redis: {e}")
        
        return cls._instance
    
    @classmethod
    def get_om_connection(cls) -> redis.Redis:
        """Get Redis-OM connection."""
        if cls._om_instance is None:
            # Use REDIS_URL if provided, otherwise construct from host, port, etc.
            if settings.REDIS_URL:
                cls._om_instance = get_redis_connection(
                    url=settings.REDIS_URL,
                    decode_responses=True
                )
            else:
                cls._om_instance = get_redis_connection(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True
                )
        
        return cls._om_instance


async def get_redis() -> redis.Redis:
    """Get Redis client instance for dependency injection."""
    return await RedisClient.get_instance()