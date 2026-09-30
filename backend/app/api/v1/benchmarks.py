"""Benchmark endpoints."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_db
from app.core.logging import get_logger
from app.schemas.api import BenchmarkRunCreate, BenchmarkRunDetail, BenchmarkRunResponse
from app.services.benchmark import BenchmarkService

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])
logger = get_logger(__name__)


@router.post("", response_model=BenchmarkRunDetail, status_code=201)
async def run_benchmark(
    data: BenchmarkRunCreate,
    session=Depends(get_db),
) -> BenchmarkRunDetail:
    """Run a new benchmark."""
    service = BenchmarkService(session)
    return await service.run_benchmark(data)


@router.get("", response_model=list[BenchmarkRunResponse])
async def list_benchmarks(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session=Depends(get_db),
) -> list[BenchmarkRunResponse]:
    """List benchmark runs."""
    service = BenchmarkService(session)
    return await service.list_runs(limit, offset)


@router.get("/{run_id}", response_model=BenchmarkRunDetail)
async def get_benchmark(
    run_id: uuid.UUID,
    session=Depends(get_db),
) -> BenchmarkRunDetail:
    """Get benchmark run with results."""
    service = BenchmarkService(session)
    result = await service.get_run(run_id)
    if not result:
        raise HTTPException(status_code=404, detail="Benchmark run not found")
    return result