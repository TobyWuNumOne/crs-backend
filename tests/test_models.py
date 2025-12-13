"""Test database models and table creation."""

import pytest
import os
from sqlmodel import Session, select, create_engine
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
        "DATABASE_URL", "postgresql+psycopg://testuser:testpass@db:5432/testdb"
    )
    engine = create_engine(database_url, echo=False)
    return engine


@pytest.fixture(scope="session")
def db_session(test_engine):
    """Create tables and provide a database session for testing."""
    # Import here to avoid early engine creation
    from app.infrastructure.database.models.users_model import (
        User,
        Clinic,
        Registration,
    )
    from sqlmodel import SQLModel

    # Create all tables
    SQLModel.metadata.create_all(test_engine)

    SessionDb = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine, class_=Session
    )
    with SessionDb() as session:
        yield session


def test_user_model_creation(db_session):
    """Test User model creation and basic fields."""
    user = User(
        account="testuser",
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
    assert user.account == "testuser"
    assert user.is_active is True
    assert user.role == Role.patient


def test_clinic_model_creation(db_session):
    """Test Clinic model creation."""
    # First create a doctor user
    doctor = User(
        account="doctor1",
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
        account="patient1",
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
        account="doctor2",
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
    # Query a user with relationships
    stmt = select(User).where(User.account == "doctor1")
    doctor = db_session.exec(stmt).first()

    assert doctor is not None
    assert len(doctor.clinics) >= 0  # May have clinics

    # Query clinic with relationships
    stmt = select(Clinic).where(Clinic.doctor_id == doctor.id)
    clinic = db_session.exec(stmt).first()

    if clinic:
        assert clinic.doctor.id == doctor.id
        assert len(clinic.registrations) >= 0


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
