# TraumaInsight Backend

Production-grade FastAPI backend for automated trauma registry chart abstraction.

## Prerequisites

- **Python 3.11+**
- **PostgreSQL 16** — via Docker Compose (from project root):
  ```bash
  docker-compose up -d
  ```

## Setup

```bash
cd backend

# Create virtual environment (optional, or use the project-level venv)
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Database Migrations

```bash
# Generate initial migration (already done)
alembic revision --autogenerate -m "initial tables"

# Apply migrations
alembic upgrade head
```

## Load Data

Run in order:

```bash
# 1. Load Synthea patient data (filters for trauma patients)
python scripts/load_synthea.py

# 2. Generate clinical notes (op reports, discharge summaries, radiology)
python scripts/generate_notes.py

# 3. Seed extraction data for first 5 patients
python scripts/seed_extractions.py
```

## Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

- **Health check:** http://localhost:8000/health
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Run Tests

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite database — no PostgreSQL required.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/patients` | List patients (filters: `?status=`, `?priority=`, `?limit=`, `?offset=`) |
| GET | `/api/patients/{id}` | Patient detail |
| GET | `/api/patients/{id}/form` | Registry form data (grouped by section) |
| PATCH | `/api/patients/{id}/status` | Update patient status |
| GET | `/api/patients/{id}/notes` | Clinical notes for patient |
| GET | `/api/patients/{id}/extractions` | Extractions for patient |
| GET | `/api/notes/{id}` | Single note |
| POST | `/api/extractions/{id}/confirm` | Confirm extraction |
| POST | `/api/extractions/{id}/correct` | Correct extraction |
| GET | `/api/stats/overview` | Dashboard statistics |
| POST | `/api/pipeline/run/{id}` | Pipeline placeholder (501) |
| POST | `/api/pipeline/run-all` | Pipeline placeholder (501) |

## Environment Variables

Loaded from `../.env` (project root):

| Variable | Default |
|----------|---------|
| `DATABASE_URL` | `postgresql://traumainsight:traumainsight_dev@localhost:5432/traumainsight` |
| `APP_ENV` | `development` |
| `APP_PORT` | `8000` |
| `FRONTEND_URL` | `http://localhost:3000` |
