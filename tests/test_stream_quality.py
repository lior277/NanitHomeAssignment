"""
Pytest configuration and fixtures
"""
import logging
import pytest
import pytest_asyncio

from infra.utils.test_suit_base import TestSuitBase
from infra.streaming_validator import StreamingValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# MOBILE FIXTURES (Existing - for Appium tests)
# ============================================================================

@pytest.fixture(scope="function")
def driver():
    """Setup and teardown fixture for each test - Mobile Appium driver"""
    logger.info("=" * 50)
    logger.info("Setting up Appium driver...")

    driver = TestSuitBase.get_driver()

    yield driver

    logger.info("Tearing down Appium driver...")
    TestSuitBase.driver_dispose(driver)
    logger.info("=" * 50)


# ============================================================================
# STREAMING FIXTURES (New - for Stage 1 async tests)
# ============================================================================

@pytest_asyncio.fixture(scope="function")
async def streaming_validator():
    """
    Async fixture to provide a StreamingValidator instance for each test

    Scope: function - New instance for each test to ensure isolation
    """
    validator = StreamingValidator(base_url="http://localhost:8082")
    logger.info("StreamingValidator fixture created")

    yield validator

    # Cleanup: Reset to normal conditions after test
    try:
        await validator.set_network_condition("normal")
        logger.info("StreamingValidator reset to normal conditions")
    except Exception as e:
        logger.warning(f"Error resetting network condition: {e}")
    finally:
        await validator.close()
        logger.info("StreamingValidator session closed")


@pytest.fixture(scope="session")
def streaming_server_url():
    """
    Fixture to provide the streaming server URL

    Scope: session - Same URL for all tests in the session
    """
    return "http://localhost:8082"


# ============================================================================
# MOBILE SESSION FIXTURES (New - for Stage 2 mock tests)
# ============================================================================

@pytest.fixture(scope="function")
def mobile_session():
    """
    Fixture to provide a mock MobileSession for testing

    Scope: function - New instance for each test
    """
    from infra.mobile_session import MobileSession

    session = MobileSession(platform="Android")
    logger.info("Mock MobileSession fixture created")

    yield session

    # Cleanup
    session.quit()
    logger.info("Mock MobileSession closed")