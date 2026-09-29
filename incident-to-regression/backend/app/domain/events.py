from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

# Event Types
EventType = Literal[
    "EXAM_STARTED",
    "QUESTION_VIEWED",
    "ANSWER_SELECTED",
    "ANSWER_SAVED",
    "ANSWER_UPDATED",
    "SUBMIT_REQUESTED",
    "SUBMISSION_PROCESSING",
    "SUBMISSION_CONFIRMED",
    "SUBMISSION_FAILED",
    "SESSION_RECOVERED",
    "SESSION_TIMEOUT"
]

class BaseDomainEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_id: str
    event_type: EventType
    session_id: str
    student_id: Optional[str] = None
    exam_id: Optional[str] = None
    sequence_number: int
    correlation_id: str
    causation_id: Optional[str] = None
    occurred_at: datetime
    received_at: Optional[datetime] = None
    payload: dict[str, Any] = Field(default_factory=dict)

class ExamStartedEvent(BaseDomainEvent):
    event_type: Literal["EXAM_STARTED"] = "EXAM_STARTED"

class QuestionViewedEvent(BaseDomainEvent):
    event_type: Literal["QUESTION_VIEWED"] = "QUESTION_VIEWED"

class AnswerSelectedEvent(BaseDomainEvent):
    event_type: Literal["ANSWER_SELECTED"] = "ANSWER_SELECTED"

class AnswerSavedEvent(BaseDomainEvent):
    event_type: Literal["ANSWER_SAVED"] = "ANSWER_SAVED"

class SubmitRequestedEvent(BaseDomainEvent):
    event_type: Literal["SUBMIT_REQUESTED"] = "SUBMIT_REQUESTED"

class SubmissionConfirmedEvent(BaseDomainEvent):
    event_type: Literal["SUBMISSION_CONFIRMED"] = "SUBMISSION_CONFIRMED"

class SubmissionFailedEvent(BaseDomainEvent):
    event_type: Literal["SUBMISSION_FAILED"] = "SUBMISSION_FAILED"
