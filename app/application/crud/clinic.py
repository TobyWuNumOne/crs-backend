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

# TODO 完成clinic的crud操作
