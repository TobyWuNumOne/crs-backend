# Clinic Registration System Backend

FastAPI-based backend for clinic registration system with PostgreSQL database.

## Features

-   User management (Doctors, Patients)
-   Clinic scheduling
-   Registration management
-   RESTful API with automatic OpenAPI documentation

## Quick Start (本地開發環境)

### Prerequisites

-   Docker and Docker Compose
-   Python 3.12+ (with uv package manager)
-   Node.js 18+ (for frontend)

### 🚀 一鍵啟動開發環境

1. **啟動後端服務（含資料庫）**

    ```bash
    cd crs-backend
    chmod +x start_dev.sh
    ./start_dev.sh
    ```

    這會啟動：

    - PostgreSQL 資料庫：`localhost:5432`
    - FastAPI 後端 API：`http://localhost:8000`
    - API 文件：`http://localhost:8000/docs`

2. **啟動前端服務**

    ```bash
    cd crs-frontend
    npm install
    npm run dev
    ```

    前端服務：`http://localhost:3000`

3. **完成！** 開啟瀏覽器訪問 `http://localhost:3000`

---

## 環境設定檔說明

### Docker Compose 設定檔

| 檔案                      | 用途             | DB Port | API Port | Container 前綴 |
| ------------------------- | ---------------- | ------- | -------- | -------------- |
| `docker-compose.dev.yml`  | **本地開發環境** | 5432    | 8000     | `crs-dev-`     |
| `docker-compose.test.yml` | **測試環境**     | 5433    | 8001     | `crs-test-`    |
| `docker-compose.yml`      | 舊有設定（保留） | 5433    | 8001     | -              |

### 環境變數檔案

```
.env                 # 本地開發環境設定（不要提交到 Git）
.env.example         # 環境變數範本（可提交到 Git）
```

### 後端 .env 設定

```bash
# 複製範本
cp .env.example .env
```

重要設定說明：

```dotenv
# ----- 資料庫設定 -----
# Docker 環境使用 db 作為 host（docker-compose 內部網路）
POSTGRES_SERVER=db
POSTGRES_PORT=5432

# 本地直接連接 PostgreSQL（不用 Docker）
# POSTGRES_SERVER=localhost

# ----- 未來連接正式資料庫 -----
# 只需修改以下設定即可切換到正式環境
# POSTGRES_USER=prod_user
# POSTGRES_PASSWORD=prod_secure_password
# POSTGRES_SERVER=your-production-db-host.com
# POSTGRES_DB=clinic_prod
```

### 前端環境設定

```bash
cd crs-frontend
cp .env.example .env.local
```

```dotenv
# 後端 API URL（本地開發）
NEXT_PUBLIC_API_URL=http://localhost:8000

# 正式環境
# NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

---

## 開發指令

### 後端服務管理

```bash
# 啟動開發環境
./start_dev.sh start

# 停止開發環境
./start_dev.sh stop

# 重啟開發環境
./start_dev.sh restart

# 查看 logs
./start_dev.sh logs

# 查看容器狀態
./start_dev.sh status

# 清理所有容器和資料
./start_dev.sh clean
```

### 執行測試

```bash
# 執行測試（獨立的測試環境，不影響開發環境）
./run_tests.sh
```

測試環境特點：

-   使用 `docker-compose.test.yml`
-   獨立的容器（`crs-test-*`）和網路
-   不同的 Port（DB: 5433, API: 8001）
-   測試完成後自動清理

### 本地直接執行（不用 Docker）

```bash
# 安裝依賴
uv sync --extra dev

# 啟動服務（需要先啟動 PostgreSQL）
uv run uvicorn app.main:app --reload

# 執行測試
uv run pytest -v
```

---

## 架構說明

### 服務架構

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│   PostgreSQL    │
│  (Next.js)      │     │   (FastAPI)     │     │   (Docker)      │
│  :3000          │     │   :8000         │     │   :5432         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### API 代理設定

前端透過 Next.js 的 `rewrites` 功能將 `/api/*` 請求代理到後端：

```
前端 /api/auth/login  ──▶  後端 http://localhost:8000/api/auth/login
```

### Database Models

The system uses SQLModel with the following main entities:

-   **User**: Doctors and patients with authentication
-   **Clinic**: Doctor's available time slots
-   **Registration**: Patient bookings for clinics

Tables are automatically created when the application starts via `create_tables()` in `app/main.py`.

---

## Project Structure

```
crs-backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   └── config.py              # Application configuration (env-based)
│   ├── api/
│   │   ├── base.py                # API router aggregation
│   │   ├── system.py              # Health check endpoints
│   │   ├── deps/                  # Dependencies (auth, etc.)
│   │   └── routes/                # API route handlers
│   ├── application/
│   │   ├── crud/                  # CRUD operations
│   │   ├── schemas/               # Pydantic schemas
│   │   └── services/              # Business logic services
│   └── infrastructure/
│       └── database/
│           ├── db_connection.py   # Database connection
│           ├── session.py         # Session management
│           └── models/            # SQLModel definitions
├── tests/                         # Test files
├── docker-compose.dev.yml         # Development environment
├── docker-compose.test.yml        # Test environment
├── start_dev.sh                   # Development startup script
├── run_tests.sh                   # Test runner script
├── Dockerfile                     # Docker image definition
├── pyproject.toml                 # Project dependencies
├── .env                           # Environment variables (local)
└── .env.example                   # Environment template
```

---

## 未來擴展

### 連接正式資料庫

只需修改 `.env` 中的資料庫設定：

```dotenv
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=prod_secure_password
POSTGRES_SERVER=your-production-db-host.com
POSTGRES_PORT=5432
POSTGRES_DB=clinic_prod
```

### 生產環境部署

1. 設定正式環境的 `.env`
2. 確保 `JWT_SECRET_KEY` 使用強密碼
3. 設定 `ENVIRONMENT=production`
4. 配置 CORS、HTTPS 等安全設定

---

## API Documentation

-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`
-   **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Troubleshooting

### Port 已被佔用

```bash
# 查看佔用 port 的程序
lsof -i :8000
lsof -i :5432

# 或使用不同 port
# 修改 docker-compose.dev.yml 中的 ports 設定
```

### 容器衝突

```bash
# 清理所有相關容器
docker ps -a | grep crs | awk '{print $1}' | xargs docker rm -f

# 清理 volumes
docker volume ls | grep crs | awk '{print $2}' | xargs docker volume rm
```

### 資料庫連接失敗

確認 `.env` 中的 `POSTGRES_SERVER` 設定：

-   Docker 環境：使用 `db`
-   本地直接連接：使用 `localhost`
