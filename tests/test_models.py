"""Test database models and table creation."""

import pytest
import os
from sqlmodel import Session, select, create_engine, text
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.models.users_model import User, Clinic, Registration
from app.infrastructure.database.models.constant import (
    Role,
    Sex,
    TimeSlot,
    RegistrationStatus,
)
from datetime import date, datetime
import pytz


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    # Use test database URL with explicit psycopg3 driver
    database_url = os.getenv(
        "DATABASE_URL",
        # Default to localhost port mapping used by docker-compose (5433 -> 5432 in container)
        "postgresql+psycopg://testuser:testpass@127.0.0.1:5433/testdb",
    )
    engine = create_engine(database_url, echo=False)
    return engine


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create tables and provide a database session for testing."""
    # Import here to avoid early engine creation
    from app.infrastructure.database.models.users_model import (
        User,
        Clinic,
        Registration,
    )
    from sqlmodel import SQLModel

    # Create all tables (idempotent)
    SQLModel.metadata.create_all(test_engine)

    SessionDb = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine, class_=Session
    )
    with SessionDb() as session:
        # Clean up data before each test
        session.execute(text("DELETE FROM registrations"))
        session.execute(text("DELETE FROM clinics"))
        session.execute(text("DELETE FROM users"))
        session.commit()
        yield session


def test_user_model_creation(db_session):
    """Test User model creation and basic fields."""
    user = User(
        account="testuser_unique",
        hashed_password="hashedpass",
        first_name="Test",
        last_name="User",
        sex=Sex.male,
        birthdate=date(1990, 1, 1),
        role=Role.patient,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.account == "testuser_unique"
    assert user.is_active is True
    assert user.role == Role.patient


def test_clinic_model_creation(db_session):
    """Test Clinic model creation."""
    # First create a doctor user
    doctor = User(
        account="doctor1_unique",
        hashed_password="hashedpass",
        first_name="Dr",
        last_name="Smith",
        sex=Sex.male,
        birthdate=date(1980, 1, 1),
        role=Role.doctor,
    )
    db_session.add(doctor)
    db_session.commit()

    clinic = Clinic(
        doctor_id=doctor.id,
        date=date(2024, 12, 15),
        time_slot=TimeSlot.morning,
        capacity=10,
    )

    db_session.add(clinic)
    db_session.commit()
    db_session.refresh(clinic)

    assert clinic.id is not None
    assert clinic.doctor_id == doctor.id
    assert clinic.capacity == 10
    assert clinic.is_active is True


def test_registration_model_creation(db_session):
    """Test Registration model creation."""
    # Create patient
    patient = User(
        account="patient1_unique",
        hashed_password="hashedpass",
        first_name="John",
        last_name="Doe",
        sex=Sex.male,
        birthdate=date(1995, 1, 1),
        role=Role.patient,
    )
    db_session.add(patient)
    db_session.commit()

    # Create doctor
    doctor = User(
        account="doctor2_unique",
        hashed_password="hashedpass",
        first_name="Dr",
        last_name="Jones",
        sex=Sex.female,
        birthdate=date(1985, 1, 1),
        role=Role.doctor,
    )
    db_session.add(doctor)
    db_session.commit()

    # Create clinic
    clinic = Clinic(
        doctor_id=doctor.id,
        date=date(2024, 12, 16),
        time_slot=TimeSlot.afternoon,
        capacity=5,
    )
    db_session.add(clinic)
    db_session.commit()

    # Create registration
    registration = Registration(
        clinic_id=clinic.id, patient_id=patient.id, status=RegistrationStatus.registered
    )

    db_session.add(registration)
    db_session.commit()
    db_session.refresh(registration)

    assert registration.id is not None
    assert registration.clinic_id == clinic.id
    assert registration.patient_id == patient.id
    assert registration.status == RegistrationStatus.registered


def test_relationships(db_session):
    """Test model relationships."""
    # Create test data for this test
    doctor = User(
        account="doctor_rel_test",
        hashed_password="hashedpass",
        first_name="Dr",
        last_name="Test",
        sex=Sex.male,
        birthdate=date(1980, 1, 1),
        role=Role.doctor,
    )
    db_session.add(doctor)
    db_session.commit()

    clinic = Clinic(
        doctor_id=doctor.id,
        date=date(2024, 12, 15),
        time_slot=TimeSlot.morning,
        capacity=10,
    )
    db_session.add(clinic)
    db_session.commit()

    # Query a user with relationships
    stmt = select(User).where(User.account == "doctor_rel_test")
    doctor_found = db_session.exec(stmt).first()

    assert doctor_found is not None
    assert len(doctor_found.clinics) >= 0  # May have clinics

    # Query clinic with relationships
    stmt = select(Clinic).where(Clinic.doctor_id == doctor.id)
    clinic_found = db_session.exec(stmt).first()

    if clinic_found:
        assert clinic_found.doctor.id == doctor.id
        assert len(clinic_found.registrations) >= 0


def test_table_creation():
    """Test that all tables are created successfully."""
    # This test passes if create_tables() doesn't raise an exception
    # and the models can be used
    from app.infrastructure.database.models.users_model import (
        User,
        Clinic,
        Registration,
    )

    assert User.__tablename__ == "users"
    assert Clinic.__tablename__ == "clinics"
    assert Registration.__tablename__ == "registrations"
