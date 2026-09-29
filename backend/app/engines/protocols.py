"""Engine protocol definitions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Protocol

import numpy as np


@dataclass(frozen=True)
class EngineResult:
    """Result from an engine execution."""

    data: any
    provider: str
    latency_ms: int
    simulated: bool = False


@dataclass(frozen=True)
class VADSegment:
    """Voice activity segment."""

    start_sample: int
    end_sample: int
    confidence: float


class VoiceActivityDetector(Protocol):
    """Protocol for voice activity detection."""

    @property
    def provider(self) -> str:
        """Return the execution provider name."""
        ...

    @property
    def simulated(self) -> bool:
        """Return whether this is a simulated implementation."""
        ...

    async def detect(self, audio: np.ndarray, sample_rate: int) -> EngineResult:
        """Detect voice activity in audio."""
        ...


class SpeechRecognizer(Protocol):
    """Protocol for speech recognition."""

    @property
    def provider(self) -> str:
        """Return the execution provider name."""
        ...

    @property
    def simulated(self) -> bool:
        """Return whether this is a simulated implementation."""
        ...

    async def transcribe(self, audio: np.ndarray, sample_rate: int, language: str | None = None) -> EngineResult:
        """Transcribe audio to text."""
        ...


class Summarizer(Protocol):
    """Protocol for text summarization."""

    @property
    def provider(self) -> str:
        """Return the execution provider name."""
        ...

    @property
    def simulated(self) -> bool:
        """Return whether this is a simulated implementation."""
        ...

    async def summarize(
        self,
        text: str,
        language: str | None = None,
        max_key_points: int = 5,
        max_action_items: int = 5,
    ) -> EngineResult:
        """Generate summary from text."""
        ...


class BaseEngine(ABC):
    """Base class for engine implementations."""

    def __init__(self, provider: str, simulated: bool = False) -> None:
        self._provider = provider
        self._simulated = simulated

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def simulated(self) -> bool:
        return self._simulated