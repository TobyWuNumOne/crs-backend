from passlib.context import CryptContext
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
import logging
from fastapi import HTTPException, status
from datetime import datetime
from uuid import UUID
import pytz
from ...infrastructure.database.models.users_model import User
from ...infrastructure.database.models.constant import Role, Sex
from ...application.schemas.user import UserCreate, UserUpdate
from ...infrastructure.database import SessionDep


logger = logging.getLogger("debug_log")

taipei_tz = pytz.timezone("Asia/Taipei")

bcrypt_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def create_admin():  # form aivc
    """Create default admin user if not exists."""
    from ...infrastructure.database import get_db_session

    with get_db_session() as db:
        # Check if admin already exists
        statement = select(User).where(User.account == "admin")
        existing_admin = db.exec(statement).first()

        if existing_admin:
            logger.info("Admin user already exists, skipping creation")
            return

        new_admin = User(
            # Auth
            account="admin",
            hashed_password=bcrypt_context.hash(
                "admin123"[:72]  # 確保密碼不超過 72 字節
            ),
            is_active=True,
            # Profile
            first_name="Admin",
            last_name="User",
            sex=Sex.other,
            birthdate=datetime.now(tz=taipei_tz).date(),
            role=Role.admin,
        )

        try:
            db.add(new_admin)
            db.commit()
            logger.info("Admin user created successfully")
        except Exception as e:
            db.rollback()  # 只 rollback 當前 user 的操作
            logger.error(f"Failed to create admin user: {e}")


def get_user_by_account(session: SessionDep, account: str) -> User | None:
    """Return a user by account or None if not found."""

    statement = select(User).where(User.account == account)
    return session.exec(statement).first()


def get_user(session: SessionDep, user_id: UUID) -> User:
    """Return a user by id or raise 404."""

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def list_users(session: SessionDep) -> list[User]:
    """List all users (could be filtered later if needed)."""

    statement = select(User)
    return list(session.exec(statement).all())


def create_user(session: SessionDep, payload: UserCreate) -> User:
    """Create a new user with hashed password and unique account handling."""

    new_user = User(
        account=payload.account,
        hashed_password=bcrypt_context.hash(payload.password[:72]),
        first_name=payload.first_name,
        last_name=payload.last_name,
        sex=payload.sex,
        birthdate=payload.birthdate,
        role=payload.role,
        is_active=True,
    )

    session.add(new_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    session.refresh(new_user)
    return new_user


def update_user(session: SessionDep, user_id: UUID, payload: UserUpdate) -> User:
    """Patch user fields; ignores None values."""

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    for field in ["first_name", "last_name", "sex", "birthdate", "role", "is_active"]:
        val = getattr(payload, field)
        if val is not None:
            setattr(user, field, val)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def change_password(session: SessionDep, user_id: UUID, new_password: str) -> None:
    """Update password for a user."""

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.hashed_password = bcrypt_context.hash(new_password[:72])
    session.add(user)
    session.commit()


def deactivate_user(session: SessionDep, user_id: UUID) -> User:
    """Soft deactivate a user."""

    user = get_user(session, user_id)
    user.is_active = False
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
