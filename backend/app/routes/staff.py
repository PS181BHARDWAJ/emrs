from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from app.config.database import db
from app.routes.auth import get_current_admin
from bson import ObjectId
import uuid
from app.utils.storage import save_uploaded_file, get_file_url

router = APIRouter()


def serialize_staff(item: dict) -> dict:
    return {
        "id": str(item.get("_id")),
        "name": item.get("name") or "",
        "designation": item.get("designation") or item.get("role") or "",
        "department": item.get("department") or "",
        "contact": item.get("contact") or item.get("phone") or item.get("email") or "",
        "email": item.get("email") or "",
        "phone": item.get("phone") or "",
        "photo_url": item.get("photo_url") or "",
        "order": int(item.get("order", 0) or 0),
        "active": bool(item.get("active", True)),
    }


@router.get("")
async def list_staff(include_inactive: bool = Query(False)):
    items = []
    async for item in db.staff.find().sort("order", 1):
        data = serialize_staff(item)
        if not include_inactive and not data["active"]:
            continue
        items.append(data)
    return items


@router.get("/all")
async def list_all_staff(admin=Depends(get_current_admin)):
    items = []
    async for item in db.staff.find().sort("order", 1):
        items.append(serialize_staff(item))
    return items


@router.post("", status_code=201)
async def create_staff(
    name: str = Form(...),
    designation: str = Form(...),
    department: str = Form(...),
    contact: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    active: bool = Form(True),
    order: Optional[int] = Form(None),
    photo: Optional[UploadFile] = File(None),
    admin=Depends(get_current_admin),
):
    photo_url = None
    if photo:
        file_id = await save_uploaded_file(db, photo, category="staff")
        photo_url = get_file_url(file_id)

    next_order = order
    if next_order is None:
        last_item = await db.staff.find_one(sort=[("order", -1)])
        next_order = (int(last_item.get("order", 0)) + 1) if last_item else 1

    result = await db.staff.insert_one({
        "name": name,
        "designation": designation,
        "department": department,
        "contact": contact or "",
        "email": email or "",
        "phone": phone or "",
        "active": active,
        "order": int(next_order),
        "photo_url": photo_url,
    })
    return {"id": str(result.inserted_id)}


@router.put("/{staff_id}")
async def update_staff(
    staff_id: str,
    name: str = Form(...),
    designation: str = Form(...),
    department: str = Form(...),
    contact: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    active: bool = Form(True),
    order: Optional[int] = Form(None),
    photo: Optional[UploadFile] = File(None),
    admin=Depends(get_current_admin),
):
    if not ObjectId.is_valid(staff_id):
        raise HTTPException(status_code=400, detail="Invalid staff id")
    doc = {
        "name": name,
        "designation": designation,
        "department": department,
        "contact": contact or "",
        "email": email or "",
        "phone": phone or "",
        "active": active,
    }
    if order is not None:
        doc["order"] = int(order)
    if photo:
        file_id = await save_uploaded_file(db, photo, category="staff")
        doc["photo_url"] = get_file_url(file_id)

    result = await db.staff.update_one({"_id": ObjectId(staff_id)}, {"$set": doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": "Updated"}


@router.delete("/{staff_id}")
async def delete_staff(staff_id: str, admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(staff_id):
        raise HTTPException(status_code=400, detail="Invalid staff id")
    result = await db.staff.delete_one({"_id": ObjectId(staff_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": "Deleted"}


@router.patch("/{staff_id}/move")
async def move_staff(staff_id: str, direction: str = Query(..., pattern="^(up|down)$"), admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(staff_id):
        raise HTTPException(status_code=400, detail="Invalid staff id")

    items = []
    async for item in db.staff.find().sort("order", 1):
        items.append(item)

    idx = next((i for i, item in enumerate(items) if str(item.get("_id")) == staff_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Staff not found")

    if direction == "up" and idx > 0:
        a, b = items[idx - 1], items[idx]
    elif direction == "down" and idx < len(items) - 1:
        a, b = items[idx], items[idx + 1]
    else:
        return {"message": "No movement"}

    await db.staff.update_one({"_id": a["_id"]}, {"$set": {"order": int(b.get("order", 0))}})
    await db.staff.update_one({"_id": b["_id"]}, {"$set": {"order": int(a.get("order", 0))}})

    return {"message": "Moved"}
