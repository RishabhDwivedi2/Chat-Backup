# app/services/attachment_service.py

import logging
from fastapi import UploadFile, HTTPException
from typing import List, Dict
from datetime import datetime
import aiofiles
import os
from minio import Minio
import tempfile
from sqlalchemy.orm import Session
from app.models.chat import Attachment

logger = logging.getLogger(__name__)

class AttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.minio_client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        self.minio_endpoint = "http://localhost:9000"
        # Using permanent bucket instead of chat-attachments
        self.bucket_name = 'permanent'
        
        # Ensure bucket exists - not needed since we already created it manually
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                logger.warning(f"Bucket {self.bucket_name} does not exist")
        except Exception as e:
            logger.error(f"Error checking MinIO bucket: {str(e)}")
            raise

    async def save_file_to_temp(self, file: UploadFile) -> str:
        """Save uploaded file to temporary location and return the path"""
        try:
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                CHUNK_SIZE = 1024 * 1024  # 1MB chunks
                while chunk := await file.read(CHUNK_SIZE):
                    temp_file.write(chunk)
                return temp_file.name
        except Exception as e:
            logger.error(f"Error saving file to temp: {str(e)}")
            raise

    async def upload_to_permanent(self, file: UploadFile) -> Dict[str, str]:
        """Upload file directly to permanent storage in MinIO"""
        try:
            temp_file_path = await self.save_file_to_temp(file)
            
            # Generate storage path without 'permanent/' prefix since we're already in permanent bucket
            timestamp = int(datetime.now().timestamp() * 1000)
            storage_path = f"{timestamp}-{file.filename}"
            
            # Upload to MinIO permanent bucket
            self.minio_client.fput_object(
                self.bucket_name,
                storage_path,
                temp_file_path,
                content_type=file.content_type
            )
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            # Get the direct URL
            download_url = f"{self.minio_endpoint}/{self.bucket_name}/{storage_path}"
            
            return {
                "storage_path": storage_path,
                "download_url": download_url
            }

        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise

    async def create_attachment(self, file: UploadFile, message_id: int, user_id: str) -> Attachment:
        """Create attachment record with MinIO storage"""
        try:
            await file.seek(0)
            
            uploaded_file = await self.upload_to_permanent(file)
            
            attachment = Attachment(
                message_id=message_id,
                file_type=self.get_file_type(file.content_type),
                file_path=uploaded_file['storage_path'],  # No longer includes 'permanent/' prefix
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
            
            logger.info(f"Successfully created attachment: {file.filename}")
            return attachment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating attachment: {str(e)}")
            raise

    def get_file_type(self, mime_type: str) -> str:
        """Determine file type based on MIME type"""
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type in ['application/pdf', 'application/msword', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'text/plain']:
            return 'document'
        else:
            return 'other'

    async def process_attachments(self, files: List[UploadFile], message_id: int, user_id: str) -> List[Attachment]:
        """Process multiple file attachments"""
        attachments = []
        for file in files:
            try:
                await file.seek(0)
                attachment = await self.create_attachment(file, message_id, user_id)
                attachments.append(attachment)
                logger.info(f"Successfully processed attachment: {file.filename}")
            except Exception as e:
                logger.error(f"Error processing attachment {file.filename}: {str(e)}")
                continue
        return attachments

    async def delete_attachment(self, file_path: str) -> bool:
        """Delete an attachment from MinIO storage"""
        try:
            self.minio_client.remove_object(self.bucket_name, file_path)
            return True
        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
            return False