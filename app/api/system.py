"""System endpoints: healthcheck, ready, and other infra routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["system"])  # health check endpoint
async def health() -> dict:
    return {"status": "ok"}
