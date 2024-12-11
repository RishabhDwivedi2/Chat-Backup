# app/cache/session_manager.py

from cachetools import TTLCache
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, session_ttl: int = 120):  # 2 minutes TTL
        self.session_cache = TTLCache(maxsize=1000, ttl=session_ttl)
        self.request_cache = TTLCache(maxsize=1000, ttl=session_ttl)
        
    def _generate_session_id(self, token: str, user_id: str) -> str:
        """Generate unique session ID from token"""
        return hashlib.sha256(f"{token}:{user_id}".encode()).hexdigest()

    def _generate_request_hash(self, platform: str, prompt: str, metadata: Dict) -> str:
        """Generate hash for request caching"""
        request_data = f"{platform}:{prompt}:{json.dumps(metadata, sort_keys=True)}"
        return hashlib.sha256(request_data.encode()).hexdigest()

    async def get_or_create_session(self, token: str, user_payload: Dict) -> Tuple[str, Dict]:
        """Get existing session or create new one"""
        session_id = self._generate_session_id(token, user_payload['sub'])
        session = self.session_cache.get(session_id)
        
        if not session:
            logger.info(f"Creating new session for user: {user_payload['sub']}")
            session = {
                'user_id': user_payload['sub'],
                'email': user_payload.get('email'),
                'created_at': datetime.utcnow().isoformat(),
                'last_activity': datetime.utcnow().isoformat(),
                'platform_verified': False,
                'request_count': 0
            }
            self.session_cache[session_id] = session
            
        return session_id, session

    async def update_session(self, session_id: str, update_data: Dict) -> None:
        """Update existing session data"""
        if session_id in self.session_cache:
            session = self.session_cache[session_id]
            session.update(update_data)
            session['last_activity'] = datetime.utcnow().isoformat()
            self.session_cache[session_id] = session

    async def get_cached_request(self, platform: str, prompt: str, metadata: Dict) -> Optional[Dict]:
        """Get cached request response"""
        request_hash = self._generate_request_hash(platform, prompt, metadata)
        return self.request_cache.get(request_hash)

    async def cache_request(self, platform: str, prompt: str, metadata: Dict, response: Dict) -> None:
        """Cache request response"""
        request_hash = self._generate_request_hash(platform, prompt, metadata)
        self.request_cache[request_hash] = {
            'response': response,
            'cached_at': datetime.utcnow().isoformat()
        }

    async def should_bypass_verification(self, session_id: str) -> bool:
        """Check if should bypass verification layers"""
        session = self.session_cache.get(session_id)
        if not session:
            return False
            
        return (
            session.get('platform_verified', False) and 
            session.get('request_count', 0) > 0
        )

    async def increment_request_count(self, session_id: str) -> None:
        """Increment request count in session"""
        if session_id in self.session_cache:
            session = self.session_cache[session_id]
            session['request_count'] = session.get('request_count', 0) + 1
            self.session_cache[session_id] = session

session_manager = SessionManager(session_ttl=120)            