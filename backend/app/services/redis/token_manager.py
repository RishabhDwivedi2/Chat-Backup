# app/services/redis/token_manager.py

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict
import json
from app.services.redis.redis_service import RedisService

logger = logging.getLogger(__name__)

# Add OAuth2 scopes as a class constant
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify'
          ]

class TokenManager:
    def __init__(self):
        self.redis_service = RedisService()
        self.token_key = "gmail_oauth_tokens"
        self.backup_token_key = "gmail_oauth_tokens_backup"
        
    async def _backup_tokens(self, token_data: dict) -> None:
        """Keep a backup of working tokens"""
        try:
            await self.redis_service.store_value(
                self.backup_token_key,
                json.dumps(token_data),
                expiry_seconds=30 * 24 * 3600  # 30 days
            )
            logger.info("Successfully backed up tokens")
        except Exception as e:
            logger.error(f"Failed to backup tokens: {str(e)}")

    async def _restore_from_backup(self) -> Optional[Dict]:
        """Restore tokens from backup if main tokens fail"""
        try:
            logger.info("Attempting to restore tokens from backup...")
            backup_data = await self.redis_service.get_value(self.backup_token_key)
            if backup_data:
                logger.info("Successfully restored tokens from backup")
                return json.loads(backup_data)
        except Exception as e:
            logger.error(f"Failed to restore from backup: {str(e)}")
        return None

    async def get_valid_credentials(self, client_id: str, client_secret: str, token_uri: str) -> Optional[Credentials]:
        """Get valid credentials, refreshing if necessary"""
        try:
            # Try primary tokens first
            logger.info("Attempting to retrieve tokens from Redis...")
            token_data = await self._get_stored_tokens()
            
            # If primary tokens fail, try backup
            if not token_data:
                logger.warning("Primary tokens not found, attempting backup restoration...")
                token_data = await self._restore_from_backup()
                
            if not token_data:
                logger.warning("No tokens found in storage or backup")
                return None

            logger.info(f"Retrieved token data with keys: {list(token_data.keys())}")

            # Convert expiry from ISO format string to datetime
            expiry = None
            if token_data.get('expiry'):
                try:
                    expiry = datetime.fromisoformat(token_data['expiry'])
                    logger.info(f"Token expiry: {expiry}")
                except Exception as e:
                    logger.error(f"Error parsing expiry date: {str(e)}")

            try:
                credentials = Credentials(
                    token=token_data.get('access_token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_uri,
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=token_data.get('scopes', SCOPES),
                    expiry=expiry
                )
                logger.info("Successfully created credentials object")

                # If token needs refresh
                if credentials.expired and credentials.refresh_token:
                    logger.info("Token expired, attempting refresh...")
                    try:
                        await self._refresh_and_store_credentials(credentials)
                    except Exception as e:
                        logger.error(f"Error during token refresh: {str(e)}")
                        
                        # If refresh fails, try backup
                        backup_data = await self._restore_from_backup()
                        if backup_data:
                            logger.info("Attempting to use backup tokens...")
                            credentials = Credentials(
                                token=backup_data.get('access_token'),
                                refresh_token=backup_data.get('refresh_token'),
                                token_uri=token_uri,
                                client_id=client_id,
                                client_secret=client_secret,
                                scopes=backup_data.get('scopes', SCOPES),
                                expiry=datetime.fromisoformat(backup_data['expiry']) if backup_data.get('expiry') else None
                            )
                            
                            # Try refreshing with backup tokens
                            await self._refresh_and_store_credentials(credentials)
                else:
                    logger.info("Token is valid")

                return credentials

            except Exception as e:
                logger.error(f"Error creating credentials object: {str(e)}")
                return None

        except Exception as e:
            logger.error(f"Error getting valid credentials: {str(e)}")
            return None

    async def store_tokens(self, credentials: Credentials) -> bool:
        """Store tokens with backup"""
        try:
            logger.info("Preparing to store tokens in Redis...")
            token_data = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
                'created_at': datetime.utcnow().isoformat()
            }

            logger.info(f"Token data prepared with keys: {list(token_data.keys())}")

            # Store main tokens with 30-day expiry
            success = await self.redis_service.store_value(
                self.token_key,
                json.dumps(token_data),
                expiry_seconds=30 * 24 * 3600  # 30 days
            )

            if success:
                # Backup successful tokens
                await self._backup_tokens(token_data)
                logger.info("Successfully stored and backed up tokens")
                return True
            
            logger.error("Failed to store tokens")
            return False

        except Exception as e:
            logger.error(f"Error storing tokens: {str(e)}")
            return False

    async def _get_stored_tokens(self) -> Optional[Dict]:
        """Get stored tokens from Redis"""
        try:
            logger.info(f"Attempting to get tokens with key: {self.token_key}")
            token_data = await self.redis_service.get_value(self.token_key)
            
            if not token_data:
                logger.warning("No token data found in Redis")
                return None
                
            logger.info("Found token data in Redis, parsing JSON...")
            parsed_data = json.loads(token_data)
            logger.info(f"Successfully parsed token data with keys: {list(parsed_data.keys())}")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding token JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting stored tokens: {str(e)}")
            return None

    async def _refresh_and_store_credentials(self, credentials: Credentials) -> bool:
        """Refresh credentials and store new tokens"""
        try:
            logger.info("Attempting to refresh token...")
            request = Request()
            credentials.refresh(request)
            
            logger.info("Token refreshed, storing updated tokens...")
            # Store the refreshed tokens
            success = await self.store_tokens(credentials)
            if success:
                logger.info("Successfully refreshed and stored new tokens")
            else:
                logger.error("Failed to store refreshed tokens")
            return success

        except Exception as e:
            logger.error(f"Error refreshing credentials: {str(e)}")
            return False

    async def clear_tokens(self) -> bool:
        """Clear stored tokens"""
        try:
            logger.info("Attempting to clear tokens from Redis...")
            success = await self.redis_service.delete_value(self.token_key)
            if success:
                logger.info("Successfully cleared tokens from Redis")
            else:
                logger.info("Failed to clear tokens from Redis")
            return success
        except Exception as e:
            logger.error(f"Error clearing tokens: {str(e)}")
            return False