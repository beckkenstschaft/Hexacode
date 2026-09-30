"""Session service."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import Session as SessionModel
from app.repositories.session import SessionRepository, StageLogRepository, SummaryRepository, TranscriptSegmentRepository
from app.schemas.api import SessionCreate, SessionDetail, SessionResponse, TranscriptSegmentCreate, SummaryCreate
from app.engines.factory import get_engine_factory
from app.engines.protocols import EngineResult, VADSegment

logger = get_logger(__name__)


class SessionService:
    """Service for session operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.session_repo = SessionRepository(session)
        self.segment_repo = TranscriptSegmentRepository(session)
        self.summary_repo = SummaryRepository(session)
        self.stage_log_repo = StageLogRepository(session)
        self.engine_factory = get_engine_factory()

    async def create_session(self, data: SessionCreate) -> SessionResponse:
        """Create a new session."""
        session_obj = await self.session_repo.create_session(data.title, data.language)
        logger.info("session_created", session_id=str(session_obj.id), title=data.title)
        return SessionResponse.model_validate(session_obj)

    async def get_session(self, session_id: uuid.UUID) -> Optional[SessionDetail]:
        """Get session with all details."""
        session_obj = await self.session_repo.get_session_with_details(session_id)
        if not session_obj:
            return None
        return SessionDetail.model_validate(session_obj)

    async def list_sessions(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> list[SessionResponse]:
        """List sessions."""
        sessions = await self.session_repo.list_sessions(limit, offset, status)
        return [SessionResponse.model_validate(s) for s in sessions]

    async def delete_session(self, session_id: uuid.UUID) -> bool:
        """Delete a session."""
        result = await self.session_repo.delete(str(session_id))
        if result:
            logger.info("session_deleted", session_id=str(session_id))
        return result

    async def end_session(self, session_id: uuid.UUID) -> Optional[SessionResponse]:
        """End a session."""
        session_obj = await self.session_repo.end_session(session_id)
        if session_obj:
            logger.info("session_ended", session_id=str(session_id))
            return SessionResponse.model_validate(session_obj)
        return None

    async def add_transcript_segment(
        self,
        session_id: uuid.UUID,
        data: TranscriptSegmentCreate,
    ) -> TranscriptSegmentCreate:
        """Add a transcript segment."""
        segment = await self.segment_repo.add_segment(
            session_id=session_id,
            start_ms=data.start_ms,
            end_ms=data.end_ms,
            text=data.text,
            language=data.language,
            provider=data.provider,
            simulated=data.simulated,
        )
        logger.debug("segment_added", session_id=str(session_id), segment_id=str(segment.id))
        return TranscriptSegmentCreate.model_validate(segment)

    async def generate_summary(self, session_id: uuid.UUID) -> SummaryCreate:
        """Generate a summary for a session."""
        # Get all transcript segments
        segments = await self.segment_repo.get_segments(session_id)
        if not segments:
            raise ValueError("No transcript segments to summarize")

        # Combine all text
        full_text = " ".join(seg.text for seg in segments)

        # Get summarizer engine
        summarizer = self.engine_factory.get_summarizer()

        # Generate summary
        start_time = datetime.now()
        result: EngineResult = await summarizer.summarize(
            text=full_text,
            language=segments[0].language if segments else "en",
        )
        latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Log stage
        await self.stage_log_repo.log_stage(
            stage="summarization",
            provider=result.provider,
            latency_ms=latency_ms,
            session_id=session_id,
        )

        # Save summary
        summary = await self.summary_repo.create_summary(
            session_id=session_id,
            key_points=result.data["key_points"],
            action_items=result.data["action_items"],
            provider=result.provider,
            simulated=result.simulated,
        )

        logger.info(
            "summary_generated",
            session_id=str(session_id),
            provider=result.provider,
            simulated=result.simulated,
        )

        return SummaryCreate.model_validate(summary)

    async def process_audio_chunk(
        self,
        session_id: uuid.UUID,
        audio_data: bytes,
        sample_rate: int,
        language: str,
    ) -> list[EngineResult]:
        """Process audio chunk through VAD and ASR pipeline."""
        import numpy as np

        # Convert bytes to numpy array
        audio = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        results = []

        # VAD
        vad = self.engine_factory.get_vad()
        vad_result: EngineResult = await vad.detect(audio, sample_rate)
        await self.stage_log_repo.log_stage(
            stage="vad",
            provider=vad_result.provider,
            latency_ms=vad_result.latency_ms,
            session_id=session_id,
        )
        results.append(vad_result)

        # Process each speech segment
        segments: list[VADSegment] = vad_result.data
        asr = self.engine_factory.get_asr()

        for segment in segments:
            seg_audio = audio[segment.start_sample:segment.end_sample]
            if len(seg_audio) < sample_rate * 0.1:  # Skip very short segments
                continue

            asr_result: EngineResult = await asr.transcribe(seg_audio, sample_rate, language)
            await self.stage_log_repo.log_stage(
                stage="asr",
                provider=asr_result.provider,
                latency_ms=asr_result.latency_ms,
                session_id=session_id,
            )
            results.append(asr_result)

            # Save transcript segment
            await self.segment_repo.add_segment(
                session_id=session_id,
                start_ms=int(segment.start_sample / sample_rate * 1000),
                end_ms=int(segment.end_sample / sample_rate * 1000),
                text=asr_result.data,
                language=language,
                provider=asr_result.provider,
                simulated=asr_result.simulated,
            )

        return results