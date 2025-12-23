"""Public statistics endpoints."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from app.application.services import stats_service
from app.infrastructure.database import SessionDep

router = APIRouter()


@router.get("/stats/users")
def get_user_counts(session: SessionDep):
    """Return counts of doctors and patients (public)."""
    return stats_service.user_counts(session)


@router.get("/stats/clinics")
def get_clinic_stats(
    session: SessionDep,
    target_date: Optional[date] = Query(None, alias="date"),
):
    """Return clinic statistics (public).

    If date is provided, returns count for that date.
    Otherwise, returns overall statistics.
    """
    if target_date:
        return {"count": stats_service.clinic_count_by_date(session, target_date)}
    return stats_service.clinic_stats(session)
