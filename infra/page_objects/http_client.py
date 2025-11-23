"""HTTP client interface and implementation."""
import logging
from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict, Any, Optional
import requests

logger: Logger = logging.getLogger(__name__)


class IHttpClient(ABC):
    """Interface for HTTP operations."""

    @abstractmethod
    def get(self, url: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Execute GET request."""

    @abstractmethod
    def post(self, url: str, json_data: Optional[Dict[str, Any]] = None,
             timeout: Optional[float] = None) -> Dict[str, Any]:
        """Execute POST request."""


class HttpClient(IHttpClient):
    """HTTP client implementation using requests."""

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, url: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Execute GET request and return JSON response."""
        timeout = timeout or self.timeout
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"GET request failed for {url}: {e}")
            raise

    def post(self, url: str, json_data: Optional[Dict[str, Any]] = None,
             timeout: Optional[float] = None) -> Dict[str, Any]:
        """Execute POST request and return JSON response."""
        timeout = timeout or self.timeout
        try:
            response = self.session.post(url, json=json_data, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"POST request failed for {url}: {e}")
            raise

    def close(self):
        """Close the session."""
        self.session.close()