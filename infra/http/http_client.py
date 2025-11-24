from __future__ import annotations
from typing import Iterable, Optional
import logging
import time
import requests
from requests import Response


class BaseSession:
    """Reusable HTTP client with retry logic and structured logging."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        retry_statuses: Iterable[int] = (502, 503, 504),
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_statuses = set(retry_statuses)
        self.session = requests.Session()
        self.log = logger or logging.getLogger(self.__class__.__name__)

    def _request(self, method: str, path: str, **kwargs) -> Response:
        url = f"{self.base_url}{path}"
        last_exc: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                self.log.debug("HTTP %s %s (attempt %s)", method, url, attempt)
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )

                if self._should_retry(response, attempt):
                    time.sleep(0.1 * attempt)
                    continue

                response.raise_for_status()
                return response

            except requests.RequestException as exc:
                last_exc = exc
                if attempt == self.max_retries:
                    raise
                time.sleep(0.1 * attempt)

        raise RuntimeError(f"HTTP {method} {url} failed") from last_exc

    def _should_retry(self, response: Response, attempt: int) -> bool:
        return (
            response.status_code in self.retry_statuses
            and attempt < self.max_retries
        )

    def _get(self, path: str, **kwargs) -> Response:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs) -> Response:
        return self._request("POST", path, **kwargs)
