import uuid
import time
from typing import Dict, Any, List
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.regression_test import RegressionTest, RegressionTestRun, RegressionAssertionResult, RegressionProof
from app.db.models.event import Event
from app.db.models.session import ExamSession, StudentAnswer, Submission
from app.domain.assertions import AssertionEngine
from app.domain.state_machine import StateMachine
from app.domain.event_processor import EventProcessor
from app.domain.failure_injector import FailureInjector
from app.db.models.enums import ExamSessionStatus
from app.domain.events import (
    ExamStartedEvent, QuestionViewedEvent, AnswerSelectedEvent, 
    AnswerSavedEvent, SubmitRequestedEvent, BaseDomainEvent
)

logger = structlog.get_logger(__name__)

class RegressionTestRunner:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.assertion_engine = AssertionEngine()
        
    async def run_test(self, test_id: uuid.UUID) -> RegressionTestRun:
        # Load test definition
        res = await self.db.execute(select(RegressionTest).where(RegressionTest.id == test_id))
        test = res.scalars().first()
        if not test:
            raise ValueError("Test not found")
            
        run_id = f"RUN-{uuid.uuid4().hex[:6].upper()}"
        start_time = time.time()
        
        # 1. Setup Isolated Environment (New DB Session context)
        # We simulate isolated execution by starting a subtransaction or creating fresh records.
        # Since SQLite async doesn't fully support nested transactions seamlessly in this driver context, 
        # we will run it in the current session but ensure we rollback on exception, 
        # or we commit isolated records with unique UUIDs.
        
        session_id = uuid.uuid4()
        test_session = ExamSession(
            id=session_id,
            student_id=uuid.uuid4(),
            exam_id=uuid.uuid4(),
            status=ExamSessionStatus.NOT_STARTED
        )
        self.db.add(test_session)
        await self.db.commit() # Commit base setup to allow foreign keys in EventProcessor
        
        raw_events = test.test_definition.get("events", [])
        domain_events = []
        
        # 2. Map JSON definition to true Domain Events
        seq = 1
        for e in raw_events:
             e_id = uuid.uuid4()
             e_type = e.get("type")
             base_kwargs = {
                 "event_id": str(e_id),
                 "session_id": str(session_id),
                 "sequence_number": seq,
                 "correlation_id": str(uuid.uuid4())
             }
             
             if e_type == "SESSION_STARTED":
                 dev = ExamStartedEvent(**base_kwargs)
             elif e_type == "QUESTION_VIEWED":
                 dev = QuestionViewedEvent(payload={"question_id": e.get("question_id")}, **base_kwargs)
             elif e_type == "ANSWER_SELECTED":
                 dev = AnswerSelectedEvent(payload={"question_id": e.get("question_id"), "answer_id": e.get("answer")}, **base_kwargs)
             elif e_type == "ANSWER_SAVED":
                 dev = AnswerSavedEvent(payload={"question_id": e.get("question_id")}, **base_kwargs)
             elif e_type == "SUBMIT_REQUESTED":
                 dev = SubmitRequestedEvent(**base_kwargs)
             else:
                 dev = BaseDomainEvent(event_type=e_type, **base_kwargs)
                 
             domain_events.append(dev)
             seq += 1

        # 3. Inject Failure
        fc = test.test_definition.get("failure", {})
        if fc:
            class MockScenario: pass
            scen = MockScenario()
            scen.failure_type = type("FT", (), {"name": fc.get("type")})()
            scen.target_event_type = fc.get("target")
            scen.parameters = fc.get("params", {})
            domain_events = FailureInjector.apply(domain_events, scen)
            
        # 4. Process Events Genuinely
        processor = EventProcessor(self.db)
        trace = []
        expected_version = 1
        
        for ev in domain_events:
            try:
                # Actual real processing utilizing optimistic locking
                res = await processor.process_event(ev, expected_version=expected_version)
                trace.append({"event": ev.event_type, "status": res.get("status"), "message": res.get("message")})
                
                # Check if it was processed cleanly
                if res.get("status") == "PROCESSED":
                    expected_version += 1
            except Exception as ex:
                trace.append({"event": ev.event_type, "status": "ERROR", "error": str(ex)})

        # 5. Extract Final State
        await self.db.refresh(test_session)
        sub_res = await self.db.execute(select(Submission).where(Submission.session_id == session_id))
        subs = sub_res.scalars().all()
        
        final_state = {
            "status": test_session.status.value,
            "submission_count": len(subs)
        }
        
        # 6. Assertions Engine Execution
        assertions = test.test_definition.get("assertions", [])
        passed = 0
        failed = 0
        
        run = RegressionTestRun(
            run_id=run_id,
            test_id=test.id,
            incident_id=test.incident_id,
            session_id=str(session_id),
            execution_trace=trace,
            assertions_total=len(assertions)
        )
        self.db.add(run)
        
        for idx, ast in enumerate(assertions):
            path = ast.get("path")
            op = ast.get("operator")
            exp = ast.get("expected")
            actual = self.assertion_engine.extract_value(final_state, path)
            
            is_pass = self.assertion_engine.evaluate(op, exp, actual)
            if is_pass: passed += 1
            else: failed += 1
            
            ar = RegressionAssertionResult(
                run_id=run.id,
                assertion_index=idx,
                path=path,
                operator=op,
                expected_value=str(exp),
                actual_value=str(actual),
                status="PASS" if is_pass else "FAIL",
                message=None if is_pass else f"Expected {exp}, got {actual}"
            )
            self.db.add(ar)
            
        run.assertions_passed = passed
        run.assertions_failed = failed
        run.status = "PASSED" if failed == 0 else "FAILED"
        run.completed_at = time.strftime('%Y-%m-%d %H:%M:%S')
        run.duration_ms = (time.time() - start_time) * 1000
        
        # 7. Update Proof / Protection Status
        proof_res = await self.db.execute(select(RegressionProof).where(RegressionProof.test_id == test.id))
        proof = proof_res.scalars().first()
        if not proof:
            proof = RegressionProof(test_id=test.id, incident_id=test.incident_id)
            self.db.add(proof)
            
        if not proof.before_run_id:
            proof.before_run_id = run.id
            proof.before_status = run.status
        else:
            proof.after_run_id = run.id
            proof.after_status = run.status
            if proof.before_status == "FAILED" and proof.after_status == "PASSED":
                proof.protected = True
                
        await self.db.commit()
        return run
