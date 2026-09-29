#!/usr/bin/env python3
"""Download ML models for offline use."""

import argparse
import os
import sys
from pathlib import Path
from urllib.request import urlretrieve

import tqdm


MODELS = {
    "silero_vad": {
        "url": "https://github.com/snakers4/silero-vad/raw/master/files/silero_vad.onnx",
        "filename": "silero_vad.onnx",
        "size_mb": 5,
    },
    "whisper_tiny": {
        "url": "https://huggingface.co/onnx-community/whisper-tiny/resolve/main/onnx/model.onnx",
        "filename": "whisper_tiny.onnx",
        "size_mb": 75,
    },
}


class TqdmUpTo(tqdm.tqdm):
    """Progress bar for urlretrieve."""

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_model(model_name: str, models_dir: Path, force: bool = False) -> Path:
    """Download a single model."""
    if model_name not in MODELS:
        raise ValueError(f"Unknown model: {model_name}")

    model_info = MODELS[model_name]
    output_path = models_dir / model_info["filename"]

    if output_path.exists() and not force:
        print(f"Model {model_name} already exists at {output_path}")
        return output_path

    print(f"Downloading {model_name} ({model_info['size_mb']} MB)...")
    models_dir.mkdir(parents=True, exist_ok=True)

    with TqdmUpTo(unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=model_name) as t:
        urlretrieve(model_info["url"], output_path, reporthook=t.update_to)

    print(f"Downloaded to {output_path}")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Download ML models")
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=Path("./models"),
        help="Directory to save models",
    )
    parser.add_argument(
        "--model",
        choices=list(MODELS.keys()) + ["all"],
        default="all",
        help="Model to download",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if file exists",
    )
    args = parser.parse_args()

    models_to_download = list(MODELS.keys()) if args.model == "all" else [args.model]

    for model in models_to_download:
        try:
            download_model(model, args.models_dir, args.force)
        except Exception as e:
            print(f"Failed to download {model}: {e}", file=sys.stderr)
            return 1

    print("All models downloaded successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())