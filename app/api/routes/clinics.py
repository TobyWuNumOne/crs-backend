"""Clinics management routes with full CRUD."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps.auth import get_current_user
from app.application.schemas.clinic import ClinicCreate, ClinicRead, ClinicUpdate
from app.application.services import clinic_service
from app.infrastructure.database import SessionDep
from app.infrastructure.database.models.users_model import User

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────────────────────────────────────
@router.post(
    "/clinics",
    response_model=ClinicRead,
    status_code=status.HTTP_201_CREATED,
    tags=["clinics"],
)
def create_clinic(
    payload: ClinicCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Doctor creates a new clinic (time slot)."""
    return clinic_service.create_clinic(session, current_user, payload)


# ──────────────────────────────────────────────────────────────────────────────
# READ (single)
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/clinics/{clinic_id}", response_model=ClinicRead, tags=["clinics"])
def get_clinic(
    clinic_id: UUID,
    session: SessionDep,
    _: User = Depends(get_current_user),
):
    """Get a single clinic by ID (any authenticated user)."""
    return clinic_service.get_clinic(session, clinic_id)


# ──────────────────────────────────────────────────────────────────────────────
# READ (all clinics)
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/clinics", response_model=list[ClinicRead], tags=["clinics"])
def list_clinics(
    session: SessionDep,
    active_only: bool = False,
    _: User = Depends(get_current_user),
):
    """List all clinics (optionally only active)."""
    return clinic_service.list_clinics(session, active_only)


# ──────────────────────────────────────────────────────────────────────────────
# READ (list by doctor)
# ──────────────────────────────────────────────────────────────────────────────
@router.get(
    "/doctors/{doctor_id}/clinics", response_model=list[ClinicRead], tags=["clinics"]
)
def list_clinics_by_doctor(
    doctor_id: UUID,
    session: SessionDep,
    active_only: bool = False,
    _: User = Depends(get_current_user),
):
    """List clinics for a given doctor (any authenticated user can view)."""
    return clinic_service.list_clinics_by_doctor(session, doctor_id, active_only)


# ──────────────────────────────────────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────────────────────────────────────
@router.patch("/clinics/{clinic_id}", response_model=ClinicRead, tags=["clinics"])
def update_clinic(
    clinic_id: UUID,
    payload: ClinicUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Doctor updates their own clinic (capacity / is_active)."""
    return clinic_service.update_clinic(session, current_user, clinic_id, payload)


# ──────────────────────────────────────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────────────────────────────────────
@router.delete(
    "/clinics/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["clinics"]
)
def delete_clinic(
    clinic_id: UUID,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Doctor deletes their own clinic."""
    clinic_service.delete_clinic(session, current_user, clinic_id)
    return None
