"""
Redis client initialization and management
"""

import redis.asyncio as redis
from loguru import logger

from app.core.config import settings

# Global Redis client
redis_client = None


async def init_redis():
    """Initialize Redis connection with fallback"""
    global redis_client
    
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Test connection
        await redis_client.ping()
        logger.success("Redis initialized successfully!")
        
    except Exception as e:
        logger.warning(f"Failed to initialize Redis: {e}")
        logger.info("Continuing without Redis (some features may be limited)")
        redis_client = None


async def get_redis():
    """Get Redis client"""
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")
