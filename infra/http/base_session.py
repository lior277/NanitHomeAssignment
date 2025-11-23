"""Shared HTTP session base with retry and logging.

This module provides :class:`BaseSession`, a small wrapper around ``requests.Session``
with:
- base URL handling
- configurable timeout
- simple retry logic on transient errors
- structured logging

Intended to be subclassed by specific API clients (e.g. ``StreamingValidator``).
"""

from __future__ import annotations

from typing import Iterable, Optional

import logging
import time

import requests
from requests import Response

LOGGER = logging.getLogger(__name__)


class BaseSession:  # pylint: disable=too-few-public-methods
    """Reusable HTTP client with basic retry and logging."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        retry_statuses: Iterable[int] = (502, 503, 504),
    ) -> None:
        """Create a new session wrapper.

        Args:
            base_url: Base URL for all requests (e.g. ``http://localhost:8082``).
            timeout: Per-request timeout in seconds.
            max_retries: Maximum number of retry attempts for retryable errors.
            retry_statuses: HTTP status codes that should trigger a retry.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_statuses = set(retry_statuses)
        self.session = requests.Session()
        self.log = logging.getLogger(self.__class__.__name__)

    def _request(self, method: str, path: str, **kwargs) -> Response:
        """Perform an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: Relative path (e.g. ``/health``).
            **kwargs: Extra arguments forwarded to ``requests.Session.request``.

        Returns:
            The final :class:`requests.Response` object.

        Raises:
            requests.RequestException: When all retry attempts fail.
            RuntimeError: If an unexpected error occurs after retries.
        """
        url = f"{self.base_url}{path}"

        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                self.log.debug("HTTP %s %s (attempt %s)", method, url, attempt)
                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    **kwargs,
                )
            except requests.RequestException as exc:
                last_exc = exc
                self.log.warning(
                    "Request error on %s %s (attempt %s/%s): %s",
                    method,
                    url,
                    attempt,
                    self.max_retries,
                    exc,
                )
                if attempt == self.max_retries:
                    raise
                time.sleep(0.1 * attempt)
                continue

            if response.status_code in self.retry_statuses and attempt < self.max_retries:
                self.log.warning(
                    "Retryable status %s on %s %s (attempt %s/%s)",
                    response.status_code,
                    method,
                    url,
                    attempt,
                    self.max_retries,
                )
                time.sleep(0.1 * attempt)
                continue

            response.raise_for_status()
            return response

        raise RuntimeError(f"HTTP {method} {url} failed after retries") from last_exc

    def _get(self, path: str, **kwargs) -> Response:
        """Convenience wrapper for GET requests."""
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs) -> Response:
        """Convenience wrapper for POST requests."""
        return self._request("POST", path, **kwargs)
