from fastapi import APIRouter, HTTPException
from app.config.database import db
from bson import ObjectId

router = APIRouter()

PAGES = ["home", "about", "vision", "campus", "admissions", "contact", "mission", "objective", "academics", "achievments", "events", "staff"]


@router.get("/{page}")
async def get_page_content(page: str):
    if page not in PAGES:
        raise HTTPException(status_code=404, detail="Page not found")

    sections = []
    async for item in db.content.find({"page": page}).sort("order", 1):
        item["id"] = str(item.get("_id"))
        item.pop("_id", None)
        sections.append(item)
    return sections


@router.get("/{page}/display")
async def get_page_display(page: str):
    if page not in PAGES:
        raise HTTPException(status_code=404, detail="Page not found")

    sections = []
    async for item in db.content.find({"page": page}).sort("order", 1):
        item["id"] = str(item.get("_id"))
        item.pop("_id", None)
        sections.append(item)

    if not sections:
        return {"page": page, "title": "", "description": "", "banner_image": "", "pdf_file": ""}

    primary = next((s for s in sections if s.get("active", True) and s.get("section") == "main"), None)
    if not primary:
        primary = next((s for s in sections if s.get("active", True)), None)
    if not primary:
        primary = sections[0]

    return {
        "page": page,
        "section": primary.get("section", "main"),
        "title": primary.get("title", ""),
        "description": primary.get("description", ""),
        "banner_image": primary.get("banner_image", ""),
        "pdf_file": primary.get("pdf_file", ""),
        "active": primary.get("active", True),
        "order": primary.get("order", 0),
        "id": primary.get("id"),
    }


@router.get("/{page}/sections/{section_id}")
async def get_section(page: str, section_id: str):
    if page not in PAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    if not ObjectId.is_valid(section_id):
        raise HTTPException(status_code=400, detail="Invalid section id")
    item = await db.content.find_one({"_id": ObjectId(section_id), "page": page})
    if not item:
        raise HTTPException(status_code=404, detail="Section not found")
    item["id"] = str(item["_id"])
    item.pop("_id", None)
    return item
