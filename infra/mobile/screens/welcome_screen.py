# infra/mobile/screens/welcome_screen.py
from infra.mobile.screens.base_screen import BaseScreen


class WelcomeScreen(BaseScreen):
    """Welcome screen actions."""

    def tap_login(self) -> None:
        # Use logical element name
        self.session.tap("welcome_login_button")
