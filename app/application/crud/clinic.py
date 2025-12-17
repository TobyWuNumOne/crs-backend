from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from uuid import UUID
from ...infrastructure.database.models.users_model import Clinic, User
from ...infrastructure.database.models.constant import Role
from ...application.schemas.clinic import ClinicCreate, ClinicUpdate
from ...infrastructure.database import SessionDep


def _get_doctor_or_404(session: SessionDep, doctor_id: UUID) -> User:
    doctor = session.get(User, doctor_id)
    if not doctor or doctor.role != Role.doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
        )
    return doctor


def get_clinic(session: SessionDep, clinic_id: UUID) -> Clinic:
    clinic = session.get(Clinic, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found"
        )
    return clinic


def list_clinics_by_doctor(
    session: SessionDep, doctor_id: UUID, active_only: bool = False
) -> list[Clinic]:
    _get_doctor_or_404(session, doctor_id)
    statement = select(Clinic).where(Clinic.doctor_id == doctor_id)
    if active_only:
        statement = statement.where(Clinic.is_active.is_(True))
    return list(session.exec(statement).all())


def create_clinic(session: SessionDep, doctor_id: UUID, payload: ClinicCreate) -> Clinic:
    _get_doctor_or_404(session, doctor_id)
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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Clinic for doctor already exists in this time slot",
        )
    session.refresh(clinic)
    return clinic


def update_clinic(
    session: SessionDep, clinic_id: UUID, payload: ClinicUpdate
) -> Clinic:
    clinic = get_clinic(session, clinic_id)
    if payload.capacity is not None:
        clinic.capacity = payload.capacity
    if payload.is_active is not None:
        clinic.is_active = payload.is_active
    session.add(clinic)
    session.commit()
    session.refresh(clinic)
    return clinic


def delete_clinic(session: SessionDep, clinic_id: UUID, doctor_id: UUID | None = None):
    clinic = get_clinic(session, clinic_id)
    if doctor_id and clinic.doctor_id != doctor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found"
        )
    session.delete(clinic)
    session.commit()
