# tests/test_mobile_login.py
"""
Stage 2 – Mock mobile login flow using screen objects.

This covers:
- Mock MobileSession (no Appium, no real devices)
- Page Objects: WelcomeScreen, LoginScreen, LiveStreamScreen
- Setup/teardown via fixture (mobile_session)
- Works alongside API tests in same pytest session
"""

import pytest


@pytest.mark.mobile
def test_mobile_login_happy_path(
    mobile_session,
    welcome_screen,
    login_screen,
    live_stream_screen,
):
    # --- Initial State ---------------------------------------------------------
    assert mobile_session.get_current_screen() == "welcome", \
        "App should launch on the welcome screen"

    # --- Navigate to login -----------------------------------------------------
    welcome_screen.tap_login()
    assert mobile_session.get_current_screen() == "login", \
        "Tapping Login button should move to login screen"

    # --- Perform login ---------------------------------------------------------
    test_email = "demo_app@nanit.com"
    test_password = "12341234"

    login_screen.login(email=test_email, password=test_password)

    # --- Validate login state --------------------------------------------------
    assert mobile_session.is_logged_in() is True, \
        "User should be marked logged in after login"

    # --- Validate navigation to stream screen ----------------------------------
    assert live_stream_screen.is_loaded() is True, \
        "Login should navigate to live stream screen"
