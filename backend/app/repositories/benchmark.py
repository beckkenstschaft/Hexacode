"""Benchmark repository."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import BenchmarkRun, BenchmarkResult
from app.repositories.base import BaseRepository


class BenchmarkRunRepository(BaseRepository[BenchmarkRun]):
    """Repository for benchmark run operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(BenchmarkRun, session)

    async def create_run(
        self,
        audio_name: str,
        audio_duration_s: float,
        device_info: dict,
    ) -> BenchmarkRun:
        """Create a new benchmark run."""
        return await self.create(
            audio_name=audio_name,
            audio_duration_s=audio_duration_s,
            device_info=device_info,
        )

    async def get_run(self, run_id: uuid.UUID) -> Optional[BenchmarkRun]:
        """Get benchmark run with results."""
        query = (
            select(BenchmarkRun)
            .options(selectinload(BenchmarkRun.results))
            .where(BenchmarkRun.id == run_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_runs(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[BenchmarkRun]:
        """List benchmark runs."""
        query = (
            select(BenchmarkRun)
            .order_by(BenchmarkRun.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def finish_run(self, run_id: uuid.UUID) -> Optional[BenchmarkRun]:
        """Mark benchmark run as finished."""
        return await self.update(str(run_id), finished_at=datetime.now())


class BenchmarkResultRepository(BaseRepository[BenchmarkResult]):
    """Repository for benchmark result operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(BenchmarkResult, session)

    async def add_result(
        self,
        run_id: uuid.UUID,
        provider: str,
        stage: str,
        latency_ms: int,
        real_time_factor: float,
        cpu_percent: float,
        npu_percent: Optional[float] = None,
        battery_delta_percent: Optional[float] = None,
        simulated: bool = False,
    ) -> BenchmarkResult:
        """Add a benchmark result."""
        return await self.create(
            run_id=run_id,
            provider=provider,
            stage=stage,
            latency_ms=latency_ms,
            real_time_factor=real_time_factor,
            cpu_percent=cpu_percent,
            npu_percent=npu_percent,
            battery_delta_percent=battery_delta_percent,
            simulated=simulated,
        )

    async def get_results(self, run_id: uuid.UUID) -> list[BenchmarkResult]:
        """Get all results for a run."""
        query = (
            select(BenchmarkResult)
            .where(BenchmarkResult.run_id == run_id)
            .order_by(BenchmarkResult.stage, BenchmarkResult.provider)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())