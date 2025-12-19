"""Statistics service.

Provides aggregate counts for users and clinics.
"""

from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlmodel import select

from app.infrastructure.database.models.constant import Role
from app.infrastructure.database.models.users_model import Clinic, User


def user_counts(session: Session) -> dict[str, int]:
    """Return counts of doctors and patients."""
    stmt = select(User.role, func.count(User.id)).group_by(User.role)
    counts = {role.value: 0 for role in Role}
    for role, cnt in session.exec(stmt).all():
        counts[role.value] = cnt
    return {"doctors": counts[Role.doctor.value], "patients": counts[Role.patient.value]}


def clinic_count_by_date(session: Session, target_date: date) -> int:
    """Count clinics for a given date."""
    stmt = select(func.count(Clinic.id)).where(Clinic.date == target_date)
    return session.exec(stmt).one()
