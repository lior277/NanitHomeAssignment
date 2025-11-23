"""
StreamingValidator - Validates streaming performance and metrics

Task A Requirements:
1. Fetches one metric from the mock service /health endpoint
2. Validates streaming performance parameter using the fetched metric
3. Handles network condition switching via /control/network/<condition>
"""

import aiohttp
import asyncio
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class StreamingValidator:
    """Validates streaming service performance and metrics using async aiohttp"""

    def __init__(self, base_url: str = "http://localhost:8082"):
        """
        Initialize StreamingValidator

        Args:
            base_url: Base URL of the streaming server
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info(f"StreamingValidator initialized with base_url: {self.base_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def fetch_health_metric(self, metric_name: str) -> any:
        """
        Fetch one metric from the mock service /health endpoint

        Args:
            metric_name: Name of the metric to fetch (e.g., 'status', 'viewers', 'network_condition')

        Returns:
            Value of the requested metric

        Raises:
            aiohttp.ClientError: If the request fails
            KeyError: If the metric doesn't exist
        """
        url = f"{self.base_url}/health"
        logger.info(f"Fetching metric '{metric_name}' from {url}")

        session = await self._get_session()

        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            health_data = await response.json()

        if metric_name not in health_data:
            raise KeyError(f"Metric '{metric_name}' not found. Available: {list(health_data.keys())}")

        metric_value = health_data[metric_name]
        logger.info(f"Fetched metric '{metric_name}' = {metric_value}")

        return metric_value

    async def validate_performance(self, expected_max_latency_ms: float) -> dict:
        """
        Validates streaming performance parameter using the fetched metric
        Measures response time and validates against expected threshold

        Args:
            expected_max_latency_ms: Maximum acceptable latency in milliseconds

        Returns:
            dict with validation results including actual_latency, threshold, and is_valid
        """
        url = f"{self.base_url}/health"
        logger.info(f"Validating performance against threshold: {expected_max_latency_ms}ms")

        session = await self._get_session()

        # Measure response time
        start_time = time.time()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            await response.json()  # Consume response
        elapsed_ms = (time.time() - start_time) * 1000

        is_valid = elapsed_ms <= expected_max_latency_ms

        result = {
            "actual_latency_ms": elapsed_ms,
            "threshold_ms": expected_max_latency_ms,
            "is_valid": is_valid
        }

        if is_valid:
            logger.info(f"✓ Performance validation PASSED: {elapsed_ms:.2f}ms <= {expected_max_latency_ms}ms")
        else:
            logger.warning(f"✗ Performance validation FAILED: {elapsed_ms:.2f}ms > {expected_max_latency_ms}ms")

        return result

    async def set_network_condition(self, condition: str) -> dict:
        """
        Handles network condition switching via /control/network/<condition>

        Args:
            condition: Network condition to set ('normal', 'poor', 'terrible')

        Returns:
            dict containing the applied condition and settings

        Raises:
            ValueError: If condition is invalid
            aiohttp.ClientError: If the request fails
        """
        valid_conditions = ['normal', 'poor', 'terrible']

        if condition not in valid_conditions:
            raise ValueError(f"Invalid condition '{condition}'. Must be one of: {valid_conditions}")

        url = f"{self.base_url}/control/network/{condition}"
        logger.info(f"Setting network condition to: {condition}")

        session = await self._get_session()

        async with session.put(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            result = await response.json()

        logger.info(f"Network condition set successfully: {result['applied']}")

        return result

    async def measure_latency(self, samples: int = 3) -> float:
        """
        Measure average latency over multiple samples

        Args:
            samples: Number of requests to average

        Returns:
            Average latency in milliseconds
        """
        url = f"{self.base_url}/health"
        total_time = 0.0

        logger.info(f"Measuring latency with {samples} samples")

        session = await self._get_session()

        for i in range(samples):
            start_time = time.time()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                await response.json()  # Consume response
            elapsed = (time.time() - start_time) * 1000
            total_time += elapsed
            logger.debug(f"Sample {i+1}: {elapsed:.2f}ms")

        avg_latency = total_time / samples
        logger.info(f"Average latency: {avg_latency:.2f}ms")

        return avg_latency

    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("StreamingValidator session closed")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()