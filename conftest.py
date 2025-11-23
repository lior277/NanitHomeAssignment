# tests/conftest.py
import pytest

from config.config import StreamingConfig, MobileTestConfig
from infra.streaming_validator import StreamingValidator
from infra.mobile_session import MobileSession
from infra.page_objects.mobile_screens import (
    WelcomeScreen,
    LoginScreen,
    LiveStreamScreen,
)


# ==============================
# CONFIG FIXTURES
# ==============================

@pytest.fixture(scope="session")
def streaming_config() -> StreamingConfig:
    """CI-friendly streaming config"""
    return StreamingConfig()


@pytest.fixture(scope="session")
def mobile_config() -> MobileTestConfig:
    """Mobile configuration (credentials + platform)"""
    return MobileTestConfig()


# ==============================
# STREAMING FIXTURES
# ==============================

@pytest.fixture(scope="function")
def streaming_validator(streaming_config: StreamingConfig) -> StreamingValidator:
    """
    Fresh StreamingValidator per test, isolating state.
    Session-level config but function-level validator is better for parallelization.
    """
    return StreamingValidator(config=streaming_config)


# ==============================
# MOBILE FIXTURES
# ==============================

@pytest.fixture(scope="function")
def mobile_session(mobile_config: MobileTestConfig) -> MobileSession:
    """
    Mock mobile driver session.
    Platform controlled by config:
        MOB_PLATFORM=ios
        MOB_PLATFORM=android
    """
    session = MobileSession(platform=mobile_config.platform)
    session.launch_app()

    yield session  # TEST EXECUTES HERE

    # teardown/reset (important if running many tests in same session)
    session.app_launched = False
    session.logged_in = False
    session.current_screen = "welcome"


# ==============================
# SCREEN OBJECT FIXTURES
# ==============================

@pytest.fixture(scope="function")
def welcome_screen(mobile_session: MobileSession) -> WelcomeScreen:
    return WelcomeScreen(mobile_session)


@pytest.fixture(scope="function")
def login_screen(mobile_session: MobileSession) -> LoginScreen:
    return LoginScreen(mobile_session)


@pytest.fixture(scope="function")
def live_stream_screen(mobile_session: MobileSession) -> LiveStreamScreen:
    return LiveStreamScreen(mobile_session)
