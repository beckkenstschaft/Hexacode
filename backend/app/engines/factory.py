"""Engine factory for creating engine instances."""

from app.core.config import get_settings
from app.core.logging import get_logger
from app.engines.mock_engines import MockASR, MockSummarizer, MockVAD
from app.engines.onnx_engines import ExtractiveSummarizer, SileroVAD, WhisperASR
from app.engines.protocols import SpeechRecognizer, Summarizer, VoiceActivityDetector

logger = get_logger(__name__)


class EngineFactory:
    """Factory for creating engine instances based on configuration."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._vad: VoiceActivityDetector | None = None
        self._asr: SpeechRecognizer | None = None
        self._summarizer: Summarizer | None = None

    def get_vad(self) -> VoiceActivityDetector:
        """Get VAD engine instance."""
        if self._vad is None:
            if self._settings.USE_MOCK_ENGINES:
                logger.info("creating_mock_vad")
                self._vad = MockVAD()
            else:
                logger.info("creating_silero_vad")
                self._vad = SileroVAD()
        return self._vad

    def get_asr(self) -> SpeechRecognizer:
        """Get ASR engine instance."""
        if self._asr is None:
            if self._settings.USE_MOCK_ENGINES:
                logger.info("creating_mock_asr")
                self._asr = MockASR()
            else:
                logger.info("creating_whisper_asr")
                self._asr = WhisperASR()
        return self._asr

    def get_summarizer(self) -> Summarizer:
        """Get summarizer engine instance."""
        if self._summarizer is None:
            if self._settings.USE_MOCK_ENGINES or not self._settings.ENABLE_GENAI_SUMMARIZER:
                logger.info("creating_extractive_summarizer")
                self._summarizer = ExtractiveSummarizer()
            else:
                # TODO: Implement GenAI summarizer when ONNX Runtime GenAI is available
                logger.info("creating_extractive_summarizer (GenAI not implemented)")
                self._summarizer = ExtractiveSummarizer()
        return self._summarizer

    def reset(self) -> None:
        """Reset all engine instances (useful for testing)."""
        self._vad = None
        self._asr = None
        self._summarizer = None


# Global factory instance
_factory: EngineFactory | None = None


def get_engine_factory() -> EngineFactory:
    """Get global engine factory instance."""
    global _factory
    if _factory is None:
        _factory = EngineFactory()
    return _factory