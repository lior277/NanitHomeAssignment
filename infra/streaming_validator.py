# infra/streaming_validator.py
from __future__ import annotations

from typing import Any, Mapping, Literal, Optional

import requests

NetworkCondition = Literal["normal", "poor", "terrible"]


class StreamingValidator:
    def __init__(self, http_client: IHttpClient, config: StreamingServiceConfig):
        self._http_client = http_client  # ✅ Injected
        self._config = config            # ✅ Injected

    # ---- low-level HTTP helper --------------------------------------------------

    def _get(self, path: str) -> requests.Response:
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    # ---- public API -------------------------------------------------------------

    def get_health(self) -> Mapping[str, Any]:
        """Return the JSON payload from /health."""
        return self._get("/health").json()

    def get_metrics(self) -> Mapping[str, Any]:
        """Return the JSON payload from /metrics."""
        return self._get("/metrics").json()

    def get_latency_ms(self) -> float:
        """
        Streaming performance parameter: average latency in ms.

        This comes from /metrics.performance.average_latency_ms.
        """
        metrics = self.get_metrics()
        return float(metrics["performance"]["average_latency_ms"])

    def set_network_condition(self, condition: NetworkCondition) -> None:
        """Switch the backend to normal / poor / terrible."""
        # server expects PUT /control/network/<condition>
        url = f"{self.base_url}/control/network/{condition}"
        resp = self.session.put(url, timeout=self.timeout)
        resp.raise_for_status()

    def get_manifest(self) -> str:
        """Fetch the HLS manifest to ensure streaming is available."""
        return self._get("/stream.m3u8").text

    def get_segment(self, n: int) -> bytes:
        """Fetch a specific TS segment."""
        return self._get(f"/segment{n}.ts").content
