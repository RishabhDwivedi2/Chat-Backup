# app/services/attachment_service.py

import os
import hashlib
import aiofiles
from fastapi import UploadFile, HTTPException
from typing import List, Dict
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.chat import Attachment
import aiohttp
from firebase_admin import storage
import firebase_admin
from firebase_admin import credentials
import shutil
import requests

logger = logging.getLogger(__name__)

class AttachmentService:
    def __init__(self, db: Session, upload_dir: str = "uploads"):
        self.db = db
        self.upload_dir = upload_dir
        self.firebase_bucket = storage.bucket()
        os.makedirs(upload_dir, exist_ok=True)

    async def move_to_permanent_storage(self, temp_path: str, user_id: str) -> Dict[str, str]:
        """Move file to permanent storage while preserving temp file"""
        try:
            # Generate permanent path while keeping temp file
            permanent_path = f"permanent/{os.path.basename(temp_path)}"
            temp_blob = self.firebase_bucket.blob(temp_path)
            permanent_blob = self.firebase_bucket.blob(permanent_path)
            
            # Load temp blob metadata
            temp_blob.reload()
            
            # Copy to permanent location without deleting temp
            self.firebase_bucket.copy_blob(temp_blob, self.firebase_bucket, permanent_path)
            
            # Add metadata to track when temp file was copied
            temp_blob.metadata = {
                'copied_to_permanent': 'true',
                'copy_timestamp': datetime.utcnow().isoformat()
            }
            temp_blob.patch()
            
            logger.info(f"File copied to permanent storage: {permanent_path}")
            logger.info(f"Temp file preserved at: {temp_path}")
            
            return {
                "storage_path": permanent_path,
                "download_url": permanent_blob.public_url
            }
            
        except Exception as e:
            logger.error(f"Storage error: {str(e)}")
            raise

    async def cleanup_old_temp_files(self):
        """Cleanup temp files older than 24 hours that have been copied to permanent storage"""
        try:
            blobs = self.firebase_bucket.list_blobs(prefix='temp/')
            current_time = datetime.utcnow()
            
            for blob in blobs:
                # Skip if not a temp file or missing metadata
                if not blob.metadata or 'copied_to_permanent' not in blob.metadata:
                    continue
                
                # Parse the copy timestamp
                copy_time = datetime.fromisoformat(blob.metadata['copy_timestamp'])
                time_difference = current_time - copy_time
                
                # Delete if older than 24 hours and has been copied
                if time_difference > timedelta(hours=24):
                    try:
                        blob.delete()
                        logger.info(f"Deleted old temp file: {blob.name}")
                    except Exception as e:
                        logger.error(f"Failed to delete old temp file {blob.name}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error during temp file cleanup: {str(e)}")

    async def create_attachment(self, file: UploadFile, message_id: int, user_id: str) -> Attachment:
        """Create attachment with temp file preservation"""
        try:
            # Move to permanent storage while preserving temp
            firebase_data = await self.move_to_permanent_storage(
                file.metadata['storagePath'],
                user_id
            )
            
            # Schedule cleanup of old temp files
            await self.cleanup_old_temp_files()
            
            attachment = Attachment(
                message_id=message_id,
                file_type=file.content_type,
                file_path=firebase_data['storage_path'],
                original_filename=file.filename,
                file_size=file.size,
                mime_type=file.content_type,
                attachment_metadata={
                    "firebase_storage_path": firebase_data['storage_path'],
                    "firebase_download_url": firebase_data['download_url'],
                    "temp_path": file.metadata['storagePath'],  # Store temp path reference
                    "temp_creation_time": datetime.utcnow().isoformat()
                }
            )
            
            self.db.add(attachment)
            self.db.commit()
            return attachment
            
        except Exception as e:
            logger.error(f"Error creating attachment: {str(e)}")
            raise

    async def process_attachments(self, files: List[UploadFile], message_id: int, user_id: str) -> List[Attachment]:
        """Process multiple file attachments"""
        attachments = []
        for file in files:
            try:
                attachment = await self.create_attachment(file, message_id, user_id)
                attachments.append(attachment)
                logger.info(f"Successfully processed attachment: {file.filename}")
                logger.info(f"Temp file location: {file.metadata['storagePath']}")
            except Exception as e:
                logger.error(f"Error processing attachment {file.filename}: {str(e)}")
                continue
        return attachments