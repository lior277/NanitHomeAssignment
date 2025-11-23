
"""Validator for the mock streaming service.

Supports:
- Reading /health and extracting latency_ms
- Switching network conditions
- Fetching manifest and segments
- Optional FAST_MODE (mocked responses, no real HTTP)
"""

from typing import Any, Mapping, Literal
import logging
import os
import random

from config.config import StreamingConfig
from infra.streaming.base_session import BaseSession

logger = logging.getLogger(__name__)

NetworkCondition = Literal["normal", "poor", "terrible"]


class StreamingValidator(BaseSession):
    """High-level helper around the mock streaming service."""

    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig()
        super().__init__(base_url=self.config.base_url, timeout=self.config.timeout)

        # FAST_MODE: bypass network entirely and use mocked values
        self.fast_mode = os.getenv("FAST_MODE", "false").lower() == "true"
        if self.fast_mode:
            logger.warning(
                "FAST_MODE enabled — StreamingValidator using mock responses"
            )

        # Track condition when mocking
        self._mock_condition: NetworkCondition = "normal"

    # ----------------------------
    # Health / Metrics
    # ----------------------------

    def get_health(self) -> Mapping[str, Any]:
        """Fetch /health JSON or return mocked data in FAST_MODE."""
        if self.fast_mode:
            return {
                "status": "healthy",
                "network_condition": self._mock_condition,
                "bitrate": {
                    "normal": 2500,
                    "poor": 1200,
                    "terrible": 500,
                }[self._mock_condition],
                "latency_ms": {
                    "normal": random.uniform(5, 20),
                    "poor": random.uniform(80, 200),
                    "terrible": random.uniform(200, 400),
                }[self._mock_condition],
                "viewers": random.randint(10, 80),
            }

        data = self._get("/health").json()
        logger.debug("Health payload: %s", data)
        return data

    def get_latency_ms(self) -> float:
        """Return numeric latency in ms."""
        health = self.get_health()
        if "latency_ms" not in health:
            raise KeyError(f"'latency_ms' missing in /health: {health}")
        latency = float(health["latency_ms"])
        logger.info("latency_ms=%s", latency)
        return latency

    # ----------------------------
    # Network Control
    # ----------------------------

    def set_network_condition(self, condition: NetworkCondition) -> None:
        """Switch network condition on the backend or in FAST_MODE."""
        if self.fast_mode:
            logger.info("FAST_MODE: switching mock network → %s", condition)
            self._mock_condition = condition
            return

        logger.info("Switching network condition → %s", condition)
        try:
            self._post(f"/control/network/{condition}")
        except Exception as first_exc:  # noqa: BLE001 - acceptable for assignment
            logger.warning(
                "Path-style control failed, retrying with JSON body: %s", first_exc
            )
            self._post("/control/network/", json={"condition": condition})

    # ----------------------------
    # Streaming Endpoints
    # ----------------------------

    def get_manifest(self) -> str:
        """Return HLS manifest text (mocked in FAST_MODE)."""
        if self.fast_mode:
            return "#EXTM3U\n#EXTINF:10,\nsegment1.ts\n"

        text = self._get("/stream.m3u8").text
        logger.debug("Manifest length=%s", len(text))
        return text

    def get_segment(self, n: int) -> bytes:
        """Return TS segment content (mocked in FAST_MODE)."""
        if self.fast_mode:
            logger.debug("FAST_MODE: returning fake segment for index %s", n)
            return b"FAKE_SEGMENT_DATA"

        data = self._get(f"/segment{n}.ts").content
        logger.debug("Segment %s length=%s bytes", n, len(data))
        return data
