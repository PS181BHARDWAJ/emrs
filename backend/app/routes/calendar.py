from fastapi import APIRouter, HTTPException, Depends, Form, Query
from app.config.database import db
from app.routes.auth import get_current_admin
from bson import ObjectId

router = APIRouter()
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def serialize_calendar(item: dict) -> dict:
    return {
        "id": str(item.get("_id")),
        "month": item.get("month") or "",
        "activity": item.get("activity") or "",
        "details": item.get("details") or "",
        "order": int(item.get("order", 0) or 0),
        "active": bool(item.get("active", True)),
    }


@router.get("")
async def list_calendar(include_inactive: bool = Query(False)):
    items = []
    async for item in db.academic_calendar.find().sort("order", 1):
        data = serialize_calendar(item)
        if not include_inactive and not data["active"]:
            continue
        items.append(data)
    return items


@router.get("/all")
async def list_all_calendar(admin=Depends(get_current_admin)):
    items = []
    async for item in db.academic_calendar.find().sort("order", 1):
        items.append(serialize_calendar(item))
    return items


@router.post("", status_code=201)
async def create_calendar(
    month: str = Form(...),
    activity: str = Form(...),
    details: str = Form(...),
    active: bool = Form(True),
    order: int | None = Form(None),
    admin=Depends(get_current_admin),
):
    if month not in MONTHS:
        raise HTTPException(status_code=400, detail="Invalid month")

    next_order = order
    if next_order is None:
        last_item = await db.academic_calendar.find_one(sort=[("order", -1)])
        next_order = (int(last_item.get("order", 0)) + 1) if last_item else 1

    result = await db.academic_calendar.insert_one({
        "month": month,
        "activity": activity,
        "details": details,
        "active": active,
        "order": int(next_order),
    })
    return {"id": str(result.inserted_id)}


@router.put("/{item_id}")
async def update_calendar(
    item_id: str,
    month: str = Form(...),
    activity: str = Form(...),
    details: str = Form(...),
    active: bool = Form(True),
    order: int | None = Form(None),
    admin=Depends(get_current_admin),
):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid calendar id")
    if month not in MONTHS:
        raise HTTPException(status_code=400, detail="Invalid month")

    doc = {
        "month": month,
        "activity": activity,
        "details": details,
        "active": active,
    }
    if order is not None:
        doc["order"] = int(order)

    result = await db.academic_calendar.update_one({"_id": ObjectId(item_id)}, {"$set": doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Calendar item not found")
    return {"message": "Updated"}


@router.delete("/{item_id}")
async def delete_calendar(item_id: str, admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid calendar id")
    result = await db.academic_calendar.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Calendar item not found")
    return {"message": "Deleted"}


@router.patch("/{item_id}/move")
async def move_calendar(item_id: str, direction: str = Query(..., pattern="^(up|down)$"), admin=Depends(get_current_admin)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid calendar id")

    items = []
    async for item in db.academic_calendar.find().sort("order", 1):
        items.append(item)

    idx = next((i for i, item in enumerate(items) if str(item.get("_id")) == item_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Calendar item not found")

    if direction == "up" and idx > 0:
        a, b = items[idx - 1], items[idx]
    elif direction == "down" and idx < len(items) - 1:
        a, b = items[idx], items[idx + 1]
    else:
        return {"message": "No movement"}

    await db.academic_calendar.update_one({"_id": a["_id"]}, {"$set": {"order": int(b.get("order", 0))}})
    await db.academic_calendar.update_one({"_id": b["_id"]}, {"$set": {"order": int(a.get("order", 0))}})

    return {"message": "Moved"}
