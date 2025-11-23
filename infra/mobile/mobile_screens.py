"""Mock mobile screen objects.

These page objects sit on top of :class:`MobileSession` and use
``MOBILE_ELEMENTS`` to resolve platform-specific element identifiers.
"""

from __future__ import annotations

from infra.mobile.mobile_session import MobileSession
from infra.mobile.mobile_elements import MOBILE_ELEMENTS


class WelcomeScreen:  # pylint: disable=too-few-public-methods
    """Welcome screen page object."""

    def __init__(self, session: MobileSession) -> None:
        """Create a welcome screen bound to a mobile session."""
        self.session = session

    def tap_login(self) -> None:
        """Tap the login button to navigate to the login screen."""
        element = MOBILE_ELEMENTS["welcome_login_button"][self.session.platform]
        self.session.tap(element)


class LoginScreen:  # pylint: disable=too-few-public-methods
    """Login screen page object."""

    def __init__(self, session: MobileSession) -> None:
        """Create a login screen bound to a mobile session."""
        self.session = session

    def login(self, email: str, password: str) -> None:
        """Enter credentials and submit the login form."""
        email_id = MOBILE_ELEMENTS["email_input"][self.session.platform]
        password_id = MOBILE_ELEMENTS["password_input"][self.session.platform]
        submit_id = MOBILE_ELEMENTS["submit_login"][self.session.platform]

        self.session.enter_text(email_id, email)
        self.session.enter_text(password_id, password)
        self.session.tap(submit_id)


class LiveStreamScreen:  # pylint: disable=too-few-public-methods
    """Live stream screen page object."""

    def __init__(self, session: MobileSession) -> None:
        """Create a live stream screen bound to a mobile session."""
        self.session = session

    def is_loaded(self) -> bool:
        """Return True when the live stream screen is logically active."""
        return self.session.get_current_screen() == "live_stream"
