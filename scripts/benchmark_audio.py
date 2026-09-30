#!/usr/bin/env python3
"""Generate benchmark audio file."""

import numpy as np
import soundfile as sf
from pathlib import Path


def generate_benchmark_audio(
    output_path: Path,
    duration: float = 30.0,
    sample_rate: int = 16000,
) -> None:
    """Generate synthetic benchmark audio with speech-like characteristics."""
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create speech-like signal with formants
    # Fundamental frequency varying like speech
    f0 = 120 + 30 * np.sin(2 * np.pi * 0.5 * t)

    # Formants (simplified)
    f1 = 700 + 100 * np.sin(2 * np.pi * 0.3 * t)
    f2 = 1200 + 200 * np.sin(2 * np.pi * 0.2 * t)
    f3 = 2500 + 300 * np.sin(2 * np.pi * 0.1 * t)

    # Generate harmonics
    audio = np.zeros_like(t)
    for harmonic in range(1, 6):
        freq = harmonic * f0
        audio += (1.0 / harmonic) * np.sin(2 * np.pi * freq * t)

    # Apply formant filtering (simplified with bandpass)
    # This is a very simplified approximation
    audio = audio * (0.5 + 0.5 * np.sin(2 * np.pi * 2 * t))

    # Add pauses (silence periods) to simulate natural speech
    pause_intervals = [
        (5.0, 5.5),
        (12.0, 12.8),
        (20.0, 21.0),
        (27.0, 27.5),
    ]

    for start, end in pause_intervals:
        start_idx = int(start * sample_rate)
        end_idx = int(end * sample_rate)
        audio[start_idx:end_idx] *= 0.01

    # Add background noise
    noise = 0.005 * np.random.randn(len(audio))
    audio += noise

    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, audio.astype(np.float32), sample_rate)
    print(f"Generated benchmark audio: {output_path} ({duration}s, {sample_rate}Hz)")


def main() -> int:
    output_path = Path("scripts/benchmark_audio.wav")
    generate_benchmark_audio(output_path, duration=30.0)
    return 0


if __name__ == "__main__":
    main()