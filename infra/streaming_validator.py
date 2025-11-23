# infra/streaming_validator.py
from __future__ import annotations

from typing import Any, Mapping, Literal

import logging

from config.config import StreamingConfig
from infra.base_session import BaseSession

logger = logging.getLogger(__name__)

NetworkCondition = Literal["normal", "poor", "terrible"]


class StreamingValidator(BaseSession):
    """
    Stage-2 streaming validator.

    Responsibilities:
    - Fetch health data and derive a performance metric (latency_ms)
    - Switch network conditions via control endpoint
    - Validate manifest/segments reachability
    - Use BaseSession for retries + logging
    """

    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig()
        super().__init__(base_url=self.config.base_url, timeout=self.config.timeout)

    # -------- health / metrics --------

    def get_health(self) -> Mapping[str, Any]:
        """Fetch /health JSON."""
        data = self._get("/health").json()
        logger.debug("Health: %s", data)
        return data

    def get_latency_ms(self) -> float:
        """Use latency_ms from /health as our quality metric."""
        health = self.get_health()
        if "latency_ms" not in health:
            raise KeyError(f"'latency_ms' missing in /health: {health}")
        latency = float(health["latency_ms"])
        logger.info("latency_ms=%s", latency)
        return latency

    # -------- network control --------

    def set_network_condition(self, condition: NetworkCondition) -> None:
        """Switch network condition.

        Prefer assignment-style path:
            POST /control/network/<condition>
        but fall back to JSON body if that fails (for compatibility).
        """
        logger.info("Switching network condition → %s", condition)
        try:
            self._post(f"/control/network/{condition}")
        except Exception as first_exc:
            logger.warning(
                "Path-style control failed, retrying with JSON body: %s", first_exc
            )
            self._post("/control/network/", json={"condition": condition})

    # -------- streaming endpoints --------

    def get_manifest(self) -> str:
        text = self._get("/stream.m3u8").text
        logger.debug("Manifest length=%s", len(text))
        return text

    def get_segment(self, n: int) -> bytes:
        data = self._get(f"/segment{n}.ts").content
        logger.debug("Segment %s length=%s bytes", n, len(data))
        return data
