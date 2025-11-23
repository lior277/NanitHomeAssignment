"""Pytest fixtures for streaming and mobile layers.

This module wires together configuration, streaming validator, and mock mobile
screen objects so that tests can focus on behavior rather than setup.
"""

# pylint: disable=redefined-outer-name

import os
from typing import Generator

import pytest

from config.config import StreamingConfig, MobileTestConfig
from infra.mobile.mobile_session import MobileSession
from infra.mobile.mobile_screens import (
    WelcomeScreen,
    LoginScreen,
    LiveStreamScreen,
)
from infra.streaming.streaming_validator import StreamingValidator


# ==============================
# CONFIG FIXTURES
# ==============================


@pytest.fixture(scope="session")
def streaming_config() -> StreamingConfig:
    """Provide CI-friendly streaming configuration instance."""
    return StreamingConfig()


@pytest.fixture(scope="session")
def mobile_config() -> MobileTestConfig:
    """Provide mobile configuration (credentials + platform)."""
    return MobileTestConfig()


# ==============================
# STREAMING FIXTURES
# ==============================


@pytest.fixture(scope="function")
def streaming_validator(
    streaming_config: StreamingConfig,
) -> StreamingValidator:
    """Create a fresh StreamingValidator per test.

    Function scope helps with future parallelization while reusing the same
    session-level configuration.
    """
    return StreamingValidator(config=streaming_config)


# ==============================
# MOBILE FIXTURES
# ==============================


@pytest.fixture(scope="function")
def mobile_session(
    mobile_config: MobileTestConfig,
) -> Generator[MobileSession, None, None]:
    """Create and manage a mock MobileSession for each test."""
    session = MobileSession(platform=mobile_config.platform)
    session.launch_app()

    yield session

    # Basic teardown/reset – useful if more state is added later
    session.reset()


@pytest.fixture(scope="function")
def welcome_screen(mobile_session: MobileSession) -> WelcomeScreen:
    """Return a WelcomeScreen page object bound to the session."""
    return WelcomeScreen(mobile_session)


@pytest.fixture(scope="function")
def login_screen(mobile_session: MobileSession) -> LoginScreen:
    """Return a LoginScreen page object bound to the session."""
    return LoginScreen(mobile_session)


@pytest.fixture(scope="function")
def live_stream_screen(mobile_session: MobileSession) -> LiveStreamScreen:
    """Return a LiveStreamScreen page object bound to the session."""
    return LiveStreamScreen(mobile_session)


def pytest_configure(config: pytest.Config) -> None:
    """Extend HTML report metadata when pytest-metadata plugin is available."""
    metadata = getattr(config, "metadata", None)
    if metadata is not None:
        metadata.update(
            {
                "Project": "Nanit Home Assignment",
                "Executor": "Pytest",
                "FastMode": os.getenv("FAST_MODE", "false"),
            },
        )
