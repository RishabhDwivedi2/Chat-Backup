# app/routers/chat_router.py

import logging
from fastapi import APIRouter, HTTPException, Depends, Request, Security
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime
from app.schemas.gpt import ChatRequest, ChatResponse
from app.services.gpt_service import GPTService
from app.services.chat_service import ChatService
from app.database import get_db
import json
from typing import Any, Dict, Optional
from app.utils.auth import get_current_user
from fastapi import UploadFile, File, Form
from app.services.agents.input_analyzer import InputAnalyzer
from app.services.agents.workflow_decider import WorkflowDecider
from app.services.agents.parent_agent import ParentAgent
from app.services.agents.title_generator import TitleGenerator
from app.services.attachment_service import AttachmentService
from app.services.artifact_service import ArtifactService
from sqlalchemy import select
from app.services.agents.response_structurer import ResponseStructurer
from app.models.base import Base  
from app.models.chat import (Message, ChatCollection, Artifact)
from app.models.chat import Conversation as ConversationDB  # Used a different name to avoid conflict
from app.config import settings 
from fastapi import Path
from app.schemas.chat import (
    ChatCollectionCreate, 
    ConversationCreate, 
    MessageCreate,
    Conversation,
    ConversationWithMessages,
    MessageWithDetails,
    ChatCollectionResponse,
    ConversationBrief,
    ArtifactResponse
)
from app.schemas.chat import Platform


router = APIRouter()
logger = logging.getLogger(__name__)

async def get_platform_from_request(request: Request) -> str:
    """Get platform from request state or default to web"""
    if hasattr(request, 'state') and hasattr(request.state, 'verified_data'):
        return request.state.verified_data.get('metadata', {}).get('platform_type', Platform.WEB)
    return Platform.WEB

@router.post("/", response_model=ChatResponse)
async def get_chat_response(
    request: Request,
    prompt: str = Form(...),
    max_tokens: Optional[int] = Form(100),
    temperature: Optional[float] = Form(0.7),
    conversation_id: Optional[int] = Form(None),
    parent_message_id: Optional[int] = Form(None),
    attachments: Optional[List[UploadFile]] = File(None),
    current_user: dict = Depends(get_current_user) if not settings.APP.TESTING_MODE else None,
    db: Session = Depends(get_db)
):
    """Enhanced chat endpoint with proper agent response handling"""

    try:
        user_email = settings.APP.TEST_USER_EMAIL if settings.APP.TESTING_MODE else current_user.get('sub')
        logger.info(f"Processing chat request for authenticated user: {user_email}")
        
        logger.debug(f"Received chat request with prompt: {prompt[:100]}...")
        if attachments:
            logger.debug(f"Received {len(attachments)} attachments")

        # Initialize services
        chat_service = ChatService(db)
        gpt_service = GPTService()
        title_generator = TitleGenerator(gpt_service=gpt_service)
        attachment_service = AttachmentService(db)
        artifact_service = ArtifactService(db)
        response_structurer = ResponseStructurer()

        start_time = datetime.utcnow()

        # Initialize conversation variables
        conversation = None
        conversation_history = []
        this_request_makes_platform_changed = False
        
        # Add platform detection debug section
        logger.info("=== PLATFORM DETECTION DEBUG ===")
        if hasattr(request.state, 'verified_data'):
            logger.info(f"Has verified_data: {True}")
            verified_data = request.state.verified_data
            logger.info(f"Verified data: {json.dumps(verified_data, indent=2)}")
        else:
            logger.info("No verified_data in request.state")
            logger.info(f"Request state attributes: {dir(request.state)}")
        
        # Platform detection logic
        platform = Platform.WEB  # Default to web
        thread_id = None
        subject = None
        
        if hasattr(request.state, 'verified_data'):
            verified_data = request.state.verified_data
            raw_platform = verified_data.get('platform', Platform.WEB)
            logger.info(f"Raw platform value: {raw_platform}")
            platform = Platform(raw_platform)
            
            metadata = verified_data.get('metadata', {})
            if platform == Platform.GMAIL:
                thread_id = metadata.get('thread_id')
                subject = metadata.get('subject')
                logger.info(f"Gmail metadata found - Thread ID: {thread_id}, Subject: {subject}")

                # Early check for Gmail requests to moved conversations
                if thread_id:
                    existing_conversation = chat_service.get_conversation_by_thread_id(thread_id)
                    if existing_conversation:
                        chat_collection = existing_conversation.collection
                        
                        # Check if this conversation has been moved to WEB
                        if chat_collection.is_platform_changed and chat_collection.platform_changed == Platform.WEB.value:
                            logger.info(f"Detected Gmail request for conversation moved to WEB. Thread ID: {thread_id}")
                            
                            # Create redirect URL
                            redirect_url = f"http://localhost:3001/chat/{existing_conversation.id}"
                            
                            # Create hardcoded response
                            response_data = {
                                "message": {
                                    "content": f"This conversation is no longer continued here. To continue, please click on this link: {redirect_url}",
                                    "conversation_id": existing_conversation.id,
                                    "is_redirect": True,
                                    "redirect_url": redirect_url
                                }
                            }
                            
                            logger.info("\n=== GMAIL REDIRECT RESPONSE ===")
                            logger.info(f"Conversation ID: {existing_conversation.id}")
                            logger.info(f"Collection ID: {chat_collection.id}")
                            logger.info(f"Redirect URL: {redirect_url}")
                            logger.info(f"Response Data: {json.dumps(response_data, indent=2)}")

                            return ChatResponse(
                                response=json.dumps(response_data),
                                conversation_id=existing_conversation.id,
                                message_id=0,  # No message created for redirect
                                this_request_makes_platform_changed=False
                            )
        
        logger.info(f"Final platform determination: {platform.value}")
        
        if conversation_id:
            conversation = chat_service.get_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            # Get associated chat collection and handle platform changes
            chat_collection = conversation.collection
            
            # Check platform change scenarios only if is_platform_changed is False
            if not chat_collection.is_platform_changed:
                # If current platform is WEB and collection platform is GMAIL
                if platform == Platform.WEB and chat_collection.platform == Platform.GMAIL.value:
                    logger.info(f"Detected platform change from GMAIL to WEB for collection {chat_collection.id}")
                    # Update chat collection
                    chat_collection.platform_changed = platform.value
                    chat_collection.is_platform_changed = True
                    db.commit()
                    this_request_makes_platform_changed = True
                    logger.info(f"Updated platform change status for collection {chat_collection.id}")
            
            # Use platform_changed value if is_platform_changed is True
            effective_platform = chat_collection.platform_changed if chat_collection.is_platform_changed else chat_collection.platform
            logger.info(f"Using effective platform: {effective_platform}")

            messages = chat_service.get_conversation_messages(conversation_id)
            conversation_history = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        else:
            # For Gmail platform, first check if there's an existing conversation with this thread_id
            if platform == Platform.GMAIL and thread_id:
                existing_conversation = chat_service.get_conversation_by_thread_id(thread_id)
                if existing_conversation:
                    conversation = existing_conversation
                    messages = chat_service.get_conversation_messages(existing_conversation.id)
                    conversation_history = [
                        {
                            "role": msg.role,
                            "content": msg.content,
                            "timestamp": msg.created_at.isoformat()
                        }
                        for msg in messages
                    ]
                    logger.info(f"Found existing conversation for Gmail thread: {thread_id}")
            
            # If no existing conversation found, create new collection and conversation
            if not conversation:
                # Determine title based on platform
                if platform == Platform.GMAIL and subject:
                    title = subject
                    logger.info(f"Using email subject as collection title: {title}")
                else:
                    title, _ = await title_generator.generate_unique_title(
                        prompt,
                        existing_titles=[],
                        conversation_history=conversation_history
                    )
                    logger.info(f"Generated title for web platform: {title}")
                
                # Create collection with proper platform and new fields
                collection_data = ChatCollectionCreate(
                    collection_name=title,
                    description="Auto-generated chat collection",
                    platform=platform.value,
                    platform_changed=None,  # Initialize as None
                    is_platform_changed=False  # Initialize as False
                )
                
                try:
                    new_collection = chat_service.create_chat_collection(
                        user_email=user_email,
                        collection_data=collection_data
                    )
                    logger.info(f"Created new collection for platform {platform.value}")
                except Exception as e:
                    logger.error(f"Failed to create chat collection: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to create chat collection"
                    )
                
                conversation_data = ConversationCreate(
                    collection_id=new_collection.id,
                    title=title,
                    description="Auto-generated conversation",
                    thread_id=thread_id if platform == Platform.GMAIL else None
                )
                conversation = chat_service.create_conversation(conversation_data)
                logger.info(f"Created new conversation with thread_id: {thread_id if platform == Platform.GMAIL else 'None'}")

        # Create user message
        user_message = chat_service.create_message(MessageCreate(
            conversation_id=conversation.id,
            role="user",
            content=prompt,
            message_type="query",
            message_metadata={"timestamp": start_time.isoformat()},
            has_artifact=False
        ))

        conversation_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": start_time.isoformat()
        })
        
        logger.info("\n=== ATTACHMENT DETAILS IN CHAT ROUTER ===")
        if attachments:
            logger.info(f"Number of attachments received: {len(attachments)}")
            for idx, attachment in enumerate(attachments):
                logger.info(f"\nAttachment {idx + 1}:")
                logger.info(f"Filename: {attachment.filename}")
                logger.info(f"Content Type: {attachment.content_type}")
                logger.info(f"Size: {attachment.size}")
                if hasattr(attachment, 'metadata'):
                    logger.info(f"Additional Metadata: {attachment.metadata}")
        else:
            logger.info("No attachments received")
            
        # Handle attachments
        stored_attachments = []
        if attachments:
            logger.info(f"Processing attachments in chat router: {[f.filename for f in attachments]}")
            stored_attachments = await attachment_service.process_attachments(
                files=attachments,
                message_id=user_message.id, 
                user_id=user_email
            )

            attachment_metadata = {
                "attachments": [{
                    "id": att.id,
                    "filename": att.original_filename,
                    "firebase_path": att.attachment_metadata.get('firebase_storage_path'),
                    "download_url": att.attachment_metadata.get('firebase_download_url')
                } for att in stored_attachments]
            }
            chat_service.update_message_metadata(user_message.id, attachment_metadata)

        # Input Analysis
        input_analyzer = InputAnalyzer(gpt_service=gpt_service)
        analysis_result = await input_analyzer.analyze_input(
            query=prompt,
            conversation_history=conversation_history,
            attachments=[{"file_path": file.filename, "file_size": file.size} for file in attachments] if attachments else None
        )
        
        logger.info("\n=== INPUT ANALYSIS IN CHAT ROUTER ===")
        logger.info(f"Input Analysis Result: {json.dumps(analysis_result, indent=2)}")

        # Workflow Decision
        workflow_decider = WorkflowDecider(gpt_service=gpt_service)
        decision_metadata = await workflow_decider.decide_workflow(analysis_result["metadata"])
        
        logger.info("\n=== WORKFLOW DECIDER IN CHAT ROUTER ===")
        logger.info(f"Workflow Decision Metadata: {json.dumps(decision_metadata, indent=2)}")
        
        logger.info("\n=== PARENT AGENT IN CHAT ROUTER ===")

        if decision_metadata["selected_agent"] == "ParentAgent":
            parent_agent = ParentAgent(gpt_service=gpt_service)
            parent_response_metadata = await parent_agent.process(
                prompt=prompt,
                metadata=decision_metadata,
                conversation_history=conversation_history
            )

            structured_response = await response_structurer.structure_response(
                parent_metadata=parent_response_metadata,
                original_prompt=prompt,
                conversation_history=conversation_history
            )

            logger.info(f"Structured Response Generated: {json.dumps(structured_response, indent=2)}")

            assistant_message_content = parent_response_metadata.get("content")
            if parent_response_metadata.get("has_artifact"):
                assistant_message_content = parent_response_metadata.get("summary", "Response contains an artifact.")

            if not assistant_message_content:
                assistant_message_content = "No response content available."

        else:  # AgenticWorkflowAgent or fallback
            assistant_message_content = await gpt_service.get_chat_response(
                prompt=prompt,
                conversation_history=conversation_history,
                max_tokens=max_tokens,
                temperature=temperature
            )

            structured_response = await response_structurer.structure_response(
                parent_metadata={
                    "content": assistant_message_content,
                    "has_artifact": False
                },
                original_prompt=prompt,
                conversation_history=conversation_history
            )

            logger.info(f"Structured Response Generated: {json.dumps(structured_response, indent=2)}")

        # Create assistant message
        assistant_message = chat_service.create_message(MessageCreate(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_message_content,
            message_type="response",
            parent_message_id=user_message.id,
            message_metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "agent": decision_metadata["selected_agent"],
                "structured_response": structured_response,
                "platform": platform.value
            },
            has_artifact=structured_response.get("has_artifact", False)  
        ))

        response_data = {
            "message": {
                "id": assistant_message.id,
                "conversation_id": conversation.id,
                "structured_response": structured_response,
                "this_request_makes_platform_changed": this_request_makes_platform_changed
            }
        }

        if structured_response.get("has_artifact") and decision_metadata["selected_agent"] == "ParentAgent":
            try:
                artifact = Artifact(
                    message_id=assistant_message.id,
                    component_type=structured_response.get("component_type", ""),
                    sub_type=structured_response.get("sub_type", ""),
                    title=structured_response.get("metadata", {}).get("title", "Untitled Artifact"),
                    description=structured_response.get("metadata", {}).get("description", ""),
                    data=structured_response.get("data", {}),
                    style=structured_response.get("style", {}),
                    configuration=structured_response.get("configuration", {})
                )

                db.add(artifact)
                db.commit()
                db.refresh(artifact)

                retrieved_artifact = artifact_service.get_artifact(artifact.id)
                structured_response["artifact_id"] = retrieved_artifact.id
                response_data["message"]["artifact_id"] = retrieved_artifact.id

            except Exception as e:
                logger.error(f"Failed to create artifact: {str(e)}")
                structured_response["artifact_error"] = "Failed to create artifact"

        logger.info("=== FINAL STRUCTURED RESPONSE AFTER ARTIFACT CREATION ===")
        logger.info(json.dumps(structured_response, indent=2))
        logger.info(f"Platform Change Made in This Request: {this_request_makes_platform_changed}")

        return ChatResponse(
            response=json.dumps(response_data),
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            this_request_makes_platform_changed=this_request_makes_platform_changed
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in chat processing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )

# Update the get_user_collections endpoint with null handling
@router.get("/collections", response_model=List[ChatCollectionResponse])
async def get_user_collections(
    request: Request,
    current_user: dict = Depends(get_current_user) if not settings.APP.TESTING_MODE else None,
    db: Session = Depends(get_db)
):
    try:
        user_email = settings.APP.TEST_USER_EMAIL if settings.APP.TESTING_MODE else current_user.get('sub')
        logger.debug(f"Fetching collections for user {user_email}")
        
        collections = (
            db.query(ChatCollection)
            .filter(
                ChatCollection.user_email == user_email,
                ChatCollection.is_active == True
            )
            .options(joinedload(ChatCollection.conversations))
            .order_by(ChatCollection.created_at.desc())
            .all()
        )
        
        collection_responses = []
        for collection in collections:
            conversations = [
                ConversationBrief(
                    id=conv.id,
                    title=conv.title,
                    last_message_at=conv.last_message_at,
                    message_count=conv.message_count
                )
                for conv in collection.conversations
                if conv.status != 'deleted'
            ]
            
            # Handle potential None values with defaults
            collection_response = ChatCollectionResponse(
                id=collection.id,
                collection_name=collection.collection_name,
                created_at=collection.created_at,
                conversation_count=collection.conversation_count,
                platform=collection.platform,
                platform_changed=collection.platform_changed if hasattr(collection, 'platform_changed') else None,
                is_platform_changed=collection.is_platform_changed if hasattr(collection, 'is_platform_changed') else None,
                conversations=conversations
            )
            collection_responses.append(collection_response)
        
        return collection_responses
        
    except Exception as e:
        logger.error(f"Error fetching user collections: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch collections: {str(e)}"
        )

# Update the get_conversation_details endpoint with null handling
@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation_details(
    conversation_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user) if not settings.APP.TESTING_MODE else None,
    db: Session = Depends(get_db)
):
    try:
        user_email = settings.APP.TEST_USER_EMAIL if settings.APP.TESTING_MODE else current_user.get('sub')
        logger.debug(f"Fetching conversation {conversation_id} for user {user_email}")
        
        conversation = (
            db.query(ConversationDB)
            .join(
                ChatCollection,
                ChatCollection.id == ConversationDB.collection_id
            )
            .filter(
                ConversationDB.id == conversation_id,
                ChatCollection.user_email == user_email
            )
            .first()
        )
        
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found or unauthorized access by {user_email}")
            raise HTTPException(
                status_code=404, 
                detail="Conversation not found or unauthorized access"
            )
        
        # Get the chat collection for platform info
        chat_collection = conversation.collection
        
        messages = (
            db.query(Message)
            .options(
                joinedload(Message.attachments),
                joinedload(Message.artifact)
            )
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .all()
        )
        
        formatted_messages = []
        for msg in messages:
            msg_dict = {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "content": msg.content,
                "role": msg.role,
                "message_type": msg.message_type,
                "created_at": msg.created_at,
                "parent_message_id": msg.parent_message_id,
                "is_edited": msg.is_edited,
                "edited_at": msg.edited_at,
                "edit_history": msg.edit_history,
                "message_metadata": msg.message_metadata,
                "attachments": [
                    {
                        "id": att.id,
                        "message_id": att.message_id,
                        "file_type": att.file_type,
                        "file_path": att.file_path,
                        "original_filename": att.original_filename,
                        "file_size": att.file_size,
                        "mime_type": att.mime_type,
                        "uploaded_at": att.uploaded_at,
                        "checksum": att.checksum,
                        "is_processed": att.is_processed,
                        "processing_error": att.processing_error,
                        "attachment_metadata": att.attachment_metadata
                    } for att in msg.attachments
                ] if msg.attachments else [],
                "artifacts": [
                    {
                        "id": msg.artifact.id,
                        "message_id": msg.artifact.message_id,
                        "component_type": msg.artifact.component_type,
                        "title": msg.artifact.title,
                        "description": msg.artifact.description,
                        "data": msg.artifact.data or {}, 
                        "style": msg.artifact.style,
                        "configuration": msg.artifact.configuration,
                        "created_at": msg.artifact.created_at
                    }
                ] if msg.artifact else []
            }
            formatted_messages.append(MessageWithDetails(**msg_dict))
        
        # Handle potential None values with defaults
        response_dict = {
            "id": conversation.id,
            "collection_id": conversation.collection_id,
            "title": conversation.title,
            "description": conversation.description,
            "created_at": conversation.created_at,
            "last_message_at": conversation.last_message_at,
            "status": conversation.status,
            "messages": formatted_messages,
            "platform": chat_collection.platform,
            "platform_changed": chat_collection.platform_changed if hasattr(chat_collection, 'platform_changed') else None,
            "is_platform_changed": chat_collection.is_platform_changed if hasattr(chat_collection, 'is_platform_changed') else None
        }
        
        conversation_response = ConversationWithMessages(**response_dict)
        return conversation_response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching conversation details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch conversation details: {str(e)}"
        )

@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact_details(
    artifact_id: int = Path(..., description="The ID of the artifact to retrieve"),
    current_user: dict = Depends(get_current_user) if not settings.APP.TESTING_MODE else None,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific artifact by its ID.
    Requires authentication with JWT token.
    """
    try:
        user_email = settings.APP.TEST_USER_EMAIL if settings.APP.TESTING_MODE else current_user.get('sub')
        logger.debug(f"Fetching artifact {artifact_id} details for user {user_email}")
        
        artifact = (
            db.query(Artifact)
            .join(Message, Message.id == Artifact.message_id)
            .join(ConversationDB, ConversationDB.id == Message.conversation_id)
            .join(ChatCollection, ChatCollection.id == ConversationDB.collection_id)
            .filter(
                Artifact.id == artifact_id,
                ChatCollection.user_email == user_email
            )
            .first()
        )
        
        if not artifact:
            logger.warning(f"Artifact {artifact_id} not found or unauthorized access by {user_email}")
            raise HTTPException(
                status_code=404,
                detail="Artifact not found or unauthorized access"
            )
            
        response = ArtifactResponse(
            id=artifact.id,
            message_id=artifact.message_id,
            component_type=artifact.component_type,
            sub_type=artifact.sub_type,
            title=artifact.title,
            description=artifact.description,
            data=artifact.data,
            style=artifact.style,
            configuration=artifact.configuration,
            created_at=artifact.created_at,
            updated_at=artifact.updated_at
        )
        
        logger.info(f"Successfully retrieved artifact {artifact_id} for user {user_email}")
        return response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching artifact details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch artifact details: {str(e)}"
        )        
        
@router.get("/conversations/{conversation_id}/artifacts", response_model=List[ArtifactResponse])
async def get_conversation_artifacts(
    conversation_id: int = Path(..., description="The ID of the conversation to get artifacts from"),
    current_user: dict = Depends(get_current_user) if not settings.APP.TESTING_MODE else None,
    db: Session = Depends(get_db)
):
    """
    Get all artifacts associated with a specific conversation.
    Requires authentication with JWT token.
    Returns a list of artifacts with their complete information.
    """
    try:
        user_email = settings.APP.TEST_USER_EMAIL if settings.APP.TESTING_MODE else current_user.get('sub')
        logger.debug(f"Fetching artifacts for conversation {conversation_id} for user {user_email}")
        
        conversation_exists = (
            db.query(ConversationDB)
            .join(ChatCollection)
            .filter(
                ConversationDB.id == conversation_id,
                ChatCollection.user_email == user_email
            )
            .first()
        )
        
        if not conversation_exists:
            logger.warning(f"Conversation {conversation_id} not found or unauthorized access by {user_email}")
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or unauthorized access"
            )
            
        artifacts = (
            db.query(Artifact)
            .join(Message, Message.id == Artifact.message_id)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc(), Artifact.created_at.desc())
            .all()
        )
        
        artifact_responses = []
        for artifact in artifacts:
            artifact_response = ArtifactResponse(
                id=artifact.id,
                message_id=artifact.message_id,
                component_type=artifact.component_type,
                sub_type=artifact.sub_type,
                title=artifact.title,
                description=artifact.description,
                data=artifact.data,
                style=artifact.style,
                configuration=artifact.configuration,
                created_at=artifact.created_at,
                updated_at=artifact.updated_at
            )
            artifact_responses.append(artifact_response)
            
        logger.info(f"Successfully retrieved {len(artifact_responses)} artifacts for conversation {conversation_id}")
        return artifact_responses
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching conversation artifacts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch conversation artifacts: {str(e)}"
        )