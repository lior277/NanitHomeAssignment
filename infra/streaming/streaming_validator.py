"""Validator for mock streaming service behavior.

Provides :class:`StreamingValidator`, which is built on top of
:class:`infra.base_session.BaseSession` and can:

- query /health for latency and status metrics
- switch network conditions
- verify manifest and segment availability
- support FAST_MODE for mocked runs without HTTP calls
"""

from __future__ import annotations

from typing import Any, Mapping, Literal
import logging
import os
import random

import requests

from config.config import StreamingConfig
from infra.http.base_session import BaseSession

LOGGER = logging.getLogger(__name__)

NetworkCondition = Literal["normal", "poor", "terrible"]


class StreamingValidator(BaseSession):
    """Client used to validate streaming backend behavior."""

    def __init__(self, config: StreamingConfig | None = None) -> None:
        """Create a new streaming validator using the given configuration."""
        self.config = config or StreamingConfig()
        super().__init__(base_url=self.config.base_url, timeout=self.config.timeout)

        self.fast_mode = os.getenv("FAST_MODE", "false").lower() == "true"
        if self.fast_mode:
            LOGGER.warning(
                "FAST_MODE enabled — StreamingValidator using mock responses",
            )

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
        LOGGER.debug("Health: %s", data)
        return data

    def get_latency_ms(self) -> float:
        """Return the numeric latency in milliseconds from /health."""
        health = self.get_health()
        latency = float(health["latency_ms"])
        LOGGER.info("latency_ms=%s", latency)
        return latency

    # ----------------------------
    # Network Control
    # ----------------------------

    def set_network_condition(self, condition: NetworkCondition) -> None:
        """Switch network condition on the backend or in mock state."""
        if self.fast_mode:
            LOGGER.info("Mock: switching network → %s", condition)
            self._mock_condition = condition
            return

        LOGGER.info("Switching network condition → %s", condition)
        try:
            self._post(f"/control/network/{condition}")
        except requests.RequestException as first_exc:
            LOGGER.warning(
                "Path-style control failed, retrying with JSON body: %s",
                first_exc,
            )
            self._post("/control/network/", json={"condition": condition})

    # ----------------------------
    # Streaming Endpoints
    # ----------------------------

    def get_manifest(self) -> str:
        """Return the manifest text."""
        if self.fast_mode:
            return "#EXTM3U\n#EXTINF:10,\nsegment1.ts\n"

        text = self._get("/stream.m3u8").text
        LOGGER.debug("Manifest length=%s", len(text))
        return text

    def get_segment(self, index: int) -> bytes:
        """Return the bytes for the given segment index."""
        if self.fast_mode:
            return b"FAKE_SEGMENT_DATA"

        data = self._get(f"/segment{index}.ts").content
        LOGGER.debug("Segment %s length=%s bytes", index, len(data))
        return data
