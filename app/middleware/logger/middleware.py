"""Access logger middleware

Logs requests and responses in JSON format, attaches correlation ID.
"""

import uuid
from time import time
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import logger


async def access_logger(request: Request, call_next):
    start = time()
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    response: Response = await call_next(request)
    latency = round((time() - start) * 1000, 2)
    logger.info(
        '{"path": "%s", "method": "%s", "status": %s, "latency_ms": %s, "correlation_id": "%s"}'
        % (
            request.url.path,
            request.method,
            response.status_code,
            latency,
            correlation_id,
        )
    )
    return response
