def test_mobile_login(welcome_screen, login_screen, mobile_session):
    # Ensure starting point
    assert mobile_session.get_current_screen() == "welcome"

    welcome_screen.tap_login()
    assert mobile_session.get_current_screen() == "login"

    login_screen.login("demo@nanit.com", "1234")

    assert mobile_session.is_logged_in() is True
    assert mobile_session.get_current_screen() == "live_stream"
