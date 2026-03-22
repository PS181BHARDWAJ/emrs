from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class ContentSectionBase(BaseModel):
    title: str
    description: str
    banner_image: Optional[str] = None
    pdf_file: Optional[str] = None
    active: bool = True
    order: Optional[int] = 0


class ContentSectionCreate(ContentSectionBase):
    section: Optional[str] = "main"


class ContentSectionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    banner_image: Optional[str] = None
    active: Optional[bool] = None
    order: Optional[int] = None


class ContentSectionResponse(ContentSectionBase):
    id: str
    page: str
    section: str

