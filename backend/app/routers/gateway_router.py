# app/routers/gateway_router.py

from fastapi import APIRouter, Request, HTTPException, Depends, File, Form, UploadFile
from typing import Optional, List
import logging
from app.schemas.gpt import ChatResponse
from app.utils.auth import get_current_user
from app.database import get_db
from pydantic import BaseModel
from typing import Dict
from app.services.platform_verifier import PlatformVerifier
from app.cache.session_manager import session_manager
import json

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
        
        # Convert attachment dict to UploadFile objects
        upload_files = []
        if attachments:
            logger.info(f"Processing attachments in forward_to_chat_endpoint: {attachments}")
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
                            'fileDetails': attachment['fileDetails']
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
    attachments: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Web entry point for chat with session management"""
    try:
        logger.info("\n=== INCOMING REQUEST DETAILS ===")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Raw form data: {await request.form()}")
        
        # Parse attachments
        processed_attachments = None
        if attachments:
            try:
                # If attachments is a single object
                attachment_data = json.loads(attachments)
                logger.info(f"Successfully parsed attachment data: {attachment_data}")
                processed_attachments = [attachment_data]  # Wrap single attachment in list
                
                logger.info("\n📎 ATTACHMENTS:")
                logger.info(f"Processed attachments: {processed_attachments}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing attachments JSON: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid attachment format")
        
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
        
        # Forward to chat endpoint with processed attachments
        return await forward_to_chat_endpoint(
            prompt=verified_data["prompt"],
            max_tokens=verified_data["metadata"]["platform_metadata"]["max_tokens"],
            temperature=verified_data["metadata"]["platform_metadata"]["temperature"],
            conversation_id=verified_data["metadata"]["platform_metadata"]["conversation_id"],
            parent_message_id=verified_data["metadata"]["platform_metadata"]["parent_message_id"],
            attachments=processed_attachments,  # Pass the processed attachments
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

# Gmail Request Schema
class GmailMessage(BaseModel):
    data: str
    messageId: str

class GmailWebhookRequest(BaseModel):
    message: GmailMessage

@router.post("/gmail/webhook", response_model=ChatResponse)
async def gmail_entry(
    request: GmailWebhookRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Gmail webhook entry point
    """
    try:
        prompt = request.message.data
        # First verify and transform through Platform Verifier
        verified_data = await platform_verifier.verify_and_transform(
            platform="gmail",
            prompt=prompt,
            attachments=None,
            metadata={
                "user_id": current_user["sub"],
                "email_id": request.message.messageId,
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
        logger.error(f"Gmail entry error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid gmail webhook")