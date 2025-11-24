from __future__ import annotations

import pytest

from config.config import MobileTestConfig
from infra.mobile.screens.live_stream_screen import LiveStreamScreen
from infra.mobile.screens.login_screen import LoginScreen
from infra.mobile.screens.welcome_screen import WelcomeScreen
from infra.streaming.streaming_validator import StreamingValidator
from infra.mobile.mobile_session import MobileSession


@pytest.mark.e2e
@pytest.mark.streaming
@pytest.mark.mobile
def test_e2e_login_and_stream_quality_degradation(
    streaming_validator: StreamingValidator,
    mobile_session: MobileSession,
    welcome_screen: WelcomeScreen,
    login_screen: LoginScreen,
    live_stream_screen: LiveStreamScreen,
    mobile_config: MobileTestConfig,
) -> None:

    # --- Streaming baseline ---
    streaming_validator.set_network_condition("normal")
    normal_latency = streaming_validator.get_latency_ms()
    manifest = streaming_validator.get_manifest()
    assert "#EXTM3U" in manifest

    # --- Mobile navigation ---
    assert mobile_session.get_current_screen() == "welcome"

    welcome_screen.tap_login()
    assert mobile_session.get_current_screen() == "login"

    login_screen.login(
        email=mobile_config.username,
        password=mobile_config.password,
    )

    # Logged in + navigated to live screen
    assert mobile_session.is_logged_in() is True
    assert live_stream_screen.is_loaded() is True

    # --- Degradation test ---
    streaming_validator.set_network_condition("poor")
    poor_latency = streaming_validator.get_latency_ms()

    assert poor_latency > normal_latency, (
        f"Expected latency under poor network to exceed normal. "
        f"normal={normal_latency}, poor={poor_latency}"
    )
