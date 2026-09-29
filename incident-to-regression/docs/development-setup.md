# Development Setup

## Prerequisites
- Docker & Docker Compose
- Python 3.12+ (if running locally)
- Node 20+ (if running locally)
- Make (optional, helpful wrapper)

## Quick Start (Docker)
1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
2. Start the stack:
   ```bash
   make up
   # or: docker compose up -d
   ```
3. Run migrations (initial setup):
   ```bash
   make migrate
   # or: docker compose exec backend alembic upgrade head
   ```

## Local Development (Without Docker)

### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Running Tests
```bash
make test
# or:
# docker compose exec backend pytest tests/
# docker compose exec frontend npm run test
```

## Quality Checks
```bash
make lint
make typecheck
```

## Windows PowerShell Equivalents
If `make` is unavailable:
- `docker compose up -d`
- `docker compose down`
- `docker compose exec backend pytest tests/`
- `docker compose exec backend alembic upgrade head`
