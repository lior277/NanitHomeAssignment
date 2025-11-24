# infra/mobile/screens/login_screen.py
from infra.mobile.screens.base_screen import BaseScreen


class LoginScreen(BaseScreen):
    """Login screen actions."""

    def login(self, email: str, password: str) -> None:
        self.session.enter_text("email_input", email)
        self.session.enter_text("password_input", password)
        self.session.tap("submit_login")
