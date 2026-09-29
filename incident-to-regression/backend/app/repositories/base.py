"""Generic async repository base class.

All domain repositories should inherit from BaseRepository[ModelT].
This provides standard CRUD operations and ensures consistent data access patterns
across all domain areas (Examination, Incident, Regression, Evaluation).
"""

from typing import Generic, Optional, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic CRUD repository for SQLAlchemy async sessions.

    Usage:
        class IncidentRepository(BaseRepository[Incident]):
            def __init__(self, session: AsyncSession) -> None:
                super().__init__(Incident, session)
    """

    def __init__(self, model: Type[ModelT], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def get_by_id(self, id: UUID) -> Optional[ModelT]:
        """Fetch a single record by primary key."""
        return await self._session.get(self._model, id)

    async def list(self, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        """Fetch a paginated list of records."""
        result = await self._session.execute(
            select(self._model).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def create(self, instance: ModelT) -> ModelT:
        """Persist a new record."""
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def update(self, instance: ModelT) -> ModelT:
        """Merge and persist changes to an existing record."""
        merged = await self._session.merge(instance)
        await self._session.flush()
        return merged

    async def delete(self, instance: ModelT) -> None:
        """Delete a record from the database."""
        await self._session.delete(instance)
        await self._session.flush()
