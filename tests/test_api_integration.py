import os
from datetime import date
from uuid import UUID

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine, text

from app.api.routes import auth as auth_routes
from app.api.routes import clinics as clinics_routes
from app.api.routes import registrations as registrations_routes
from app.infrastructure.database import get_session
from app.infrastructure.database.models.constant import Role, Sex, TimeSlot


def _make_engine():
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://testuser:testpass@db:5432/testdb",
    )
    return create_engine(database_url, echo=False)


@pytest.fixture(scope="session")
def test_engine():
    return _make_engine()


@pytest.fixture(scope="function")
def client(test_engine):
    SQLModel.metadata.create_all(test_engine)
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine, class_=Session
    )

    # Clean tables ONCE at fixture setup, not per-request
    with SessionLocal() as setup_session:
        setup_session.execute(text("DELETE FROM registrations"))
        setup_session.execute(text("DELETE FROM clinics"))
        setup_session.execute(text("DELETE FROM users"))
        setup_session.commit()

    def get_session_override():
        with SessionLocal() as session:
            yield session

    app = FastAPI()
    app.include_router(auth_routes.router)
    app.include_router(clinics_routes.router)
    app.include_router(registrations_routes.router)
    app.dependency_overrides[get_session] = get_session_override

    return TestClient(app)


# Helpers


def _register_user(client: TestClient, account: str, role: Role) -> dict:
    payload = {
        "account": account,
        "password": "secret123",
        "first_name": "T",
        "last_name": "User",
        "sex": Sex.male.value,
        "birthdate": str(date(1990, 1, 1)),
        "role": role.value,
    }
    resp = client.post("/register", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.json()


def _login(client: TestClient, account: str, password: str) -> str:
    resp = client.post(
        "/login",
        data={"username": account, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == status.HTTP_200_OK
    return resp.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_clinic_crud_flow(client: TestClient):
    # Arrange doctor
    _register_user(client, "doc_crud", Role.doctor)
    doc_token = _login(client, "doc_crud", "secret123")

    # Create clinic
    create_payload = {
        "date": "2024-12-31",
        "time_slot": TimeSlot.morning.value,
        "capacity": 5,
    }
    resp = client.post("/clinics", json=create_payload, headers=auth_header(doc_token))
    assert resp.status_code == status.HTTP_201_CREATED
    clinic = resp.json()
    clinic_id = clinic["id"]

    # List clinics by doctor
    resp_list = client.get(
        f"/doctors/{clinic['doctor_id']}/clinics", headers=auth_header(doc_token)
    )
    assert resp_list.status_code == status.HTTP_200_OK
    assert len(resp_list.json()) == 1

    # Update clinic
    resp_upd = client.patch(
        f"/clinics/{clinic_id}",
        json={"capacity": 10, "is_active": False},
        headers=auth_header(doc_token),
    )
    assert resp_upd.status_code == status.HTTP_200_OK
    assert resp_upd.json()["capacity"] == 10
    assert resp_upd.json()["is_active"] is False

    # Delete clinic
    resp_del = client.delete(f"/clinics/{clinic_id}", headers=auth_header(doc_token))
    assert resp_del.status_code == status.HTTP_204_NO_CONTENT


def test_registration_flow(client: TestClient):
    # Arrange doctor + clinic
    doc_user = _register_user(client, "doc_reg", Role.doctor)
    doc_token = _login(client, "doc_reg", "secret123")
    resp_clinic = client.post(
        "/clinics",
        json={
            "date": "2024-12-30",
            "time_slot": TimeSlot.afternoon.value,
            "capacity": 3,
        },
        headers=auth_header(doc_token),
    )
    assert resp_clinic.status_code == status.HTTP_201_CREATED
    clinic_id = resp_clinic.json()["id"]

    # Arrange patient
    pat_user = _register_user(client, "pat_reg", Role.patient)
    pat_token = _login(client, "pat_reg", "secret123")

    # Arrange another patient
    pat2_user = _register_user(client, "pat_reg2", Role.patient)
    pat2_id = pat2_user["id"]

    # Patient registers
    resp_reg = client.post(
        "/registrations",
        json={"clinic_id": clinic_id},
        headers=auth_header(pat_token),
    )
    assert resp_reg.status_code == status.HTTP_201_CREATED
    reg_id = resp_reg.json()["id"]

    # Doctor registers another patient
    resp_reg_doc_for_other = client.post(
        "/registrations",
        json={"clinic_id": clinic_id, "patient_id": pat2_id},
        headers=auth_header(doc_token),
    )
    assert resp_reg_doc_for_other.status_code == status.HTTP_201_CREATED
    reg_other_id = resp_reg_doc_for_other.json()["id"]

    # Doctor registers themselves (doctor can also be a patient)
    resp_reg_doc_self = client.post(
        "/registrations",
        json={"clinic_id": clinic_id},
        headers=auth_header(doc_token),
    )
    assert resp_reg_doc_self.status_code == status.HTTP_201_CREATED
    reg_doc_id = resp_reg_doc_self.json()["id"]

    # Patient lists own registrations
    resp_my = client.get("/registrations/me", headers=auth_header(pat_token))
    assert resp_my.status_code == status.HTTP_200_OK
    assert len(resp_my.json()) == 1

    # Doctor (as patient) lists own registrations
    resp_doc_my = client.get("/registrations/me", headers=auth_header(doc_token))
    assert resp_doc_my.status_code == status.HTTP_200_OK
    assert len(resp_doc_my.json()) == 1

    # Doctor lists registrations for clinic
    resp_doc = client.get(
        f"/clinics/{clinic_id}/registrations",
        headers=auth_header(doc_token),
    )
    assert resp_doc.status_code == status.HTTP_200_OK
    assert len(resp_doc.json()) == 3
    patient_ids = {r["patient_id"] for r in resp_doc.json()}
    assert patient_ids == {pat_user["id"], pat2_id, doc_user["id"]}

    # Patient cancels
    resp_cancel = client.post(
        f"/registrations/{reg_id}/cancel", headers=auth_header(pat_token)
    )
    assert resp_cancel.status_code == status.HTTP_200_OK
    assert resp_cancel.json()["status"].lower() == "cancelled"

    # Patient cannot delete; doctor can delete
    resp_del_patient = client.delete(
        f"/registrations/{reg_id}", headers=auth_header(pat_token)
    )
    assert resp_del_patient.status_code == status.HTTP_403_FORBIDDEN

    resp_del_doctor = client.delete(
        f"/registrations/{reg_id}", headers=auth_header(doc_token)
    )
    assert resp_del_doctor.status_code == status.HTTP_204_NO_CONTENT


def test_list_all_clinics(client):
    # create doctor and clinics
    _register_user(client, "doc_list", Role.doctor)
    doc_token = _login(client, "doc_list", "secret123")

    # create two clinics, one inactive
    c1 = client.post(
        "/clinics",
        json={"date": "2025-01-01", "time_slot": TimeSlot.morning.value, "capacity": 3},
        headers=auth_header(doc_token),
    )
    assert c1.status_code == status.HTTP_201_CREATED

    c2 = client.post(
        "/clinics",
        json={
            "date": "2025-01-02",
            "time_slot": TimeSlot.afternoon.value,
            "capacity": 4,
            "is_active": False,
        },
        headers=auth_header(doc_token),
    )
    assert c2.status_code == status.HTTP_201_CREATED
    clinic2_id = c2.json()["id"]

    # deactivate second clinic via patch
    client.patch(
        f"/clinics/{clinic2_id}",
        json={"is_active": False},
        headers=auth_header(doc_token),
    )

    # list all
    resp = client.get("/clinics", headers=auth_header(doc_token))
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list) and len(items) == 2

    # filter active_only
    resp_active = client.get(
        "/clinics?active_only=true", headers=auth_header(doc_token)
    )
    assert resp_active.status_code == 200
    assert all(c["is_active"] for c in resp_active.json())
