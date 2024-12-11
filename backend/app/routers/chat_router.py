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
from app.models.chat import (Message, ChatCollection)
from app.models.chat import Conversation as ConversationDB  # Used a different name to avoid conflict
from app.schemas.chat import (
    ChatCollectionCreate, 
    ConversationCreate, 
    MessageCreate,
    Conversation,
    ConversationWithMessages,
    MessageWithDetails,
    ChatCollectionResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ChatResponse)
async def get_chat_response(
    prompt: str = Form(...),
    max_tokens: Optional[int] = Form(100),
    temperature: Optional[float] = Form(0.7),
    conversation_id: Optional[int] = Form(None),
    parent_message_id: Optional[int] = Form(None),
    attachments: Optional[List[UploadFile]] = File(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enhanced chat endpoint with proper agent response handling"""

    try:
        user_email = current_user['sub']
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
        response_structurer = ResponseStructurer(gpt_service=gpt_service)

        start_time = datetime.utcnow()

        # Handle conversation and history
        conversation = None
        conversation_history = []
        
        if conversation_id:
            conversation = chat_service.get_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
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
            existing_titles_query = select(ChatCollection.collection_name)
            existing_titles = [row[0] for row in db.execute(existing_titles_query).fetchall()]
            
            # Generate unique title
            title, is_fallback = await title_generator.generate_unique_title(
                prompt,
                existing_titles=existing_titles,
                conversation_history=conversation_history
            )
            
            if is_fallback:
                logger.warning(f"Used fallback title generation for query: {prompt}")
            
            collection_data = ChatCollectionCreate(
                collection_name=title,
                description="Auto-generated chat collection"
            )
            
            try:
                new_collection = chat_service.create_chat_collection(
                    user_email=user_email,
                    collection_data=collection_data
                )
            except Exception as e:
                logger.error(f"Failed to create chat collection: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create chat collection due to title conflict"
                )
            
            conversation_data = ConversationCreate(
                collection_id=new_collection.id,
                title=title,
                description="Auto-generated conversation"
            )
            conversation = chat_service.create_conversation(conversation_data)

        # Store user message
        user_message = chat_service.create_message(MessageCreate(
            conversation_id=conversation.id,
            role="user",
            content=prompt,
            message_type="query",
            message_metadata={"timestamp": start_time.isoformat()},
            has_artifact=False
        ))

        # Add current message to conversation history
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
            
        logger.debug(f"Received chat request with prompt: {prompt[:100]}...")
        
        # Handle attachments
        stored_attachments = []
        if attachments:
            logger.info(f"Processing attachments in chat router: {[f.filename for f in attachments]}")
            stored_attachments = await attachment_service.process_attachments(
                files=attachments,
                message_id=user_message.id, 
                user_id=user_email
            )

            # Update message metadata with attachment info
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

        # Workflow Decision
        workflow_decider = WorkflowDecider(gpt_service=gpt_service)
        decision_metadata = await workflow_decider.decide_workflow(analysis_result["metadata"])
        
        response_data = {
            "message": {
                "content": None,
                "conversation_id": conversation.id,
                "has_artifact": False,
                "artifact_id": None
            }
        }

        if decision_metadata["selected_agent"] == "ParentAgent":
            parent_agent = ParentAgent(gpt_service=gpt_service)
            parent_response_metadata = await parent_agent.process(
                prompt=prompt,
                metadata=decision_metadata,
                conversation_history=conversation_history
            )

            # Process through ResponseStructurer
            structured_response = await response_structurer.structure_response(
                parent_metadata=parent_response_metadata,
                original_prompt=prompt,
                conversation_history=conversation_history
            )

            # Log the structured response
            logger.info(f"Structured Response Generated: {json.dumps(structured_response, indent=2)}")

            assistant_message_content = parent_response_metadata.get("content")
            if parent_response_metadata.get("has_artifact"):
                assistant_message_content = parent_response_metadata.get("summary", "Response contains an artifact.")

            if not assistant_message_content:
                assistant_message_content = "No response content available."

        else:  # AgenticWorkflowAgent or fallback
            # Get direct response for simple queries
            assistant_message_content = await gpt_service.get_chat_response(
                prompt=prompt,
                conversation_history=conversation_history,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # Process through ResponseStructurer even for simple responses
            structured_response = await response_structurer.structure_response(
                parent_metadata={
                    "content": assistant_message_content,
                    "has_artifact": False
                },
                original_prompt=prompt,
                conversation_history=conversation_history
            )

            # Log the structured response
            logger.info(f"Structured Response Generated: {json.dumps(structured_response, indent=2)}")

        # Store assistant message with structured metadata
        assistant_message = chat_service.create_message(MessageCreate(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_message_content,
            message_type="response",
            parent_message_id=user_message.id,
            message_metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "agent": decision_metadata["selected_agent"],
                "structured_response": structured_response
            },
            has_artifact=structured_response.get("has_artifact", False)  # Use structured response's has_artifact
        ))

        # Build response using structured response format
        response_data = {
            "message": {
                "id": assistant_message.id,
                "conversation_id": conversation.id,
                "structured_response": structured_response  # Include the entire structured response
            }
        }

        # Handle artifact creation if needed
        if structured_response.get("has_artifact") and decision_metadata["selected_agent"] == "ParentAgent":
            try:
                artifact = await artifact_service.create_artifact_from_parent_response(
                    message_id=assistant_message.id,
                    parent_response=parent_response_metadata
                )
                if artifact:
                    response_data["message"]["artifact_id"] = artifact.id
                    structured_response["artifact_id"] = artifact.id  # Add artifact ID to structured response
            except Exception as e:
                logger.error(f"Failed to create artifact: {str(e)}")
                structured_response["artifact_error"] = "Failed to create artifact"

        logger.info(f"Response Data: {json.dumps(response_data, indent=2)}")

        return ChatResponse(
            response=json.dumps(response_data),
            conversation_id=conversation.id,
            message_id=assistant_message.id
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in chat processing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )
        

@router.get("/collections", response_model=List[ChatCollectionResponse])
async def get_user_collections(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all chat collections for the authenticated user.
    Returns a list of collections with their IDs and names.
    """
    try:
        user_email = current_user.get('sub')
        logger.debug(f"Fetching collections for user {user_email}")
        
        collections = (
            db.query(ChatCollection)
            .filter(
                ChatCollection.user_email == user_email,
                ChatCollection.is_active == True
            )
            .order_by(ChatCollection.created_at.desc())
            .all()
        )
        
        # Format the response using the schema
        collection_responses = [
            ChatCollectionResponse(
                id=collection.id,
                collection_name=collection.collection_name,
                created_at=collection.created_at,
                conversation_count=collection.conversation_count
            ) for collection in collections
        ]
        
        logger.info(f"Successfully retrieved {len(collection_responses)} collections for user {user_email}")
        return collection_responses
        
    except Exception as e:
        logger.error(f"Error fetching user collections: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch collections: {str(e)}"
        )

        
@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation_details(
    conversation_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete conversation details including all messages, attachments, and artifacts.
    Requires authentication with JWT token.
    """
    try:
        user_email = current_user.get('sub')
        logger.debug(f"Fetching conversation {conversation_id} for user {user_email}")
        
        # Use ConversationDB (the model) instead of Conversation
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
        
        # Query messages with eager loading
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
        
        # Format messages
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
                        "data": msg.artifact.data,
                        "style": msg.artifact.style,
                        "configuration": msg.artifact.configuration,
                        "created_at": msg.artifact.created_at
                    }
                ] if msg.artifact else []
            }
            formatted_messages.append(MessageWithDetails(**msg_dict))
        
        # Create response
        response_dict = {
            "id": conversation.id,
            "collection_id": conversation.collection_id,
            "title": conversation.title,
            "description": conversation.description,
            "created_at": conversation.created_at,
            "last_message_at": conversation.last_message_at,
            "status": conversation.status,
            "messages": formatted_messages
        }
        
        conversation_response = ConversationWithMessages(**response_dict)
        
        logger.info(f"Successfully retrieved conversation {conversation_id} for user {user_email}")
        return conversation_response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching conversation details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch conversation details: {str(e)}"
        )