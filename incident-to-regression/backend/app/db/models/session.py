import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.db.models.enums import ExamSessionStatus, AnswerStatus, SubmissionStatus

class ExamSession(BaseModel):
    __tablename__ = "exam_sessions"

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), index=True)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id"), index=True)
    status: Mapped[ExamSessionStatus] = mapped_column(SQLEnum(ExamSessionStatus, name="exam_session_status_enum"), default=ExamSessionStatus.NOT_STARTED, nullable=False)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False) # Optimistic concurrency

    student = relationship("Student", back_populates="sessions")
    exam = relationship("Exam", back_populates="sessions")
    answers: Mapped[List["StudentAnswer"]] = relationship("StudentAnswer", back_populates="session")
    submissions: Mapped[List["Submission"]] = relationship("Submission", back_populates="session")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="session")

class StudentAnswer(BaseModel):
    __tablename__ = "student_answers"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_sessions.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"), index=True)
    selected_option: Mapped[Optional[str]] = mapped_column(String(50))
    answer_status: Mapped[AnswerStatus] = mapped_column(SQLEnum(AnswerStatus, name="answer_status_enum"), default=AnswerStatus.UNANSWERED, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    session = relationship("ExamSession", back_populates="answers")
    question = relationship("Question")

    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uix_session_question"),
    )

class Submission(BaseModel):
    __tablename__ = "submissions"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_sessions.id", ondelete="CASCADE"), index=True)
    submission_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True) # Important for idempotency
    status: Mapped[SubmissionStatus] = mapped_column(SQLEnum(SubmissionStatus, name="submission_status_enum"), default=SubmissionStatus.PENDING, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    session = relationship("ExamSession", back_populates="submissions")
