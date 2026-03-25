"""
File serving endpoint for MongoDB-stored files.
"""

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import StreamingResponse
from bson import ObjectId
from app.config.database import db

router = APIRouter()


@router.get("/{file_id}/{filename}")
async def get_file(file_id: str, filename: str = Path(...)):
    """
    Retrieve a file from MongoDB.
    URL format: /api/files/{file_id}/{filename}
    """
    try:
        # Convert string to ObjectId
        try:
            oid = ObjectId(file_id)
        except:
            raise HTTPException(status_code=404, detail="Invalid file ID")
        
        file_doc = await db.files.find_one({"_id": oid})
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        
        content = file_doc.get("data")
        content_type = file_doc.get("content_type", "application/octet-stream")
        original_name = file_doc.get("filename", filename)
        
        return StreamingResponse(
            iter([content]),
            media_type=content_type,
            headers={
                "Content-Disposition": f'inline; filename="{original_name}"'
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found")


@router.get("/{file_id}")
async def get_file_simple(file_id: str):
    """
    Simple file retrieval endpoint.
    URL format: /api/files/{file_id}
    """
    try:
        # Convert string to ObjectId
        try:
            oid = ObjectId(file_id)
        except:
            raise HTTPException(status_code=404, detail="Invalid file ID")
        
        file_doc = await db.files.find_one({"_id": oid})
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        
        content = file_doc.get("data")
        content_type = file_doc.get("content_type", "application/octet-stream")
        original_name = file_doc.get("filename", "file")
        
        return StreamingResponse(
            iter([content]),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{original_name}"'
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")
