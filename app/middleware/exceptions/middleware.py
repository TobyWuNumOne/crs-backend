"""FastAPI middleware which converts AppError into structured JSON responses (rcode/message)."""

from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import Request as FastAPIRequest

from app.core.exceptions import AppError


async def app_error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except AppError as exc:
        payload = {"rcode": exc.rcode, "message": exc.message}
        return JSONResponse(status_code=400, content=payload)
    except Exception as exc:
        payload = {"rcode": "APP_500", "message": "Internal Server Error"}
        return JSONResponse(status_code=500, content=payload)
