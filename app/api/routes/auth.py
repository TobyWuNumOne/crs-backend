"""Auth routes for registration and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.application.crud import users as user_crud
from app.application.schemas.user import UserCreate, UserRead
from app.application.services import auth_service
from app.infrastructure.database import SessionDep

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    tags=["auth"],
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserCreate, session: SessionDep):
    """Register a new user (doctor/patient/admin). Password stored as hash."""
    return user_crud.create_user(session, payload)


@router.post("/login", tags=["auth"])
def login(
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = user_crud.get_user_by_account(session, form_data.username)
    user = auth_service.authenticate_user(user, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = auth_service.create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    return {"access_token": token, "token_type": "bearer"}
