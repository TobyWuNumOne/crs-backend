"""Pydantic schemas for User (Doctor / Patient)"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    sex: Optional[str]
    birthdate: Optional[date]
    role: str = Field(..., description="doctor|patient")


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
