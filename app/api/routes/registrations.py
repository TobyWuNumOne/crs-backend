"""Registrations routes skeleton."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/clinics/{clinic_id}/registrations", tags=["registrations"])
async def register_patient(clinic_id: int, payload: dict):
    """Patient registers for clinic (or doctor registers a patient)."""
    return {"ok": True}


@router.get("/patients/{patient_id}/registrations", tags=["registrations"])
async def get_patient_registrations(patient_id: int):
    """Return list of registrations for a patient."""
    return {"items": []}
