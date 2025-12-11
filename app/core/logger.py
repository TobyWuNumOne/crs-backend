"""JSON logger wrapper used by the app. Replace with structured logger (e.g., structlog) in production."""

import logging

logger = logging.getLogger("crs")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter(
    '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
ch.setFormatter(formatter)
logger.addHandler(ch)
