import logging
import pytest

from config.config import StreamingConfig, MobileTestConfig
from infra.streaming.streaming_validator import StreamingValidator
from infra.mobile.mobile_session import MobileSession

from infra.mobile.screens.welcome_screen import WelcomeScreen
from infra.mobile.screens.login_screen import LoginScreen
from infra.mobile.screens.live_stream_screen import LiveStreamScreen

from typing import Generator


def pytest_configure(config) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    metadata = getattr(config, "metadata", None)
    if metadata:
        metadata.update(
            {
                "Project": "Nanit Home Assignment",
                "Executor": "Pytest",
                "Environment": "Local",
                "StreamingBackend": "http://localhost:8082",
            }
        )


@pytest.fixture(scope="session")
def streaming_config() -> StreamingConfig:
    return StreamingConfig()


@pytest.fixture(scope="session")
def mobile_config() -> MobileTestConfig:
    return MobileTestConfig()


@pytest.fixture(scope="function")
def streaming_validator(
    streaming_config: StreamingConfig,
) -> StreamingValidator:
    return StreamingValidator(config=streaming_config)


@pytest.fixture(scope="function")
def mobile_session(
    mobile_config: MobileTestConfig,
) -> Generator[MobileSession, None, None]:
    session = MobileSession(platform=mobile_config.platform)
    session.launch_app()
    yield session
    session.close()


@pytest.fixture(scope="function")
def welcome_screen(mobile_session: MobileSession) -> WelcomeScreen:
    return WelcomeScreen(mobile_session)


@pytest.fixture(scope="function")
def login_screen(mobile_session: MobileSession) -> LoginScreen:
    return LoginScreen(mobile_session)


@pytest.fixture(scope="function")
def live_stream_screen(mobile_session: MobileSession) -> LiveStreamScreen:
    return LiveStreamScreen(mobile_session)
