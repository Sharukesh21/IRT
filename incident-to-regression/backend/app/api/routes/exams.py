from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.api.dependencies import get_db
from app.db.models.exam import Exam
from app.schemas.exam import ExamResponse, ExamListResponse
from app.schemas.common import PagedResponse

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.get("", response_model=PagedResponse[ExamListResponse])
async def list_exams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exam).order_by(Exam.created_at.desc()))
    exams = result.scalars().all()
    return {"items": exams, "total": len(exams), "page": 1, "size": len(exams)}

@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(exam_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Exam)
        .options(selectinload(Exam.questions).selectinload("options"))
        .where(Exam.id == exam_id)
    )
    exam = result.scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam
