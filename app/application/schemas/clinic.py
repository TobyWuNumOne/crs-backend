"""Schemas for Clinic resource"""

from pydantic import BaseModel
from datetime import date
from typing import Optional


class ClinicCreate(BaseModel):
    doctor_id: int
    date: date
    time_slot: str


class ClinicOut(BaseModel):
    id: int
    doctor_id: int
    date: date
    time_slot: str
