from __future__ import annotations
from abc import ABC, abstractmethod
import logging
import time
from typing import Iterable, Optional

import requests
from requests import Response


class BaseSession(ABC):
    """
    Abstract base class for all session clients:
    - StreamingValidator (HTTP)
    - MobileSession (mock driver)
    - Future API sessions

    Provides:
    - retries
    - structured logging
    - shared timeout handling
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 5.0,
        max_retries: int = 3,
        retry_statuses: Iterable[int] = (502, 503, 504),
    ) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_statuses = set(retry_statuses)
        self.session = requests.Session()
        self.log = logging.getLogger(self.__class__.__name__)

    # --------- ABSTRACT METHODS ----------
    @abstractmethod
    def reset(self):
        """Reset session state (implemented by subclasses)."""
        ...


    # --------- COMMON HTTP WRAPPERS ----------
    def _request(self, method: str, path: str, **kwargs) -> Response:
        if not self.base_url:
            raise ValueError("BaseSession requires base_url for HTTP operations")

        url = f"{self.base_url}{path}"
        last_exc: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                self.log.debug("HTTP %s %s attempt %s", method, url, attempt)
                resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
            except requests.RequestException as exc:
                last_exc = exc
                self.log.warning(
                    "Request error on %s %s (attempt %s/%s): %s",
                    method, url, attempt, self.max_retries, exc,
                )
                if attempt == self.max_retries:
                    raise
                time.sleep(0.1 * attempt)
                continue

            if resp.status_code in self.retry_statuses and attempt < self.max_retries:
                self.log.warning(
                    "Retrying due to %s on %s %s",
                    resp.status_code, method, url
                )
                time.sleep(0.1 * attempt)
                continue

            resp.raise_for_status()
            return resp

        raise RuntimeError(f"HTTP {method} {url} failed after retries") from last_exc

    def _get(self, path: str, **kwargs) -> Response:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs) -> Response:
        return self._request("POST", path, **kwargs)
