import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.db.models.regression import RegressionCandidate, ReproductionSpec
from app.db.models.incident import Incident
from app.db.models.regression_test import RegressionTest, RegressionTestRun, RegressionAssertionResult, RegressionProof, RegressionSuiteRun
from app.domain.test_generator import RegressionTestGenerator
from app.domain.test_runner import RegressionTestRunner
from app.domain.suite import RegressionSuite

router = APIRouter(prefix="/regression", tags=["Regression Engineering"])

@router.get("/candidates")
async def list_candidates(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(RegressionCandidate).order_by(RegressionCandidate.created_at.desc()))
    return {"items": res.scalars().all()}

@router.post("/candidates/{candidate_id}/generate")
async def generate_test(candidate_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = select(RegressionCandidate).where(RegressionCandidate.candidate_id == candidate_id)
    res = await db.execute(stmt)
    cand = res.scalars().first()
    if not cand:
        raise HTTPException(404, "Candidate not found")
        
    spec_res = await db.execute(select(ReproductionSpec).where(ReproductionSpec.id == cand.reproduction_spec_id))
    spec = spec_res.scalars().first()
    
    inc_res = await db.execute(select(Incident).where(Incident.id == cand.incident_id))
    inc = inc_res.scalars().first()
    
    gen = RegressionTestGenerator(db)
    test = await gen.generate_from_candidate(cand, spec, inc)
    
    return {"status": "SUCCESS", "test_id": test.test_id}

@router.get("/tests")
async def list_tests(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(RegressionTest).order_by(RegressionTest.created_at.desc()))
    return {"items": res.scalars().all()}

@router.get("/tests/{test_id}")
async def get_test(test_id: str, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(RegressionTest).where(RegressionTest.test_id == test_id))
    test = res.scalars().first()
    if not test:
        raise HTTPException(404, "Test not found")
        
    proof_res = await db.execute(select(RegressionProof).where(RegressionProof.test_id == test.id))
    proof = proof_res.scalars().first()
    
    runs_res = await db.execute(select(RegressionTestRun).where(RegressionTestRun.test_id == test.id).order_by(RegressionTestRun.created_at.desc()))
    
    return {
        "test": test,
        "proof": proof,
        "runs": runs_res.scalars().all()
    }

from fastapi import BackgroundTasks
from app.core.job_store import job_store, JobStatus
from app.db.session import get_session_factory
import time

@router.post("/tests/{test_id}/run")
async def run_test(test_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(RegressionTest).where(RegressionTest.test_id == test_id))
    test = res.scalars().first()
    if not test:
        raise HTTPException(404, "Test not found")
        
    job = job_store.create('REGRESSION_TEST_RUN')
    
    async def _run_single_test():
        job_store.update_status(job.job_id, JobStatus.RUNNING, started_at=time.time())
        try:
            factory = get_session_factory()
            async with factory() as bg_db:
                # Reload test in background session
                bg_res = await bg_db.execute(select(RegressionTest).where(RegressionTest.test_id == test_id))
                bg_test = bg_res.scalars().first()
                runner = RegressionTestRunner(bg_db)
                run = await runner.run_test(bg_test.id)
                job_store.update_status(
                    job.job_id, JobStatus.COMPLETED, completed_at=time.time(),
                    result={"status": run.status, "run_id": run.run_id}
                )
        except Exception as e:
            job_store.update_status(job.job_id, JobStatus.FAILED, completed_at=time.time(), error=str(e))
            
    background_tasks.add_task(_run_single_test)
    return {"job_id": job.job_id, "status": "PENDING"}

@router.get("/runs/{run_id}")
async def get_run(run_id: str, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(RegressionTestRun).where(RegressionTestRun.run_id == run_id))
    run = res.scalars().first()
    if not run:
        raise HTTPException(404, "Run not found")
        
    asr_res = await db.execute(select(RegressionAssertionResult).where(RegressionAssertionResult.run_id == run.id))
    return {
        "run": run,
        "assertions": asr_res.scalars().all()
    }

@router.post("/suite/run")
async def run_suite(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db_session)):
    job = job_store.create('REGRESSION_SUITE_RUN')
    
    async def _run_full_suite():
        job_store.update_status(job.job_id, JobStatus.RUNNING, started_at=time.time())
        try:
            factory = get_session_factory()
            async with factory() as bg_db:
                suite = RegressionSuite(bg_db)
                result = await suite.run_suite()
                job_store.update_status(
                    job.job_id, JobStatus.COMPLETED, completed_at=time.time(),
                    result={"suite_run_id": result.suite_run_id, "pass_rate": result.pass_rate}
                )
        except Exception as e:
            job_store.update_status(job.job_id, JobStatus.FAILED, completed_at=time.time(), error=str(e))
            
    background_tasks.add_task(_run_full_suite)
    return {"job_id": job.job_id, "status": "PENDING"}

@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db_session)):
    # Simple metrics aggregation
    tests_res = await db.execute(select(func.count(RegressionTest.id)))
    runs_res = await db.execute(select(func.count(RegressionTestRun.id)))
    passed_res = await db.execute(select(func.count(RegressionTestRun.id)).where(RegressionTestRun.status == "PASSED"))
    
    t_count = tests_res.scalar()
    r_count = runs_res.scalar()
    p_count = passed_res.scalar()
    
    return {
        "total_tests": t_count,
        "total_runs": r_count,
        "pass_rate": (p_count / r_count * 100) if r_count > 0 else 0
    }
