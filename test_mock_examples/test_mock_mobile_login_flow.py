from __future__ import annotations

def test_mock_mobile_login_flow(mobile_session, mobile_config,
                                welcome_screen, login_screen, live_stream_screen):

    assert mobile_session.get_current_screen() == "welcome"

    welcome_screen.tap_login()
    assert mobile_session.get_current_screen() == "login"

    login_screen.login(mobile_config.username, mobile_config.password)
    assert mobile_session.is_logged_in()

    assert live_stream_screen.is_loaded()

