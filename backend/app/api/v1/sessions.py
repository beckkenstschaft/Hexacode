"""Session endpoints."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, verify_content_length
from app.core.logging import get_logger
from app.schemas.api import (
    SessionCreate,
    SessionDetail,
    SessionResponse,
    SessionUpdate,
    TranscriptSegmentCreate,
    SummaryCreate,
)
from app.services.session import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])
logger = get_logger(__name__)


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    data: SessionCreate,
    session: AsyncSession = Depends(get_db),
) -> SessionResponse:
    """Create a new session."""
    service = SessionService(session)
    return await service.create_session(data)


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, pattern=r"^(active|completed|archived)$"),
    session: AsyncSession = Depends(get_db),
) -> list[SessionResponse]:
    """List sessions with pagination."""
    service = SessionService(session)
    return await service.list_sessions(limit, offset, status)


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(
    session_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> SessionDetail:
    """Get session with full details."""
    service = SessionService(session)
    result = await service.get_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: uuid.UUID,
    data: SessionUpdate,
    session: AsyncSession = Depends(get_db),
) -> SessionResponse:
    """Update a session."""
    service = SessionService(session)
    result = await service.get_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")

    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] == "completed":
        result = await service.end_session(session_id)
    else:
        # For title updates, we'd need to add an update method to the service
        # For now, just return the session
        pass

    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a session."""
    service = SessionService(session)
    deleted = await service.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")


@router.post("/{session_id}/summary", response_model=SummaryCreate)
async def generate_summary(
    session_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> SummaryCreate:
    """Generate a summary for a session."""
    service = SessionService(session)
    try:
        return await service.generate_summary(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# WebSocket endpoint for live captions
@router.websocket("/{session_id}/stream")
async def stream_captions(
    websocket: WebSocket,
    session_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    """WebSocket endpoint for live caption streaming."""
    await websocket.accept()
    logger.info("ws_connected", session_id=str(session_id))

    service = SessionService(session)

    # Verify session exists
    session_obj = await service.get_session(session_id)
    if not session_obj:
        await websocket.close(code=4004, reason="Session not found")
        return

    try:
        while True:
            # Receive audio chunk
            data = await websocket.receive_bytes()

            # Parse message (expecting raw audio for simplicity)
            # In production, you might want a more structured protocol
            import numpy as np
            audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

            if len(audio_data) == 0:
                continue

            # Process through pipeline
            results = await service.process_audio_chunk(
                session_id=session_id,
                audio_data=data,
                sample_rate=16000,  # Assume 16kHz
                language=session_obj.language,
            )

            # Send caption for each ASR result
            for result in results:
                if hasattr(result, 'data') and isinstance(result.data, str):
                    await websocket.send_json({
                        "type": "caption",
                        "payload": {
                            "text": result.data,
                            "provider": result.provider,
                            "simulated": result.simulated,
                            "latency_ms": result.latency_ms,
                        }
                    })

    except WebSocketDisconnect:
        logger.info("ws_disconnected", session_id=str(session_id))
    except Exception as e:
        logger.error("ws_error", session_id=str(session_id), error=str(e))
        await websocket.send_json({
            "type": "error",
            "payload": {"message": str(e)}
        })
        await websocket.close(code=4000)