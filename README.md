# TaskService v2.0.0

Production-ready REST API for task management with full observability stack (MELT: Metrics, Events, Logs, Traces).

[![CI](https://github.com/wittiden/TaskService/actions/workflows/ci.yaml/badge.svg)](https://github.com/wittiden/TaskService/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/wittiden/TaskService/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/TaskService)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.138.2-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Observability](#-observability)
- [CI/CD](#-cicd)
- [Docker Deployment](#-docker-deployment)
- [API Documentation](#-api-documentation)
- [License](#-license)

## ✨ Features

- **JWT Authentication** — Access + Refresh tokens with RSA encryption
- **Role-Based Access Control** — Admin, VIP, Standard users
- **Task Management** — CRUD operations with status tracking (closed/completed)
- **Rate Limiting** — Per-endpoint rate limiting with SlowAPI
- **Dependency Injection** — Clean architecture with Dishka
- **Full Observability** — MELT stack (Metrics, Events, Logs, Traces)
- **Audit Logging** — Track all user and task changes
- **Async PostgreSQL** — High-performance async ORM with SQLAlchemy 2.0
- **Redis Caching** — User sessions and current user cache
- **Database Migrations** — Alembic with version control
- **Testing** — Unit, integration, and E2E tests with 70%+ coverage

## 🛠️ Technology Stack

### Core
| Component | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.138.2 | Web framework |
| **Starlette** | 1.3.1 | ASGI middleware |
| **Uvicorn** | 0.49.0 | ASGI server |
| **Gunicorn** | 26.0.0 | Production server |
| **SlowAPI** | 0.1.10 | Rate limiting |

### Dependency Injection
| Component | Version | Purpose |
|-----------|---------|---------|
| **Dishka** | 1.10.1 | DI container |

### Data Layer
| Component | Version | Purpose |
|-----------|---------|---------|
| **SQLAlchemy** | 2.0.51 | Async ORM |
| **AsyncPG** | 0.31.0 | PostgreSQL driver |
| **Alembic** | 1.18.5 | Migrations |
| **Redis** | 8.0.1 | Cache & sessions |

### Security
| Component | Version | Purpose |
|-----------|---------|---------|
| **PyJWT** | 2.13.0 | JWT handling |
| **Bcrypt** | 5.0.0 | Password hashing |

### Observability (MELT)
| Component | Version | Purpose |
|-----------|---------|---------|
| **Prometheus** | v3.1.0 | Metrics collection |
| **Grafana** | 13.1 | Visualization |
| **Sentry** | 2.66.1 | Error tracking |
| **Loguru** | 0.7.3 | Structured logging |

### Code Quality
| Component | Version | Purpose |
|-----------|---------|---------|
| **Ruff** | 0.15.20 | Linting & formatting |
| **Pyright** | 1.1.411 | Type checking |
| **Pre-commit** | 4.6.0 | Git hooks |

### Testing
| Component | Version | Purpose |
|-----------|---------|---------|
| **Pytest** | 9.1.1 | Test framework |
| **Pytest-Asyncio** | 1.4.0 | Async tests |
| **Pytest-Cov** | 7.1.0 | Coverage reporting |
| **Testcontainers** | 4.14.2 | Integration tests |
| **Factory-Boy** | 3.3.3 | Test data factories |
| **Faker** | 40.28.1 | Fake data generation |
| **HTTPX** | 0.28.1 | Async HTTP client |

## 🏗️ Architecture

The project follows **Clean Architecture** principles with a clear separation of concerns:

```
┌──────────────────────────────────────────────────────────────┐
│                      Presentation Layer                     │
│                    (API Routers + Schemas)                   │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                      Application Layer                      │
│              (Use Cases + Services + DTOs)                   │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                       Domain Layer                          │
│               (Entities + Value Objects)                     │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                     │
│      (Repositories + Database + Redis + HTTP)               │
└──────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

- **Repository Pattern** — Data access abstraction
- **Use Case Pattern** — Business logic encapsulation
- **Dependency Injection** — Decoupling with Dishka
- **Unit of Work** — Transaction management
- **Factory Pattern** — Object creation
- **Observer Pattern** — Audit logging

## 📁 Project Structure

```
TaskService/
├── app/
│   ├── main.py                    # Application entry point
│   ├── bootstrap/                 # Application bootstrap
│   │   ├── application.py         # FastAPI app factory
│   │   ├── handlers.py            # Exception handlers
│   │   ├── middlewares.py         # Global middleware
│   │   └── routers.py             # Route registration
│   ├── common/                    # Shared utilities
│   │   ├── config.py              # Pydantic settings
│   │   ├── enums/                 # Enumerations
│   │   ├── exceptions/            # Base exceptions
│   │   ├── limiter/               # Rate limiting
│   │   ├── observability/         # MELT stack
│   │   │   ├── logs/              # Loguru configuration
│   │   │   ├── events/            # Sentry configuration
│   │   │   └── metrics.py         # Prometheus metrics
│   │   └── security/              # JWT & password utils
│   ├── container/                 # Dishka DI container
│   │   └── container.py
│   ├── infrastructure/            # Infrastructure layer
│   │   ├── database/              # PostgreSQL + SQLAlchemy
│   │   │   ├── base.py            # Base model
│   │   │   ├── config.py          # DB config
│   │   │   └── model/             # SQLAlchemy models
│   │   ├── http/                  # HTTP layer
│   │   │   ├── lifespan.py        # Startup/shutdown
│   │   │   ├── healthcheck/       # Health endpoints
│   │   │   ├── middleware/        # CORS, logging, timeout
│   │   │   └── server/            # Server config
│   │   ├── redis/                 # Redis cache
│   │   │   ├── config.py          # Redis config
│   │   │   └── repositories/      # Cache repositories
│   │   └── unit_of_work/          # UoW pattern
│   │       └── uow.py
│   └── modules/                   # Business modules
│       ├── audits/                # Audit module
│       ├── auth/                  # Authentication
│       ├── sessions/              # Session management
│       ├── tasks/                 # Task management
│       └── users/                 # User management
├── migrations/                    # Alembic migrations
├── tests/                         # Tests
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── factories/                 # Test data factories
├── certs/                         # JWT RSA keys
├── logs/                          # Log files
├── .env                           # Environment variables
├── .env.example                   # Example environment
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml                 # Project configuration
├── pytest.ini                     # Pytest configuration
├── docker-compose.yml             # Docker services
├── Dockerfile                     # App Docker image
├── prometheus.yml                 # Prometheus config
├── requirements-dev.txt           # Dev dependencies
├── requirements-prod.txt          # Production dependencies
├── LICENSE
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git
- Make (optional)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/TaskService.git
   cd TaskService
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   pip install -r requirements-prod.txt
   ```

4. **Copy environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Generate JWT keys:**
   ```bash
   cd certs
   openssl genrsa -out access-private.pem 2048
   openssl genrsa -out refresh-private.pem 2048
   openssl rsa -in access-private.pem -pubout -out access-public.pem
   openssl rsa -in refresh-private.pem -pubout -out refresh-public.pem
   cd ..
   ```

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

8. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Metrics: http://localhost:8000/metrics

## 🐳 Docker Deployment

### Full Stack with Docker Compose

1. **Start all services:**
   ```bash
   docker compose up -d
   ```

2. **Start with monitoring (Prometheus + Grafana):**
   ```bash
   docker compose --profile grafana up -d
   ```

3. **Start all services including PgAdmin and RedisInsight:**
   ```bash
   docker compose --profile pgadmin --profile redisinsight --profile grafana up -d
   ```

4. **View logs:**
   ```bash
   docker compose logs -f app
   ```

5. **Stop all services:**
   ```bash
   docker compose down
   ```

### Services Overview

| Service | Container Name | Port | Purpose |
|---------|---------------|------|---------|
| **App** | task_service_app | 8000 | FastAPI application |
| **PostgreSQL** | task_service_db | 5432 | Primary database |
| **Redis** | task_service_redis | 6379 | Cache & sessions |
| **PgAdmin** | task_service_pgadmin | 5050 | DB management (profile) |
| **RedisInsight** | task_service_redisinsight | 5540 | Redis UI (profile) |
| **Prometheus** | task_service_prometheus | 9090 | Metrics collection |
| **Grafana** | task_service_grafana | 3000 | Visualization (profile) |

### Docker Commands

```bash
# Build and start
docker compose up -d --build

# Check status
docker compose ps

# View logs for specific service
docker compose logs -f app

# Execute command inside container
docker compose exec app bash

# Stop and remove containers
docker compose down

# Remove volumes (WARNING: deletes all data)
docker compose down -v
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Environment
ENVIRONMENT=development

# Database
DB_USER=postgres
DB_PASS=root
DB_NAME=task_service
DB_PORT=5432

# Redis
REDIS_PASS=root
REDIS_PORT=6379

# JWT
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256

# Sentry
SENTRY_DSN=your_sentry_dsn

# Grafana
GRAFANA_USERNAME=admin
GRAFANA_PASSWORD=admin

# Server
SERVER_PORT=8000

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60
```

### Application Settings (app/common/config.py)

The application uses `pydantic-settings` for configuration management:

```python
class ApplicationConfig(BaseSettings):
    ENVIRONMENT: str = "development"
    DB_USER: str = "postgres"
    DB_PASS: str = "root"
    # ... all settings are validated automatically
```

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_auth_service.py

# Specific test
pytest tests/unit/test_auth_service.py::test_login_user

# Parallel execution
pytest -n auto

# Integration tests only
pytest tests/integration/
```

### Test Coverage

```bash
pytest --cov=app --cov-fail-under=70 --cov-report=html
open htmlcov/index.html
```

### Coverage Configuration (pyproject.toml)

```toml
[tool.coverage.run]
source = ["app"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 70
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
]
```

## 📊 Observability (MELT Stack)

### Metrics — Prometheus + Grafana

**Available metrics:**
- `http_requests_total` — Total requests by endpoint
- `http_request_duration_seconds` — Request latency histogram
- `http_request_size_bytes` — Request size summary
- `http_response_size_bytes` — Response size summary
- `http_combined_size_bytes` — Combined traffic size
- Custom business metrics (users, tasks, etc.)

**Access:**
- Prometheus UI: http://localhost:9090
- Grafana: http://localhost:3000 (login: admin/admin)
- App metrics: http://localhost:8000/metrics

**Grafana Dashboards:**
- FastAPI dashboard (ID: 11361)
- Prometheus dashboard (ID: 1860)
- PostgreSQL dashboard (ID: 11074)
- Redis dashboard (ID: 11835)

### Events — Sentry

**Captured events:**
- All unhandled exceptions
- Error-level logs from Loguru
- Performance traces (sampled at 10%)

**Access:** https://sentry.io

### Logs — Loguru + Loki (planned)

**Log levels:**
- `DEBUG` — Development details (console only)
- `INFO` — Business events (file + console)
- `WARNING` — Expected issues (file + console)
- `ERROR` — Technical errors (file + console + Sentry)

**Log rotation:**
- Rotation: 500 MB
- Retention: 15 days
- Compression: ZIP

**Log files:**
- `logs/app.log` — Human-readable logs
- `logs/app.json` — JSON structured logs for Loki

## 🔄 CI/CD Pipeline

### GitHub Actions (CI)

The CI pipeline runs on every push and pull request to `main`:

```yaml
name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Clone Repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'
          cache: 'pip'
          cache-dependency-path: |
            requirements-dev.txt
            requirements-prod.txt

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements-dev.txt
          python -m pip install -r requirements-prod.txt

      - name: Linting
        run: ruff check .

      - name: Formatting
        run: ruff format . --check

      - name: Type Checking
        run: pyright

  tests:
    needs: check
    runs-on: ubuntu-latest
    timeout-minutes: 10

    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.12', '3.13', '3.14']

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: root
          POSTGRES_DB: test_postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:8.0-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Clone Repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
          cache-dependency-path: |
            requirements-dev.txt
            requirements-prod.txt

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements-dev.txt
          python -m pip install -r requirements-prod.txt

      - name: Generate JWT Keys
        run: |
          cd certs
          openssl genrsa -out access-private.pem 2048
          openssl genrsa -out refresh-private.pem 2048
          openssl rsa -in access-private.pem -pubout -out access-public.pem
          openssl rsa -in refresh-private.pem -pubout -out refresh-public.pem

      - name: Run Unit & Integration Tests
        if: matrix.python-version != '3.14'
        run: python -m pytest -m "unit or integration" -n auto

      - name: Run Unit & Integration Tests & Coverage
        if: matrix.python-version == '3.14'
        run: python -m pytest -m "unit or integration" -n auto --cov=app --cov-fail-under=70 --cov-report=term --cov-report=html --cov-report=xml

      - name: Upload coverage reports to Codecov
        if: matrix.python-version == '3.14'
        uses: codecov/codecov-action@v5
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: true

```

### Pipeline Status

| Check | Status |
|-------|--------|
| **Linting** | ✅ Ruff |
| **Formatting** | ✅ Ruff |
| **Type Checking** | ✅ Pyright |
| **Unit Tests** | ✅ Pytest |
| **Integration Tests** | ✅ Pytest |
| **Coverage** | ✅ ≥70% |
| **Codecov** | ✅ Uploaded |

### Code Quality Tools

```bash
# Run linting
ruff check .

# Run formatting check
ruff format . --check

# Run type checking
pyright

# Auto-fix linting issues
ruff check . --fix

# Format code
ruff format .
```

## 📚 API Documentation

### Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | Login user |
| `POST` | `/api/v1/auth/logout` | Logout from device |
| `POST` | `/api/v1/auth/logout-all` | Logout from all devices |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |

#### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/users/standard` | Create standard user |
| `POST` | `/api/v1/users/vip` | Create VIP user |
| `POST` | `/api/v1/users/admin` | Create admin user |
| `GET` | `/api/v1/users/me` | Get current user |
| `GET` | `/api/v1/users/{user_id}` | Get user by ID |
| `GET` | `/api/v1/users` | Get users list |
| `PATCH` | `/api/v1/users/me` | Update current user |
| `PATCH` | `/api/v1/users/{user_id}/block` | Block user |
| `PATCH` | `/api/v1/users/{user_id}/unblock` | Unblock user |
| `DELETE` | `/api/v1/users/me` | Close account |
| `DELETE` | `/api/v1/users/{user_id}` | Delete user |

#### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/tasks` | Create task |
| `GET` | `/api/v1/tasks/me` | Get user tasks |
| `GET` | `/api/v1/tasks/me/completed` | Get completed tasks |
| `GET` | `/api/v1/tasks/me/closed` | Get closed tasks |
| `GET` | `/api/v1/tasks/me/active` | Get active tasks |
| `GET` | `/api/v1/tasks/{task_id}` | Get task by ID |
| `PATCH` | `/api/v1/tasks/{task_id}` | Update task |
| `PATCH` | `/api/v1/tasks/{task_id}/close` | Close task |
| `PATCH` | `/api/v1/tasks/{task_id}/complete` | Complete task |
| `DELETE` | `/api/v1/tasks/{task_id}` | Delete task |
| `DELETE` | `/api/v1/tasks/me/completed` | Delete completed tasks |
| `DELETE` | `/api/v1/tasks/me/closed` | Delete closed tasks |
| `DELETE` | `/api/v1/tasks/me` | Delete all tasks |

#### Audits
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/audits/users` | Get user audits |
| `GET` | `/api/v1/audits/users/{user_id}` | Get user audits by user |
| `GET` | `/api/v1/audits/users/{audit_id}` | Get user audit by ID |
| `GET` | `/api/v1/audits/tasks` | Get task audits |
| `GET` | `/api/v1/audits/tasks/{task_id}` | Get task audits by task |
| `GET` | `/api/v1/audits/tasks/{audit_id}` | Get task audit by ID |

#### Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/sessions/me` | Get user sessions |
| `GET` | `/api/v1/sessions/{token_id}` | Get session by ID |
| `GET` | `/api/v1/sessions` | Get all sessions |
| `DELETE` | `/api/v1/sessions/{token_id}` | Delete session |

#### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health/app` | App health |
| `GET` | `/api/v1/health/db` | Database health |
| `GET` | `/api/v1/health/redis` | Redis health |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

1. **Code Style**: Follow PEP 8 and Ruff rules
2. **Type Hints**: Use type annotations everywhere
3. **Tests**: Write tests for new features
4. **Coverage**: Maintain ≥70% test coverage
5. **Documentation**: Update README and API docs
6. **Pre-commit**: Run pre-commit hooks before committing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**wittiden**
- GitHub: [@wittiden](https://github.com/wittiden)

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) — SQL toolkit
- [Prometheus](https://prometheus.io/) — Monitoring system
- [Grafana](https://grafana.com/) — Visualization platform
- [Sentry](https://sentry.io/) — Error tracking

---


⭐ Star this repository if you find it useful!
