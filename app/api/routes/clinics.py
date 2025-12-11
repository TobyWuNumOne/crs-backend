"""Clinics management routes skeleton."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/doctors/{doctor_id}/clinics", tags=["clinics"])
async def add_clinic(doctor_id: int, payload: dict):
    """Add a clinic for a doctor."""
    return {"ok": True}


@router.delete("/doctors/{doctor_id}/clinics/{clinic_id}", tags=["clinics"])
async def delete_clinic(doctor_id: int, clinic_id: int):
    """Delete a doctor's clinic."""
    return {"ok": True}
