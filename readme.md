# Clinic Registration System Backend

FastAPI backend for the clinic registration system with PostgreSQL.

## Features

-   User management (Doctors, Patients)
-   Clinic scheduling
-   Registration management
-   RESTful API with OpenAPI docs

## Quick Start (Local Development)

### Prerequisites

-   Docker and Docker Compose
-   Python 3.12+ (uv package manager)
-   Node.js 18+ (for frontend)

### 🚀 One-Command Dev Startup

1. **Start backend (DB included)**

```bash
cd crs-backend
chmod +x start_dev.sh
./start_dev.sh
```

This starts:

-   PostgreSQL: `localhost:5432`
-   FastAPI: `http://localhost:8000`
-   API docs: `http://localhost:8000/docs`

2. **Start frontend**

```bash
cd crs-frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`

3. Open `http://localhost:3000` and you’re set.

---

## Config Files

### Docker Compose

| File                      | Purpose           | DB Port | API Port | Container Prefix |
| ------------------------- | ----------------- | ------- | -------- | ---------------- |
| `docker-compose.dev.yml`  | Dev environment   | 5432    | 8000     | `crs-dev-`       |
| `docker-compose.test.yml` | Test environment  | 5433    | 8001     | `crs-test-`      |
| `docker-compose.yml`      | Production deploy | 5432    | 8000     | `crs-prod-`      |

### Env Files

```
.env                 # Local / deployment config
.env.example         # Template
```

### Backend .env

```bash
# Copy template
cp .env.example .env
```

Key settings:

```dotenv
# Database
POSTGRES_SERVER=db          # Use 'db' inside Docker network; use 'localhost' when running locally
POSTGRES_PORT=5432
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=prod_secure_password
POSTGRES_DB=clinic_prod

# Service
HOST=0.0.0.0
PORT=8000
WORKERS=4
API_PREFIX=/api
JWT_SECRET_KEY=please-change-me
```

### Frontend env

```bash
cd crs-frontend
cp .env.example .env.local
```

```dotenv
# Backend API URL (dev)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production
# NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

---

## Dev Commands

### Backend service control

```bash
# Start dev env
./start_dev.sh start

# Stop dev env
./start_dev.sh stop

# Restart
./start_dev.sh restart

# Logs
./start_dev.sh logs

# Status
./start_dev.sh status

# Clean all containers/data
./start_dev.sh clean
```

### Run tests

```bash
# Isolated test env (docker-compose.test.yml)
./run_tests.sh
```

Test env uses separate containers/network/ports (DB: 5433, API: 8001) and auto-cleans when done.

### Run locally without Docker

```bash
# Install deps
uv sync --extra dev

# Start API (requires Postgres running)
uv run uvicorn app.main:app --reload

# Tests
uv run pytest -v
```

---

### Production Deploy (Docker)

1. Prepare `.env` on the server (DB + JWT at minimum):

```bash
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=prod_secure_password
POSTGRES_SERVER=db
POSTGRES_DB=clinic_prod
HOST=0.0.0.0
PORT=8000
WORKERS=4
API_PREFIX=/api
JWT_SECRET_KEY=please-change-me
```

2. Bring up production stack (creates `crs-prod-db` / `crs-prod-backend`):

```bash
docker compose up -d --build
```

3. Default exposed ports: API `:8000`, DB `:5432`. Adjust `ports` mapping in compose if needed.

## Architecture

### Service layout

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│   PostgreSQL    │
│  (Next.js)      │     │   (FastAPI)     │     │   (Docker)      │
│  :3000          │     │   :8000         │     │   :5432         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### API proxy

Frontend rewrites `/api/*` to the backend:

```
Frontend /api/auth/login  ──▶  Backend http://localhost:8000/api/auth/login
```

### Database Models

-   **User**: doctors and patients with authentication
-   **Clinic**: doctor time slots
-   **Registration**: patient bookings

Tables are auto-created at startup via `create_tables()` in `app/main.py`.

---

## Project Structure

```
crs-backend/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── core/
│   │   └── config.py              # Env-based config
│   ├── api/
│   │   ├── base.py                # API router aggregation
│   │   ├── system.py              # Health checks
│   │   ├── deps/                  # Dependencies (auth, etc.)
│   │   └── routes/                # API route handlers
│   ├── application/
│   │   ├── crud/                  # CRUD operations
│   │   ├── schemas/               # Pydantic schemas
│   │   └── services/              # Business logic services
│   └── infrastructure/
│       └── database/
│           ├── db_connection.py   # DB connection
│           ├── session.py         # Session management
│           └── models/            # SQLModel definitions
├── tests/                         # Tests
├── docker-compose.dev.yml         # Dev environment
├── docker-compose.test.yml        # Test environment
├── start_dev.sh                   # Dev startup script
├── run_tests.sh                   # Test runner
├── Dockerfile                     # Docker image
├── pyproject.toml                 # Dependencies
├── .env                           # Env vars (local/deploy)
└── .env.example                   # Env template
```

---

## Future Expansion

### Connect to production DB

Update `.env` accordingly:

```dotenv
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=prod_secure_password
POSTGRES_SERVER=your-production-db-host.com
POSTGRES_PORT=5432
POSTGRES_DB=clinic_prod
```

### Production hardening

1. Set `.env` for production
2. Use a strong `JWT_SECRET_KEY`
3. Set `ENVIRONMENT=production`
4. Configure CORS/HTTPS/load balancer as needed

---

## API Documentation

-   Swagger UI: `http://localhost:8000/docs`
-   ReDoc: `http://localhost:8000/redoc`
-   OpenAPI JSON: `http://localhost:8000/openapi.json`

## Troubleshooting

### Port in use

```bash
lsof -i :8000
lsof -i :5432
# Or change ports in docker-compose.dev.yml
```

### Container conflicts

```bash
docker ps -a | grep crs | awk '{print $1}' | xargs docker rm -f
docker volume ls | grep crs | awk '{print $2}' | xargs docker volume rm
```

### Database connection failure

Check `POSTGRES_SERVER` in `.env`:

-   Docker: use `db`
-   Local: use `localhost`
