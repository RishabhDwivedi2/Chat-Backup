# app/services/redis/redis_service.py

from redis import Redis
from datetime import datetime, timedelta
import logging
from typing import Optional, Any, Dict
import json
from enum import Enum
import time

logger = logging.getLogger(__name__)

class RedisStatus(Enum):
    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"

class RedisHealthMetrics:
    def __init__(self):
        self.status = RedisStatus.UNKNOWN
        self.last_health_check = None
        self.connection_failures = 0
        self.operation_failures = 0
        self.last_failure_time = None
        self.consecutive_failures = 0

class RedisService:
    def __init__(self):
        self.redis_enabled = False
        self.redis_client = None
        self.connection_attempted = False
        self.health_metrics = RedisHealthMetrics()
        self.health_check_interval = 60  # seconds
        
    def is_enabled(self) -> bool:
        """Check if Redis is enabled and connected"""
        if not self.connection_attempted:
            return self._init_redis()
        return self.redis_enabled

    def _init_redis(self) -> bool:
        """Initialize Redis with enhanced error handling and metrics"""
        if self.connection_attempted and (datetime.now() - self.health_metrics.last_health_check).seconds < self.health_check_interval:
            return self.redis_enabled
            
        try:
            logger.info("🔄 Attempting Redis connection...")
            self.redis_client = Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection
            self.redis_client.ping()
            self.redis_enabled = True
            self.health_metrics.status = RedisStatus.HEALTHY
            self.health_metrics.connection_failures = 0
            self.health_metrics.consecutive_failures = 0
            logger.info("✅ Redis connection established successfully")
            
        except Exception as e:
            self.redis_enabled = False
            self.redis_client = None
            self.health_metrics.status = RedisStatus.DOWN
            self.health_metrics.connection_failures += 1
            self.health_metrics.consecutive_failures += 1
            self.health_metrics.last_failure_time = datetime.now()
            
            logger.error(f"❌ Redis connection failed: {str(e)}")
            logger.warning(f"⚠️ System running in degraded mode - Rate limiting and deduplication disabled")
            
            # Alert if consecutive failures are high
            if self.health_metrics.consecutive_failures >= 3:
                logger.critical(f"🚨 Critical: Redis has failed {self.health_metrics.consecutive_failures} times in a row")
            
        finally:
            self.connection_attempted = True
            self.health_metrics.last_health_check = datetime.now()
            return self.redis_enabled

    async def get_health_status(self) -> Dict:
        """Get detailed health status of Redis service"""
        return {
            "status": self.health_metrics.status.value,
            "last_health_check": self.health_metrics.last_health_check.isoformat() if self.health_metrics.last_health_check else None,
            "connection_failures": self.health_metrics.connection_failures,
            "operation_failures": self.health_metrics.operation_failures,
            "last_failure": self.health_metrics.last_failure_time.isoformat() if self.health_metrics.last_failure_time else None,
            "consecutive_failures": self.health_metrics.consecutive_failures,
            "redis_enabled": self.redis_enabled
        }

    async def get_rate_limit(self, key: str, window_seconds: int = 5) -> bool:
        """Enhanced rate limit check with failure tracking"""
        if not self.is_enabled():
            logger.warning("⚠️ Rate limiting bypassed - Redis unavailable")
            return False

        try:
            current_time = datetime.utcnow().timestamp()
            last_time = self.redis_client.get(f"rate_limit:{key}")

            if last_time is None:
                self.redis_client.set(f"rate_limit:{key}", current_time)
                return False

            time_passed = current_time - float(last_time)
            if time_passed < window_seconds:
                logger.info(f"🛑 Rate limit triggered for {key}")
                return True

            self.redis_client.set(f"rate_limit:{key}", current_time)
            return False

        except Exception as e:
            self._handle_operation_failure(f"Rate limit check failed: {str(e)}")
            return False

    async def was_processed(self, message_id: str) -> bool:
        """Check if a message was already processed with enhanced error handling"""
        if not self.is_enabled():
            logger.warning("⚠️ Message processing check bypassed - Redis unavailable")
            return False

        try:
            key = f"processed_message:{message_id}"
            result = bool(self.redis_client.exists(key))
            if result:
                logger.debug(f"✓ Message {message_id} was previously processed")
            return result
        except Exception as e:
            self._handle_operation_failure(f"Error checking processed status: {str(e)}")
            return False

    async def set_processed(self, message_id: str, expiry_hours: int = 24) -> bool:
        """Enhanced message processing status with failure tracking"""
        if not self.is_enabled():
            logger.warning("⚠️ Message processing status bypassed - Redis unavailable")
            return False

        try:
            key = f"processed_message:{message_id}"
            self.redis_client.set(
                key,
                datetime.utcnow().isoformat(),
                ex=expiry_hours * 3600
            )
            logger.debug(f"✅ Message {message_id} marked as processed")
            return True
        except Exception as e:
            self._handle_operation_failure(f"Failed to mark message as processed: {str(e)}")
            return False

    def _handle_operation_failure(self, error_message: str):
        """Centralized handling of Redis operation failures"""
        self.health_metrics.operation_failures += 1
        self.health_metrics.last_failure_time = datetime.now()
        
        if self.health_metrics.status == RedisStatus.HEALTHY:
            self.health_metrics.status = RedisStatus.DEGRADED
            
        logger.error(f"❌ Redis operation failed: {error_message}")
        
        # Trigger health check after failures
        if self.health_metrics.operation_failures % 5 == 0:
            logger.warning(f"⚠️ High number of Redis operation failures: {self.health_metrics.operation_failures}")
            self._init_redis()  # Attempt reconnection

    def close(self):
        """Enhanced cleanup with status update"""
        if self.redis_client:
            try:
                self.redis_client.close()
                logger.info("✅ Redis connection closed gracefully")
            except Exception as e:
                logger.error(f"❌ Error closing Redis connection: {str(e)}")
            finally:
                self.redis_enabled = False
                self.redis_client = None
                self.connection_attempted = False
                self.health_metrics.status = RedisStatus.UNKNOWN
    
    async def set_oauth_tokens(self, access_token: str, refresh_token: str, expiry: datetime = None):
        """Store OAuth tokens in Redis with expiration"""
        if not self.is_enabled():
            logger.warning("⚠️ OAuth token storage bypassed - Redis unavailable")
            return False

        try:
            # Store tokens with metadata
            token_data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "created_at": datetime.utcnow().isoformat(),
                "expiry": expiry.isoformat() if expiry else None
            }

            # Store in Redis with 24 hour expiry
            self.redis_client.setex(
                "oauth_tokens",
                24 * 3600,  # 24 hours in seconds
                json.dumps(token_data)
            )
            logger.info("✅ OAuth tokens stored successfully in Redis")
            return True

        except Exception as e:
            self._handle_operation_failure(f"Failed to store OAuth tokens: {str(e)}")
            return False

    async def get_oauth_tokens(self) -> Optional[Dict[str, Any]]:
        """Retrieve stored OAuth tokens from Redis"""
        if not self.is_enabled():
            logger.warning("⚠️ OAuth token retrieval bypassed - Redis unavailable")
            return None

        try:
            token_data = self.redis_client.get("oauth_tokens")
            if token_data:
                return json.loads(token_data)
            return None

        except Exception as e:
            self._handle_operation_failure(f"Failed to retrieve OAuth tokens: {str(e)}")
            return None

    async def clear_oauth_tokens(self) -> bool:
        """Clear stored OAuth tokens from Redis"""
        if not self.is_enabled():
            logger.warning("⚠️ OAuth token clearing bypassed - Redis unavailable")
            return False

        try:
            self.redis_client.delete("oauth_tokens")
            logger.info("✅ OAuth tokens cleared from Redis")
            return True

        except Exception as e:
            self._handle_operation_failure(f"Failed to clear OAuth tokens: {str(e)}")
            return False    
    
    async def store_value(self, key: str, value: str, expiry_seconds: int = None) -> bool:
        """Store a value in Redis with optional expiry"""
        if not self.is_enabled():
            logger.warning("⚠️ Redis storage bypassed - Redis unavailable")
            return False

        try:
            logger.info(f"Storing value for key: {key}")
            logger.debug(f"Value length: {len(value)} characters")
            
            if expiry_seconds:
                self.redis_client.setex(key, expiry_seconds, value)
                logger.info(f"Stored with expiry: {expiry_seconds} seconds")
            else:
                self.redis_client.set(key, value)
                logger.info("Stored without expiry")
                
            # Verify storage
            stored_value = self.redis_client.get(key)
            if stored_value:
                logger.info("✅ Value successfully verified in Redis")
                return True
            else:
                logger.error("❌ Value not found after storage")
                return False
                
        except Exception as e:
            self._handle_operation_failure(f"Failed to store value: {str(e)}")
            return False

    async def get_value(self, key: str) -> Optional[str]:
        """Get a value from Redis"""
        if not self.is_enabled():
            logger.warning("⚠️ Redis retrieval bypassed - Redis unavailable")
            return None

        try:
            logger.info(f"Attempting to retrieve value for key: {key}")
            value = self.redis_client.get(key)
            
            if value:
                logger.info(f"✅ Successfully retrieved value for key: {key}")
                logger.debug(f"Retrieved value length: {len(value)} characters")
                return value
            else:
                logger.warning(f"⚠️ No value found for key: {key}")
                return None
                
        except Exception as e:
            self._handle_operation_failure(f"Failed to get value: {str(e)}")
            return None

    async def delete_value(self, key: str) -> bool:
        """Delete a value from Redis"""
        if not self.is_enabled():
            logger.warning("⚠️ Redis deletion bypassed - Redis unavailable")
            return False

        try:
            logger.info(f"Attempting to delete key: {key}")
            result = self.redis_client.delete(key)
            
            if result:
                logger.info(f"✅ Successfully deleted key: {key}")
                return True
            else:
                logger.warning(f"⚠️ Key not found for deletion: {key}")
                return False
                
        except Exception as e:
            self._handle_operation_failure(f"Failed to delete value: {str(e)}")
            return False                