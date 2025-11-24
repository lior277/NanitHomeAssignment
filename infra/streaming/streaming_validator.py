from __future__ import annotations
import logging
from typing import Mapping, Any, Literal

import requests

from config.config import StreamingConfig
from infra.http.http_client import BaseSession

logger = logging.getLogger(__name__)

NetworkCondition = Literal["normal", "poor", "terrible"]


class StreamingValidator(BaseSession):
    """Validator for the real mock streaming service."""

    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig()
        super().__init__(base_url=self.config.base_url, timeout=self.config.timeout)

        # Kept for backward compatibility with older tests
        self.fast_mode: bool = False

    def get_health(self) -> Mapping[str, Any]:
        response = self._get("/health")
        response.raise_for_status()
        return response.json()

    def get_latency_ms(self) -> float:
        health = self.get_health()

        if "latency_ms" not in health:
            raise KeyError(f"'latency_ms' missing in response: {health}")

        return float(health["latency_ms"])

    def set_network_condition(self, condition: NetworkCondition) -> None:
        if condition not in ("normal", "poor", "terrible"):
            raise ValueError("Unsupported network condition")

        try:
            resp = self._post(f"/control/network/{condition}")
            resp.raise_for_status()
        except requests.RequestException:
            # fallback JSON body version
            resp = self._post("/control/network/", json={"condition": condition})
            resp.raise_for_status()

    def get_manifest(self) -> str:
        resp = self._get("/stream.m3u8")
        resp.raise_for_status()
        return resp.text

    def get_segment(self, n: int) -> bytes:
        if n < 0:
            raise ValueError("Segment number must be >= 0")

        resp = self._get(f"/segment{n}.ts")
        resp.raise_for_status()
        return resp.content
