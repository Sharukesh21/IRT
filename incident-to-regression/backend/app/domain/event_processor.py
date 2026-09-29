from datetime import datetime, timezone
import uuid
from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import structlog

from app.db.models.enums import EventStatus, ExamSessionStatus, SubmissionStatus
from app.db.models.event import Event
from app.db.models.session import ExamSession, Submission
from app.domain.events import BaseDomainEvent
from app.domain.state_machine import StateMachine

logger = structlog.get_logger(__name__)

class EventProcessor:
    """Processes domain events, evaluates state transitions, and guarantees idempotency."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_event(self, domain_event: BaseDomainEvent, expected_version: Optional[int] = None) -> dict:
        """Process a single event deterministically, with optional optimistic concurrency."""
        
        now = datetime.now(timezone.utc)
        
        # 1. Idempotency Check (Duplicate by ID)
        stmt = select(Event).where(Event.event_id == domain_event.event_id)
        result = await self.db.execute(stmt)
        existing_event = result.scalars().first()
        
        if existing_event:
            return self._build_result(
                existing_event, EventStatus.DUPLICATE, 
                None, None, "Event ID already exists."
            )

        # 2. Fetch Session & Optimistic Lock
        stmt_session = select(ExamSession).where(ExamSession.id == domain_event.session_id)
        res_session = await self.db.execute(stmt_session)
        session = res_session.scalars().first()
        
        if not session:
            # We can't save an event if the session doesn't exist, due to FK
            return self._build_result(
                domain_event, EventStatus.REJECTED, 
                None, None, "Session not found."
            )
            
        if expected_version is not None and session.version != expected_version:
            return self._build_result(
                domain_event, EventStatus.FAILED, 
                session.status, session.status, f"Concurrency conflict: expected version {expected_version}, got {session.version}"
            )

        previous_state = session.status

        # Create the Event record in RECEIVED state
        event_record = Event(
            event_id=domain_event.event_id,
            event_type=domain_event.event_type,
            session_id=uuid.UUID(str(domain_event.session_id)),
            student_id=uuid.UUID(str(domain_event.student_id)) if domain_event.student_id else None,
            exam_id=uuid.UUID(str(domain_event.exam_id)) if domain_event.exam_id else None,
            sequence_number=domain_event.sequence_number,
            correlation_id=domain_event.correlation_id,
            causation_id=domain_event.causation_id,
            occurred_at=domain_event.occurred_at,
            received_at=domain_event.received_at or now,
            status=EventStatus.RECEIVED,
            payload=domain_event.payload,
        )
        self.db.add(event_record)

        # 3. Domain Logic Idempotency Check
        if domain_event.event_type == "SUBMIT_REQUESTED":
            sub_key = f"{session.id}_submit_key" 
            stmt_sub = select(Submission).where(Submission.submission_key == sub_key)
            res_sub = await self.db.execute(stmt_sub)
            if res_sub.scalars().first():
                event_record.status = EventStatus.DUPLICATE
                event_record.processed_at = now
                await self.db.commit()
                return self._build_result(event_record, EventStatus.DUPLICATE, previous_state, session.status, "Submission already requested.")

        # 4. State Transition Check
        transition_result = StateMachine.evaluate_transition(session.status, domain_event.event_type)
        
        if not transition_result.allowed:
            # Graceful handle duplicate SUBMIT_REQUESTED when already SUBMITTED
            if session.status == ExamSessionStatus.SUBMITTED and domain_event.event_type == "SUBMIT_REQUESTED":
                event_record.status = EventStatus.DUPLICATE
                event_record.processed_at = now
                await self.db.commit()
                return self._build_result(event_record, EventStatus.DUPLICATE, previous_state, session.status, "Session already submitted.")

            event_record.status = EventStatus.REJECTED
            event_record.error_code = "INVALID_STATE_TRANSITION"
            event_record.error_message = transition_result.reason
            event_record.processed_at = now
            await self.db.commit()
            return self._build_result(event_record, EventStatus.REJECTED, previous_state, session.status, transition_result.reason)

        # 5. Apply Domain Operation
        if domain_event.event_type == "SUBMIT_REQUESTED":
            sub_key = f"{session.id}_submit_key"
            new_sub = Submission(
                session_id=session.id,
                submission_key=sub_key,
                status=SubmissionStatus.PENDING,
                submitted_at=now
            )
            self.db.add(new_sub)

        # 6. Update State
        if transition_result.new_state:
            session.status = transition_result.new_state
        
        session.last_activity_at = now
        session.version += 1 # Optimistic concurrency bump

        # 7. Finalize Event
        event_record.status = EventStatus.PROCESSED
        event_record.processed_at = now
        
        try:
            await self.db.commit()
            logger.info(
                "Event processed",
                event_id=event_record.event_id,
                type=event_record.event_type,
                session=str(session.id),
                previous=previous_state.value if previous_state else None,
                new=session.status.value,
                status=EventStatus.PROCESSED.value
            )
            return self._build_result(event_record, EventStatus.PROCESSED, previous_state, session.status)
        except IntegrityError as e:
            await self.db.rollback()
            logger.warning("Integrity error processing event", error=str(e))
            return self._build_result(
                domain_event, EventStatus.FAILED, 
                previous_state, session.status, "Database integrity error (possible duplicate sequence)."
            )
        except Exception as e:
            await self.db.rollback()
            logger.exception("Unexpected error processing event")
            return self._build_result(
                domain_event, EventStatus.FAILED, 
                previous_state, session.status, str(e)
            )

    def _build_result(
        self, event: Any, status: EventStatus, 
        prev_state: Optional[ExamSessionStatus], 
        new_state: Optional[ExamSessionStatus],
        message: Optional[str] = None
    ) -> dict:
        return {
            "event_id": getattr(event, "event_id", None),
            "status": status.value,
            "previous_state": prev_state.value if prev_state else None,
            "new_state": new_state.value if new_state else None,
            "message": message
        }
