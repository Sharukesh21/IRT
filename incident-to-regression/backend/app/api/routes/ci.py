import uuid
import hashlib
import hmac
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.db.session import get_db_session
from app.db.models.ci import (
    ExternalIncident, RegressionOrchestration, CIRegressionRun,
    RegressionPolicy, RegressionEscape
)
from app.db.models.incident import Incident
from app.db.models.regression_test import RegressionTest
from app.domain.ingestion import ExternalIncidentIngestor
from app.domain.orchestrator import RegressionOrchestrator
from app.core.config import get_settings

router = APIRouter(tags=["CI / Production Incidents"])
settings = get_settings()


# ── Schemas ────────────────────────────────────────────────────────────────────

class ExternalIncidentPayload(BaseModel):
    external_incident_id: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    severity: str = Field(default="HIGH")
    failure_type: str = Field(default="UNKNOWN")
    event_type: Optional[str] = None
    category: Optional[str] = "UNKNOWN"
    service: Optional[str] = None
    environment: Optional[str] = None
    session_id: Optional[str] = None
    source: Optional[str] = "PRODUCTION_API"
    metadata: Optional[dict] = None


class CIRunRequest(BaseModel):
    commit_sha: Optional[str] = None
    branch: Optional[str] = None
    incident_id: Optional[str] = None
    strategy: str = "TARGETED"
    trigger_source: Optional[str] = "PULL_REQUEST"
    repository: Optional[str] = None
    pull_request_number: Optional[int] = None


class PolicyCreate(BaseModel):
    policy_name: str
    strategy: str = "TARGETED"
    block_on_failure: bool = True
    required_severity: Optional[str] = None
    enabled: bool = True


# ── Ingestion ──────────────────────────────────────────────────────────────────

@router.post("/ci/incidents/ingest")
async def ingest_incident(payload: ExternalIncidentPayload, db: AsyncSession = Depends(get_db_session)):
    ingestor = ExternalIncidentIngestor(db)
    ext = await ingestor.ingest(payload.model_dump())
    return {
        "status": ext.status,
        "external_incident_id": ext.external_incident_id,
        "normalized_incident_id": str(ext.normalized_incident_id) if ext.normalized_incident_id else None
    }

@router.get("/ci/incidents")
async def list_external_incidents(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(ExternalIncident).order_by(ExternalIncident.received_at.desc()))
    return {"items": res.scalars().all()}

@router.get("/ci/incidents/{external_id}")
async def get_external_incident(external_id: str, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(ExternalIncident).where(ExternalIncident.external_incident_id == external_id))
    ext = res.scalars().first()
    if not ext:
        raise HTTPException(404, "Not found")
    return ext


# ── Regression CI Run ──────────────────────────────────────────────────────────

@router.post("/ci/regression/run")
async def trigger_ci_regression(req: CIRunRequest, db: AsyncSession = Depends(get_db_session)):
    if not req.incident_id:
        raise HTTPException(400, "incident_id is required")

    orch = RegressionOrchestrator(db)
    result = await orch.orchestrate(
        incident_id=req.incident_id,
        strategy=req.strategy,
        trigger_source=req.trigger_source or "PULL_REQUEST"
    )

    # Record CI Run
    ci_run = CIRegressionRun(
        run_id=f"CI-{uuid.uuid4().hex[:6].upper()}",
        orchestration_id=result.id,
        provider="github",
        repository=req.repository,
        branch=req.branch,
        commit_sha=req.commit_sha,
        pull_request_number=req.pull_request_number,
        status=result.status,
        completed_at=datetime.utcnow()
    )
    db.add(ci_run)
    await db.commit()

    return {
        "status": result.status,
        "tests": result.total_tests,
        "passed": result.passed,
        "failed": result.failed,
        "errors": result.errors,
        "orchestration_id": result.orchestration_id,
        "ci_run_id": ci_run.run_id
    }


# ── Orchestrations ─────────────────────────────────────────────────────────────

@router.get("/ci/orchestrations")
async def list_orchestrations(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(RegressionOrchestration).order_by(RegressionOrchestration.created_at.desc()))
    return {"items": res.scalars().all()}

@router.get("/ci/orchestrations/{orch_id}")
async def get_orchestration(orch_id: str, db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(RegressionOrchestration).where(RegressionOrchestration.orchestration_id == orch_id))
    orch = res.scalars().first()
    if not orch:
        raise HTTPException(404, "Not found")
    return orch


# ── CI Runs ────────────────────────────────────────────────────────────────────

@router.get("/ci/runs")
async def list_ci_runs(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(CIRegressionRun).order_by(CIRegressionRun.created_at.desc()))
    return {"items": res.scalars().all()}


# ── Policies ───────────────────────────────────────────────────────────────────

@router.get("/ci/policies")
async def list_policies(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(RegressionPolicy))
    return {"items": res.scalars().all()}

@router.post("/ci/policies")
async def create_policy(body: PolicyCreate, db: AsyncSession = Depends(get_db_session)):
    policy = RegressionPolicy(
        policy_name=body.policy_name,
        strategy=body.strategy,
        block_on_failure=body.block_on_failure,
        required_severity=body.required_severity,
        enabled=body.enabled
    )
    db.add(policy)
    await db.commit()
    return {"status": "CREATED"}


# ── Escapes ────────────────────────────────────────────────────────────────────

@router.get("/ci/escapes")
async def list_escapes(db: AsyncSession = Depends(get_db_session)):
    res = await db.execute(select(RegressionEscape).order_by(RegressionEscape.detected_at.desc()))
    return {"items": res.scalars().all()}


# ── Metrics ────────────────────────────────────────────────────────────────────

@router.get("/ci/metrics")
async def get_ci_metrics(db: AsyncSession = Depends(get_db_session)):
    incidents_total = (await db.execute(select(func.count(Incident.id)))).scalar()
    tests_total = (await db.execute(select(func.count(RegressionTest.id)))).scalar()
    escapes_total = (await db.execute(select(func.count(RegressionEscape.id)))).scalar()
    external_total = (await db.execute(select(func.count(ExternalIncident.id)))).scalar()
    orches_passed = (await db.execute(
        select(func.count(RegressionOrchestration.id)).where(RegressionOrchestration.status == "PASSED")
    )).scalar()
    orches_total = (await db.execute(select(func.count(RegressionOrchestration.id)))).scalar()

    return {
        "incidents_total": incidents_total,
        "tests_total": tests_total,
        "escapes_total": escapes_total,
        "external_ingested": external_total,
        "ci_pass_rate": round(orches_passed / orches_total * 100, 1) if orches_total else 0
    }


# ── GitHub Webhook ─────────────────────────────────────────────────────────────

@router.post("/integrations/github/webhook")
async def github_webhook(request: Request, db: AsyncSession = Depends(get_db_session)):
    secret = getattr(settings, "GITHUB_WEBHOOK_SECRET", None)
    body = await request.body()

    if secret:
        sig_header = request.headers.get("x-hub-signature-256", "")
        expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig_header, expected):
            raise HTTPException(403, "Invalid webhook signature")

    payload = await request.json()
    event_type = request.headers.get("x-github-event", "unknown")

    # Log and acknowledge — trigger orchestration for PR events
    if event_type == "pull_request" and payload.get("action") in ("opened", "synchronize"):
        pr = payload.get("pull_request", {})
        commit_sha = pr.get("head", {}).get("sha")
        branch = pr.get("head", {}).get("ref")
        pr_number = pr.get("number")
        repository = payload.get("repository", {}).get("full_name")
        return {
            "accepted": True,
            "event": event_type,
            "commit_sha": commit_sha,
            "branch": branch,
            "pr": pr_number,
            "repository": repository,
            "note": "CI regression run should be triggered via /api/v1/ci/regression/run"
        }

    return {"accepted": True, "event": event_type, "action": "logged"}
