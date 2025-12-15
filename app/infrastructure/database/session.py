"""Database session helpers and FastAPI dependencies.

Central place for creating SQLAlchemy sessions and providing FastAPI DI
helpers. Keeps infrastructure responsibilities inside the infra layer.
"""

from typing import Annotated, Generator
import logging
from contextlib import contextmanager
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .db_connection import SessionDb

logger = logging.getLogger(__name__)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:  #
    """Context-managed database session with commit/rollback/close."""
    session = SessionDb()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")
    except Exception as e:  # pragma: no cover - safety net
        session.rollback()
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        session.close()


def get_session() -> Generator[Session, None, None]:
    with get_db_session() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
