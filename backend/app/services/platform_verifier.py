# app/services/platform_verifier.py

from typing import Dict, Any, Optional, List
from fastapi import UploadFile, HTTPException, Request
from datetime import datetime
import logging
from app.cache.token_cache import TokenVerifier
from app.cache.session_manager import session_manager
import json

logger = logging.getLogger(__name__)

class PlatformVerifier:
    def __init__(self):
        self.supported_platforms = ["web", "telegram", "gmail"]

    async def verify_and_transform(
        self,
        platform: str,
        prompt: str,
        attachments: Optional[List[UploadFile]] = None,
        metadata: Dict[str, Any] = None,
        request: Request = None
    ):
        """Verify and transform request based on platform with session awareness"""
        
        logger.info(f"Starting platform verification for: {platform}")
        
        if platform not in self.supported_platforms:
            logger.error(f"Unsupported platform attempted: {platform}")
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

        try:
            # Check if we can use cached response
            if hasattr(request.state, 'bypass_verification') and request.state.bypass_verification:
                logger.info("Checking cached request response...")
                cached_response = await session_manager.get_cached_request(
                    platform=platform,
                    prompt=prompt,
                    metadata=metadata
                )
                if cached_response:
                    logger.info("Using cached request response")
                    return cached_response['response']
                logger.info("No cached response found, proceeding with verification")

            # Basic platform verification
            logger.info("Starting platform-specific verification...")
            verified_data = await self._verify_platform_request(platform, prompt, attachments, metadata)
            logger.info(f"Verification successful. Verified data: {verified_data}")
            
            # Transform to standard format
            logger.info("Transforming to standard format...")
            transformed_data = await self._transform_to_standard_format(platform, verified_data)
            
            # If we have a session, mark it as platform verified
            if hasattr(request.state, 'session_id'):
                await session_manager.update_session(
                    request.state.session_id,
                    {'platform_verified': True}
                )
            
            logger.info(f"Transformation complete. Final format: {transformed_data}")
            return transformed_data

        except Exception as e:
            logger.error(f"Platform verification failed: {str(e)}")
            raise HTTPException(status_code=400, detail="Platform verification failed")

    async def _verify_platform_request(
        self,
        platform: str,
        prompt: str,
        attachments: Optional[List[UploadFile]] = None,
        metadata: Dict[str, Any] = None
    ):
        """Verify platform-specific request format"""
        
        if platform == "web":
            return await self._verify_web_request(prompt, attachments, metadata)
        elif platform == "telegram":
            return await self._verify_telegram_request(prompt, metadata)
        elif platform == "gmail":
            return await self._verify_gmail_request(prompt, metadata)

    async def _verify_web_request(self, prompt: str, attachments: Optional[Any], metadata: Dict):
        """Verify web platform request"""
        logger.info("Verifying web request...")
        logger.info(f"Checking prompt: {prompt[:50]}...")
        
        if not prompt:
            logger.error("Empty prompt received")
            raise HTTPException(status_code=400, detail="Prompt is required for web platform")

        verified_attachments = []
        # Verify attachments if present
        if attachments:
            try:
                if isinstance(attachments, str):
                    # Handle JSON string attachment (metadata)
                    attachment_data = json.loads(attachments)
                    logger.info(f"Processing JSON attachment data: {attachment_data}")
                    verified_attachments.append(attachment_data)
                    
                elif isinstance(attachments, list):
                    # Handle list of attachments (could be UploadFile or dict)
                    for idx, attachment in enumerate(attachments):
                        if isinstance(attachment, UploadFile):
                            # Handle UploadFile type attachments
                            logger.info(f"Processing UploadFile attachment {idx + 1}: {attachment.filename}")
                            if attachment.filename and attachment.content_type:
                                verified_attachments.append({
                                    "name": attachment.filename,
                                    "type": attachment.content_type,
                                    "size": attachment.size,
                                    "is_upload": True
                                })
                        elif isinstance(attachment, (str, dict)):
                            # Handle string/dict type attachments (metadata)
                            att_data = attachment if isinstance(attachment, dict) else json.loads(attachment)
                            logger.info(f"Processing metadata attachment {idx + 1}: {att_data}")
                            verified_attachments.append(att_data)
                        else:
                            logger.error(f"Unknown attachment type: {type(attachment)}")
                            continue
                
                logger.info(f"Verified {len(verified_attachments)} attachments")
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing attachment JSON: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid attachment format")
            except Exception as e:
                logger.error(f"Error processing attachments: {str(e)}")
                raise HTTPException(status_code=400, detail="Error processing attachments")

        logger.info("Web request verification completed successfully")
        return {
            "prompt": prompt,
            "attachments": verified_attachments,
            "metadata": metadata or {},
            "user_info": metadata.get("user_info", {}) if metadata else {}
        }

    async def _transform_to_standard_format(self, platform: str, verified_data: Dict):
            """Transform to standard format while preserving both Gmail and web functionality"""
            # Base metadata structure
            platform_metadata = {
                "max_tokens": verified_data.get("metadata", {}).get("max_tokens", 100),
                "temperature": verified_data.get("metadata", {}).get("temperature", 0.7),
            }

            # For Gmail, add thread_id and subject to platform_metadata
            if platform == "gmail":
                platform_metadata.update({
                    "thread_id": verified_data["metadata"].get("thread_id"),
                    "subject": verified_data["metadata"].get("subject")
                })

            # For web, preserve conversation_id and parent_message_id
            if platform == "web":
                platform_metadata.update({
                    "conversation_id": verified_data.get("metadata", {}).get("conversation_id"),
                    "parent_message_id": verified_data.get("metadata", {}).get("parent_message_id")
                })

            return {
                "platform": platform,
                "prompt": verified_data["prompt"],
                "attachments": verified_data.get("attachments"),
                "metadata": {
                    "platform": platform,
                    "platform_type": platform,
                    "platform_metadata": platform_metadata,
                    "user_context": verified_data.get("user_info", {}),
                    "thread_id": verified_data["metadata"].get("thread_id") if platform == "gmail" else None,
                    "subject": verified_data["metadata"].get("subject") if platform == "gmail" else None,
                    "verified_at": str(datetime.utcnow())
                }
            }

    async def _verify_telegram_request(self, prompt: str, metadata: Dict):
        """Verify telegram platform request"""
        if not prompt:
            raise HTTPException(status_code=400, detail="Message text is required for telegram")
        
        required_fields = ["chat_id", "user_id"]
        if not all(field in metadata for field in required_fields):
            raise HTTPException(status_code=400, detail="Missing required telegram metadata")

        return {
            "prompt": prompt,
            "metadata": metadata,
            "user_info": metadata.get("user_info", {})
        }

    async def _verify_gmail_request(self, prompt: str, metadata: Dict):
            """Verify Gmail platform request"""
            if not prompt:
                raise HTTPException(status_code=400, detail="Email content required")
                    
            required_fields = ["email_id", "thread_id", "from_email", "subject"]
            if not all(field in metadata for field in required_fields):
                raise HTTPException(status_code=400, detail="Missing required Gmail metadata")

            # Additional Gmail-specific verifications
            if not isinstance(metadata.get("thread_id"), str) and metadata.get("thread_id") is not None:
                raise HTTPException(status_code=400, detail="Invalid thread_id format")

            if "@" not in metadata.get("from_email", ""):
                raise HTTPException(status_code=400, detail="Invalid email format")

            platform_metadata = {
                "max_tokens": metadata.get("platform_metadata", {}).get("max_tokens", 100),
                "temperature": metadata.get("platform_metadata", {}).get("temperature", 0.7),
                "thread_id": metadata.get("thread_id"),
                "subject": metadata.get("subject")
            }

            return {
                "prompt": prompt,
                "metadata": {
                    **metadata,
                    "platform": "gmail",
                    "platform_type": "gmail",
                    "platform_metadata": platform_metadata,
                    "verified_at": datetime.utcnow().isoformat()
                }
            }