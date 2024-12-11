# app/utils/file_handler.py

import os
from fastapi import UploadFile
from typing import Optional
import aiofiles
import uuid

class FileHandler:
    def __init__(self, base_upload_dir: str):
        self.base_upload_dir = base_upload_dir

    async def save_file(self, file: UploadFile, subfolder: str) -> tuple[str, str]:
        """
        Save uploaded file and return the file path and public URL
        """
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        
        folder_path = os.path.join(self.base_upload_dir, subfolder)
        os.makedirs(folder_path, exist_ok=True)
        
        file_path = os.path.join(folder_path, unique_filename)
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
            
        return file_path, f"/uploads/{subfolder}/{unique_filename}"

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file given its path
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            return False