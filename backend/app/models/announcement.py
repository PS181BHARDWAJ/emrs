from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AnnouncementBase(BaseModel):
    title: str
    message: Optional[str] = None
    link: Optional[str] = None
    pdf_url: Optional[str] = None
    file_size: Optional[str] = None
    is_new: bool = False
    category: Optional[str] = None
    show_in_ticker: bool = True
    image_url: Optional[str] = None
    active: bool = True


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementInDB(AnnouncementBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True
