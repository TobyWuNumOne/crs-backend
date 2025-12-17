from uuid import UUID
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from fastapi import HTTPException, status
from sqlmodel import select

from ...infrastructure.database import SessionDep
from ...infrastructure.database.models.users_model import (
    Registration,
    Clinic,
    User,
    now_tpe,
)
from ...infrastructure.database.models.constant import Role, RegistrationStatus


def _get_patient_or_404(session: SessionDep, patient_id: UUID) -> User:
    patient = session.get(User, patient_id)
    if not patient or patient.role != Role.patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    return patient


def _get_clinic_or_404(session: SessionDep, clinic_id: UUID) -> Clinic:
    clinic = session.get(Clinic, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found"
        )
    return clinic


def _ensure_capacity(session: SessionDep, clinic: Clinic) -> None:
    if clinic.capacity is None:
        return
    statement = (
        select(func.count(Registration.id))
        .where(Registration.clinic_id == clinic.id)
        .where(Registration.status == RegistrationStatus.registered)
    )
    current = session.exec(statement).one()
    if current >= clinic.capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Clinic is fully booked"
        )


def get_registration(session: SessionDep, registration_id: UUID) -> Registration:
    registration = session.get(Registration, registration_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found"
        )
    return registration


def list_by_patient(
    session: SessionDep, patient_id: UUID, include_cancelled: bool = False
) -> list[Registration]:
    _get_patient_or_404(session, patient_id)
    statement = select(Registration).where(Registration.patient_id == patient_id)
    if not include_cancelled:
        statement = statement.where(Registration.status != RegistrationStatus.cancelled)
    return list(session.exec(statement).all())


def list_by_clinic(
    session: SessionDep, clinic_id: UUID, status_filter: RegistrationStatus | None = None
) -> list[Registration]:
    _get_clinic_or_404(session, clinic_id)
    statement = select(Registration).where(Registration.clinic_id == clinic_id)
    if status_filter:
        statement = statement.where(Registration.status == status_filter)
    return list(session.exec(statement).all())


def create_registration(
    session: SessionDep, clinic_id: UUID, patient_id: UUID
) -> Registration:
    clinic = _get_clinic_or_404(session, clinic_id)
    _get_patient_or_404(session, patient_id)
    if not clinic.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Clinic is not active"
        )
    _ensure_capacity(session, clinic)

    registration = Registration(
        clinic_id=clinic_id,
        patient_id=patient_id,
        status=RegistrationStatus.registered,
    )
    session.add(registration)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient already registered for this clinic",
        )
    session.refresh(registration)
    return registration


def cancel_registration(session: SessionDep, registration_id: UUID) -> Registration:
    registration = get_registration(session, registration_id)
    if registration.status == RegistrationStatus.cancelled:
        return registration
    registration.status = RegistrationStatus.cancelled
    registration.cancelled_at = now_tpe()
    session.add(registration)
    session.commit()
    session.refresh(registration)
    return registration


def update_registration(
    session: SessionDep,
    registration_id: UUID,
    *,
    status_value: RegistrationStatus | None = None,
    cancelled_at: datetime | None = None,
) -> Registration:
    registration = get_registration(session, registration_id)
    if status_value is not None:
        registration.status = status_value
        if status_value == RegistrationStatus.cancelled and registration.cancelled_at is None:
            registration.cancelled_at = now_tpe()
    if cancelled_at is not None:
        registration.cancelled_at = cancelled_at
    session.add(registration)
    session.commit()
    session.refresh(registration)
    return registration


def delete_registration(session: SessionDep, registration_id: UUID) -> None:
    registration = get_registration(session, registration_id)
    session.delete(registration)
    session.commit()
