"""Auth dependency utilities (get_current_user, role guards)."""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.application.crud import users as user_crud
from app.application.services import auth_service
from app.infrastructure.database import SessionDep
from app.infrastructure.database.models.constant import Role


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep = Depends()
):
    payload = auth_service.decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    user = user_crud.get_user(session, user_id)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )
    return user


def get_current_doctor(current_user=Depends(get_current_user)):
    if current_user.role != Role.doctor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor only")
    return current_user


def get_current_patient(current_user=Depends(get_current_user)):
    if current_user.role != Role.patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Patient only"
        )
    return current_user
