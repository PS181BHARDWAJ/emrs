"""
MongoDB GridFS-based file storage for persistent uploads.
Prevents data loss from ephemeral filesystems.
"""

import os
from io import BytesIO
from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase
from gridfs import GridFS
import uuid
from datetime import datetime


async def save_uploaded_file(db: AsyncIOMotorDatabase, file: UploadFile, category: str = "uploads") -> str:
    """
    Save uploaded file to MongoDB GridFS.
    Returns the file_id that can be used to retrieve the file later.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Create file metadata
        file_id = f"{uuid.uuid4().hex}_{file.filename}"
        metadata = {
            "original_name": file.filename,
            "content_type": file.content_type,
            "category": category,
            "size": len(content),
            "uploaded_at": datetime.utcnow(),
        }
        
        # Upload to GridFS
        gfs = GridFS(db)
        stored_file_id = await gfs.put(
            BytesIO(content),
            filename=file_id,
            metadata=metadata
        )
        
        return str(stored_file_id)
    except Exception as e:
        raise Exception(f"Failed to save file: {str(e)}")


async def get_file(db: AsyncIOMotorDatabase, file_id: str) -> dict:
    """
    Retrieve file from GridFS.
    Returns dict with 'content' (bytes) and 'metadata' (original_name, content_type, etc).
    """
    try:
        gfs = GridFS(db)
        grid_out = await gfs.get(file_id)
        content = await grid_out.read()
        metadata = grid_out.metadata or {}
        
        return {
            "content": content,
            "metadata": metadata,
            "filename": grid_out.filename,
        }
    except Exception as e:
        raise Exception(f"File not found: {str(e)}")


async def delete_file(db: AsyncIOMotorDatabase, file_id: str) -> bool:
    """Delete a file from GridFS."""
    try:
        gfs = GridFS(db)
        await gfs.delete(file_id)
        return True
    except Exception as e:
        raise Exception(f"Failed to delete file: {str(e)}")


def get_file_url(file_id: str) -> str:
    """Generate the URL to retrieve a file from the API."""
    return f"/api/files/{file_id}"
