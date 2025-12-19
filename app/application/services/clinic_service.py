"""Clinic business logic / service layer.

Centralizes permission checks and business rules.
CRUD layer should only do pure DB operations.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.crud import clinic as clinic_crud
from app.application.schemas.clinic import ClinicCreate, ClinicUpdate
from app.infrastructure.database.models.constant import Role
from app.infrastructure.database.models.users_model import Clinic, User


def create_clinic(session: Session, actor: User, payload: ClinicCreate) -> Clinic:
    """Only doctors can create clinics (for themselves)."""
    if actor.role != Role.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create clinics",
        )
    try:
        return clinic_crud.create_clinic(session, actor.id, payload)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Clinic for doctor already exists in this time slot",
        )


def get_clinic(session: Session, clinic_id: UUID) -> Clinic:
    """Any authenticated user can view a clinic."""
    clinic = clinic_crud.get_clinic(session, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found"
        )
    return clinic


def list_clinics(session: Session, active_only: bool = False) -> list[Clinic]:
    """Any authenticated user can list clinics."""
    return clinic_crud.list_clinics(session, active_only)


def list_clinics_by_doctor(
    session: Session, doctor_id: UUID, active_only: bool = False
) -> list[Clinic]:
    """Any authenticated user can list a doctor's clinics."""
    return clinic_crud.list_clinics_by_doctor(session, doctor_id, active_only)


def update_clinic(
    session: Session, actor: User, clinic_id: UUID, payload: ClinicUpdate
) -> Clinic:
    """Only the owning doctor can update their clinic."""
    if actor.role != Role.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update clinics",
        )
    clinic = clinic_crud.get_clinic(session, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found"
        )
    if clinic.doctor_id != actor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your clinic"
        )
    updated = clinic_crud.update_clinic(session, clinic_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found"
        )
    return updated


def delete_clinic(session: Session, actor: User, clinic_id: UUID) -> None:
    """Only the owning doctor can delete their clinic."""
    if actor.role != Role.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can delete clinics",
        )
    clinic = clinic_crud.get_clinic(session, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found"
        )
    if clinic.doctor_id != actor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your clinic"
        )
    clinic_crud.delete_clinic(session, clinic_id)
