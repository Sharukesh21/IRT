import uuid
import time
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.db.models.ci import (
    RegressionPlan, RegressionPlanTest, RegressionOrchestration, RegressionEscape
)
from app.db.models.incident import Incident
from app.db.models.regression_test import RegressionTest, RegressionTestRun
from app.domain.test_runner import RegressionTestRunner


RELEVANCE_RULES = {
    "exact_incident": 100,
    "same_fingerprint": 80,
    "same_root_cause": 60,
    "same_failure_type": 40,
    "same_event_type": 30,
    "same_category": 20,
}

DOMAIN_TAG_MAP = {
    "submission_service": ["submission", "retry"],
    "answer_service": ["answers", "ordering"],
    "session_service": ["session", "network"],
}


class RegressionOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def score_test(self, test: RegressionTest, incident: Incident) -> tuple[int, str]:
        """Compute a deterministic relevance score with a human-readable reason."""
        score = 0
        reasons = []

        # Direct link via candidate
        if test.candidate_id:
            cand_res = await self.db.execute(
                select("app.db.models.regression.RegressionCandidate").where(  # type: ignore[arg-type]
                    __import__("app.db.models.regression", fromlist=["RegressionCandidate"]).RegressionCandidate.id == test.candidate_id
                )
            )

        if test.incident_id == incident.id:
            score += RELEVANCE_RULES["exact_incident"]
            reasons.append("Direct incident association")

        if test.failure_type and test.failure_type == incident.failure_type:
            score += RELEVANCE_RULES["same_failure_type"]
            reasons.append(f"Same failure type ({incident.failure_type})")

        if test.category and test.category == incident.category:
            score += RELEVANCE_RULES["same_category"]
            reasons.append(f"Same category ({incident.category})")

        return score, " | ".join(reasons) if reasons else "Partial match"

    async def select_tests(self, incident: Incident, strategy: str) -> List[Dict[str, Any]]:
        """Select and score tests relevant to an incident."""
        res = await self.db.execute(
            select(RegressionTest).where(RegressionTest.status.in_(["READY", "ACTIVE"]))
        )
        all_tests = res.scalars().all()

        if strategy == "FULL":
            return [{"test": t, "score": 0, "reason": "Full suite"} for t in all_tests]

        scored = []
        for t in all_tests:
            score, reason = await self.score_test(t, incident)
            if score > 0:
                scored.append({"test": t, "score": score, "reason": reason})

        # Safety: fallback to FULL if no targeted tests found
        if not scored:
            return [{"test": t, "score": 0, "reason": "No targets found — full suite fallback"} for t in all_tests]

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    async def orchestrate(self, incident_id: str, strategy: str = "TARGETED", trigger_source: str = "MANUAL") -> RegressionOrchestration:
        # Load incident
        inc_res = await self.db.execute(select(Incident).where(Incident.incident_id == incident_id))
        incident = inc_res.scalars().first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        # Select tests
        selected = await self.select_tests(incident, strategy)

        # Create plan
        plan_id = f"PLAN-{uuid.uuid4().hex[:6].upper()}"
        plan = RegressionPlan(
            plan_id=plan_id,
            incident_id=incident.id,
            selection_strategy=strategy,
            test_count=len(selected),
            status="CREATED"
        )
        self.db.add(plan)
        await self.db.flush()

        for order, item in enumerate(selected):
            pt = RegressionPlanTest(
                plan_id=plan.id,
                test_id=item["test"].id,
                relevance_score=item["score"],
                selection_reason=item["reason"],
                execution_order=order
            )
            self.db.add(pt)

        # Create orchestration
        orch_id = f"ORCH-{uuid.uuid4().hex[:6].upper()}"
        orch = RegressionOrchestration(
            orchestration_id=orch_id,
            incident_id=incident.id,
            plan_id=plan.id,
            trigger_source=trigger_source,
            status="PLANNING",
            total_tests=len(selected)
        )
        self.db.add(orch)
        await self.db.commit()

        # Execute
        orch.status = "RUNNING"
        orch.started_at = datetime.utcnow()
        self.db.add(orch)
        await self.db.commit()

        runner = RegressionTestRunner(self.db)
        passed = failed = errors = 0

        for item in selected:
            try:
                run = await runner.run_test(item["test"].id)
                if run.status == "PASSED":
                    passed += 1
                else:
                    failed += 1
                    # Check escape: if this incident already had a protective test, flag as escape
                    if item["test"].incident_id == incident.id:
                        escape = RegressionEscape(
                            incident_id=incident.id,
                            test_id=item["test"].id,
                            test_last_status="FAILED",
                            explanation="Test failed during orchestration of a recurring incident."
                        )
                        self.db.add(escape)
            except Exception as e:
                errors += 1

        orch.passed = passed
        orch.failed = failed
        orch.errors = errors
        orch.status = "PASSED" if failed == 0 and errors == 0 else ("ERROR" if failed == 0 else "FAILED")
        orch.completed_at = datetime.utcnow()
        self.db.add(orch)
        await self.db.commit()

        return orch
