"""Pydantic schemas for User (Doctor / Patient)

ser-related API schemas.

- Input schemas accept `password` (raw) but ORM stores only `hashed_password`.
- Output schemas never expose `hashed_password`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel, Field
from pydantic import field_validator

from app.infrastructure.database.models.constant import Role, Sex


# =====================
# Auth
# =====================


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(SQLModel):
    account: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=128)


# =====================
# User
# =====================


class UserBase(SQLModel):
    first_name: str
    last_name: str
    sex: Sex
    birthdate: date
    role: Role

    @field_validator("birthdate")  # ai
    @classmethod
    def birthdate_not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("birthdate cannot be in the future")
        return v


class UserCreate(UserBase):
    """Registration input."""

    account: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    id: UUID
    account: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(SQLModel):
    """PATCH input. Keep it optional; enforce permissions in service."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    sex: Optional[Sex] = None
    birthdate: Optional[date] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None

    model_config = {"from_attributes": True}
