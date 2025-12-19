"""Statistics service.

Provides aggregate counts for users and clinics.
"""

from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlmodel import select

from app.infrastructure.database.models.constant import Role, RegistrationStatus
from app.infrastructure.database.models.users_model import Clinic, Registration, User


def user_counts(session: Session) -> dict[str, int]:
    """Return counts of doctors and patients."""
    stmt = select(User.role, func.count(User.id)).group_by(User.role)
    counts = {role.value: 0 for role in Role}
    for role, cnt in session.exec(stmt).all():
        counts[role.value] = cnt
    return {
        "total_users": sum(counts.values()),
        "doctors": counts[Role.doctor.value],
        "patients": counts[Role.patient.value],
        "admins": counts.get(Role.admin.value, 0),
    }


def clinic_count_by_date(session: Session, target_date: date) -> int:
    """Count clinics for a given date."""
    stmt = select(func.count(Clinic.id)).where(Clinic.date == target_date)
    return session.exec(stmt).one()


def clinic_stats(session: Session) -> dict:
    """Return overall clinic and registration statistics."""
    # Total clinics
    total_clinics_stmt = select(func.count(Clinic.id))
    total_clinics = session.exec(total_clinics_stmt).one()
    
    # Active clinics
    active_clinics_stmt = select(func.count(Clinic.id)).where(Clinic.is_active == True)
    active_clinics = session.exec(active_clinics_stmt).one()
    
    # Total registrations
    total_registrations_stmt = select(func.count(Registration.id))
    total_registrations = session.exec(total_registrations_stmt).one()
    
    # Registrations by status
    status_stmt = select(Registration.status, func.count(Registration.id)).group_by(Registration.status)
    status_counts = {status.value: 0 for status in RegistrationStatus}
    for status, cnt in session.exec(status_stmt).all():
        status_counts[status.value] = cnt
    
    return {
        "total_clinics": total_clinics,
        "active_clinics": active_clinics,
        "total_registrations": total_registrations,
        "registrations_by_status": status_counts,
    }
