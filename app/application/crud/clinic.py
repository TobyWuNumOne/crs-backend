from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from ...infrastructure.database.models.users_model import Clinic, User
from ...infrastructure.database.models.constant import Role
from ...application.schemas.clinic import ClinicCreate, ClinicUpdate
from ...infrastructure.database import SessionDep


def get_doctor(session: SessionDep, doctor_id: UUID) -> User | None:
    """Fetch a doctor by id; returns None if not found or not a doctor."""
    doctor = session.get(User, doctor_id)
    if not doctor or doctor.role != Role.doctor:
        return None
    return doctor


def get_clinic(session: SessionDep, clinic_id: UUID) -> Clinic | None:
    """Fetch a clinic by id; returns None if not found."""
    return session.get(Clinic, clinic_id)


def list_clinics_by_doctor(
    session: SessionDep, doctor_id: UUID, active_only: bool = False
) -> list[Clinic]:
    statement = select(Clinic).where(Clinic.doctor_id == doctor_id)
    if active_only:
        statement = statement.where(Clinic.is_active.is_(True))
    return list(session.exec(statement).all())


def list_clinics(session: SessionDep, active_only: bool = False) -> list[Clinic]:
    """List all clinics; optionally filter active ones only."""

    statement = select(Clinic)
    if active_only:
        statement = statement.where(Clinic.is_active.is_(True))
    return list(session.exec(statement).all())


def create_clinic(
    session: SessionDep, doctor_id: UUID, payload: ClinicCreate
) -> Clinic:
    clinic = Clinic(
        doctor_id=doctor_id,
        date=payload.date,
        time_slot=payload.time_slot,
        capacity=payload.capacity,
    )
    session.add(clinic)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    session.refresh(clinic)
    return clinic


def update_clinic(
    session: SessionDep, clinic_id: UUID, payload: ClinicUpdate
) -> Clinic | None:
    clinic = session.get(Clinic, clinic_id)
    if not clinic:
        return None
    if payload.capacity is not None:
        clinic.capacity = payload.capacity
    if payload.is_active is not None:
        clinic.is_active = payload.is_active
    session.add(clinic)
    session.commit()
    session.refresh(clinic)
    return clinic


def delete_clinic(session: SessionDep, clinic_id: UUID) -> bool:
    clinic = session.get(Clinic, clinic_id)
    if not clinic:
        return False
    session.delete(clinic)
    session.commit()
    return True
