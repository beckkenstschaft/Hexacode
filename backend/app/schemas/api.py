"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SessionBase(BaseModel):
    """Base session schema."""

    title: str = Field(..., min_length=1, max_length=255)
    language: str = Field(default="en", pattern=r"^[a-z]{2}$")


class SessionCreate(SessionBase):
    """Schema for creating a session."""

    pass


class SessionUpdate(BaseModel):
    """Schema for updating a session."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern=r"^(active|completed|archived)$")


class SessionResponse(SessionBase):
    """Schema for session response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    started_at: datetime
    ended_at: Optional[datetime]
    status: str


class SessionDetail(SessionResponse):
    """Detailed session with transcript and summary."""

    transcript_segments: list["TranscriptSegmentResponse"] = []
    summaries: list["SummaryResponse"] = []


class TranscriptSegmentBase(BaseModel):
    """Base transcript segment schema."""

    start_ms: int = Field(..., ge=0)
    end_ms: int = Field(..., ge=0)
    text: str
    language: str = Field(default="en", pattern=r"^[a-z]{2}$")
    provider: str
    simulated: bool = False


class TranscriptSegmentCreate(TranscriptSegmentBase):
    """Schema for creating a transcript segment."""

    pass


class TranscriptSegmentResponse(TranscriptSegmentBase):
    """Schema for transcript segment response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID


class SummaryBase(BaseModel):
    """Base summary schema."""

    key_points: list[str] = []
    action_items: list[str] = []
    provider: str
    simulated: bool = False


class SummaryCreate(SummaryBase):
    """Schema for creating a summary."""

    pass


class SummaryResponse(SummaryBase):
    """Schema for summary response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    created_at: datetime


class SystemCapabilitiesResponse(BaseModel):
    """System capabilities response."""

    model_config = ConfigDict(from_attributes=True)

    product_name: str
    providers: dict
    models_loaded: dict
    simulated_mode: bool


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime


class ErrorDetail(BaseModel):
    """Error detail schema."""

    code: str
    message: str
    details: dict = {}


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: ErrorDetail


# Benchmark schemas
class BenchmarkRunCreate(BaseModel):
    """Schema for creating a benchmark run."""

    audio_name: str
    audio_duration_s: float
    device_info: dict = {}


class BenchmarkRunResponse(BaseModel):
    """Schema for benchmark run response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    audio_name: str
    audio_duration_s: float
    started_at: datetime
    finished_at: Optional[datetime]
    device_info: dict


class BenchmarkResultResponse(BaseModel):
    """Schema for benchmark result response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: UUID
    provider: str
    stage: str
    latency_ms: int
    real_time_factor: float
    cpu_percent: float
    npu_percent: Optional[float]
    battery_delta_percent: Optional[float]
    simulated: bool


class BenchmarkRunDetail(BenchmarkRunResponse):
    """Detailed benchmark run with results."""

    results: list[BenchmarkResultResponse] = []


# WebSocket message schemas
class WSMessageType(str):
    """WebSocket message types."""

    AUDIO = "audio"
    CAPTION = "caption"
    ERROR = "error"
    END = "end"


class WSMessage(BaseModel):
    """Base WebSocket message."""

    type: str
    payload: dict


class WSAudioMessage(WSMessage):
    """WebSocket audio message."""

    type: str = "audio"
    payload: dict = Field(default_factory=dict)


class WSCaptionMessage(WSMessage):
    """WebSocket caption message."""

    type: str = "caption"
    payload: dict = Field(default_factory=dict)


class WSEndMessage(WSMessage):
    """WebSocket end message."""

    type: str = "end"
    payload: dict = Field(default_factory=dict)


class WSErrorMessage(WSMessage):
    """WebSocket error message."""

    type: str = "error"
    payload: dict = Field(default_factory=dict)