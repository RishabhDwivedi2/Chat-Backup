# app/services/attachment_service.py

import logging
from fastapi import UploadFile, HTTPException
from typing import List, Dict, Optional
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
        self._minio_client = None
        self._minio_available = None
        self.minio_endpoint = "http://localhost:9000"
        self.bucket_name = 'permanent'
        
        # Don't initialize MinIO on startup
        # We'll do it only when needed

    def _init_minio(self) -> bool:
        """Initialize MinIO client with single attempt"""
        try:
            if self._minio_available is not None:
                return self._minio_available

            logger.debug("Attempting to initialize MinIO connection...")
            self._minio_client = Minio(
                "localhost:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False
            )
            
            # Test connection with single attempt
            self._minio_client.bucket_exists(self.bucket_name)
            self._minio_available = True
            logger.info("Successfully connected to MinIO")
            return True
            
        except Exception as e:
            self._minio_available = False
            self._minio_client = None
            logger.error(f"MinIO initialization failed: {str(e)}. File storage will be unavailable.")
            return False

    @property
    def minio_client(self) -> Optional[Minio]:
        """Get MinIO client with single connection attempt"""
        if not self._minio_available and not self._init_minio():
            raise HTTPException(
                status_code=503,
                detail="File storage service (MinIO) is not available. Please ensure MinIO server is running."
            )
        return self._minio_client

    async def process_attachments(self, files: List[UploadFile], message_id: int, user_id: str) -> List[Attachment]:
        """Process multiple file attachments with early MinIO check"""
        if not files:
            logger.debug("No attachments to process")
            return []

        # Try to initialize MinIO only if we have attachments
        if not self._init_minio():
            raise HTTPException(
                status_code=503,
                detail="File storage service (MinIO) is not available. Please start the MinIO server to process attachments."
            )

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

    async def create_attachment(self, file: UploadFile, message_id: int, user_id: str) -> Attachment:
        """Create attachment record with MinIO storage"""
        if not self._minio_available:
            raise HTTPException(
                status_code=503,
                detail="File storage service is currently unavailable. Please ensure MinIO server is running."
            )

        try:
            await file.seek(0)
            
            uploaded_file = await self.upload_to_permanent(file)
            
            attachment = Attachment(
                message_id=message_id,
                file_type=self.get_file_type(file.content_type),
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
            
            return attachment
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating attachment: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create attachment"
            )

    async def upload_to_permanent(self, file: UploadFile) -> Dict[str, str]:
        """Upload file directly to permanent storage in MinIO"""
        if not self._minio_available:
            raise HTTPException(
                status_code=503,
                detail="File storage service is currently unavailable. Please try again later."
            )

        temp_file_path = None
        try:
            temp_file_path = await self.save_file_to_temp(file)
            
            timestamp = int(datetime.now().timestamp() * 1000)
            storage_path = f"{timestamp}-{file.filename}"
            
            self.minio_client.fput_object(
                self.bucket_name,
                storage_path,
                temp_file_path,
                content_type=file.content_type
            )
            
            download_url = f"{self.minio_endpoint}/{self.bucket_name}/{storage_path}"
            
            return {
                "storage_path": storage_path,
                "download_url": download_url
            }

        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage"
            )
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

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

    async def delete_attachment(self, file_path: str) -> bool:
        """Delete an attachment from MinIO storage"""
        try:
            self.minio_client.remove_object(self.bucket_name, file_path)
            return True
        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
            return False