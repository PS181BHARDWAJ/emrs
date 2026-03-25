"""
File serving endpoint for GridFS-stored files.
"""

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import StreamingResponse
import io
from gridfs import GridFS
from bson import ObjectId
from app.config.database import db

router = APIRouter()


@router.get("/{file_id}/{filename}")
async def get_file(file_id: str, filename: str = Path(...)):
    """
    Retrieve a file from GridFS.
    URL format: /api/files/{file_id}/{filename}
    """
    try:
        # Validate ObjectId
        try:
            oid = ObjectId(file_id)
        except:
            # Try as string file_id (for backward compatibility)
            oid = file_id
        
        gfs = GridFS(db)
        grid_out = await gfs.get(oid)
        
        # Read file content
        content = await grid_out.read()
        
        # Get metadata for content-type
        metadata = grid_out.metadata or {}
        content_type = metadata.get("content_type", "application/octet-stream")
        original_name = metadata.get("original_name", filename)
        
        return StreamingResponse(
            iter([content]),
            media_type=content_type,
            headers={
                "Content-Disposition": f'inline; filename="{original_name}"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")


@router.get("/{file_id}")
async def get_file_simple(file_id: str):
    """
    Simple file retrieval endpoint.
    URL format: /api/files/{file_id}
    """
    try:
        # Validate ObjectId
        try:
            oid = ObjectId(file_id)
        except:
            oid = file_id
        
        gfs = GridFS(db)
        grid_out = await gfs.get(oid)
        
        # Read file content
        content = await grid_out.read()
        
        # Get metadata
        metadata = grid_out.metadata or {}
        content_type = metadata.get("content_type", "application/octet-stream")
        original_name = metadata.get("original_name", "file")
        
        return StreamingResponse(
            iter([content]),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{original_name}"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")
