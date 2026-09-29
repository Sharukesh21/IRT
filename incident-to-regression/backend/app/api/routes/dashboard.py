from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api.dependencies import get_db
from app.db.models.incident import Incident
from app.db.models.regression_test import RegressionTest, RegressionTestRun
from app.db.models.ci import CIRegressionRun

router = APIRouter()

@router.get("/overview", response_model=Dict[str, Any])
async def get_overview(db: AsyncSession = Depends(get_db)):
    # Incidents
    total_incidents = await db.execute(select(func.count(Incident.id)))
    total_incidents_val = total_incidents.scalar() or 0
    
    open_incidents = await db.execute(select(func.count(Incident.id)).where(Incident.status == "OPEN"))
    open_incidents_val = open_incidents.scalar() or 0
    
    # Regression Tests
    total_tests = await db.execute(select(func.count(RegressionTest.id)))
    total_tests_val = total_tests.scalar() or 0
    
    # Test Runs
    passing_runs = await db.execute(select(func.count(RegressionTestRun.id)).where(RegressionTestRun.status == "PASSED"))
    passing_runs_val = passing_runs.scalar() or 0

    total_runs = await db.execute(select(func.count(RegressionTestRun.id)))
    total_runs_val = total_runs.scalar() or 0
    
    failing_tests_val = total_runs_val - passing_runs_val

    # CI Runs
    ci_runs = await db.execute(select(func.count(CIRegressionRun.id)))
    ci_runs_val = ci_runs.scalar() or 0

    return {
        "incidents": {
            "total": total_incidents_val,
            "open": open_incidents_val,
            "critical": 0 # simplified
        },
        "regressions": {
            "total_tests": total_tests_val,
            "passing": passing_runs_val,
            "failing": failing_tests_val
        },
        "ci": {
            "runs": ci_runs_val,
            "pass_rate": 1.0 if ci_runs_val == 0 else passing_runs_val / max(total_runs_val, 1)
        },
        "escapes": {
            "total": 0,
            "last_30_days": 0
        }
    }
