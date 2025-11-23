# tests/test_e2e_stream_mobile.py
"""
End-to-end style test combining:
- Streaming API layer (StreamingValidator)
- Mock mobile layer (MobileSession + screen objects)

Flow:
1. Ensure streaming is healthy under normal network.
2. Perform mobile login (welcome -> login -> live stream).
3. Switch network to 'poor' and validate that streaming latency degrades.
"""

import pytest


@pytest.mark.e2e
@pytest.mark.streaming
@pytest.mark.mobile
def test_e2e_login_and_stream_quality_degradation(
    streaming_validator,
    mobile_session,
    welcome_screen,
    login_screen,
    live_stream_screen,
    mobile_config,  # <-- injected from fixture (MobileTestConfig)
):
    v = streaming_validator

    # --- Step 1: Start with normal network on the streaming side ---------------
    v.set_network_condition("normal")
    normal_latency = v.get_latency_ms()
    manifest = v.get_manifest()
    assert "#EXTM3U" in manifest, "Streaming manifest should be available under normal network"

    # --- Step 2: Mobile login flow (welcome -> login -> live stream) ----------
    assert mobile_session.get_current_screen() == "welcome", \
        "App should initially be on the welcome screen"

    welcome_screen.tap_login()
    assert mobile_session.get_current_screen() == "login", \
        "Tapping login from welcome should navigate to login screen"

    # Use credentials from config instead of hard-coded values
    login_screen.login(
        email=mobile_config.username,
        password=mobile_config.password,
    )

    assert mobile_session.is_logged_in() is True, \
        "User should be logged in after submitting correct credentials"
    assert live_stream_screen.is_loaded() is True, \
        "After login, the live stream screen should be considered loaded"

    # --- Step 3: Degrade network and verify streaming quality worsens ---------
    v.set_network_condition("poor")
    poor_latency = v.get_latency_ms()

    assert poor_latency > normal_latency, (
        f"Expected higher latency under 'poor' network. "
        f"Got normal={normal_latency} ms, poor={poor_latency} ms"
    )
