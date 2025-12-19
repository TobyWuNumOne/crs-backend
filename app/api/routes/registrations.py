"""Registrations routes with full CRUD."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps.auth import get_current_doctor, get_current_patient, get_current_user
from app.application.crud import registration as reg_crud
from app.application.schemas.registration import (
    RegistrationCreate,
    RegistrationRead,
    RegistrationUpdate,
)
from app.infrastructure.database import SessionDep
from app.infrastructure.database.models.constant import RegistrationStatus
from app.infrastructure.database.models.users_model import User

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
# CREATE (patient self-register)
# ──────────────────────────────────────────────────────────────────────────────
@router.post(
    "/registrations",
    response_model=RegistrationRead,
    status_code=status.HTTP_201_CREATED,
    tags=["registrations"],
)
def create_registration(
    payload: RegistrationCreate,
    session: SessionDep,
    current_patient: User = Depends(get_current_patient),
):
    """Patient registers themselves for a clinic."""
    return reg_crud.create_registration(session, payload.clinic_id, current_patient.id)


# ──────────────────────────────────────────────────────────────────────────────
# READ (list by patient - my registrations)
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/registrations/me", response_model=list[RegistrationRead], tags=["registrations"]
)
def list_my_registrations(
    session: SessionDep,
    include_cancelled: bool = Query(False),
    current_patient: User = Depends(get_current_patient),
):
    """Patient lists their own registrations."""
    return reg_crud.list_by_patient(session, current_patient.id, include_cancelled)


# ──────────────────────────────────────────────────────────────────────────────
# READ (single)
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/registrations/{registration_id}",
    response_model=RegistrationRead,
    tags=["registrations"],
)
def get_registration(
    registration_id: UUID,
    session: SessionDep,
    _: User = Depends(get_current_user),
):
    """Get a single registration by ID (any authenticated user)."""
    return reg_crud.get_registration(session, registration_id)


# ──────────────────────────────────────────────────────────────────────────────
# READ (list by clinic - for doctor)
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/clinics/{clinic_id}/registrations",
    response_model=list[RegistrationRead],
    tags=["registrations"],
)
def list_registrations_by_clinic(
    clinic_id: UUID,
    session: SessionDep,
    status_filter: RegistrationStatus | None = None,
    _: User = Depends(get_current_doctor),
):
    """Doctor lists registrations for a specific clinic."""
    return reg_crud.list_by_clinic(session, clinic_id, status_filter)


# ──────────────────────────────────────────────────────────────────────────────
# UPDATE (general patch)
# ──────────────────────────────────────────────────────────────────────────────
@router.patch(
    "/registrations/{registration_id}",
    response_model=RegistrationRead,
    tags=["registrations"],
)
def update_registration(
    registration_id: UUID,
    payload: RegistrationUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Update a registration (owner or doctor can update)."""
    reg = reg_crud.get_registration(session, registration_id)
    # Only the patient who owns this or a doctor can update
    if reg.patient_id != current_user.id and current_user.role.value != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return reg_crud.update_registration(
        session,
        registration_id,
        status_value=payload.status,
        cancelled_at=payload.cancelled_at,
    )


# ──────────────────────────────────────────────────────────────────────────────
# CANCEL (convenience endpoint)
# ──────────────────────────────────────────────────────────────────────────────
@router.post(
    "/registrations/{registration_id}/cancel",
    response_model=RegistrationRead,
    tags=["registrations"],
)
def cancel_registration(
    registration_id: UUID,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Cancel a registration (patient can cancel their own)."""
    reg = reg_crud.get_registration(session, registration_id)
    if reg.patient_id != current_user.id and current_user.role.value != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return reg_crud.cancel_registration(session, registration_id)


# ──────────────────────────────────────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────────────────────────────────────
@router.delete(
    "/registrations/{registration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["registrations"],
)
def delete_registration(
    registration_id: UUID,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Delete a registration (only owner or doctor)."""
    if current_user.role.value != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    reg_crud.delete_registration(session, registration_id)
    return None
