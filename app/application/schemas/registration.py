"""Registration-related API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel

from app.infrastructure.database.models.constant import RegistrationStatus


class RegistrationBase(SQLModel):
    status: RegistrationStatus = RegistrationStatus.registered


class RegistrationCreate(SQLModel):
    """Create a registration.

    - Patient flow: patient registers self for a clinic.
    - Doctor flow: doctor registers a specific patient for a clinic.
    - Admin flow: admin registers any patient (or doctor) for a clinic.

    NOTE: service layer must enforce permissions.
    """

    clinic_id: UUID
    # Doctor may supply a patient_id; patient endpoint should reject/ignore.
    patient_id: Optional[UUID] = None


class RegistrationRead(RegistrationBase):
    id: UUID
    clinic_id: UUID
    patient_id: UUID

    registered_at: datetime
    cancelled_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RegistrationCancel(SQLModel):
    """Cancel a registration (status -> cancelled)."""

    reason: Optional[str] = None


class RegistrationUpdate(SQLModel):
    """PATCH input. Keep narrow; state transitions should be explicit actions."""

    status: Optional[RegistrationStatus] = None
    cancelled_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
