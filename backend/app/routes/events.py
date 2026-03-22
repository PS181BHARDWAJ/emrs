from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from app.config.database import db
from app.routes.auth import get_current_admin
from bson import ObjectId
import uuid, os

router = APIRouter()

BACKEND_DIR = Path(__file__).resolve().parents[2]
upload_dir = BACKEND_DIR / "uploads" / "events"
upload_dir.mkdir(parents=True, exist_ok=True)


def save_file(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    name = f"{uuid.uuid4().hex}{ext}"
    path = upload_dir / name
    with open(path, "wb") as f:
        f.write(file.file.read())
    return f"/uploads/events/{name}"


def serialize_event(item: dict) -> dict:
    created_at = item.get("created_at")
    category = str(item.get("category") or "event").lower()
    if category not in {"event", "achievement", "home_slider"}:
        category = "event"

    return {
        "id": str(item.get("_id")),
        "title": item.get("title") or "Untitled",
        "short_description": item.get("short_description") or item.get("summary") or "",
        "full_description": item.get("full_description") or item.get("details") or item.get("description") or "",
        "category": category,
        "active": bool(item.get("active", True)),
        "event_date": item.get("event_date") or "",
        "image_url": item.get("image_url"),
        "created_at": created_at.isoformat() if isinstance(created_at, datetime) else None,
    }


@router.get("")
async def list_events(
    category: Optional[str] = Query(None, description="Single category or comma-separated categories"),
    include_inactive: bool = Query(False),
):
    filters = {}
    items = []
    async for ev in db.events.find(filters).sort("created_at", -1):
        item = serialize_event(ev)
        if not include_inactive and not item.get("active", True):
            continue
        items.append(item)

    if category:
        categories = {c.strip().lower() for c in category.split(",") if c.strip()}
        if categories:
            items = [item for item in items if item.get("category") in categories]

    return items


@router.get("/all")
async def list_all_events(admin=Depends(get_current_admin)):
    items = []
    async for ev in db.events.find().sort("created_at", -1):
        items.append(serialize_event(ev))
    return items


@router.post("", status_code=201)
async def create_event(
    title: str = Form(...),
    short_description: str = Form(...),
    full_description: Optional[str] = Form(None),
    category: str = Form("event"),
    active: bool = Form(True),
    event_date: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    admin=Depends(get_current_admin),
):
    normalized_category = str(category or "event").lower()
    if normalized_category not in {"event", "achievement", "home_slider"}:
        normalized_category = "event"

    image_url = None
    if image:
        image_url = save_file(image)

    result = await db.events.insert_one({
        "title": title,
        "short_description": short_description,
        "full_description": full_description,
        "category": normalized_category,
        "active": active,
        "event_date": event_date,
        "image_url": image_url,
        "created_at": datetime.utcnow(),
    })
    return {"id": str(result.inserted_id)}


@router.put("/{event_id}")
async def update_event(
    event_id: str,
    title: str = Form(...),
    short_description: str = Form(...),
    full_description: Optional[str] = Form(None),
    category: str = Form("event"),
    active: bool = Form(True),
    event_date: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    admin=Depends(get_current_admin),
):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")

    normalized_category = str(category or "event").lower()
    if normalized_category not in {"event", "achievement", "home_slider"}:
        normalized_category = "event"

    doc = {
        "title": title,
        "short_description": short_description,
        "full_description": full_description,
        "category": normalized_category,
        "active": active,
        "event_date": event_date,
    }

    if image:
        doc["image_url"] = save_file(image)

    result = await db.events.update_one({"_id": ObjectId(event_id)}, {"$set": doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Updated"}


@router.delete("/{event_id}")
async def delete_event(event_id: str, admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event id")
    result = await db.events.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Deleted"}
