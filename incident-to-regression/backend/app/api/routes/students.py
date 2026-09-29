from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, ConfigDict
from uuid import UUID

from app.api.dependencies import get_db
from app.db.models.exam import Student
from app.schemas.common import PagedResponse

router = APIRouter(prefix="/students", tags=["Students"])

class StudentResponse(BaseModel):
    id: UUID
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=PagedResponse[StudentResponse])
async def list_students(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student))
    students = result.scalars().all()
    return {"items": students, "total": len(students), "page": 1, "size": len(students)}
