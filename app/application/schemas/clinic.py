"""Clinic-related API schemas."""

from __future__ import annotations  # 延遲評估型別註解

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel

from app.infrastructure.database.models.constant import TimeSlot


class ClinicBase(SQLModel):
    date: date
    time_slot: TimeSlot
    capacity: Optional[int] = None
    is_active: bool = True


class ClinicCreate(SQLModel):
    """Doctor creates a clinic for a given date + time_slot."""

    date: date
    time_slot: TimeSlot
    capacity: Optional[int] = None


class ClinicRead(ClinicBase):
    id: UUID
    doctor_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClinicUpdate(SQLModel):
    """PATCH input.

    For safety we typically do not allow doctor_id/date/time_slot changes.
    If you want to support rescheduling, do it explicitly as a new clinic.
    """

    capacity: Optional[int] = None
    is_active: Optional[bool] = None

    model_config = {"from_attributes": True}
