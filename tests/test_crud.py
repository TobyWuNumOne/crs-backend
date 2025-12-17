"""CRUD-level integration tests using the real database models.

These tests exercise the application CRUD functions (users, clinic, registration)
against a temporary Postgres instance configured via DATABASE_URL.
"""

import os
from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine, text

from app.application.crud import clinic as clinic_crud
from app.application.crud import registration as reg_crud
from app.application.crud import users as user_crud
from app.application.schemas.clinic import ClinicCreate, ClinicUpdate
from app.application.schemas.user import UserCreate, UserUpdate
from app.infrastructure.database.models.constant import (
    RegistrationStatus,
    Role,
    Sex,
    TimeSlot,
)
from app.infrastructure.database.models.users_model import Clinic, Registration, User


def _make_engine():
    """Build an engine; default to in-memory SQLite to avoid external DB dependency."""

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return create_engine(database_url, echo=False)
    return create_engine(
        "sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False}
    )


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""

    return _make_engine()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Provide a clean session with tables created per test."""

    SQLModel.metadata.create_all(test_engine)

    SessionDb = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine, class_=Session
    )
    with SessionDb() as session:
        # Clean tables between tests
        session.execute(text("DELETE FROM registrations"))
        session.execute(text("DELETE FROM clinics"))
        session.execute(text("DELETE FROM users"))
        session.commit()
        yield session


def _create_user(session: Session, *, account: str, role: Role) -> User:
    return user_crud.create_user(
        session,
        UserCreate(
            account=account,
            password="secret123",
            first_name="Test",
            last_name="User",
            sex=Sex.male,
            birthdate=date(1990, 1, 1),
            role=role,
        ),
    )


def test_user_crud(db_session: Session):
    # Create
    user = _create_user(db_session, account="acc_user", role=Role.patient)
    assert user.id is not None
    assert user.hashed_password != "secret123"

    # List
    users = user_crud.list_users(db_session)
    assert len(users) == 1

    # Update
    updated = user_crud.update_user(
        db_session,
        user.id,
        UserUpdate(first_name="New", role=Role.doctor),
    )
    assert updated.first_name == "New"
    assert updated.role == Role.doctor

    # Change password
    old_hash = user.hashed_password
    user_crud.change_password(db_session, user.id, "another_pass")
    db_session.refresh(user)
    assert user.hashed_password != old_hash

    # Duplicate account should raise 409
    with pytest.raises(HTTPException) as exc:
        _create_user(db_session, account="acc_user", role=Role.patient)
    assert exc.value.status_code == 409

    # Deactivate
    deactivated = user_crud.deactivate_user(db_session, user.id)
    assert deactivated.is_active is False


def test_clinic_crud(db_session: Session):
    doctor = _create_user(db_session, account="dr1", role=Role.doctor)

    # Create clinic
    clinic = clinic_crud.create_clinic(
        db_session,
        doctor.id,
        ClinicCreate(date=date(2024, 12, 20), time_slot=TimeSlot.morning, capacity=5),
    )
    assert clinic.doctor_id == doctor.id

    # List by doctor
    clinics = clinic_crud.list_clinics_by_doctor(db_session, doctor.id)
    assert len(clinics) == 1

    # Conflict on same timeslot
    with pytest.raises(HTTPException) as exc:
        clinic_crud.create_clinic(
            db_session,
            doctor.id,
            ClinicCreate(
                date=date(2024, 12, 20), time_slot=TimeSlot.morning, capacity=8
            ),
        )
    assert exc.value.status_code == 409

    # Update capacity and active flag
    updated = clinic_crud.update_clinic(
        db_session,
        clinic.id,
        ClinicUpdate(capacity=10, is_active=False),
    )
    assert updated.capacity == 10
    assert updated.is_active is False

    # Delete with wrong doctor should 404
    other_doctor = _create_user(db_session, account="dr2", role=Role.doctor)
    with pytest.raises(HTTPException) as exc_del:
        clinic_crud.delete_clinic(db_session, clinic.id, doctor_id=other_doctor.id)
    assert exc_del.value.status_code == 404

    # Delete with owner succeeds
    clinic_crud.delete_clinic(db_session, clinic.id, doctor_id=doctor.id)
    assert db_session.get(Clinic, clinic.id) is None


def test_registration_crud(db_session: Session):
    patient = _create_user(db_session, account="pt1", role=Role.patient)
    doctor = _create_user(db_session, account="dr3", role=Role.doctor)
    clinic = clinic_crud.create_clinic(
        db_session,
        doctor.id,
        ClinicCreate(date=date(2024, 12, 21), time_slot=TimeSlot.afternoon, capacity=1),
    )

    # Create registration
    reg = reg_crud.create_registration(db_session, clinic.id, patient.id)
    assert reg.status == RegistrationStatus.registered

    # Duplicate registration for same patient -> 409
    with pytest.raises(HTTPException) as exc_dup:
        reg_crud.create_registration(db_session, clinic.id, patient.id)
    assert exc_dup.value.status_code == 409

    # Capacity reached -> 409 when another patient registers
    other_patient = _create_user(db_session, account="pt2", role=Role.patient)
    with pytest.raises(HTTPException) as exc_full:
        reg_crud.create_registration(db_session, clinic.id, other_patient.id)
    assert exc_full.value.status_code == 409

    # Cancel registration
    cancelled = reg_crud.cancel_registration(db_session, reg.id)
    assert cancelled.status == RegistrationStatus.cancelled
    assert cancelled.cancelled_at is not None

    # list_by_patient excludes cancelled by default
    regs_for_patient = reg_crud.list_by_patient(db_session, patient.id)
    assert regs_for_patient == []

    # list_by_patient with include_cancelled returns the cancelled one
    regs_all = reg_crud.list_by_patient(db_session, patient.id, include_cancelled=True)
    assert len(regs_all) == 1
    assert regs_all[0].status == RegistrationStatus.cancelled

    # list_by_clinic filtered by status
    regs_cancelled = reg_crud.list_by_clinic(
        db_session, clinic.id, status_filter=RegistrationStatus.cancelled
    )
    assert len(regs_cancelled) == 1
    assert regs_cancelled[0].id == reg.id

    # Delete registration
    reg_crud.delete_registration(db_session, reg.id)
    assert db_session.get(Registration, reg.id) is None
