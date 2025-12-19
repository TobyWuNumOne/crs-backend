"""API routes package. Each module under routes/ should register routers.

Examples:
- routes/auth.py -> router for auth endpoints
- routes/clinics.py -> endpoints for clinic management
- routes/registrations.py -> endpoints for registrations
"""

from . import auth, clinics, registrations, stats

__all__ = ["auth", "clinics", "registrations", "stats"]
