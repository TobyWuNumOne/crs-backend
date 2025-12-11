"""Schemas for Registration resource"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RegistrationCreate(BaseModel):
    clinic_id: int
    patient_id: int


class RegistrationOut(BaseModel):
    id: int
    clinic_id: int
    patient_id: int
    status: str
    registered_at: datetime
    cancelled_at: Optional[datetime]
