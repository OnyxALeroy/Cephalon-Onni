import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
import redis.asyncio as aioredis
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from models.worldstate import WorldState, parse_worldstate

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
WORLDSTATE_KEY = "worldstate:data"
WORLDSTATE_ETAG_KEY = "worldstate:etag"
WORLDSTATE_FETCHED_AT_KEY = "worldstate:fetched_at"


class WorldStateCache:
    """Redis-backed cache for worldstate data with MongoDB persistence."""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
        self._redis: Optional[aioredis.Redis] = None
        self._redis_available = True
        self._lock = asyncio.Lock()
    
    async def _get_redis(self) -> Optional[aioredis.Redis]:
        """Get or create Redis connection. Returns None if Redis is unavailable."""
        if not self._redis_available:
            return None
        if self._redis is None:
            try:
                self._redis = await aioredis.from_url(
                    REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self._redis.ping()
            except Exception as e:
                logger.warning(f"Redis unavailable: {e}. Using MongoDB-only mode.")
                self._redis = None
                self._redis_available = False
                return None
        return self._redis
    
    async def connect(self) -> None:
        """Initialize Redis connection."""
        try:
            r = await self._get_redis()
            if r:
                logger.info(f"Connected to Redis at {REDIS_URL}")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Falling back to MongoDB-only mode.")
            self._redis = None
            self._redis_available = False
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def get(self) -> Optional[WorldState]:
        """Get current worldstate from cache, fallback to MongoDB."""
        async with self._lock:
            r = await self._get_redis()
            if r:
                try:
                    payload_data = await r.get(WORLDSTATE_KEY)
                    if payload_data:
                        data = json.loads(payload_data)
                        return parse_worldstate(data)
                except Exception as e:
                    logger.warning(f"Redis get failed, trying MongoDB: {e}")
            
            doc = await self.collection.find_one({"_id": "worldstate"})
            if doc:
                try:
                    worldstate = parse_worldstate(doc["payload"])
                    
                    if r:
                        try:
                            await r.set(WORLDSTATE_KEY, json.dumps(doc["payload"]))
                            await r.set(WORLDSTATE_ETAG_KEY, doc.get("etag", ""))
                            await r.set(WORLDSTATE_FETCHED_AT_KEY, doc["fetched_at"].isoformat())
                        except Exception as e:
                            logger.warning(f"Failed to cache to Redis: {e}")
                    
                    return worldstate
                except Exception as e:
                    logger.error(f"Failed to parse cached worldstate: {e}")
            
            return None
    
    async def update(self, data: Dict[str, Any], etag: Optional[str] = None) -> None:
        """Update cache and persist to MongoDB."""
        async with self._lock:
            try:
                worldstate = parse_worldstate(data)
                now = datetime.utcnow()
                
                r = await self._get_redis()
                if r:
                    try:
                        pipe = r.pipeline()
                        pipe.set(WORLDSTATE_KEY, json.dumps(data))
                        if etag:
                            pipe.set(WORLDSTATE_ETAG_KEY, etag)
                        pipe.set(WORLDSTATE_FETCHED_AT_KEY, now.isoformat())
                        await pipe.execute()
                    except Exception as e:
                        logger.warning(f"Failed to update Redis cache: {e}")
                
                await self.collection.update_one(
                    {"_id": "worldstate"},
                    {"$set": {
                        "payload": data,
                        "parsed_payload": worldstate.model_dump(),
                        "fetched_at": now,
                        "etag": etag
                    }},
                    upsert=True
                )
                
                logger.info(f"WorldState updated at {now}")
                
            except Exception as e:
                logger.error(f"Failed to update worldstate cache: {e}")


class WorldStateFetcher:
    """Background fetcher for Warframe worldstate data."""
    
    def __init__(
        self,
        cache: WorldStateCache,
        url: str = "https://api.warframe.com/cdn/worldState.php",
        interval: int = 2,
        timeout: int = 5
    ):
        self.cache = cache
        self.url = url
        self.interval = interval
        self.timeout = timeout
        self._running = False
        self._last_etag: Optional[str] = None
        self.stop_requested = False
    
    async def start(self) -> None:
        """Start the background fetching loop."""
        if self._running:
            logger.warning("WorldState fetcher is already running")
            return
        
        self._running = True
        logger.info(f"Starting WorldState fetcher with {self.interval}s interval")
        
        while self._running:
            try:
                await self._fetch_once()
            except Exception as e:
                logger.error(f"WorldState fetch error: {e}")
            
            await asyncio.sleep(self.interval)
    
    async def stop(self) -> None:
        """Stop the background fetching loop."""
        self._running = False
        logger.info("WorldState fetcher stopped")
    
    async def _fetch_once(self) -> None:
        """Fetch worldstate data once and update cache if changed."""
        headers = {}
        if self._last_etag:
            headers["If-None-Match"] = self._last_etag
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(self.url, headers=headers)
                
                if response.status_code == 304:
                    # Not modified, skip update
                    return
                
                response.raise_for_status()
                data = response.json()
                etag = response.headers.get("etag")
                
                # Validate we have the expected structure
                if "WorldSeed" not in data:
                    raise ValueError("Invalid worldstate structure: missing WorldSeed")
                
                await self.cache.update(data, etag)
                self._last_etag = etag
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.error("WorldState endpoint not found (404)")
                elif e.response.status_code >= 500:
                    logger.warning(f"Server error fetching worldstate: {e.response.status_code}")
                else:
                    logger.error(f"HTTP error fetching worldstate: {e}")
            except httpx.RequestError as e:
                logger.error(f"Network error fetching worldstate: {e}")
            except ValueError as e:
                logger.error(f"Invalid JSON from worldstate endpoint: {e}")


# Global cache instance
_worldstate_cache: Optional[WorldStateCache] = None


def get_worldstate_cache() -> Optional[WorldStateCache]:
    """Get the global worldstate cache instance."""
    return _worldstate_cache


def set_worldstate_cache(cache: WorldStateCache) -> None:
    """Set the global worldstate cache instance."""
    global _worldstate_cache
    _worldstate_cache = cache