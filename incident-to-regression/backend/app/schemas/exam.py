from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

# Exam Schemas
class AnswerOptionBase(BaseModel):
    option_key: str
    option_text: str

class AnswerOptionResponse(AnswerOptionBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class QuestionBase(BaseModel):
    question_number: int
    question_text: str
    question_type: str
    points: int

class QuestionResponse(QuestionBase):
    id: UUID
    options: List[AnswerOptionResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ExamBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_seconds: int

class ExamResponse(ExamBase):
    id: UUID
    status: str
    questions: List[QuestionResponse] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExamListResponse(ExamBase):
    id: UUID
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
