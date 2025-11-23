"""
Pytest configuration and fixtures for Nanit QA Automation

This module provides reusable fixtures for:
- Appium mobile testing (existing)
- Streaming validation (new - Stage 1)
- Mobile session mocking (new - Stage 2)

All fixtures include proper setup, teardown, and error handling.
"""
import asyncio
import logging
import pytest
import pytest_asyncio
from typing import Generator, AsyncGenerator

from infra.utils.test_suit_base import TestSuitBase
from infra.streaming_validator import StreamingValidator
from infra.mobile_session import MobileSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# MOBILE FIXTURES (Existing - for Real Appium tests)
# ============================================================================

@pytest.fixture(scope="function")
def driver() -> Generator:
    """
    Setup and teardown fixture for Appium WebDriver.

    Provides a real Appium driver for mobile automation tests.
    Scope: function - New driver instance for each test to ensure isolation.

    Yields:
        webdriver.Remote: Configured Appium WebDriver instance

    Raises:
        Exception: If driver setup or teardown fails
    """
    logger.info("=" * 50)
    logger.info("Setting up Appium driver...")

    driver = None
    try:
        driver = TestSuitBase.get_driver()
        logger.info("✓ Appium driver created successfully")

        yield driver

    except Exception as e:
        logger.error(f"✗ Failed to create Appium driver: {e}")
        raise
    finally:
        logger.info("Tearing down Appium driver...")
        try:
            TestSuitBase.driver_dispose(driver)
            logger.info("✓ Appium driver disposed successfully")
        except Exception as e:
            logger.warning(f"Error during driver disposal: {e}")
        logger.info("=" * 50)


# ============================================================================
# STREAMING FIXTURES (New - for Stage 1 async tests)
# ============================================================================

@pytest_asyncio.fixture(scope="function")
async def streaming_validator() -> AsyncGenerator[StreamingValidator, None]:
    """
    Async fixture to provide a StreamingValidator instance for streaming tests.

    Provides:
    - Configured StreamingValidator connected to mock streaming server
    - Automatic cleanup and network condition reset after test
    - Error handling for failed cleanup operations

    Scope: function - New instance for each test to ensure isolation

    Yields:
        StreamingValidator: Configured validator instance

    Note:
        Ensures mock streaming server is running on http://localhost:8082
        Resets network to 'normal' conditions after test completes
    """
    validator = None
    try:
        validator = StreamingValidator(base_url="http://localhost:8082")
        logger.info("✓ StreamingValidator fixture created")

        # Verify server is accessible
        try:
            await validator.fetch_health_metric("status")
            logger.info("✓ Mock streaming server is accessible")
        except Exception as e:
            logger.error(
                f"✗ Cannot connect to mock streaming server: {e}\n"
                f"Make sure to start the server:\n"
                f"  python mock_services/mock_stream_server.py"
            )
            raise

        yield validator

    except Exception as e:
        logger.error(f"✗ Error in streaming_validator fixture: {e}")
        raise
    finally:
        # Cleanup: Reset to normal conditions after test
        if validator:
            try:
                await validator.set_network_condition("normal")
                logger.info("✓ StreamingValidator reset to normal conditions")
            except Exception as e:
                logger.warning(f"Failed to reset network condition: {e}")

            try:
                await validator.close()
                logger.info("✓ StreamingValidator session closed")
            except Exception as e:
                logger.warning(f"Failed to close validator session: {e}")


@pytest.fixture(scope="session")
def streaming_server_url() -> str:
    """
    Fixture to provide the streaming server URL.

    Scope: session - Same URL for all tests in the session

    Returns:
        str: URL of the mock streaming server
    """
    return "http://localhost:8082"


@pytest.fixture(scope="session")
def streaming_server_health_check(streaming_server_url: str) -> bool:
    """
    Session-scoped fixture to verify streaming server is running.

    Performs a health check at session start to fail fast if server is down.

    Args:
        streaming_server_url: URL of streaming server (from fixture)

    Returns:
        bool: True if server is healthy

    Raises:
        RuntimeError: If server is not accessible
    """
    import aiohttp
    import asyncio

    async def check_server():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{streaming_server_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        logger.info("✓ Streaming server health check passed")
                        return True
                    else:
                        raise RuntimeError(
                            f"Server returned status {response.status}"
                        )
        except Exception as e:
            raise RuntimeError(
                f"Streaming server health check failed: {e}\n"
                f"Make sure the server is running:\n"
                f"  python mock_services/mock_stream_server.py"
            )

    # Run async health check
    try:
        return asyncio.run(check_server())
    except RuntimeError:
        # Re-raise to fail session startup
        raise


# ============================================================================
# MOBILE SESSION FIXTURES (New - for Stage 2 mock tests)
# ============================================================================

@pytest.fixture(scope="function")
def mobile_session(request) -> Generator[MobileSession, None, None]:
    """
    Fixture to provide a mock MobileSession for mobile testing.

    Provides:
    - Mock MobileSession that simulates Appium without real devices
    - Automatic cleanup after test completes
    - Platform configuration via test parameters

    Scope: function - New instance for each test

    Yields:
        MobileSession: Mock mobile session instance

    Usage:
        @pytest.mark.parametrize("platform", ["Android", "iOS"])
        def test_cross_platform(mobile_session, platform):
            # mobile_session will use the specified platform
            pass
    """
    # Get platform from test parameter if available, else default to Android
    platform = getattr(request, 'param', 'Android')

    try:
        session = MobileSession(platform=platform)
        logger.info(f"✓ Mock MobileSession fixture created for {platform}")

        yield session

    except Exception as e:
        logger.error(f"✗ Error creating MobileSession: {e}")
        raise
    finally:
        # Cleanup
        try:
            if 'session' in locals():
                session.quit()
                logger.info("✓ Mock MobileSession closed")
        except Exception as e:
            logger.warning(f"Error during MobileSession cleanup: {e}")


@pytest.fixture(scope="function")
def mobile_session_android() -> Generator[MobileSession, None, None]:
    """
    Fixture specifically for Android mobile session.

    Yields:
        MobileSession: Android mobile session
    """
    session = MobileSession(platform="Android", app_name="Nanit")
    logger.info("✓ Android MobileSession created")
    yield session
    session.quit()
    logger.info("✓ Android MobileSession closed")


@pytest.fixture(scope="function")
def mobile_session_ios() -> Generator[MobileSession, None, None]:
    """
    Fixture specifically for iOS mobile session.

    Yields:
        MobileSession: iOS mobile session
    """
    session = MobileSession(platform="iOS", app_name="Nanit")
    logger.info("✓ iOS MobileSession created")
    yield session
    session.quit()
    logger.info("✓ iOS MobileSession closed")


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def test_data_factory():
    """
    Factory fixture for generating test data.

    Returns:
        dict: Factory methods for creating test data
    """
    import time

    return {
        'timestamp': lambda: int(time.time()),
        'unique_id': lambda prefix='test': f"{prefix}_{int(time.time())}",
        'test_email': lambda: f"test_{int(time.time())}@nanit.com",
        'test_password': lambda: "Test12341234",
    }


@pytest.fixture(autouse=True)
def log_test_start_end(request):
    """
    Auto-use fixture that logs test start and end.

    This runs automatically for every test without being explicitly requested.
    """
    test_name = request.node.name
    logger.info(f"\n{'='*80}")
    logger.info(f"Starting test: {test_name}")
    logger.info(f"{'='*80}")

    yield

    logger.info(f"\n{'='*80}")
    logger.info(f"Finished test: {test_name}")
    logger.info(f"{'='*80}\n")


# ============================================================================
# HOOKS
# ============================================================================

def pytest_configure(config):
    """
    Pytest hook called once at configuration time.

    Register custom markers to avoid warnings about unknown markers.
    """
    config.addinivalue_line(
        "markers", "streaming: Streaming validation tests (API layer)"
    )
    config.addinivalue_line(
        "markers", "asyncio: Async tests requiring asyncio support"
    )
    config.addinivalue_line(
        "markers", "mobile: Mobile testing tests (mock or real Appium)"
    )
    config.addinivalue_line(
        "markers", "smoke: Smoke tests for quick validation"
    )
    config.addinivalue_line(
        "markers", "regression: Regression tests for comprehensive coverage"
    )
    config.addinivalue_line(
        "markers", "critical: Critical path tests that must always pass"
    )


def pytest_collection_modifyitems(config, items):
    """
    Pytest hook called after test collection.

    Automatically mark async tests with asyncio marker if not already marked.
    """
    for item in items:
        # Auto-mark coroutine functions with asyncio marker
        if asyncio.iscoroutinefunction(item.function):
            if not any(mark.name == 'asyncio' for mark in item.iter_markers()):
                item.add_marker(pytest.mark.asyncio)