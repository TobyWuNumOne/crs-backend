"""Public statistics endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.application.services import stats_service
from app.infrastructure.database import SessionDep

router = APIRouter()


@router.get("/stats/users")
def get_user_counts(session: SessionDep):
    """Return counts of doctors and patients (public)."""
    return stats_service.user_counts(session)


@router.get("/stats/clinics")
def get_clinic_count(
    session: SessionDep,
    target_date: date = Query(..., alias="date"),
):
    """Return number of clinics for a given date (public)."""
    return {"count": stats_service.clinic_count_by_date(session, target_date)}
