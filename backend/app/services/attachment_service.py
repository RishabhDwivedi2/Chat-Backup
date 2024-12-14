# app/services/attachment_service.py

import logging
from fastapi import UploadFile, HTTPException
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.chat import Attachment
from app.config import settings
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class AttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.supabase: Client = create_client(
            settings.SUPABASE.URL,
            settings.SUPABASE.KEY
        )
        self.bucket_name = 'chat-attachments'

    async def upload_to_permanent(self, file: UploadFile) -> Dict[str, str]:
        """Upload file directly to permanent storage in Supabase"""
        try:
            # Generate storage path
            timestamp = int(datetime.now().timestamp() * 1000)
            storage_path = f"permanent/{timestamp}-{file.filename}"
            
            # Read file content
            file_content = await file.read()
            
            # Upload to Supabase
            response = self.supabase.storage \
                .from_(self.bucket_name) \
                .upload(
                    path=storage_path,
                    file=file_content,
                    file_options={"content-type": file.content_type}
                )

            if hasattr(response, 'error') and response.error is not None:
                raise Exception(f"Upload error: {response.error}")

            # Get the public URL
            public_url = self.supabase.storage \
                .from_(self.bucket_name) \
                .get_public_url(storage_path)

            # Seek back to start of file for any future operations
            await file.seek(0)

            return {
                "storage_path": storage_path,
                "download_url": public_url
            }

        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise

    async def create_attachment(self, file: UploadFile, message_id: int, user_id: str) -> Attachment:
        """Create attachment record with direct permanent storage"""
        try:
            # Upload directly to permanent storage
            uploaded_file = await self.upload_to_permanent(file)
            
            # Create attachment record
            attachment = Attachment(
                message_id=message_id,
                file_type=file.content_type,
                file_path=uploaded_file['storage_path'],
                original_filename=file.filename,
                file_size=file.size,
                mime_type=file.content_type,
                attachment_metadata={
                    "storage_path": uploaded_file['storage_path'],
                    "download_url": uploaded_file['download_url'],
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "uploader_id": user_id
                }
            )
            
            self.db.add(attachment)
            self.db.commit()
            self.db.refresh(attachment)
            
            logger.info(f"Successfully created permanent attachment: {file.filename}")
            return attachment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating attachment: {str(e)}")
            raise

    async def process_attachments(self, files: List[UploadFile], message_id: int, user_id: str) -> List[Attachment]:
        """Process multiple file attachments with direct permanent storage"""
        attachments = []
        for file in files:
            try:
                attachment = await self.create_attachment(file, message_id, user_id)
                attachments.append(attachment)
                logger.info(f"Successfully processed attachment: {file.filename}")
            except Exception as e:
                logger.error(f"Error processing attachment {file.filename}: {str(e)}")
                continue
        return attachments

    async def delete_attachment(self, file_path: str) -> bool:
        """Delete an attachment from storage"""
        try:
            response = self.supabase.storage \
                .from_(self.bucket_name) \
                .remove([file_path])

            if hasattr(response, 'error') and response.error is not None:
                raise Exception(f"Delete error: {response.error}")

            return True

        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
            return False