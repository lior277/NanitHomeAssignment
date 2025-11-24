
import os
from dataclasses import dataclass, field


@dataclass
class StreamingConfig:
    """Streaming service configuration with CI-friendly overrides."""

    base_url: str = os.getenv("STREAMING_BASE_URL", "http://localhost:8082")
    timeout: float = float(os.getenv("STREAMING_TIMEOUT", "5.0"))

    @property
    def health_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/health"

    @property
    def manifest_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/stream.m3u8"

    @property
    def control_base_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/control/network"

    def control_url_for(self, condition: str) -> str:
        return f"{self.control_base_url}/{condition}"

    def segment_url(self, n: int) -> str:
        return f"{self.base_url.rstrip('/')}/segment{n}.ts"


@dataclass
class MobileTestConfig:
    """Credentials and settings for mocked mobile flow."""

    username: str = os.getenv("MOB_USER", "demo_app@nanit.com")
    password: str = os.getenv("MOB_PASS", "12341234")
    platform: str = os.getenv("MOB_PLATFORM", "ios")


@dataclass
class AppConfig:
    """Combined application configuration."""
    streaming: StreamingConfig = field(default_factory=StreamingConfig)
    mobile: MobileTestConfig = field(default_factory=MobileTestConfig)
