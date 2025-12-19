"""Registrations routes with full CRUD."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps.auth import get_current_user
from app.application.schemas.registration import (
    RegistrationCreate,
    RegistrationRead,
    RegistrationUpdate,
)
from app.application.services import registration_service
from app.infrastructure.database import SessionDep
from app.infrastructure.database.models.constant import RegistrationStatus
from app.infrastructure.database.models.users_model import User

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
# CREATE (patient/doctor register)
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
    current_user: User = Depends(get_current_user),
):
    """Create registration.

    - Patient callers register themselves (ignores patient_id).
    - Doctor callers may register any patient_id or themselves if omitted.
    """

    return registration_service.create_registration(
        session, current_user, payload.clinic_id, payload.patient_id
    )


# ──────────────────────────────────────────────────────────────────────────────
# READ (list by patient - my registrations)
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/registrations/me", response_model=list[RegistrationRead], tags=["registrations"]
)
def list_my_registrations(
    session: SessionDep,
    include_cancelled: bool = Query(False),
    current_user: User = Depends(get_current_user),
):
    """Patient lists their own registrations."""
    return registration_service.list_my_registrations(
        session, current_user, include_cancelled
    )


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
    return registration_service.get_registration(session, registration_id)


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
    current_user: User = Depends(get_current_user),
):
    """Doctor lists registrations for a specific clinic."""
    return registration_service.list_by_clinic(
        session, current_user, clinic_id, status_filter
    )


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
    return registration_service.update_registration(
        session,
        current_user,
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
    return registration_service.cancel_registration(
        session, current_user, registration_id
    )


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
    registration_service.delete_registration(session, current_user, registration_id)
    return None
