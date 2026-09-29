import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from app.db.session import get_db_session
from app.db.models.incident import Incident, IncidentGroup, IncidentTimeline, IncidentEvidence, IncidentRootCause, IncidentExpectation
from app.db.models.regression import ReproductionSpec, RegressionCandidate
from app.db.models.failure import FailureExperiment
from app.domain.incident_detector import IncidentDetector
from app.domain.incident_intelligence import IncidentIntelligence
from pydantic import BaseModel

router = APIRouter(prefix="/incidents", tags=["Incident Intelligence"])

@router.get("")
async def list_incidents(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(Incident).order_by(Incident.created_at.desc()))
    return {"items": res.scalars().all()}

@router.get("/groups")
async def list_incident_groups(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(IncidentGroup).order_by(IncidentGroup.last_seen_at.desc()))
    return {"items": res.scalars().all()}

from fastapi import BackgroundTasks
from app.core.job_store import job_store, JobStatus
from app.db.session import get_session_factory
import time

@router.post("/detect")
async def detect_incidents(
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db_session)
):
    """Scans all experiments for undetected incidents (runs in background)"""
    # Create the job tracking record
    job = job_store.create('INCIDENT_DETECTION')
    
    async def _run_detection():
        job_store.update_status(job.job_id, JobStatus.RUNNING, started_at=time.time())
        try:
            factory = get_session_factory()
            async with factory() as bg_db:
                # Get experiments that don't have an incident yet
                exp_res = await bg_db.execute(select(FailureExperiment.id).order_by(FailureExperiment.started_at.desc()).limit(20))
                exp_ids = exp_res.scalars().all()
                
                detector = IncidentDetector(bg_db)
                intelligence = IncidentIntelligence(bg_db)
                
                created_count = 0
                for eid in exp_ids:
                    # Check if incident exists
                    existing = await bg_db.execute(select(Incident).where(Incident.experiment_id == eid))
                    if existing.scalars().first():
                        continue
                        
                    detection = await detector.detect_from_experiment(eid)
                    if detection:
                        await intelligence.create_incident(detection)
                        created_count += 1
                        
                job_store.update_status(
                    job.job_id, 
                    JobStatus.COMPLETED, 
                    completed_at=time.time(), 
                    result={"detected_count": created_count}
                )
        except Exception as e:
            job_store.update_status(
                job.job_id, 
                JobStatus.FAILED, 
                completed_at=time.time(), 
                error=str(e)
            )
            
    background_tasks.add_task(_run_detection)
    return {"job_id": job.job_id, "status": "PENDING", "message": "Incident detection started in background"}

@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db_session)):
    # Can fetch by UUID or INC- string
    stmt = select(Incident).where(Incident.id == uuid.UUID(incident_id)) if len(incident_id) > 20 else select(Incident).where(Incident.incident_id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalars().first()
    if not incident:
        raise HTTPException(status_code=404)
        
    # Fetch relations
    tl_res = await db.execute(select(IncidentTimeline).where(IncidentTimeline.incident_id == incident.id).order_by(IncidentTimeline.sequence))
    rc_res = await db.execute(select(IncidentRootCause).where(IncidentRootCause.incident_id == incident.id))
    ex_res = await db.execute(select(IncidentExpectation).where(IncidentExpectation.incident_id == incident.id))
    ev_res = await db.execute(select(IncidentEvidence).where(IncidentEvidence.incident_id == incident.id))
    rep_res = await db.execute(select(ReproductionSpec).where(ReproductionSpec.incident_id == incident.id))
    reg_res = await db.execute(select(RegressionCandidate).where(RegressionCandidate.incident_id == incident.id))
    
    return {
        "incident": incident,
        "timeline": tl_res.scalars().all(),
        "root_cause": rc_res.scalars().first(),
        "expectations": ex_res.scalars().first(),
        "evidence": ev_res.scalars().all(),
        "reproduction": rep_res.scalars().first(),
        "regression_candidate": reg_res.scalars().first()
    }

@router.post("/{incident_id}/reproduce")
async def reproduce_incident(incident_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = select(Incident).where(Incident.id == uuid.UUID(incident_id)) if len(incident_id) > 20 else select(Incident).where(Incident.incident_id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalars().first()
    if not incident:
        raise HTTPException(status_code=404)
        
    rep_res = await db.execute(select(ReproductionSpec).where(ReproductionSpec.incident_id == incident.id))
    spec = rep_res.scalars().first()
    
    if not spec:
        raise HTTPException(status_code=400, detail="No reproduction spec available")

    # Genuine Execution of Reproduction
    from app.domain.test_runner import RegressionTestRunner
    from app.db.models.regression_test import RegressionTest
    import json
    
    # We dynamically create a temporary test definition for the reproduction
    temp_test = RegressionTest(
        test_id=f"REP-{uuid.uuid4().hex[:6].upper()}",
        incident_id=incident.id,
        name="Temporary Reproduction Test",
        test_definition={
            "events": spec.event_sequence,
            "failure": spec.failure_configuration,
            "assertions": [{"path": "status", "operator": "eq", "expected": "FAILED"}]
        }
    )
    db.add(temp_test)
    await db.commit()
    await db.refresh(temp_test)
    
    runner = RegressionTestRunner(db)
    run = await runner.run_test(temp_test.id)
    
    # Cleanup temporary test
    await db.delete(temp_test)
    await db.commit()

    reproduced = run.assertions_passed > 0 or "FAIL" in run.status or run.assertions_failed > 0
    
    return {
        "status": "REPRODUCED_SUCCESSFULLY" if reproduced else "REPRODUCTION_FAILED",
        "original_outcome": "CORRUPTED" if incident.state_corrupted else "RECOVERED",
        "reproduced_outcome": "CORRUPTED" if reproduced else "RECOVERED",
        "match": reproduced,
        "run_id": run.run_id
    }

@router.post("/{incident_id}/regression-candidate")
async def create_regression_candidate(incident_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = select(Incident).where(Incident.id == uuid.UUID(incident_id)) if len(incident_id) > 20 else select(Incident).where(Incident.incident_id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalars().first()
    
    rep_res = await db.execute(select(ReproductionSpec).where(ReproductionSpec.incident_id == incident.id))
    spec = rep_res.scalars().first()
    
    if not spec:
        raise HTTPException(status_code=400, detail="No reproduction spec available")
        
    cand = RegressionCandidate(
        candidate_id=f"RC-{uuid.uuid4().hex[:6].upper()}",
        incident_id=incident.id,
        reproduction_spec_id=spec.id,
        name=f"Automated test for {incident.failure_type}",
        trigger_condition=f"Apply {incident.failure_type} on {incident.primary_event_id}",
        expected_behavior="System must recover and maintain state invariants.",
        status="PENDING"
    )
    db.add(cand)
    incident.regression_candidate = True
    await db.commit()
    
    return {"status": "CREATED", "candidate_id": cand.candidate_id}
