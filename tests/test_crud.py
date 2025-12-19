"""CRUD-level integration tests using the real database models.

These tests exercise the application CRUD functions (users) and service functions
(clinic, registration) against a temporary Postgres instance configured via DATABASE_URL.
"""

import os
from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine, text

from app.application.crud import users as user_crud
from app.application.schemas.clinic import ClinicCreate, ClinicUpdate
from app.application.schemas.user import UserCreate, UserUpdate
from app.application.services import clinic_service, registration_service
from app.infrastructure.database.models.constant import (
    RegistrationStatus,
    Role,
    Sex,
    TimeSlot,
)
from app.infrastructure.database.models.users_model import Clinic, Registration, User


def _make_engine():
    """Build an engine; default to docker Postgres service if env not provided."""

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://testuser:testpass@db:5432/testdb",
    )
    return create_engine(database_url, echo=False)


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

    # Create clinic via service (requires actor)
    clinic = clinic_service.create_clinic(
        db_session,
        doctor,
        ClinicCreate(date=date(2024, 12, 20), time_slot=TimeSlot.morning, capacity=5),
    )
    assert clinic.doctor_id == doctor.id

    # List by doctor
    clinics = clinic_service.list_clinics_by_doctor(db_session, doctor.id)
    assert len(clinics) == 1

    # Conflict on same timeslot
    with pytest.raises(HTTPException) as exc:
        clinic_service.create_clinic(
            db_session,
            doctor,
            ClinicCreate(
                date=date(2024, 12, 20), time_slot=TimeSlot.morning, capacity=8
            ),
        )
    assert exc.value.status_code == 409

    # Update capacity and active flag
    updated = clinic_service.update_clinic(
        db_session,
        doctor,
        clinic.id,
        ClinicUpdate(capacity=10, is_active=False),
    )
    assert updated.capacity == 10
    assert updated.is_active is False

    # Delete with wrong doctor should 403
    other_doctor = _create_user(db_session, account="dr2", role=Role.doctor)
    with pytest.raises(HTTPException) as exc_del:
        clinic_service.delete_clinic(db_session, other_doctor, clinic.id)
    assert exc_del.value.status_code == 403

    # Delete with owner succeeds
    clinic_service.delete_clinic(db_session, doctor, clinic.id)
    assert db_session.get(Clinic, clinic.id) is None


def test_registration_crud(db_session: Session):
    patient = _create_user(db_session, account="pt1", role=Role.patient)
    doctor = _create_user(db_session, account="dr3", role=Role.doctor)
    clinic = clinic_service.create_clinic(
        db_session,
        doctor,
        ClinicCreate(date=date(2024, 12, 21), time_slot=TimeSlot.afternoon, capacity=1),
    )

    # Create registration via service (patient self-register)
    reg = registration_service.create_registration(db_session, patient, clinic.id)
    assert reg.status == RegistrationStatus.registered

    # Duplicate registration for same patient -> 409
    with pytest.raises(HTTPException) as exc_dup:
        registration_service.create_registration(db_session, patient, clinic.id)
    assert exc_dup.value.status_code == 409

    # Capacity reached -> 409 when another patient registers
    other_patient = _create_user(db_session, account="pt2", role=Role.patient)
    with pytest.raises(HTTPException) as exc_full:
        registration_service.create_registration(db_session, other_patient, clinic.id)
    assert exc_full.value.status_code == 409

    # Cancel registration
    cancelled = registration_service.cancel_registration(db_session, patient, reg.id)
    assert cancelled.status == RegistrationStatus.cancelled
    assert cancelled.cancelled_at is not None

    # list_my_registrations excludes cancelled by default
    regs_for_patient = registration_service.list_my_registrations(db_session, patient)
    assert regs_for_patient == []

    # list_my_registrations with include_cancelled returns the cancelled one
    regs_all = registration_service.list_my_registrations(
        db_session, patient, include_cancelled=True
    )
    assert len(regs_all) == 1
    assert regs_all[0].status == RegistrationStatus.cancelled

    # list_by_clinic filtered by status (only doctor can call)
    regs_cancelled = registration_service.list_by_clinic(
        db_session, doctor, clinic.id, status_filter=RegistrationStatus.cancelled
    )
    assert len(regs_cancelled) == 1
    assert regs_cancelled[0].id == reg.id

    # Delete registration (only doctor can delete)
    registration_service.delete_registration(db_session, doctor, reg.id)
    assert db_session.get(Registration, reg.id) is None
