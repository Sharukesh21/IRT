from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.db.models.enums import ExamSessionStatus

class SessionStartRequest(BaseModel):
    student_id: UUID
    exam_id: UUID

class AnswerSubmitRequest(BaseModel):
    selected_option: str
    # In a full app this might have timestamp, etc.

class SessionResponse(BaseModel):
    id: UUID
    student_id: UUID
    exam_id: UUID
    status: ExamSessionStatus
    started_at: Optional[datetime]
    submitted_at: Optional[datetime]
    last_activity_at: Optional[datetime]
    version: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EventTraceResponse(BaseModel):
    id: UUID
    event_id: str
    event_type: str
    sequence_number: int
    status: str
    occurred_at: datetime
    received_at: datetime
    delay_ms: int
    correlation_id: str
    causation_id: Optional[str]
    payload: dict
    processed_at: Optional[datetime]
    error_message: Optional[str]

    model_config = ConfigDict(from_attributes=True)
