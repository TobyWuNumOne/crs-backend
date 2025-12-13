# Clinic Registration System Backend

FastAPI-based backend for clinic registration system with PostgreSQL database.

## Features

-   User management (Doctors, Patients)
-   Clinic scheduling
-   Registration management
-   RESTful API with automatic OpenAPI documentation

## Setup

### Prerequisites

-   Docker and Docker Compose
-   Python 3.12+

### Local Development

1. Clone the repository
2. Install dependencies:

    ```bash
    uv sync --extra dev
    ```

3. Set up environment variables in `.env` file:

    ```
    POSTGRES_USER=your_db_user
    POSTGRES_PASSWORD=your_db_password
    POSTGRES_SERVER=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=your_db_name
    ENVIRONMENT=development
    PORT=8000
    HOST=0.0.0.0
    RELOAD=true
    WORKERS=1
    DEVTEAM_PATH=/path/to/project
    API_PREFIX=/api
    ```

4. Run the application:
    ```bash
    uv run uvicorn app.main:app --reload
    ```

### Docker Testing

To run tests with Docker:

```bash
./run_tests.sh
```

This will:

1. Build the Docker image
2. Start PostgreSQL database
3. Run the application
4. Execute tests
5. Clean up containers

### Database Models

The system uses SQLModel with the following main entities:

-   **User**: Doctors and patients with authentication
-   **Clinic**: Doctor's available time slots
-   **Registration**: Patient bookings for clinics

Tables are automatically created when the application starts via `create_tables()` in `app/main.py`.

### Testing

Run tests locally:

```bash
uv run pytest
```

Tests include:

-   Model creation and validation
-   Database relationships
-   Table creation verification

### API Documentation

When running, visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```
crs-backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   └── config.py        # Application configuration
│   ├── infrastructure/
│   │   └── database/
│   │       ├── db_connection.py    # Database connection and session
│   │       └── models/
│   │           ├── users_model.py  # SQLModel definitions
│   │           └── constant.py     # Enums and constants
│   └── api/                 # API routes
├── tests/                   # Test files
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker services for testing
├── pyproject.toml          # Project dependencies
└── pytest.ini              # Test configuration
```

Please do this on your local machine. I’ll get a remote PostgresDB for you later.
