"""Domain models for Users, Clinics, and Registrations using SQLModel.

Timezone-aware timestamps with Asia/Taipei, UUID primary keys, and explicit enums
from `constant.py`.

NOTE:
- `account` is unique and used as the login identifier.
- Store only `hashed_password` (never store raw passwords).
- `updated_at` auto-bumps on UPDATE via SQLAlchemy `onupdate`.
"""

import pytz
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime, date
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from .constant import *

taipei_tz = pytz.timezone("Asia/Taipei")


def now_tpe() -> datetime:
    return datetime.now(tz=taipei_tz)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    # Auth
    account: str = Field(max_length=50, index=True, unique=True)  # unique
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)

    # Profile
    first_name: str
    last_name: str
    sex: Sex
    birthdate: date
    role: Role

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_tpe),
        default_factory=now_tpe,
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_tpe, onupdate=now_tpe),
        default_factory=now_tpe,
    )

    clinics: List["Clinic"] = Relationship(back_populates="doctor")
    registrations: List["Registration"] = Relationship(back_populates="patient")


class Clinic(SQLModel, table=True):
    __tablename__ = "clinics"
    __table_args__ = (
        UniqueConstraint("doctor_id", "date", "time_slot", name="uq_doctor_date_slot"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    doctor_id: UUID = Field(foreign_key="users.id", index=True)

    date: date
    time_slot: TimeSlot

    capacity: Optional[int] = Field(default=None)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_tpe),
        default_factory=now_tpe,
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_tpe, onupdate=now_tpe),
        default_factory=now_tpe,
    )

    doctor: User = Relationship(back_populates="clinics")
    registrations: List["Registration"] = Relationship(back_populates="clinic")


class Registration(SQLModel, table=True):
    __tablename__ = "registrations"
    __table_args__ = (
        UniqueConstraint("clinic_id", "patient_id", name="uq_clinic_patient"),  #
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    clinic_id: UUID = Field(foreign_key="clinics.id", index=True)
    patient_id: UUID = Field(foreign_key="users.id", index=True)

    status: RegistrationStatus = Field(default=RegistrationStatus.registered)

    registered_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_tpe),
        default_factory=now_tpe,
    )
    cancelled_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True)),
        default=None,
    )

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_tpe),
        default_factory=now_tpe,
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_tpe, onupdate=now_tpe),  #
        default_factory=now_tpe,
    )

    clinic: Clinic = Relationship(back_populates="registrations")
    patient: User = Relationship(back_populates="registrations")
