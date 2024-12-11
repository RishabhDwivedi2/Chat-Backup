# app/models/chat.py

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    ForeignKey, JSON, Enum as SQLAlchemyEnum, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy import Enum
from .base import Base
from .enums import ComponentType

class ChatCollection(Base):
    __tablename__ = "chat_collections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email", ondelete="CASCADE"), nullable=False)
    collection_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    conversation_count = Column(Integer, default=0)
    description = Column(Text)

    # Relationships
    user = relationship("User", back_populates="chat_collections")
    conversations = relationship("Conversation", back_populates="collection", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('conversation_count >= 0', name='check_conversation_count_positive'),
        UniqueConstraint('user_email', 'collection_name', name='unique_collection_per_user'),
    )

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("chat_collections.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum('active', 'archived', 'deleted', name='conversation_status'), default='active')
    message_count = Column(Integer, default=0)

    # Relationships
    collection = relationship("ChatCollection", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('message_count >= 0', name='check_message_count_positive'),
    )

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(10), nullable=False)  
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    message_type = Column(String(10), nullable=False)  
    parent_message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"))
    has_artifact = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    edit_history = Column(JSON, nullable=True)
    message_metadata = Column(JSON, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    artifact = relationship("Artifact", back_populates="message", uselist=False, cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="message", cascade="all, delete-orphan")
    replies = relationship(
        "Message",
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan"
    )

class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    file_type = Column(String(10), nullable=False)  
    file_path = Column(String(512), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    checksum = Column(String(64))
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    attachment_metadata = Column(JSON)

    # Relationship back to Message
    message = relationship("Message", back_populates="attachments")

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    component_type = Column(String(20), nullable=False)
    title = Column(String(255))
    description = Column(Text)
    data = Column(JSON, nullable=False)
    style = Column(JSON)
    configuration = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship back to Message
    message = relationship("Message", back_populates="artifact")
