<!-- .github/copilot-instructions.md - guidance for AI coding agents -->

# Copilot / AI Agent Instructions — clinic-registration-system (crs-backend)

Purpose: help an AI coding agent become productive quickly in this repository.

---

## Quick facts (explicitly discoverable)

-   Backend framework: **FastAPI** (see `readme.md`).
-   Database: **PostgresDB** (see `readme.md`).
-   Authentication: **JWT tokens** (see `readme.md`).
-   Project currently contains only `readme.md` and an empty `.github/` folder — there is no existing app code, tests, or CI config to inspect.

> Note: `readme.md` lists `Package manager: uv` — this appears ambiguous (likely meant `uvicorn` or `pip`/`poetry`). Ask maintainers when unsure.

---

## Big-picture guidance (what changes should match)

-   Implement a FastAPI service with three primary domains that the README describes: **Users** (Doctors, Patients), **Clinics**, and **Registrations**.
-   Keep the business rules from the `readme.md` authoritative:

    -   Roles: `doctor` and `patient`. Record first name, last name, sex, birthdate, role.
    -   Clinics belong to doctors and record doctor ID, date, time slot.
    -   Registrations store clinic ID, patient, status, registered_at, cancelled_at.
    -   Patients cannot register other patients; doctors can register patients for their clinics.

    ### Software design principle

    -   **Clean Architecture** is preferred: keep domain logic independent of frameworks and adapters. Use `domain/`, `application/`, `infrastructure/` layers (see "File structure" below).

## API conventions to follow (examples derived from README requirements)

-   Use RESTful endpoints that are obvious and self-documenting:
    -   POST /auth/register (role-aware registration)
    -   POST /auth/login -> returns JWT
    -   POST /doctors/{doctor_id}/clinics
    -   DELETE /doctors/{doctor_id}/clinics/{clinic_id}
    -   POST /clinics/{clinic_id}/registrations (patient registration)
    -   GET /doctors/{doctor_id}/clinics/{date}/patients (doctor's patients for a day)
    -   GET /patients/{patient_id}/registrations
    -   GET /stats?date=YYYY-MM-DD (counts of doctors/patients/clinics)

Include concrete request/response schemas in the code (Pydantic models) and expose OpenAPI docs (FastAPI's built-in docs).

### URL & endpoint naming conventions

-   Base URL forms we expect to follow when exposing services:
    -   `http://{HOST_IP}:{PORT}/`
    -   `https://{DOMAIN}/{ROOT_PATH,BASE_PATH}/`
-   Endpoint examples and naming style (resource-oriented, plural nouns, nested where necessary):
    -   `GET /patients/{patient_id}/registrations`
    -   `POST /clinics/{clinic_id}/registrations`
    -   `GET /doctors/{doctor_id}/clinics/{date}/patients`

### File & directory structure (preferred skeleton)

Follow this layout when adding code; it reflects Clean Architecture separation and is the recommended starting point:

```text
app/
├── api/
│   ├── deps/
│   ├── routes/
│   ├── base.py
│   └── system.py
├── application/
│   ├── crud/
│   ├── schemas/
│   └── services/
├── core/
│   ├── RAG_LOGIC.py
│   ├── config.py
│   ├── logger.py
│   └── exceptions.py
├── domain/
│   ├── entities/
│   └── repositories/
├── infrastructure/
│   ├── adapters/
│   └── database/
├── middleware/
│   ├── exceptions/
│   └── logger/
├── prompts/
└── main.py
```

### Error handling

-   Use a consistent error model and map exceptions to structured error responses. Two patterns to follow:
    1. Raise explicit domain exceptions (e.g., `AuthorizationError`, `ValidationError`) in `domain/` or `application/` layers.
    2. Use an **RCode** design (short machine-friendly error codes + human message). Example JSON error:

```json
{
    "rcode": "REG_001",
    "message": "Patient cannot register other patients",
    "details": null
}
```

Map these to appropriate HTTP status codes via middleware (`middleware/exceptions/`).

### Audit & logs (JSON)

-   All logs must be JSON formatted (access, error, debug). Use `core/logger.py` and middleware to emit:
    -   Access Log: request/response metadata (path, method, status, latency, user_id)
    -   Error Log: exception details, rcode, stacktrace (when available)
    -   Debug Log: developer-centric diagnostics (include correlation IDs)

### Datetime

-   Use consistent timezone-aware datetimes (ISO 8601). Refer to the project's datetime guidelines: https://www.notion.so/datetime-26e638ad6aaa800ba762dc2b3ef523b4?pvs=21

---

## Developer workflows & commands (inferred & recommended)

-   Local dev run (typical FastAPI):
    -   `uvicorn app.main:app --reload --port 8000` (confirm module path once app exists)
-   DB: developer should run a local Postgres instance (docker-compose recommended) and set `DATABASE_URL` env var.
-   Tests: add `pytest`-based tests and run with `pytest -q`.

If you are unsure about a command or environment variable, add a short `README.md` change explaining the required dev steps and ask for maintainer confirmation.

---

## Project-specific conventions / guardrails for AI edits

-   Preserve the business rules from the `readme.md` exactly (role enforcement, who can register whom, required fields).
-   When adding DB schema changes: add migrations (e.g., Alembic) and include a short migration description in the commit.
-   Add tests for every API that implements business logic — tests should assert role-based behavior (e.g., patient cannot register another patient).
-   Do not add external services (3rd-party analytics, remote DBs) without either: (a) a maintainer issue describing the need, or (b) configurable env vars with sensible defaults.

-   Follow the repository's **URL naming** and **endpoint** conventions when adding routes.

---

## Tech stack (explicit)

-   `uv` : Python package and project manager (per project notes)
-   `FastAPI` : framework for building the API
-   `Postgres` : primary database

---

## Files & locations to reference when they exist

-   `readme.md` — authoritative description of entities and required APIs
-   `app/` or `src/` — place service code here (if not present yet)
-   `tests/` — place pytest tests here
-   `.github/workflows/` — add CI workflows only after test suite exists

---

## When you are blocked / need confirmation

-   Confirm what `uv` means in `readme.md` (package manager vs uvicorn) before assuming tooling.
-   Ask a maintainer before adding secrets, remote DB connections, or long-lived cloud infra.

---

If anything above is unclear or missing (for example, preferred packaging, test runner, or directory layout), please tell me which part to expand and I will update this file. ✅
