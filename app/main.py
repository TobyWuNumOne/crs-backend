"""App entrypoint for module-based import.

This `app.main` module can be used as a uvicorn import path (e.g. `uvicorn app.main:app --reload`).
"""

from fastapi import FastAPI

from .api.base import api_router
from .api import system

app = FastAPI(title="Clinic Registration System")

# include API router with prefix
app.include_router(api_router, prefix="/api")
# include system routes (healthchecks, etc.)
app.include_router(system.router, prefix="/api/system")


@app.get("/", include_in_schema=False)
async def _root():
    return {"message": "Clinic Registration System"}
