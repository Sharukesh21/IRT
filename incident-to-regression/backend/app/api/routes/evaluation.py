from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db_session
from app.db.models.evaluation import EvaluationBenchmark, EvaluationExperiment
from app.domain.evaluation_engine import EvaluationEngine

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

@router.post("/seed")
async def seed_benchmarks(db: AsyncSession = Depends(get_db_session)):
    engine = EvaluationEngine(db)
    await engine.seed_benchmarks()
    return {"status": "seeded"}

@router.get("/benchmarks")
async def list_benchmarks(db: AsyncSession = Depends(get_db_session)):
    engine = EvaluationEngine(db)
    benchmarks = await engine.get_benchmarks()
    return {"items": benchmarks}

@router.post("/experiments/run")
async def run_experiment(benchmark_id: str, db: AsyncSession = Depends(get_db_session)):
    engine = EvaluationEngine(db)
    try:
        exp = await engine.run_experiment(benchmark_id)
        return {"status": "completed", "experiment_id": exp.experiment_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db_session)):
    engine = EvaluationEngine(db)
    metrics = await engine.get_metrics()
    return metrics
