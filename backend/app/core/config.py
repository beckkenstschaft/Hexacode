"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Product
    PRODUCT_NAME: str = Field(default="Sahayak", description="Product name displayed in UI")

    # Environment
    ENVIRONMENT: Literal["development", "testing", "production"] = Field(
        default="development", description="Runtime environment"
    )
    DEBUG: bool = Field(default=True, description="Enable debug mode")

    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of workers")

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins",
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/sahayak.db",
        description="Database connection URL",
    )
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")

    # File storage
    DATA_DIR: Path = Field(default=Path("./data"), description="Data directory")
    MODELS_DIR: Path = Field(default=Path("./models"), description="Models directory")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="Max upload size in bytes")
    MAX_WS_MESSAGE_SIZE: int = Field(default=4 * 1024 * 1024, description="Max WebSocket message size")

    # ML Engine
    USE_MOCK_ENGINES: bool = Field(
        default=True,
        description="Use mock engines instead of real ONNX models",
    )
    VAD_MODEL_PATH: str = Field(default="models/silero_vad.onnx", description="VAD model path")
    ASR_MODEL_PATH: str = Field(default="models/whisper_tiny.onnx", description="ASR model path")
    SUMMARIZER_MODEL_PATH: str = Field(default="", description="Optional GenAI summarizer model path")
    ENABLE_GENAI_SUMMARIZER: bool = Field(default=False, description="Enable GenAI summarizer")

    # Provider selection
    PREFERRED_PROVIDERS: list[str] = Field(
        default=["QNNExecutionProvider", "CUDAExecutionProvider", "DmlExecutionProvider", "CPUExecutionProvider"],
        description="Ordered list of preferred ONNX Runtime execution providers",
    )

    # Benchmark
    BENCHMARK_AUDIO_PATH: str = Field(default="scripts/benchmark_audio.wav", description="Benchmark audio file")
    BENCHMARK_ITERATIONS: int = Field(default=3, description="Number of benchmark iterations")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: Literal["json", "console"] = Field(default="json", description="Log format")

    @field_validator("DATA_DIR", "MODELS_DIR", mode="before")
    @classmethod
    def resolve_path(cls, v: str | Path) -> Path:
        """Resolve path relative to project root."""
        if isinstance(v, str):
            v = Path(v)
        return v.resolve()

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()