import os
import pytest

from config.config import StreamingConfig, MobileTestConfig
from infra.streaming.streaming_validator import StreamingValidator
from infra.mobile.mobile_session import MobileSession
from infra.mobile.mobile_screens import (
    WelcomeScreen, LoginScreen, LiveStreamScreen
)


# ==============================
# CONFIG FIXTURES
# ==============================

@pytest.fixture(scope="session")
def streaming_config() -> StreamingConfig:
    return StreamingConfig()


@pytest.fixture(scope="session")
def mobile_config() -> MobileTestConfig:
    return MobileTestConfig()


# ==============================
# STREAMING FIXTURE
# ==============================

@pytest.fixture(scope="function")
def streaming_validator(streaming_config: StreamingConfig) -> StreamingValidator:
    return StreamingValidator(config=streaming_config)


# ==============================
# MOBILE FIXTURES
# ==============================

@pytest.fixture(scope="function")
def mobile_session(mobile_config: MobileTestConfig) -> MobileSession:
    session = MobileSession(platform=mobile_config.platform)
    session.launch_app()
    yield session
    session.reset()


# ==============================
# SCREEN OBJECT FIXTURES
# ==============================

@pytest.fixture()
def welcome_screen(mobile_session): return WelcomeScreen(mobile_session)

@pytest.fixture()
def login_screen(mobile_session): return LoginScreen(mobile_session)

@pytest.fixture()
def live_stream_screen(mobile_session): return LiveStreamScreen(mobile_session)


# ==============================
# REPORT METADATA (optional)
# ==============================

def pytest_configure(config):
    metadata = getattr(config, "metadata", None)
    if metadata:
        metadata.update({
            "FAST_MODE": os.getenv("FAST_MODE", "false"),
            "MOB_PLATFORM": os.getenv("MOB_PLATFORM", "ios")
        })
