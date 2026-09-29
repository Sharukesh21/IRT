import uuid
import time
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from app.db.session import get_db_session
from app.db.models.failure import FailureScenario, FailureExperiment, InjectedEvent, StateSnapshot, IntegrityResult, FailureType, SnapshotType
from app.db.models.session import ExamSession, Submission
from app.db.models.event import Event
from app.domain.events import BaseDomainEvent
from app.domain.failure_injector import FailureInjector
from app.domain.integrity_checker import IntegrityChecker
from app.domain.event_processor import EventProcessor
from pydantic import BaseModel

router = APIRouter(prefix="/failure", tags=["Failure Injection"])

# --- Schemas ---
class ScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    failure_type: FailureType
    target_event_type: Optional[str] = None
    target_event_id: Optional[str] = None
    parameters: dict = {}
    seed: Optional[int] = None

class ScenarioRunRequest(BaseModel):
    session_id: str

# --- Endpoints ---

@router.post("/scenarios", status_code=201)
async def create_scenario(scenario_in: ScenarioCreate, db: AsyncSession = Depends(get_db_session)):
    scenario = FailureScenario(
        name=scenario_in.name,
        description=scenario_in.description,
        failure_type=scenario_in.failure_type,
        target_event_type=scenario_in.target_event_type,
        target_event_id=scenario_in.target_event_id,
        parameters=scenario_in.parameters,
        seed=scenario_in.seed
    )
    db.add(scenario)
    await db.commit()
    await db.refresh(scenario)
    return {"data": {"id": str(scenario.id), "status": "READY"}}

@router.get("/scenarios")
async def list_scenarios(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(FailureScenario).order_by(FailureScenario.created_at.desc()))
    scenarios = result.scalars().all()
    return {"items": scenarios}

@router.post("/scenarios/{scenario_id}/run")
async def run_scenario(scenario_id: str, req: ScenarioRunRequest, db: AsyncSession = Depends(get_db_session)):
    # 1. Fetch scenario and session
    scenario_uuid = uuid.UUID(scenario_id)
    session_uuid = uuid.UUID(req.session_id)
    
    res_scen = await db.execute(select(FailureScenario).where(FailureScenario.id == scenario_uuid))
    scenario = res_scen.scalars().first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    res_sess = await db.execute(select(ExamSession).where(ExamSession.id == session_uuid))
    session = res_sess.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Create Experiment Record
    experiment = FailureExperiment(
        scenario_id=scenario_uuid,
        session_id=session_uuid,
        initial_state=session.status.value,
        started_at=datetime.utcnow()
    )
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)

    # 2. Capture Initial State Snapshot
    res_sub = await db.execute(select(func.count()).select_from(Submission).where(Submission.session_id == session_uuid))
    submission_count_before = res_sub.scalar() or 0
    
    state_before = {
        "status": session.status.value,
        "submission_count": submission_count_before,
        "version": session.version
    }
    
    snapshot_before = StateSnapshot(
        experiment_id=experiment.id,
        session_id=session_uuid,
        snapshot_type=SnapshotType.BEFORE,
        session_status=session.status.value,
        submission_count=submission_count_before,
        version=session.version,
        answer_state={} # Mock for now
    )
    db.add(snapshot_before)
    
    # 3. Get normal event stream (for this session)
    res_ev = await db.execute(select(Event).where(Event.session_id == session_uuid).order_by(Event.sequence_number))
    db_events = res_ev.scalars().all()
    
    domain_events = []
    for ev in db_events:
        domain_events.append(BaseDomainEvent(
            event_id=ev.event_id,
            event_type=ev.event_type,
            session_id=str(ev.session_id),
            sequence_number=ev.sequence_number,
            correlation_id=ev.correlation_id,
            occurred_at=ev.occurred_at,
            received_at=ev.received_at,
            payload=ev.payload
        ))
    
    # 4. Apply Failure Injector
    injector = FailureInjector()
    modified_events = injector.apply(domain_events, scenario)
    
    # Track injected metrics
    experiment.event_count = len(modified_events)
    experiment.duplicate_count = len(modified_events) - len(domain_events) if len(modified_events) > len(domain_events) else 0
    # simplified tracking for prototype
    
    # 5. Process Modified Events
    start_time = time.monotonic()
    processor = EventProcessor(db)
    
    processed_results = []
    for i, m_ev in enumerate(modified_events):
        # We process it by generating a new event_id if it's a completely new event, 
        # but for duplicates we keep the ID (the processor will catch it)
        # Actually, since these events might already exist in the DB (from normal processing),
        # running them AGAIN will just trigger DUPLICATE for all of them.
        # To truly simulate, we might need a test harness that intercepts BEFORE they are saved.
        # But for this API endpoint (re-running a trace), we will just pass them to the processor.
        # If they are already in DB, they will correctly return DUPLICATE.
        # To simulate a fresh run, you'd apply this to a new session.
        
        result = await processor.process_event(m_ev)
        processed_results.append(result)
        
        # Log injected event
        inj_ev = InjectedEvent(
            experiment_id=experiment.id,
            original_event_id=m_ev.event_id,
            injected_event_id=m_ev.event_id,
            failure_type=scenario.failure_type,
            modification="Injected",
            delivery_sequence=i+1,
            occurred_at=m_ev.occurred_at,
            received_at=m_ev.received_at or m_ev.occurred_at,
            status=result["status"]
        )
        db.add(inj_ev)

    end_time = time.monotonic()
    experiment.processing_time_ms = (end_time - start_time) * 1000

    # 6. Capture Final State Snapshot
    await db.refresh(session)
    res_sub_after = await db.execute(select(func.count()).select_from(Submission).where(Submission.session_id == session_uuid))
    submission_count_after = res_sub_after.scalar() or 0
    
    state_after = {
        "status": session.status.value,
        "submission_count": submission_count_after,
        "version": session.version
    }
    
    snapshot_after = StateSnapshot(
        experiment_id=experiment.id,
        session_id=session_uuid,
        snapshot_type=SnapshotType.AFTER,
        session_status=session.status.value,
        submission_count=submission_count_after,
        version=session.version,
        answer_state={}
    )
    db.add(snapshot_after)
    
    # 7. Validate Invariants
    integrity_res = IntegrityChecker.verify(state_before, state_after, processed_results)
    
    int_result = IntegrityResult(
        experiment_id=experiment.id,
        status=integrity_res["status"],
        state_corrupted=integrity_res["state_corrupted"],
        expected_state=integrity_res["expected_state"],
        actual_state=integrity_res["actual_state"],
        submission_count=integrity_res["submission_count"],
        violations=integrity_res["violations"]
    )
    db.add(int_result)
    
    experiment.completed_at = datetime.utcnow()
    experiment.final_state = state_after["status"]
    experiment.recovery_status = int_result.status
    experiment.state_corrupted = int_result.state_corrupted

    await db.commit()
    
    return {"data": {"experiment_id": str(experiment.id), "status": "COMPLETED"}}

@router.get("/experiments")
async def list_experiments(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(FailureExperiment).order_by(FailureExperiment.started_at.desc()))
    experiments = result.scalars().all()
    return {"items": experiments}

@router.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: str, db: AsyncSession = Depends(get_db_session)):
    exp_uuid = uuid.UUID(experiment_id)
    res = await db.execute(select(FailureExperiment).where(FailureExperiment.id == exp_uuid))
    experiment = res.scalars().first()
    if not experiment:
        raise HTTPException(status_code=404)
        
    res_int = await db.execute(select(IntegrityResult).where(IntegrityResult.experiment_id == exp_uuid))
    integrity = res_int.scalars().first()
    
    res_scen = await db.execute(select(FailureScenario).where(FailureScenario.id == experiment.scenario_id))
    scenario = res_scen.scalars().first()
    
    return {
        "experiment": experiment,
        "integrity": integrity,
        "scenario": scenario
    }

@router.get("/experiments/{experiment_id}/trace")
async def get_experiment_trace(experiment_id: str, db: AsyncSession = Depends(get_db_session)):
    exp_uuid = uuid.UUID(experiment_id)
    res = await db.execute(select(InjectedEvent).where(InjectedEvent.experiment_id == exp_uuid).order_by(InjectedEvent.delivery_sequence))
    events = res.scalars().all()
    return {"items": events}

@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db_session)):
    res_total = await db.execute(select(func.count()).select_from(FailureExperiment))
    total = res_total.scalar() or 0
    
    if total == 0:
        return {
            "total_experiments": 0,
            "recovery_rate": 0,
            "corruption_rate": 0
        }
        
    res_corrupt = await db.execute(select(func.count()).select_from(FailureExperiment).where(FailureExperiment.state_corrupted == True))
    corrupted = res_corrupt.scalar() or 0
    
    return {
        "total_experiments": total,
        "recovery_rate": round(((total - corrupted) / total) * 100, 2),
        "corruption_rate": round((corrupted / total) * 100, 2)
    }
