from __future__ import annotations
from typing import Any, Mapping, Literal
import logging
import os
import random

from config.config import StreamingConfig
from infra.http.base_session import BaseSession

logger = logging.getLogger(__name__)

NetworkCondition = Literal["normal", "poor", "terrible"]


class StreamingValidator(BaseSession):
    """
    Streaming validator with FAST_MODE support.

    FAST_MODE=true  → no HTTP requests, return mocked numbers
    FAST_MODE=false → real HTTP requests to mock_stream_server.py
    """

    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig()
        super().__init__(base_url=self.config.base_url, timeout=self.config.timeout)

        # FAST MODE toggle
        self.fast_mode = os.getenv("FAST_MODE", "false").lower() == "true"
        if self.fast_mode:
            logger.warning("⚡ FAST_MODE enabled — mocking streaming responses")

        # Track mock state
        self._mock_condition: NetworkCondition = "normal"

    # ----------------------------
    # Health / Metrics
    # ----------------------------

    def get_health(self) -> Mapping[str, Any]:
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
                    "normal": random.uniform(5, 25),
                    "poor": random.uniform(80, 200),
                    "terrible": random.uniform(200, 400),
                }[self._mock_condition],
                "viewers": random.randint(5, 50),
            }

        # Real network call
        return self._get("/health").json()

    def get_latency_ms(self) -> float:
        health = self.get_health()
        latency = float(health["latency_ms"])
        logger.info("latency_ms=%s", latency)
        return latency

    # ----------------------------
    # Network Behavior
    # ----------------------------

    def set_network_condition(self, condition: NetworkCondition) -> None:
        if self.fast_mode:
            logger.info(f"Mock network switching → {condition}")
            self._mock_condition = condition
            return

        logger.info("Switching network condition → %s", condition)
        try:
            self._post(f"/control/network/{condition}")
        except Exception:
            self._post("/control/network/", json={"condition": condition})

    # ----------------------------
    # Streaming Endpoints
    # ----------------------------

    def get_manifest(self) -> str:
        if self.fast_mode:
            return "#EXTM3U\n#EXTINF:10,\nsegment1.ts\n"

        return self._get("/stream.m3u8").text

    def get_segment(self, n: int) -> bytes:
        if self.fast_mode:
            return b"FAKE_SEGMENT_DATA"

        return self._get(f"/segment{n}.ts").content

    def reset(self):
        """Compatibility with BaseSession abstract reset()"""
        self.set_network_condition("normal")
