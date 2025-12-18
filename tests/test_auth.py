# By AI generated code
import os
from datetime import date

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine, text

from app.api.routes import auth as auth_routes
from app.infrastructure.database import get_session
from app.infrastructure.database.models.constant import Role, Sex


def _make_engine():
    database_url = os.getenv(
        "DATABASE_URL",
        # default to docker-compose service name
        "postgresql+psycopg://testuser:testpass@db:5432/testdb",
    )
    return create_engine(database_url, echo=False)


@pytest.fixture(scope="session")
def test_engine():
    return _make_engine()


@pytest.fixture(scope="function")
def db_session(test_engine):
    SQLModel.metadata.create_all(test_engine)
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine, class_=Session
    )
    with SessionLocal() as session:
        session.execute(text("DELETE FROM registrations"))
        session.execute(text("DELETE FROM clinics"))
        session.execute(text("DELETE FROM users"))
        session.commit()
        yield session


@pytest.fixture(scope="function")
def client(db_session):
    app = FastAPI()

    # Dependency override to use test session
    def get_session_override():
        yield db_session

    app.dependency_overrides = {}
    app.dependency_overrides[get_session] = get_session_override

    app.include_router(auth_routes.router, prefix="")
    return TestClient(app)


def test_register_and_login_success(client: TestClient):
    payload = {
        "account": "user1",
        "password": "secret123",
        "first_name": "Test",
        "last_name": "User",
        "sex": Sex.male.value,
        "birthdate": str(date(1990, 1, 1)),
        "role": Role.patient.value,
    }

    # Register
    resp = client.post("/register", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["account"] == "user1"

    # Login
    resp_login = client.post(
        "/login",
        data={"username": "user1", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp_login.status_code == status.HTTP_200_OK
    token_data = resp_login.json()
    assert token_data["token_type"] == "bearer"
    assert token_data["access_token"]


def test_login_wrong_password(client: TestClient):
    # Pre-register a user
    client.post(
        "/register",
        json={
            "account": "user2",
            "password": "rightpass",
            "first_name": "Jane",
            "last_name": "Doe",
            "sex": Sex.female.value,
            "birthdate": str(date(1991, 2, 2)),
            "role": Role.patient.value,
        },
    )

    resp_login = client.post(
        "/login",
        data={"username": "user2", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp_login.status_code == status.HTTP_401_UNAUTHORIZED
