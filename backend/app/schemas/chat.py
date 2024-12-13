# app/schemas/chat.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class MessageType(str, Enum):
    TEXT = "text"
    QUERY = "query"
    RESPONSE = "response"

class FileType(str, Enum):
    MEDIA = "media"
    DOCUMENT = "document"
    VOICE = "voice"

class ArtifactType(str, Enum):
    CODE = "code"
    MARKDOWN = "markdown"
    HTML = "html"
    SVG = "svg"
    MERMAID = "mermaid"
    REACT = "react"

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ChatCollectionBase(BaseModel):
    collection_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class ChatCollectionCreate(ChatCollectionBase):
    pass

class ChatCollection(ChatCollectionBase):
    id: int
    user_email: str 
    created_at: datetime
    last_accessed: datetime
    is_active: bool
    conversation_count: int

    class Config:
        from_attributes = True 

# Conversation Schemas
class ConversationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class ConversationCreate(ConversationBase):
    collection_id: int

class Conversation(ConversationBase):
    id: int
    collection_id: int
    created_at: datetime
    last_message_at: datetime
    is_archived: bool = False
    status: ConversationStatus

    class Config:
        from_attributes = True

# Message Schemas

class MessageBase(BaseModel):
    content: str
    role: MessageRole
    message_type: MessageType
    message_metadata: Optional[Dict[str, Any]] = None 

class MessageCreate(MessageBase):
    conversation_id: int
    parent_message_id: Optional[int] = None
    message_metadata: Optional[Dict[str, Any]] = None
    has_artifact: bool = False 

class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime
    parent_message_id: Optional[int] = None
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    edit_history: Optional[Dict[str, Any]] = None
    message_metadata: Optional[Dict[str, Any]] = None 

    class Config:
        from_attributes = True
        
# Attachment Schemas
        
class AttachmentBase(BaseModel):
    file_type: str
    file_path: str
    original_filename: str
    file_size: int
    mime_type: str
    checksum: Optional[str] = None
    attachment_metadata: Optional[dict] = None
    is_processed: bool = False
    processing_error: Optional[str] = None

class AttachmentCreate(AttachmentBase):
    message_id: int

class AttachmentDB(AttachmentBase):
    id: int
    message_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True   

class Attachment(AttachmentBase):
    id: int
    message_id: int
    file_path: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

# Artifact Schemas

class ArtifactBase(BaseModel):
    """Base Artifact schema with common attributes"""
    component_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    data: Dict[str, Any]
    style: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None

class ArtifactCreate(ArtifactBase):
    """Schema for creating a new artifact"""
    message_id: int

class ArtifactInDB(ArtifactBase):
    """Schema for artifact as stored in database"""
    id: int
    message_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ArtifactResponse(BaseModel):
    id: int
    message_id: int
    component_type: str
    title: Optional[str]
    description: Optional[str]
    data: Dict[str, Any]
    style: Optional[Dict[str, Any]]
    configuration: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class Artifact(ArtifactBase):
    id: int
    message_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Artifact Metadata Schemas

class ArtifactMetadataBase(BaseModel):
    meta_data: Dict[str, Any]

class ArtifactMetadataCreate(ArtifactMetadataBase):
    artifact_id: int

class ArtifactMetadata(ArtifactMetadataBase):
    id: int
    artifact_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Response Schemas


class ConversationBrief(BaseModel):
    id: int
    title: str
    last_message_at: datetime
    message_count: int

    class Config:
        from_attributes = True
        
class ChatCollectionResponse(BaseModel):
    id: int
    collection_name: str
    created_at: datetime
    conversation_count: int
    conversations: List[ConversationBrief] = []

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    title: str
    last_message_at: datetime
    message_count: int

class MessageResponse(BaseModel):
    id: int
    content: str
    role: MessageRole
    created_at: datetime
    attachments: Optional[List[AttachmentDB]] = None
    artifacts: Optional[List[Artifact]] = None

class MessageWithDetails(Message):
    attachments: List[AttachmentDB] = []
    artifacts: List[Artifact] = []
    artifact_metadata: Dict[int, ArtifactMetadata] = {}

class ConversationWithMessages(Conversation):
    messages: List[MessageWithDetails] = []

class ChatCollectionWithConversations(ChatCollection):
    conversations: List[ConversationResponse] = []

# Request Schemas for File Upload

class FileUploadResponse(BaseModel):
    file_id: int
    file_path: str
    file_type: FileType
    original_filename: str
    mime_type: str
    file_size: int

# Update Schemas
class MessageUpdate(BaseModel):
    content: Optional[str] = None
    is_edited: bool = True
    edited_at: datetime

class ArtifactUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
