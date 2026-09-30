"""Provider selection for ONNX Runtime."""

import onnxruntime as ort
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProviderSelector:
    """Selects the best available ONNX Runtime execution provider."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._available_providers: list[str] = []
        self._initialized = False

    def initialize(self) -> None:
        """Initialize and detect available providers."""
        if self._initialized:
            return

        available = ort.get_available_providers()
        preferred = self.settings.PREFERRED_PROVIDERS

        # Filter preferred providers that are actually available
        self._available_providers = [p for p in preferred if p in available]

        # Log detection results
        logger.info(
            "provider_detection",
            available_providers=available,
            preferred_providers=preferred,
            selected_providers=self._available_providers,
        )

        # Check for NPU specifically
        has_npu = "QNNExecutionProvider" in available
        has_gpu = any(p in available for p in ["CUDAExecutionProvider", "DmlExecutionProvider"])
        logger.info(
            "hardware_capabilities",
            npu_available=has_npu,
            gpu_available=has_gpu,
            cpu_available="CPUExecutionProvider" in available,
        )

        self._initialized = True

    def get_provider(self, stage: str) -> str:
        """Get the best provider for a given stage."""
        self.initialize()

        if not self._available_providers:
            logger.warning("no_providers_available", stage=stage, fallback="CPUExecutionProvider")
            return "CPUExecutionProvider"

        provider = self._available_providers[0]
        logger.debug("provider_selected", stage=stage, provider=provider)
        return provider

    def get_all_providers(self) -> list[str]:
        """Get all available providers in priority order."""
        self.initialize()
        return self._available_providers.copy()

    def is_provider_available(self, provider: str) -> bool:
        """Check if a specific provider is available."""
        self.initialize()
        return provider in self._available_providers

    def get_capabilities(self) -> dict:
        """Get hardware capabilities."""
        self.initialize()
        available = ort.get_available_providers()
        return {
            "npu_available": "QNNExecutionProvider" in available,
            "gpu_available": any(p in available for p in ["CUDAExecutionProvider", "DmlExecutionProvider"]),
            "cpu_available": "CPUExecutionProvider" in available,
            "available_providers": available,
            "selected_providers": self._available_providers,
        }


# Global instance
_provider_selector: Optional[ProviderSelector] = None


def get_provider_selector() -> ProviderSelector:
    """Get global provider selector instance."""
    global _provider_selector
    if _provider_selector is None:
        _provider_selector = ProviderSelector()
    return _provider_selector