"""Registration CRUD (pure database operations).

No permission or business logic here; service layer handles that.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.infrastructure.database.models.constant import RegistrationStatus
from app.infrastructure.database.models.users_model import (
    Clinic,
    Registration,
    User,
    now_tpe,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def get_user(session: Session, user_id: UUID) -> User | None:
    return session.get(User, user_id)


def get_clinic(session: Session, clinic_id: UUID) -> Clinic | None:
    return session.get(Clinic, clinic_id)


def count_active_registrations(session: Session, clinic_id: UUID) -> int:
    statement = (
        select(func.count(Registration.id))
        .where(Registration.clinic_id == clinic_id)
        .where(Registration.status == RegistrationStatus.registered)
    )
    return session.exec(statement).one()


# ─────────────────────────────────────────────────────────────────────────────
# Read
# ─────────────────────────────────────────────────────────────────────────────
def get_registration(session: Session, registration_id: UUID) -> Registration | None:
    return session.get(Registration, registration_id)


def list_by_patient(
    session: Session, patient_id: UUID, include_cancelled: bool = False
) -> list[Registration]:
    statement = select(Registration).where(Registration.patient_id == patient_id)
    if not include_cancelled:
        statement = statement.where(Registration.status != RegistrationStatus.cancelled)
    return list(session.exec(statement).all())


def list_by_clinic(
    session: Session, clinic_id: UUID, status_filter: RegistrationStatus | None = None
) -> list[Registration]:
    statement = select(Registration).where(Registration.clinic_id == clinic_id)
    if status_filter:
        statement = statement.where(Registration.status == status_filter)
    return list(session.exec(statement).all())


# ─────────────────────────────────────────────────────────────────────────────
# Create
# ─────────────────────────────────────────────────────────────────────────────
def create_registration(
    session: Session, clinic_id: UUID, patient_id: UUID
) -> Registration:
    """Insert a registration; may raise IntegrityError on duplicate."""
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
        raise
    session.refresh(registration)
    return registration


# ─────────────────────────────────────────────────────────────────────────────
# Update
# ─────────────────────────────────────────────────────────────────────────────
def update_registration(
    session: Session,
    registration: Registration,
    *,
    status_value: RegistrationStatus | None = None,
    cancelled_at: datetime | None = None,
) -> Registration:
    if status_value is not None:
        registration.status = status_value
        if (
            status_value == RegistrationStatus.cancelled
            and registration.cancelled_at is None
        ):
            registration.cancelled_at = now_tpe()
    if cancelled_at is not None:
        registration.cancelled_at = cancelled_at
    session.add(registration)
    session.commit()
    session.refresh(registration)
    return registration


def cancel_registration(session: Session, registration: Registration) -> Registration:
    if registration.status == RegistrationStatus.cancelled:
        return registration
    registration.status = RegistrationStatus.cancelled
    registration.cancelled_at = now_tpe()
    session.add(registration)
    session.commit()
    session.refresh(registration)
    return registration


# ─────────────────────────────────────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────────────────────────────────────
def delete_registration(session: Session, registration: Registration) -> None:
    session.delete(registration)
    session.commit()
