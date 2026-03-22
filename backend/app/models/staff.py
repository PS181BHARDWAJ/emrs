from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class StaffBase(BaseModel):
    name: str
    role: str
    department: str
    email: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None


class StaffCreate(StaffBase):
    pass


class StaffUpdate(StaffBase):
    pass


class StaffInDB(StaffBase):
    id: str

    class Config:
        orm_mode = True
