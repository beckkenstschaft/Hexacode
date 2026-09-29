"""Benchmark service."""

import time
import uuid
from datetime import datetime
from typing import Optional

import numpy as np
import psutil

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.models import BenchmarkRun, BenchmarkResult
from app.repositories.benchmark import BenchmarkRunRepository, BenchmarkResultRepository
from app.engines.factory import get_engine_factory
from app.engines.protocols import EngineResult, VADSegment
from app.schemas.api import BenchmarkRunCreate, BenchmarkRunDetail

logger = get_logger(__name__)


class BenchmarkService:
    """Service for benchmark operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.run_repo = BenchmarkRunRepository(session)
        self.result_repo = BenchmarkResultRepository(session)
        self.engine_factory = get_engine_factory()
        self.settings = get_settings()

    async def run_benchmark(self, data: BenchmarkRunCreate) -> BenchmarkRunDetail:
        """Run a full benchmark across all available providers."""
        # Load benchmark audio
        audio, sample_rate = await self._load_audio(data.audio_name)
        if audio is None:
            # Generate synthetic audio for testing
            audio = self._generate_synthetic_audio(data.audio_duration_s, sample_rate)

        # Create benchmark run
        device_info = self._get_device_info()
        run = await self.run_repo.create_run(
            audio_name=data.audio_name,
            audio_duration_s=data.audio_duration_s,
            device_info=device_info,
        )

        # Get all available providers
        from app.engines.provider_selector import get_provider_selector
        selector = get_provider_selector()
        providers = selector.get_all_providers()

        # If no real providers, use CPU
        if not providers:
            providers = ["CPUExecutionProvider"]

        stages = ["vad", "asr", "summarization"]

        for provider in providers:
            for stage in stages:
                await self._run_stage(
                    run_id=run.id,
                    provider=provider,
                    stage=stage,
                    audio=audio,
                    sample_rate=sample_rate,
                    audio_duration=data.audio_duration_s,
                )

        # Finish run
        await self.run_repo.finish_run(run.id)

        # Return detailed result
        return await self.get_run(run.id)

    async def _run_stage(
        self,
        run_id: uuid.UUID,
        provider: str,
        stage: str,
        audio: np.ndarray,
        sample_rate: int,
        audio_duration: float,
    ) -> None:
        """Run a single benchmark stage."""
        logger.info("benchmark_stage_start", run_id=str(run_id), provider=provider, stage=stage)

        # Measure CPU before
        cpu_before = psutil.cpu_percent(interval=0.1)
        battery_before = self._get_battery_level()

        start_time = time.perf_counter()

        try:
            if stage == "vad":
                engine = self.engine_factory.get_vad()
                result: EngineResult = await engine.detect(audio, sample_rate)
            elif stage == "asr":
                engine = self.engine_factory.get_asr()
                result: EngineResult = await engine.transcribe(audio, sample_rate)
            elif stage == "summarization":
                engine = self.engine_factory.get_summarizer()
                # Use a sample text for summarization benchmark
                sample_text = " ".join(["This is a test sentence for benchmarking."] * 100)
                result: EngineResult = await engine.summarize(sample_text)
            else:
                raise ValueError(f"Unknown stage: {stage}")

            latency_ms = int((time.perf_counter() - start_time) * 1000)
            real_time_factor = latency_ms / (audio_duration * 1000) if audio_duration > 0 else 0

            # Measure CPU after
            cpu_after = psutil.cpu_percent(interval=0.1)
            battery_after = self._get_battery_level()

            cpu_percent = (cpu_before + cpu_after) / 2
            battery_delta = None
            if battery_before is not None and battery_after is not None:
                battery_delta = battery_before - battery_after

            # NPU usage (placeholder - would need platform-specific implementation)
            npu_percent = None
            if "QNN" in provider:
                npu_percent = 50.0  # Placeholder

            simulated = result.simulated

        except Exception as e:
            logger.error("benchmark_stage_failed", run_id=str(run_id), provider=provider, stage=stage, error=str(e))
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            real_time_factor = 0
            cpu_percent = 0
            npu_percent = None
            battery_delta = None
            simulated = True
            result = EngineResult(data=str(e), provider=provider, latency_ms=latency_ms, simulated=True)

        # Save result
        await self.result_repo.add_result(
            run_id=run_id,
            provider=provider,
            stage=stage,
            latency_ms=latency_ms,
            real_time_factor=real_time_factor,
            cpu_percent=cpu_percent,
            npu_percent=npu_percent,
            battery_delta_percent=battery_delta,
            simulated=simulated,
        )

        logger.info(
            "benchmark_stage_complete",
            run_id=str(run_id),
            provider=provider,
            stage=stage,
            latency_ms=latency_ms,
            rtf=real_time_factor,
            simulated=simulated,
        )

    async def _load_audio(self, audio_name: str) -> tuple[Optional[np.ndarray], int]:
        """Load audio file."""
        try:
            import soundfile as sf
            path = self.settings.DATA_DIR / audio_name
            if path.exists():
                audio, sample_rate = sf.read(path)
                if len(audio.shape) > 1:
                    audio = audio.mean(axis=1)  # Convert to mono
                return audio.astype(np.float32), sample_rate
        except ImportError:
            logger.warning("soundfile_not_available")
        except Exception as e:
            logger.warning("audio_load_failed", error=str(e))
        return None, 16000

    def _generate_synthetic_audio(self, duration_s: float, sample_rate: int) -> np.ndarray:
        """Generate synthetic audio for testing."""
        t = np.linspace(0, duration_s, int(sample_rate * duration_s))
        # Generate speech-like signal (multiple tones)
        audio = (
            0.3 * np.sin(2 * np.pi * 200 * t) +
            0.2 * np.sin(2 * np.pi * 400 * t) +
            0.1 * np.sin(2 * np.pi * 800 * t)
        )
        # Add some noise
        audio += 0.01 * np.random.randn(len(audio))
        return audio.astype(np.float32)

    def _get_device_info(self) -> dict:
        """Get device information."""
        import platform
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        }

    def _get_battery_level(self) -> Optional[float]:
        """Get battery level percentage."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return battery.percent
        except Exception:
            pass
        return None

    async def get_run(self, run_id: uuid.UUID) -> Optional[BenchmarkRunDetail]:
        """Get benchmark run with results."""
        run = await self.run_repo.get_run(run_id)
        if not run:
            return None
        return BenchmarkRunDetail.model_validate(run)

    async def list_runs(self, limit: int = 50, offset: int = 0) -> list[BenchmarkRunDetail]:
        """List benchmark runs."""
        runs = await self.run_repo.list_runs(limit, offset)
        return [BenchmarkRunDetail.model_validate(r) for r in runs]