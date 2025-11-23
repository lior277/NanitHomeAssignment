"""
Pytest configuration and fixtures
"""
import pytest
from utils.test_suit_base import TestSuitBase
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def driver():
    """Setup and teardown fixture for each test"""
    logger.info("=" * 50)
    logger.info("Setting up Appium driver...")

    driver = TestSuitBase.get_driver()

    yield driver

    logger.info("Tearing down Appium driver...")
    TestSuitBase.driver_dispose(driver)
    logger.info("=" * 50)