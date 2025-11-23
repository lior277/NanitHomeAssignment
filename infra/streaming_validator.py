"""Configuration for streaming service."""

from dataclasses import dataclass


@dataclass
class StreamingConfig:
    """Streaming service configuration."""

    base_url: str = "http://localhost:8082"
    timeout: float = 5.0

    @property
    def health_url(self) -> str:
        return f"{self.base_url}/health"

    @property
    def control_url(self) -> str:
        return f"{self.base_url}/control/network/"