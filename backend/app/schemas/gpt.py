# app/schemas/gpt.py

from fastapi import APIRouter, HTTPException, Depends, Request, File, Form, UploadFile
from typing import List, Optional, Any
from pydantic import BaseModel, Field
import json

class ChatRequest(BaseModel):
    prompt: str = Field(..., description="The message to send to the chat model")
    max_tokens: Optional[int] = Field(100, ge=1, le=2000)
    temperature: Optional[float] = Field(0.7, ge=0, le=2.0)
    conversation_id: Optional[int] = None
    parent_message_id: Optional[int] = None
    collection_name: Optional[str] = None

class ChatRequestForm:
    def __init__(
        self,
        prompt: str = Form(...),
        max_tokens: Optional[int] = Form(100),
        temperature: Optional[float] = Form(0.7),
        conversation_id: Optional[int] = Form(None),
        parent_message_id: Optional[int] = Form(None),
        collection_name: Optional[str] = Form(None),
        attachments: Any = File(None)
    ):
        self.prompt = prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.conversation_id = conversation_id
        self.parent_message_id = parent_message_id
        self.collection_name = collection_name

        if attachments is None or attachments == "":
            self.attachments = []
        elif isinstance(attachments, list):
            self.attachments = attachments
        elif isinstance(attachments, UploadFile):
            self.attachments = [attachments]
        else:
            self.attachments = []
            
class ChatRequestWithAttachments:
    def __init__(
        self,
        prompt: str,
        max_tokens: Optional[int],
        temperature: Optional[float],
        conversation_id: Optional[int],
        parent_message_id: Optional[int],
        collection_name: Optional[str],
        attachments: Optional[List[UploadFile]] = None
    ):
        self.prompt = prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.conversation_id = conversation_id
        self.parent_message_id = parent_message_id
        self.collection_name = collection_name
        self.attachments = attachments or []            

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    message_id: int
    this_request_makes_platform_changed: bool = False