"""ONNX Runtime engine implementations."""

import asyncio
import time
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort

from app.core.config import get_settings
from app.core.logging import get_logger
from app.engines.protocols import BaseEngine, EngineResult, VADSegment, VoiceActivityDetector, SpeechRecognizer, Summarizer
from app.engines.provider_selector import get_provider_selector

logger = get_logger(__name__)


class SileroVAD(BaseEngine, VoiceActivityDetector):
    """Silero VAD using ONNX Runtime."""

    def __init__(self, model_path: str | None = None) -> None:
        settings = get_settings()
        model_path = model_path or settings.VAD_MODEL_PATH
        self._model_path = Path(model_path)
        self._session: ort.InferenceSession | None = None
        self._provider = "CPUExecutionProvider"
        self._simulated = not self._model_path.exists()
        self._sample_rate = 16000
        self._window_size = 512

    def _load_model(self) -> None:
        """Load the ONNX model."""
        if self._session is not None:
            return

        if self._simulated:
            logger.warning("vad_model_not_found", path=str(self._model_path))
            return

        selector = get_provider_selector()
        provider = selector.get_provider("vad")

        try:
            self._session = ort.InferenceSession(
                str(self._model_path),
                providers=[provider],
            )
            self._provider = self._session.get_providers()[0]
            logger.info("vad_model_loaded", provider=self._provider, path=str(self._model_path))
        except Exception as e:
            logger.error("vad_model_load_failed", error=str(e), provider=provider)
            self._simulated = True
            raise

    async def detect(self, audio: np.ndarray, sample_rate: int) -> EngineResult:
        """Detect voice activity using Silero VAD."""
        start_time = time.perf_counter()

        if self._simulated or self._session is None:
            # Fallback to simple energy-based VAD
            return await self._fallback_vad(audio, sample_rate, start_time)

        # Resample if needed
        if sample_rate != self._sample_rate:
            audio = self._resample(audio, sample_rate, self._sample_rate)

        # Process in windows
        segments = []
        for i in range(0, len(audio), self._window_size):
            window = audio[i:i + self._window_size]
            if len(window) < self._window_size:
                window = np.pad(window, (0, self._window_size - len(window)))

            # Run inference
            input_tensor = window.astype(np.float32).reshape(1, 1, -1)
            try:
                outputs = self._session.run(None, {"input": input_tensor})
                speech_prob = float(outputs[0][0][0])
            except Exception as e:
                logger.error("vad_inference_failed", error=str(e))
                return await self._fallback_vad(audio, sample_rate, start_time)

            if speech_prob > 0.5:
                segments.append(VADSegment(
                    start_sample=i,
                    end_sample=min(i + self._window_size, len(audio)),
                    confidence=speech_prob,
                ))

        latency_ms = int((time.perf_counter() - start_time) * 1000)
        return EngineResult(
            data=self._merge_segments(segments),
            provider=self._provider,
            latency_ms=latency_ms,
            simulated=False,
        )

    async def _fallback_vad(self, audio: np.ndarray, sample_rate: int, start_time: float) -> EngineResult:
        """Fallback energy-based VAD."""
        await asyncio.sleep(0.001)
        # Simple energy threshold
        energy = np.abs(audio).mean()
        segments = []
        if energy > 0.01:
            segments.append(VADSegment(
                start_sample=0,
                end_sample=len(audio),
                confidence=min(energy * 10, 0.9),
            ))
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        return EngineResult(
            data=segments,
            provider=self._provider,
            latency_ms=latency_ms,
            simulated=True,
        )

    def _resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Simple linear resampling."""
        if orig_sr == target_sr:
            return audio
        ratio = target_sr / orig_sr
        new_length = int(len(audio) * ratio)
        indices = np.linspace(0, len(audio) - 1, new_length)
        return np.interp(indices, np.arange(len(audio)), audio)

    def _merge_segments(self, segments: list[VADSegment], max_gap: int = 1600) -> list[VADSegment]:
        """Merge nearby segments."""
        if not segments:
            return []

        merged = [segments[0]]
        for seg in segments[1:]:
            last = merged[-1]
            if seg.start_sample - last.end_sample <= max_gap:
                merged[-1] = VADSegment(
                    start_sample=last.start_sample,
                    end_sample=seg.end_sample,
                    confidence=max(last.confidence, seg.confidence),
                )
            else:
                merged.append(seg)
        return merged


class WhisperASR(BaseEngine, SpeechRecognizer):
    """Whisper ASR using ONNX Runtime."""

    def __init__(self, model_path: str | None = None) -> None:
        settings = get_settings()
        model_path = model_path or settings.ASR_MODEL_PATH
        self._model_path = Path(model_path)
        self._session: ort.InferenceSession | None = None
        self._provider = "CPUExecutionProvider"
        self._simulated = not self._model_path.exists()
        self._sample_rate = 16000
        self._n_mels = 80

    def _load_model(self) -> None:
        """Load the ONNX model."""
        if self._session is not None:
            return

        if self._simulated:
            logger.warning("asr_model_not_found", path=str(self._model_path))
            return

        selector = get_provider_selector()
        provider = selector.get_provider("asr")

        try:
            self._session = ort.InferenceSession(
                str(self._model_path),
                providers=[provider],
            )
            self._provider = self._session.get_providers()[0]
            logger.info("asr_model_loaded", provider=self._provider, path=str(self._model_path))
        except Exception as e:
            logger.error("asr_model_load_failed", error=str(e), provider=provider)
            self._simulated = True
            raise

    async def transcribe(self, audio: np.ndarray, sample_rate: int, language: str | None = None) -> EngineResult:
        """Transcribe audio using Whisper."""
        start_time = time.perf_counter()

        if self._simulated or self._session is None:
            return await self._fallback_transcribe(audio, sample_rate, language, start_time)

        # Preprocess audio to mel spectrogram
        mel = self._audio_to_mel(audio, sample_rate)

        # Run inference
        try:
            input_name = self._session.get_inputs()[0].name
            outputs = self._session.run(None, {input_name: mel})
            # Simplified - real implementation would decode tokens
            text = self._decode_output(outputs[0], language)
        except Exception as e:
            logger.error("asr_inference_failed", error=str(e))
            return await self._fallback_transcribe(audio, sample_rate, language, start_time)

        latency_ms = int((time.perf_counter() - start_time) * 1000)
        return EngineResult(
            data=text,
            provider=self._provider,
            latency_ms=latency_ms,
            simulated=False,
        )

    async def _fallback_transcribe(self, audio: np.ndarray, sample_rate: int, language: str | None, start_time: float) -> EngineResult:
        """Fallback mock transcription."""
        await asyncio.sleep(0.05)
        duration = len(audio) / sample_rate
        text = f"[Simulated transcription - {duration:.1f}s audio]"
        if language:
            text = f"[{language}] {text}"
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        return EngineResult(
            data=text,
            provider=self._provider,
            latency_ms=latency_ms,
            simulated=True,
        )

    def _audio_to_mel(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Convert audio to mel spectrogram (simplified)."""
        # Resample
        if sample_rate != self._sample_rate:
            ratio = self._sample_rate / sample_rate
            new_length = int(len(audio) * ratio)
            indices = np.linspace(0, len(audio) - 1, new_length)
            audio = np.interp(indices, np.arange(len(audio)), audio)

        # Simple STFT -> Mel (placeholder - real impl would use librosa or torchaudio)
        n_fft = 400
        hop_length = 160
        window = np.hanning(n_fft)

        frames = []
        for i in range(0, len(audio) - n_fft, hop_length):
            frame = audio[i:i + n_fft] * window
            spectrum = np.abs(np.fft.rfft(frame))
            frames.append(spectrum)

        if not frames:
            return np.zeros((1, self._n_mels, 1), dtype=np.float32)

        spectrogram = np.stack(frames, axis=1)
        # Simplified mel filterbank
        mel_spec = spectrogram[:self._n_mels, :]
        mel_spec = np.log(mel_spec + 1e-6)
        return mel_spec.astype(np.float32)[np.newaxis, ...]

    def _decode_output(self, output: np.ndarray, language: str | None) -> str:
        """Decode model output to text (placeholder)."""
        return f"[Whisper ONNX output - {output.shape}]"


class ExtractiveSummarizer(BaseEngine, Summarizer):
    """Extractive summarizer using simple algorithms."""

    def __init__(self) -> None:
        super().__init__(provider="CPU", simulated=False)

    async def summarize(
        self,
        text: str,
        language: str | None = None,
        max_key_points: int = 5,
        max_action_items: int = 5,
    ) -> EngineResult:
        """Generate extractive summary."""
        start_time = time.perf_counter()

        # Simple extractive summarization
        sentences = [s.strip() for s in text.split(".") if s.strip() and len(s.strip()) > 10]

        # Score sentences by position and length
        scored = []
        for i, sent in enumerate(sentences):
            # Prefer earlier sentences and medium-length ones
            position_score = 1.0 - (i / max(len(sentences), 1))
            length_score = 1.0 - abs(len(sent) - 100) / 200
            score = (position_score + length_score) / 2
            scored.append((score, sent))

        scored.sort(reverse=True, key=lambda x: x[0])
        key_points = [s for _, s in scored[:max_key_points]]

        # Extract action items (sentences with action verbs)
        action_verbs = ["need", "should", "must", "will", "action", "todo", "assign", "complete", "finish", "review"]
        action_items = []
        for sent in sentences:
            if any(verb in sent.lower() for verb in action_verbs):
                action_items.append(sent)
            if len(action_items) >= max_action_items:
                break

        if not action_items:
            action_items = ["No specific action items detected"]

        latency_ms = int((time.perf_counter() - start_time) * 1000)
        return EngineResult(
            data={
                "key_points": key_points,
                "action_items": action_items[:max_action_items],
            },
            provider=self.provider,
            latency_ms=latency_ms,
            simulated=False,
        )