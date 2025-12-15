"""App entrypoint for module-based import.

This `app.main` module can be used as a uvicorn import path (e.g. `uvicorn app.main:app --reload`).
"""

from fastapi import FastAPI
from .infrastructure.database.db_connection import create_tables
from .api.base import api_router
from .api import system
from .core.config import settings
from .application.crud.users import create_admin

app = FastAPI(title="Clinic Registration System")

create_tables()
create_admin()
# include API router with prefix from config
app.include_router(api_router, prefix=settings.API_PREFIX)
# include system routes (healthchecks, etc.) under API prefix
app.include_router(system.router, prefix=f"{settings.API_PREFIX}/system")


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Clinic Registration System"}


@app.get("/healthy")
def health_check():
    return {"status": "OK"}
