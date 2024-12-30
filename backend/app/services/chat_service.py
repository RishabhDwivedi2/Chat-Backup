# app/services/chat_service.py

from datetime import datetime
from sqlalchemy.orm import Session
from app.models.chat import ChatCollection, Conversation, Message
from app.schemas.chat import ChatCollectionCreate, ConversationCreate, MessageCreate
from fastapi import HTTPException
import logging
from typing import List, Dict, Any, Optional
from app.schemas.chat import AttachmentCreate, Attachment

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_chat_collection(self, user_email: str, collection_data: ChatCollectionCreate) -> ChatCollection:
        """Create a new chat collection for a user"""
        try:
            collection = ChatCollection(
                user_email=user_email,
                collection_name=collection_data.collection_name,
                description=collection_data.description,
                platform=collection_data.platform,  # Add this line
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                is_active=True,
                conversation_count=0
            )
            
            self.db.add(collection)
            self.db.commit()
            self.db.refresh(collection)
            
            logger.info(f"Created new collection '{collection_data.collection_name}' for user {user_email} on platform {collection_data.platform}")
            return collection
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating chat collection: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create chat collection: {str(e)}"
            )

    def get_user_collections(self, user_email: str) -> list[ChatCollection]:
        """Get all active collections for a user"""
        try:
            collections = self.db.query(ChatCollection).filter(
                ChatCollection.user_email == user_email,
                ChatCollection.is_active == True
            ).all()
            return collections
        except Exception as e:
            logger.error(f"Error fetching user collections: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch user collections"
            )
    
    def create_message(self, message_data: MessageCreate) -> Message:
        """Create a new message with artifact flag"""
        try:
            conversation = self.db.query(Conversation).filter_by(id=message_data.conversation_id).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            message = Message(
                conversation_id=message_data.conversation_id,
                role=message_data.role,
                content=message_data.content,
                message_type=message_data.message_type,
                created_at=datetime.utcnow(),
                parent_message_id=getattr(message_data, 'parent_message_id', None),
                is_edited=False,
                message_metadata=message_data.message_metadata,
                has_artifact=message_data.has_artifact  
            )
            
            self.db.add(message)
            self.db.flush() 
            
            conversation.message_count += 1
            conversation.last_message_at = message.created_at
            
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Created message with ID: {message.id}, has_artifact: {message.has_artifact}")
            return message
            
        except HTTPException as he:
            self.db.rollback()
            raise he
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating message: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")


    def get_message(self, message_id: int) -> Message:
        """Get a message by ID including metadata"""
        message = self.db.query(Message).filter_by(id=message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    
    def update_message_metadata(self, message_id: int, metadata: Dict[str, Any]) -> Message:
        """Update just the metadata of a message"""
        try:
            message = self.get_message(message_id)
            
            message.message_metadata = metadata
            message.edited_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Updated metadata for message {message_id}: {metadata}")
            return message
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating message metadata: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update message metadata: {str(e)}")


    def create_conversation(self, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation with all required fields"""
        try:
            current_time = datetime.utcnow()
            
            conversation = Conversation(
                collection_id=conversation_data.collection_id,
                title=conversation_data.title,
                description=conversation_data.description,
                thread_id=conversation_data.thread_id,  # Add this line
                created_at=current_time,
                last_message_at=current_time,
                status='active',
                message_count=0
            )
            
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            
            collection = self.db.query(ChatCollection).filter_by(id=conversation_data.collection_id).first()
            if collection:
                collection.conversation_count += 1
                collection.last_accessed = current_time
                self.db.commit()
            
            return conversation
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating conversation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create conversation: {str(e)}"
            )

    def get_or_create_default_collection(self) -> ChatCollection:
        """Get or create a default collection for chat messages"""
        user_email = "default@user.com"
        default_collection = self.get_collection_by_name(user_email, "Default Collection")
        if not default_collection:
            collection = ChatCollectionCreate(
                collection_name="Default Collection",
                description="Default collection for chat messages"
            )
            default_collection = self.create_chat_collection(user_email, collection)
        return default_collection

    def get_collection_by_name(self, user_email: str, collection_name: str) -> ChatCollection:
        return self.db.query(ChatCollection).filter(
            ChatCollection.user_email == user_email,
            ChatCollection.collection_name == collection_name,
            ChatCollection.is_active == True
        ).first()

    def get_conversation(self, conversation_id: int) -> Conversation:
        """Fetch a conversation by its ID."""
        try:
            conversation = self.db.query(Conversation).filter_by(id=conversation_id).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            return conversation
        except Exception as e:
            logger.error(f"Error fetching conversation: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch conversation")

    def get_conversation_messages(self, conversation_id: int) -> List[Message]:
        """
        Get all messages for a conversation to maintain context.
        """
        try:
            messages = self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
            return messages
        except Exception as e:
            logger.error(f"Error fetching conversation messages: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch conversation messages")
        
    def update_message_artifact_flag(self, message_id: int, has_artifact: bool) -> Message:
        """Update the has_artifact flag for a message"""
        try:
            message = self.get_message(message_id)
            if not message:
                raise HTTPException(status_code=404, detail="Message not found")
            
            message.has_artifact = has_artifact
            message.edited_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Updated has_artifact flag for message {message_id} to {has_artifact}")
            return message
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating message artifact flag: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to update message artifact flag: {str(e)}"
            )
    
    def create_attachment(self, attachment_data: AttachmentCreate) -> Attachment:
        """Store an attachment in the database."""
        try:
            attachment = Attachment(
                message_id=attachment_data.message_id,
                file_type=attachment_data.file_type,
                file_path=attachment_data.file_path,
                original_filename=attachment_data.original_filename,
                file_size=attachment_data.file_size,
                mime_type=attachment_data.mime_type,
                checksum=attachment_data.checksum,
                attachment_metadata=attachment_data.attachment_metadata
            )

            self.db.add(attachment)
            self.db.commit()
            self.db.refresh(attachment)
            
            logger.info(f"Stored attachment '{attachment.original_filename}' for message {attachment.message_id}")
            return attachment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing attachment: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store attachment: {str(e)}"
            )            

    def get_collection_and_first_conversation(self, user_email: str, subject: str) -> Optional[int]:
        """
        Given a subject, see if there's a matching ChatCollection for this user,
        and if so return the first conversation ID. Else return None.
        """
        try:
            collection = self.db.query(ChatCollection).filter_by(
                user_email=user_email,
                collection_name=subject,
                is_active=True
            ).first()

            if collection and collection.conversations:
                # Let's just use the first conversation in that collection
                return collection.conversations[0].id
            else:
                return None
        except Exception as e:
            logger.error(f"Error in get_collection_and_first_conversation: {str(e)}")
            return None
    
    def get_conversation_by_thread_id(self, thread_id: str) -> Optional[Conversation]:
        """Get a conversation by its Gmail thread ID"""
        try:
            return self.db.query(Conversation).filter_by(thread_id=thread_id).first()
        except Exception as e:
            logger.error(f"Error fetching conversation by thread_id: {str(e)}")
            return None    
        