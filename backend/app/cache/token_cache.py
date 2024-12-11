# app/cache/token_cache.py

from cachetools import TTLCache
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from app.utils.jwt import decode_jwt

logger = logging.getLogger(__name__)

class TokenCache:
    def __init__(self, ttl: int = 900):  # 15 minutes default TTL
        self.cache = TTLCache(maxsize=1000, ttl=ttl)
        
    async def get_verified_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """Get verified token payload from cache"""
        return self.cache.get(token)
        
    async def cache_verified_token(self, token: str, payload: Dict[str, Any]) -> None:
        """Cache verified token payload"""
        self.cache[token] = {
            **payload,
            'cached_at': datetime.utcnow().isoformat(),
            'verification_status': 'verified'
        }

    async def invalidate_token(self, token: str) -> None:
        """Invalidate token from cache"""
        if token in self.cache:
            del self.cache[token]

class TokenVerifier:
    def __init__(self):
        self.token_cache = TokenCache()
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token with caching"""
        try:
            # Check cache first
            cached_payload = await self.token_cache.get_verified_payload(token)
            if cached_payload:
                logger.debug("Using cached token verification")
                return cached_payload

            # Verify token if not in cache
            payload = decode_jwt(token)
            if payload:
                # Cache successful verification
                await self.token_cache.cache_verified_token(token, payload)
                return payload
                
            return None

        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None