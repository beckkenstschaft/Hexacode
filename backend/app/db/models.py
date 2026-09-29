"""SQLAlchemy models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.db.models import Session as SessionModel


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Session(Base):
    """Session model for live caption sessions."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # Relationships
    transcript_segments: Mapped[list["TranscriptSegment"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", lazy="selectin"
    )
    summaries: Mapped[list["Summary"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", lazy="selectin"
    )
    stage_logs: Mapped[list["StageLog"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_sessions_started_at", "started_at"),
        Index("ix_sessions_status", "status"),
    )


class TranscriptSegment(Base):
    """Transcript segment with timestamps and language."""

    __tablename__ = "transcript_segments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    start_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    end_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    simulated: Mapped[bool] = mapped_column(nullable=False, default=False)

    # Relationship
    session: Mapped["Session"] = relationship(back_populates="transcript_segments")

    __table_args__ = (
        Index("ix_transcript_segments_session_id", "session_id"),
        Index("ix_transcript_segments_start_ms", "start_ms"),
    )


class Summary(Base):
    """Generated summary for a session."""

    __tablename__ = "summaries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    key_points: Mapped[list[str]] = mapped_column(SQLiteJSON, nullable=False, default=list)
    action_items: Mapped[list[str]] = mapped_column(SQLiteJSON, nullable=False, default=list)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    simulated: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relationship
    session: Mapped["Session"] = relationship(back_populates="summaries")

    __table_args__ = (
        Index("ix_summaries_session_id", "session_id"),
        Index("ix_summaries_created_at", "created_at"),
    )


class StageLog(Base):
    """Processing stage log for latency tracking."""

    __tablename__ = "stage_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relationship
    session: Mapped["Session | None"] = relationship(back_populates="stage_logs")

    __table_args__ = (
        Index("ix_stage_logs_session_id", "session_id"),
        Index("ix_stage_logs_stage", "stage"),
        Index("ix_stage_logs_created_at", "created_at"),
    )


class BenchmarkRun(Base):
    """Benchmark run metadata."""

    __tablename__ = "benchmark_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    audio_name: Mapped[str] = mapped_column(String(255), nullable=False)
    audio_duration_s: Mapped[float] = mapped_column(Float, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    device_info: Mapped[dict] = mapped_column(SQLiteJSON, nullable=False, default=dict)

    # Relationship
    results: Mapped[list["BenchmarkResult"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_benchmark_runs_started_at", "started_at"),
    )


class BenchmarkResult(Base):
    """Benchmark result for a specific provider and stage."""

    __tablename__ = "benchmark_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("benchmark_runs.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    real_time_factor: Mapped[float] = mapped_column(Float, nullable=False)
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    npu_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    battery_delta_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    simulated: Mapped[bool] = mapped_column(nullable=False, default=False)

    # Relationship
    run: Mapped["BenchmarkRun"] = relationship(back_populates="results")

    __table_args__ = (
        Index("ix_benchmark_results_run_id", "run_id"),
        Index("ix_benchmark_results_provider", "provider"),
        Index("ix_benchmark_results_stage", "stage"),
    )