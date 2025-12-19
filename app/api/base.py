"""Router registry and central API router

The `include_router` calls for all routes should be added here, and this file exported by the app entry point.
"""

from fastapi import APIRouter  #

api_router = APIRouter()

# Register route modules that exist in the `app/api/routes` package.
from .routes import *

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    clinics.router, prefix="", tags=["clinics"]
)  # clinics route define full path
api_router.include_router(
    registrations.router, prefix="", tags=["registrations"]
)  # registrations define full path
api_router.include_router(stats.router, prefix="", tags=["stats"])
