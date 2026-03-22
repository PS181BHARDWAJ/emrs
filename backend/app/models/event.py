from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EventBase(BaseModel):
    title: str
    short_description: str
    full_description: Optional[str] = None
    category: str = "event"
    active: bool = True
    event_date: Optional[str] = None
    image_url: Optional[str] = None


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventInDB(EventBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
