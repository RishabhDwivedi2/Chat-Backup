# app/routers/gateway_router.py

from fastapi import APIRouter, Request, HTTPException, Depends, File, Form, UploadFile
from typing import Optional, List, Any
import logging
from sqlalchemy.orm import Session
from app.schemas.gpt import ChatResponse
from app.utils.auth import get_current_user
from app.database import get_db
from pydantic import BaseModel
from typing import Dict
from app.services.platform_verifier import PlatformVerifier
from app.cache.session_manager import session_manager
import json
from app.services.chat_service import ChatService
from app.config import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from google.oauth2.credentials import Credentials
from app.services.gmail_service import GmailService

logger = logging.getLogger(__name__)
router = APIRouter()
platform_verifier = PlatformVerifier()

async def forward_to_chat_endpoint(
    prompt: str,
    max_tokens: int,
    temperature: float,
    conversation_id: Optional[int],
    parent_message_id: Optional[int],
    attachments: Optional[List[dict]],
    current_user: dict,
    db,
    request: Request = None
):
    """Forward the request to chat endpoint with caching"""
    try:
        from app.routers.chat_router import get_chat_response
        from io import BytesIO
        import aiohttp
        from fastapi import UploadFile
        import tempfile
        import os
        
        # Convert attachment dicts to UploadFile objects
        upload_files = []
        if attachments:
            logger.info(f"Processing {len(attachments)} attachments in forward_to_chat_endpoint")
            for attachment in attachments:
                try:
                    # Create a temporary file to store the downloaded content
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(attachment['name'])[1]) as temp_file:
                        # Download the file from downloadUrl
                        async with aiohttp.ClientSession() as session:
                            async with session.get(attachment['downloadUrl']) as response:
                                if response.status == 200:
                                    content = await response.read()
                                    temp_file.write(content)
                                    temp_file.flush()
                        
                        # Create SpooledTemporaryFile for the UploadFile
                        file_obj = open(temp_file.name, 'rb')
                        
                        # Create UploadFile with correct parameters
                        upload_file = UploadFile(
                            file=file_obj,
                            filename=attachment['name']
                        )
                        
                        # Set additional attributes
                        upload_file.headers = {"content-type": attachment['type']}
                        upload_file.size = attachment['size']
                        upload_file.metadata = {
                            'storagePath': attachment['storagePath'],
                            'downloadUrl': attachment['downloadUrl'],
                            'fileDetails': attachment.get('fileDetails', {})
                        }
                        
                        upload_files.append(upload_file)
                        logger.info(f"Successfully processed attachment: {attachment['name']}")
                                
                except Exception as e:
                    logger.error(f"Error processing attachment {attachment['name']}: {str(e)}")
                    continue
                finally:
                    # Clean up the temporary file
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
        
        # Log the final state of upload_files
        logger.info(f"Number of attachments prepared for chat router: {len(upload_files)}")
        for upload_file in upload_files:
            logger.info(f"Prepared attachment: {upload_file.filename}, "
                      f"size: {upload_file.size}, "
                      f"content_type: {upload_file.headers.get('content-type')}")
        
        response = await get_chat_response(
            request=request,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            conversation_id=conversation_id,
            parent_message_id=parent_message_id,
            attachments=upload_files, 
            current_user=current_user,
            db=db
        )
        
        # Clean up any remaining file objects
        for upload_file in upload_files:
            await upload_file.close()
        
        # Cache successful response if we have a session
        if hasattr(request.state, 'session_id'):
            await session_manager.cache_request(
                platform="web",
                prompt=prompt,
                metadata={
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "conversation_id": conversation_id,
                    "parent_message_id": parent_message_id
                },
                response=response
            )
            
        return response
        
    except Exception as e:
        logger.error(f"Error forwarding to chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web", response_model=ChatResponse)
async def web_entry(
    request: Request,
    prompt: str = Form(...),
    max_tokens: Optional[int] = Form(100),
    temperature: Optional[float] = Form(0.7),
    conversation_id: Optional[int] = Form(None),
    parent_message_id: Optional[int] = Form(None),
    attachments: Optional[List[str]] = Form(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Web entry point for chat with session management"""
    try:
        logger.info("\n=== INCOMING REQUEST DETAILS ===")
        logger.info(f"Prompt: {prompt}")
        
        form_data = await request.form()
        logger.info(f"Raw form data: {form_data}")
        
        # Get all attachment values from form data
        attachment_values = form_data.getlist('attachments')
        logger.info(f"Number of attachment values received: {len(attachment_values)}")
        
        # Parse attachments
        processed_attachments = []
        if attachment_values:
            try:
                for attachment_str in attachment_values:
                    try:
                        attachment_data = json.loads(attachment_str)
                        processed_attachments.append(attachment_data)
                        logger.info(f"Successfully parsed attachment: {attachment_data.get('name')}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing attachment JSON: {str(e)}")
                        logger.error(f"Problematic attachment string: {attachment_str}")
                        continue
                
                logger.info("\n📎 ATTACHMENTS:")
                logger.info(f"Number of processed attachments: {len(processed_attachments)}")
                for idx, att in enumerate(processed_attachments, 1):
                    logger.info(f"\nAttachment {idx}:")
                    logger.info(f"Name: {att.get('name')}")
                    logger.info(f"Type: {att.get('type')}")
                    logger.info(f"Size: {att.get('size')}")
                    logger.info(f"Storage Path: {att.get('storagePath')}")
                
            except Exception as e:
                logger.error(f"Error processing attachments: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error processing attachments: {str(e)}")
        
        # First verify and transform through Platform Verifier
        verified_data = await platform_verifier.verify_and_transform(
            platform="web",
            prompt=prompt,
            attachments=processed_attachments,
            metadata={
                "user_id": current_user["sub"],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "conversation_id": conversation_id,
                "parent_message_id": parent_message_id
            },
            request=request
        )
        
        # Preserve platform-specific parameters
        platform_metadata = verified_data["metadata"].get("platform_metadata", {})
        if verified_data["platform"] == "web":
            # For web requests, preserve conversation_id and parent_message_id from metadata
            conversation_id = platform_metadata.get("conversation_id")
            parent_message_id = platform_metadata.get("parent_message_id")
        else:
            # For other platforms (like Gmail), these should be None
            conversation_id = None
            parent_message_id = None
        
        # Forward to chat endpoint
        return await forward_to_chat_endpoint(
            prompt=verified_data["prompt"],
            max_tokens=platform_metadata.get("max_tokens", 100),
            temperature=platform_metadata.get("temperature", 0.7),
            conversation_id=conversation_id,
            parent_message_id=parent_message_id,
            attachments=processed_attachments,
            current_user=current_user,
            db=db,
            request=request
        )
        
    except Exception as e:
        logger.error(f"Web entry error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
# Telegram Request Schema
class TelegramMessage(BaseModel):
    text: str
    chat: Dict[str, int]
    from_user: Dict[str, int]

class TelegramWebhookRequest(BaseModel):
    message: TelegramMessage

@router.post("/telegram/webhook", response_model=ChatResponse)
async def telegram_entry(
    request: TelegramWebhookRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Telegram webhook entry point
    """
    try:
        prompt = request.message.text
        # First verify and transform through Platform Verifier
        verified_data = await platform_verifier.verify_and_transform(
            platform="telegram",
            prompt=prompt,
            attachments=None,
            metadata={
                "user_id": current_user["sub"],
                "chat_id": request.message.chat["id"],
                "telegram_user_id": request.message.from_user["id"],
                "max_tokens": 100,
                "temperature": 0.7,
                "conversation_id": None,
                "parent_message_id": None
            }
        )
        
        # Then forward to chat endpoint with all required parameters
        return await forward_to_chat_endpoint(
            prompt=verified_data["prompt"],
            max_tokens=verified_data["metadata"]["platform_metadata"]["max_tokens"],
            temperature=verified_data["metadata"]["platform_metadata"]["temperature"],
            conversation_id=verified_data["metadata"]["platform_metadata"]["conversation_id"],
            parent_message_id=verified_data["metadata"]["platform_metadata"]["parent_message_id"],
            attachments=None,
            current_user=current_user,
            db=db
        )
    except Exception as e:
        logger.error(f"Telegram entry error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid telegram webhook")

async def gmail_entry(
    prompt: str,
    metadata: Dict[str, Any],
    current_user: dict,
    db: Session,
    request: Request = None
):
    """Gmail entry point for chat with proper verification"""
    try:
        logger.info("\n=== INCOMING GMAIL REQUEST ===")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Metadata: {metadata}")

        # First verify and transform through Platform Verifier
        verified_data = await platform_verifier.verify_and_transform(
            platform="gmail",
            prompt=prompt,
            attachments=None,
            metadata={
                **metadata,
                "platform": "gmail",
                "platform_type": "gmail",
                "thread_id": metadata.get("thread_id"),
                "subject": metadata.get("subject")
            },
            request=request
        )
        
        logger.info("=== VERIFIED DATA BEFORE CHAT ROUTER ===")
        logger.info(f"Verified data: {json.dumps(verified_data, indent=2)}")
        
        # Set verified data in request state
        if request:
            request.state.verified_data = verified_data
            logger.info("Set verified_data in request.state")
        
        # Forward to chat endpoint
        return await forward_to_chat_endpoint(
            prompt=verified_data["prompt"],
            max_tokens=verified_data["metadata"]["platform_metadata"].get("max_tokens", 100),
            temperature=verified_data["metadata"]["platform_metadata"].get("temperature", 0.7),
            conversation_id=verified_data["metadata"]["platform_metadata"].get("conversation_id"),
            parent_message_id=verified_data["metadata"]["platform_metadata"].get("parent_message_id"),
            attachments=None,
            current_user=current_user,
            db=db,
            request=request
        )

    except Exception as e:
        logger.error(f"Gmail entry error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))