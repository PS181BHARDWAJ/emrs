from fastapi import APIRouter
from app.config.database import db
from datetime import datetime

router = APIRouter()

@router.post("/increment")
async def increment_visitor():
    """Increment visitor count and return current total"""
    try:
        # Find or create the visitor count document
        result = await db.visitors.find_one_and_update(
            {"_id": "global_count"},
            {
                "$inc": {"count": 1},
                "$set": {"last_updated": datetime.utcnow()}
            },
            upsert=True,
            return_document=True
        )
        return {
            "success": True,
            "count": result.get("count", 0)
        }
    except Exception as e:
        print(f"Error incrementing visitor count: {e}")
        return {
            "success": False,
            "error": str(e),
            "count": 0
        }

@router.get("/count")
async def get_visitor_count():
    """Get current visitor count"""
    try:
        result = await db.visitors.find_one({"_id": "global_count"})
        count = result.get("count", 0) if result else 0
        return {
            "success": True,
            "count": count
        }
    except Exception as e:
        print(f"Error getting visitor count: {e}")
        return {
            "success": False,
            "error": str(e),
            "count": 0
        }
