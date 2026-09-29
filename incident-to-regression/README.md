# Incident-to-Regression Pipeline

An automated capstone platform that transforms production failures into reproducible, executable regression tests and orchestrates their execution in targeted CI workflows.

## Core Capabilities
- **Event-Sourcing Engine:** A complete online examination platform built on CQRS/Event-Sourcing.
- **Chaos & Failure Simulation:** Configurable DSL for injecting network drops, duplicates, timeouts, and state corruption.
- **Incident Intelligence:** Automatically detects integrity violations and isolates root causes from event timelines.
- **Automated Regression:** Converts failure scenarios into executable DSL regression tests with assertion engines.
- **Targeted CI Orchestration:** Ingests external production incidents, maps them to existing regression tests deterministically, and runs a targeted CI pipeline.
- **Evaluation Engine:** Benchmarking framework to objectively measure pipeline detection, reproduction, and test reduction efficiency.

## Architecture
- **Backend:** FastAPI, SQLAlchemy, Async PostgreSQL / SQLite, Pydantic
- **Frontend:** React, TypeScript, Tailwind CSS, Vite, Lucide Icons

## Quick Start (Single Click)
To start the entire project (backend and frontend concurrently), simply double-click the `start.bat` file in the root directory.

### Manual Start
**Backend:**
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## System Dashboards
- **`/simulator`**: Inject chaos and simulate failures
- **`/incidents`**: View detected incidents and root cause analysis
- **`/regression`**: View automatically generated regression tests
- **`/production-incidents`**: Simulate an external CI/CD incident ingestion
- **`/ci-regression`**: Dashboard showing targeted CI test executions and regression escapes
- **`/evaluation`**: Final Capstone evaluation benchmarks and metrics

## Limitations & Future Work
- The Incident Root Cause engine uses deterministic JSON rules. Future work could incorporate LLMs for dynamic unstructured log clustering.
- Targeted Test Selection is metadata-driven (Tags, Categories). Future work could integrate static AST code analysis to map tests precisely to changed code paths.
- Escapes detect *known* regressions returning. Zero-day defect prediction remains out of scope.
