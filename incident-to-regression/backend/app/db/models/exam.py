import uuid
from typing import List, Optional

from sqlalchemy import String, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.db.models.enums import ExamSessionStatus

class Student(BaseModel):
    __tablename__ = "students"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    sessions: Mapped[List["ExamSession"]] = relationship("ExamSession", back_populates="student")

class Exam(BaseModel):
    __tablename__ = "exams"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PUBLISHED")

    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="exam", order_by="Question.question_number"
    )
    sessions: Mapped[List["ExamSession"]] = relationship("ExamSession", back_populates="exam")

class Question(BaseModel):
    __tablename__ = "questions"

    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), index=True)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), default="MULTIPLE_CHOICE")
    points: Mapped[int] = mapped_column(Integer, default=1)

    exam: Mapped["Exam"] = relationship("Exam", back_populates="questions")
    options: Mapped[List["AnswerOption"]] = relationship("AnswerOption", back_populates="question")

class AnswerOption(BaseModel):
    __tablename__ = "answer_options"

    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    option_key: Mapped[str] = mapped_column(String(10), nullable=False) # e.g. "A", "B"
    option_text: Mapped[str] = mapped_column(Text, nullable=False)

    question: Mapped["Question"] = relationship("Question", back_populates="options")
