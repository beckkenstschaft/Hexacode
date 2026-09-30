"""Mock engine implementations for development and testing."""

import asyncio
import random
import time
from typing import Any

import numpy as np

from app.engines.protocols import BaseEngine, EngineResult, VADSegment, VoiceActivityDetector, SpeechRecognizer, Summarizer


class MockVAD(BaseEngine, VoiceActivityDetector):
    """Mock Voice Activity Detector."""

    def __init__(self) -> None:
        super().__init__(provider="Mock", simulated=True)

    async def detect(self, audio: np.ndarray, sample_rate: int) -> EngineResult:
        """Simulate VAD detection."""
        await asyncio.sleep(0.01)  # Simulate processing time

        # Create fake segments based on audio length
        duration_samples = len(audio)
        segment_length = sample_rate * 2  # 2 second segments
        segments = []

        for start in range(0, duration_samples, segment_length):
            end = min(start + segment_length, duration_samples)
            if random.random() > 0.3:  # 70% chance of speech
                segments.append(VADSegment(
                    start_sample=start,
                    end_sample=end,
                    confidence=random.uniform(0.7, 0.99),
                ))

        return EngineResult(
            data=segments,
            provider=self.provider,
            latency_ms=random.randint(5, 15),
            simulated=True,
        )


class MockASR(BaseEngine, SpeechRecognizer):
    """Mock Speech Recognizer."""

    def __init__(self) -> None:
        super().__init__(provider="Mock", simulated=True)
        self._sample_texts = [
            "Hello everyone, welcome to today's meeting.",
            "Let's start with the agenda for this session.",
            "The first item is the project update from the team.",
            "We have made significant progress on the frontend.",
            "The backend API is now fully functional.",
            "Next, let's discuss the timeline for the next sprint.",
            "Any questions or concerns before we continue?",
            "Thank you all for your hard work.",
        ]

    async def transcribe(self, audio: np.ndarray, sample_rate: int, language: str | None = None) -> EngineResult:
        """Simulate transcription."""
        # Simulate processing time proportional to audio length
        duration = len(audio) / sample_rate
        await asyncio.sleep(min(duration * 0.1, 0.5))

        # Return a sample text
        text = random.choice(self._sample_texts)
        if language and language != "en":
            text = f"[{language}] {text}"

        return EngineResult(
            data=text,
            provider=self.provider,
            latency_ms=random.randint(50, 200),
            simulated=True,
        )


class MockSummarizer(BaseEngine, Summarizer):
    """Mock Summarizer."""

    def __init__(self) -> None:
        super().__init__(provider="Mock", simulated=True)

    async def summarize(
        self,
        text: str,
        language: str | None = None,
        max_key_points: int = 5,
        max_action_items: int = 5,
    ) -> EngineResult:
        """Simulate summarization."""
        await asyncio.sleep(0.1)

        # Generate mock summary based on input
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        key_points = sentences[:max_key_points] if sentences else ["No content to summarize"]

        action_items = [
            "Review project timeline",
            "Update documentation",
            "Schedule follow-up meeting",
            "Assign tasks to team members",
        ][:max_action_items]

        return EngineResult(
            data={
                "key_points": key_points,
                "action_items": action_items,
            },
            provider=self.provider,
            latency_ms=random.randint(100, 300),
            simulated=True,
        )