from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import auth, content, events, staff, announcements, calendar, visitors

app = FastAPI(title="EMRS Dornala CMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if True else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(staff.router, prefix="/api/staff", tags=["staff"])
app.include_router(announcements.router, prefix="/api/announcements", tags=["announcements"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(visitors.router, prefix="/api/visitors", tags=["visitors"])

import os

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(APP_DIR, ".."))
UPLOADS_DIR = os.path.join(ROOT_DIR, "backend", "uploads")
WRITEREADDATA_DIR = os.path.join(ROOT_DIR, "WriteReadData")
IMAGES_DIR = os.path.join(ROOT_DIR, "images")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
if os.path.isdir(WRITEREADDATA_DIR):
    app.mount("/WriteReadData", StaticFiles(directory=WRITEREADDATA_DIR), name="writereaddata")
if os.path.isdir(IMAGES_DIR):
    app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

@app.on_event("startup")
async def startup_event():
    from app.config.database import db
    # Ensure admin exists
    admin = await db.admins.find_one({"username": "admin"})
    if not admin:
        from app.utils.security import get_password_hash
        await db.admins.insert_one({
            "username": "admin",
            "password": get_password_hash("Admin@123".strip()),
            "role": "admin",
        })

@app.get("/")
def root():
    return {"message": "EMRS Dornala dynamic API running."}
