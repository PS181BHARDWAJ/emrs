from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.config.database import db
from app.routes.auth import get_current_admin
from bson import ObjectId
import uuid
from app.utils.storage import save_uploaded_file, get_file_url

router = APIRouter()


def serialize_announcement(item: Dict[str, Any]) -> Dict[str, Any]:
    created_at = item.get("created_at")
    created_at_value = created_at.isoformat() if isinstance(created_at, datetime) else None

    message = item.get("message") or item.get("description") or ""
    link = item.get("link") or item.get("pdf_url") or item.get("url") or "#"
    if isinstance(link, str) and "/uploads/annoucements/" in link:
        link = link.replace("/uploads/annoucements/", "/uploads/announcements/")

    pdf_url = item.get("pdf_url") or (link if str(link).lower().endswith(".pdf") else None)
    if isinstance(pdf_url, str) and "/uploads/annoucements/" in pdf_url:
        pdf_url = pdf_url.replace("/uploads/annoucements/", "/uploads/announcements/")

    category = str(item.get("category") or "notification").lower()
    if category not in {"whats_new", "notification"}:
        category = "notification"

    return {
        "id": str(item.get("_id")),
        "title": item.get("title") or "Untitled",
        "message": message,
        "link": link,
        "pdf_url": pdf_url,
        "file_size": item.get("file_size") or "",
        "is_new": bool(item.get("is_new", False)),
        "category": category,
        "show_in_ticker": bool(item.get("show_in_ticker", True)),
        "image_url": item.get("image_url"),
        "active": bool(item.get("active", True)),
        "created_at": created_at_value,
    }


@router.get("")
async def list_announcements():
    items = []
    async for item in db.announcements.find({"active": True}).sort("created_at", -1):
        items.append(serialize_announcement(item))
    return items


@router.get("/all")
async def list_all_announcements(admin=Depends(get_current_admin)):
    items = []
    async for item in db.announcements.find().sort("created_at", -1):
        items.append(serialize_announcement(item))
    return items


@router.get("/feed")
async def get_announcements_feed():
    items = []
    async for item in db.announcements.find({"active": True}).sort("created_at", -1):
        items.append(serialize_announcement(item))

    ticker = [item for item in items if item.get("show_in_ticker")]
    whats_new = [item for item in items if item.get("category") == "whats_new"]
    notification = [item for item in items if item.get("category") == "notification"]

    if not ticker:
        ticker = items[:12]
    if not whats_new:
        whats_new = items[:10]
    if not notification:
        notification = items[:10]

    return {
        "ticker": ticker,
        "whats_new": whats_new,
        "notification": notification,
        "view_all_url": "achievments and events.html",
    }


@router.post("", status_code=201)
async def create_announcement(
    title: str = Form(...),
    message: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    pdf_url: Optional[str] = Form(None),
    file_size: Optional[str] = Form(None),
    is_new: bool = Form(False),
    category: Optional[str] = Form("notification"),
    show_in_ticker: bool = Form(True),
    active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    pdf_file: Optional[UploadFile] = File(None),
    admin=Depends(get_current_admin),
):
    image_url = None
    pdf_file_url = None
    if image:
        file_id = await save_uploaded_file(db, image, category="announcements")
        image_url = get_file_url(file_id)

    if pdf_file:
        file_id = await save_uploaded_file(db, pdf_file, category="announcements")
        pdf_file_url = get_file_url(file_id)

    normalized_category = str(category or "notification").lower()
    if normalized_category not in {"whats_new", "notification"}:
        normalized_category = "notification"

    doc = {
        "title": title,
        "message": message,
        "link": link,
        "pdf_url": pdf_file_url or pdf_url,
        "file_size": file_size,
        "is_new": is_new,
        "category": normalized_category,
        "show_in_ticker": show_in_ticker,
        "active": active,
        "image_url": image_url,
        "created_at": datetime.utcnow(),
    }
    result = await db.announcements.insert_one(doc)
    return {"id": str(result.inserted_id)}


@router.put("/{announcement_id}")
async def update_announcement(
    announcement_id: str,
    title: str = Form(...),
    message: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    pdf_url: Optional[str] = Form(None),
    file_size: Optional[str] = Form(None),
    is_new: bool = Form(False),
    category: Optional[str] = Form("notification"),
    show_in_ticker: bool = Form(True),
    active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    pdf_file: Optional[UploadFile] = File(None),
    admin=Depends(get_current_admin),
):
    if not ObjectId.is_valid(announcement_id):
        raise HTTPException(status_code=400, detail="Invalid announcement id")

    normalized_category = str(category or "notification").lower()
    if normalized_category not in {"whats_new", "notification"}:
        normalized_category = "notification"

    update_data = {
        "title": title,
        "message": message,
        "link": link,
        "pdf_url": pdf_url,
        "file_size": file_size,
        "is_new": is_new,
        "category": normalized_category,
        "show_in_ticker": show_in_ticker,
        "active": active,
    }

    if image:
        file_id = await save_uploaded_file(db, image, category="announcements")
        update_data["image_url"] = get_file_url(file_id)

    if pdf_file:
        file_id = await save_uploaded_file(db, pdf_file, category="announcements")
        update_data["pdf_url"] = get_file_url(file_id)

    result = await db.announcements.update_one({"_id": ObjectId(announcement_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Updated"}


@router.patch("/{announcement_id}/toggle")
async def toggle_announcement(announcement_id: str, admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(announcement_id):
        raise HTTPException(status_code=400, detail="Invalid announcement id")
    item = await db.announcements.find_one({"_id": ObjectId(announcement_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Announcement not found")
    new_status = not item.get("active", True)
    await db.announcements.update_one({"_id": ObjectId(announcement_id)}, {"$set": {"active": new_status}})
    return {"message": "Toggled", "active": new_status}


@router.delete("/{announcement_id}")
async def delete_announcement(announcement_id: str, admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(announcement_id):
        raise HTTPException(status_code=400, detail="Invalid announcement id")
    result = await db.announcements.delete_one({"_id": ObjectId(announcement_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Deleted"}
