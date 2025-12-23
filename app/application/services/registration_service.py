"""Registration business logic / service layer.

Centralizes permission checks and business rules.
CRUD layer should only do pure DB operations.
"""

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.crud import registration as reg_crud
from app.infrastructure.database.models.constant import RegistrationStatus, Role
from app.infrastructure.database.models.users_model import Registration, User


def create_registration(
    session: Session,
    actor: User,
    clinic_id: UUID,
    patient_id: UUID | None = None,
) -> Registration:
    """Create a registration with permission checks.

    - Patients can only register themselves (patient_id ignored).
    - Doctors can register any patient or themselves if patient_id omitted.
    - Admins can register any patient/doctor (patient_id required if not self).
    - Others are forbidden.
    """
    if actor.role == Role.patient:
        target_patient_id = actor.id
    elif actor.role == Role.doctor:
        target_patient_id = patient_id or actor.id
    elif actor.role == Role.admin:
        target_patient_id = patient_id or actor.id
        if patient_id is None:
            # Admin should explicitly choose when registering others; fallback to self is allowed but unusual
            target_patient_id = actor.id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to register"
        )

    # Validate clinic exists and active
    clinic = reg_crud.get_clinic(session, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found"
        )
    if not clinic.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Clinic is not active"
        )

    # Validate patient (patient or doctor role)
    patient = reg_crud.get_user(session, target_patient_id)
    if not patient or patient.role not in {Role.patient, Role.doctor}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

    # Check capacity
    if clinic.capacity is not None:
        current = reg_crud.count_active_registrations(session, clinic_id)
        if current >= clinic.capacity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Clinic is fully booked"
            )

    try:
        return reg_crud.create_registration(session, clinic_id, target_patient_id)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient already registered for this clinic",
        )


def get_registration(session: Session, registration_id: UUID) -> Registration:
    """Any authenticated user can view a registration."""
    reg = reg_crud.get_registration(session, registration_id)
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found"
        )
    return reg


def list_my_registrations(
    session: Session, actor: User, include_cancelled: bool = False
) -> list[Registration]:
    """List the actor's own registrations (works for patient or doctor)."""
    return reg_crud.list_by_patient(session, actor.id, include_cancelled)


def list_by_clinic(
    session: Session,
    actor: User,
    clinic_id: UUID,
    status_filter: RegistrationStatus | None = None,
) -> list[Registration]:
    """Only doctors can list registrations for a clinic."""
    if actor.role not in {Role.doctor, Role.admin}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view clinic registrations",
        )
    clinic = reg_crud.get_clinic(session, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found"
        )
    return reg_crud.list_by_clinic(session, clinic_id, status_filter)


def update_registration(
    session: Session,
    actor: User,
    registration_id: UUID,
    status_value: RegistrationStatus | None = None,
    cancelled_at: datetime | None = None,
) -> Registration:
    """Owner or doctor can update a registration."""
    reg = get_registration(session, registration_id)
    _check_owner_or_doctor(actor, reg)
    return reg_crud.update_registration(
        session, reg, status_value=status_value, cancelled_at=cancelled_at
    )


def cancel_registration(
    session: Session, actor: User, registration_id: UUID
) -> Registration:
    """Owner or doctor can cancel a registration."""
    reg = get_registration(session, registration_id)
    _check_owner_or_doctor(actor, reg)
    return reg_crud.cancel_registration(session, reg)


def delete_registration(session: Session, actor: User, registration_id: UUID) -> None:
    """Only doctors can delete a registration."""
    if actor.role not in {Role.doctor, Role.admin}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can delete registrations",
        )
    reg = get_registration(session, registration_id)
    reg_crud.delete_registration(session, reg)


def _check_owner_or_doctor(actor: User, reg: Registration) -> None:
    """Raise 403 if actor is neither the owner nor a doctor."""
    if reg.patient_id != actor.id and actor.role not in {Role.doctor, Role.admin}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
