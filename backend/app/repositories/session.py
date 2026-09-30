"""Session repository."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Session, TranscriptSegment, Summary, StageLog
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    """Repository for session operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Session, session)

    async def create_session(
        self,
        title: str,
        language: str = "en",
    ) -> Session:
        """Create a new session."""
        return await self.create(
            title=title,
            language=language,
            status="active",
        )

    async def get_session(self, session_id: uuid.UUID) -> Optional[Session]:
        """Get session by ID."""
        return await self.get(str(session_id))

    async def list_sessions(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> list[Session]:
        """List sessions with optional status filter."""
        query = select(Session).order_by(Session.started_at.desc())
        if status:
            query = query.where(Session.status == status)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def end_session(self, session_id: uuid.UUID) -> Optional[Session]:
        """Mark session as ended."""
        return await self.update(str(session_id), status="completed", ended_at=func.now())

    async def get_session_with_details(self, session_id: uuid.UUID) -> Optional[Session]:
        """Get session with all related data."""
        from sqlalchemy.orm import selectinload
        query = (
            select(Session)
            .options(
                selectinload(Session.transcript_segments),
                selectinload(Session.summaries),
                selectinload(Session.stage_logs),
            )
            .where(Session.id == session_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class TranscriptSegmentRepository(BaseRepository[TranscriptSegment]):
    """Repository for transcript segment operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(TranscriptSegment, session)

    async def add_segment(
        self,
        session_id: uuid.UUID,
        start_ms: int,
        end_ms: int,
        text: str,
        language: str,
        provider: str,
        simulated: bool,
    ) -> TranscriptSegment:
        """Add a transcript segment."""
        return await self.create(
            session_id=session_id,
            start_ms=start_ms,
            end_ms=end_ms,
            text=text,
            language=language,
            provider=provider,
            simulated=simulated,
        )

    async def get_segments(
        self,
        session_id: uuid.UUID,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[TranscriptSegment]:
        """Get segments for a session."""
        query = (
            select(TranscriptSegment)
            .where(TranscriptSegment.session_id == session_id)
            .order_by(TranscriptSegment.start_ms)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class SummaryRepository(BaseRepository[Summary]):
    """Repository for summary operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Summary, session)

    async def create_summary(
        self,
        session_id: uuid.UUID,
        key_points: list[str],
        action_items: list[str],
        provider: str,
        simulated: bool,
    ) -> Summary:
        """Create a summary."""
        return await self.create(
            session_id=session_id,
            key_points=key_points,
            action_items=action_items,
            provider=provider,
            simulated=simulated,
        )

    async def get_latest_summary(self, session_id: uuid.UUID) -> Optional[Summary]:
        """Get the latest summary for a session."""
        query = (
            select(Summary)
            .where(Summary.session_id == session_id)
            .order_by(Summary.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class StageLogRepository(BaseRepository[StageLog]):
    """Repository for stage log operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(StageLog, session)

    async def log_stage(
        self,
        stage: str,
        provider: str,
        latency_ms: int,
        session_id: Optional[uuid.UUID] = None,
    ) -> StageLog:
        """Log a processing stage."""
        return await self.create(
            session_id=session_id,
            stage=stage,
            provider=provider,
            latency_ms=latency_ms,
        )