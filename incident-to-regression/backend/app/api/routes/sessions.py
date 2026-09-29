import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.api.dependencies import get_db
from app.db.models.session import ExamSession, StudentAnswer
from app.db.models.event import Event
from app.schemas.session import SessionStartRequest, SessionResponse, AnswerSubmitRequest, EventTraceResponse
from app.domain.events import BaseDomainEvent, EventType
from app.domain.event_processor import EventProcessor

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.get("", tags=["Sessions"])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ExamSession).order_by(ExamSession.created_at.desc()).limit(50)
    )
    sessions = result.scalars().all()
    return {"items": sessions, "total": len(sessions), "page": 1, "size": len(sessions)}

def _generate_event_id() -> str:
    return f"evt_{uuid.uuid4().hex}"

async def _dispatch_event(
    db: AsyncSession, 
    request: Request,
    session: ExamSession, 
    event_type: EventType, 
    payload: dict
) -> dict:
    req_id = request.state.request_id if hasattr(request.state, "request_id") else uuid.uuid4().hex
    # For a real implementation, sequence_number comes from atomic counter or DB
    # For prototype, we count existing events
    count_stmt = select(Event).where(Event.session_id == session.id)
    ev_result = await db.execute(count_stmt)
    seq = len(ev_result.scalars().all()) + 1
    
    event = BaseDomainEvent(
        event_id=_generate_event_id(),
        event_type=event_type,
        session_id=str(session.id),
        student_id=str(session.student_id),
        exam_id=str(session.exam_id),
        sequence_number=seq,
        correlation_id=req_id,
        occurred_at=datetime.now(timezone.utc),
        payload=payload
    )
    processor = EventProcessor(db)
    return await processor.process_event(event)

@router.post("", response_model=SessionResponse)
async def start_session(
    req: SessionStartRequest, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Create the session model directly, but trigger the event to log it and transition state
    session = ExamSession(
        student_id=req.student_id,
        exam_id=req.exam_id,
        started_at=datetime.now(timezone.utc)
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    await _dispatch_event(db, request, session, "EXAM_STARTED", {})
    await db.refresh(session)
    return session

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExamSession).where(ExamSession.id == session_id))
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/{session_id}/answers/{question_id}")
async def save_answer(
    session_id: UUID, 
    question_id: UUID, 
    payload: AnswerSubmitRequest, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    session_result = await db.execute(select(ExamSession).where(ExamSession.id == session_id))
    session = session_result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Let the event processor handle state logic
    await _dispatch_event(db, request, session, "ANSWER_SELECTED", {
        "question_id": str(question_id),
        "selected_option": payload.selected_option
    })
    
    # Save to db
    ans_stmt = select(StudentAnswer).where(
        StudentAnswer.session_id == session_id,
        StudentAnswer.question_id == question_id
    )
    ans_res = await db.execute(ans_stmt)
    answer = ans_res.scalars().first()
    if answer:
        answer.selected_option = payload.selected_option
        answer.version += 1
    else:
        answer = StudentAnswer(
            session_id=session_id,
            question_id=question_id,
            selected_option=payload.selected_option
        )
        db.add(answer)
    await db.commit()
    
    await _dispatch_event(db, request, session, "ANSWER_SAVED", {
        "question_id": str(question_id)
    })
    
    return {"status": "saved"}

@router.post("/{session_id}/submit")
async def submit_exam(
    session_id: UUID, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    session_result = await db.execute(select(ExamSession).where(ExamSession.id == session_id))
    session = session_result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    res1 = await _dispatch_event(db, request, session, "SUBMIT_REQUESTED", {})
    
    # If the submit was rejected, bubble up error
    if res1.get("status") == "REJECTED":
        raise HTTPException(status_code=400, detail=res1.get("message"))
        
    # If it was duplicate, just acknowledge it safely
    if res1.get("status") == "DUPLICATE":
        return {"status": "duplicate_acknowledged"}
    
    # If successful, confirm it
    await _dispatch_event(db, request, session, "SUBMISSION_CONFIRMED", {})
    return {"status": "submitted"}

@router.get("/{session_id}/events")
async def get_session_events(session_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Event)
        .where(Event.session_id == session_id)
        .order_by(Event.sequence_number.asc())
    )
    events = result.scalars().all()
    
    # Calculate delay inline
    traced_events = []
    for ev in events:
        delay_ms = int((ev.received_at - ev.occurred_at).total_seconds() * 1000)
        trace_dict = {
            "id": ev.id,
            "event_id": ev.event_id,
            "event_type": ev.event_type,
            "sequence_number": ev.sequence_number,
            "status": ev.status.value,
            "occurred_at": ev.occurred_at,
            "received_at": ev.received_at,
            "delay_ms": delay_ms,
            "correlation_id": ev.correlation_id,
            "causation_id": ev.causation_id,
            "payload": ev.payload,
            "processed_at": ev.processed_at,
            "error_message": ev.error_message
        }
        traced_events.append(trace_dict)
    
    return {"items": traced_events}
