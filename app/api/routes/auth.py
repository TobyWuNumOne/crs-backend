"""Auth routes skeleton for registration/login endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/register", tags=["auth"])
async def register(payload: dict):
    """Register a new user with role-aware payload (doctor/patient)."""
    return {"ok": True}


@router.post("/login", tags=["auth"])
async def login(payload: dict):
    """Login and return JWT token"""
    return {"token": "TODO"}
