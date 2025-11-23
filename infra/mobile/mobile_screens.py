from infra.mobile.mobile_session import MobileSession
from infra.mobile.mobile_elements import MOBILE_ELEMENTS


class WelcomeScreen:
    def __init__(self, session: MobileSession):
        self.session = session

    def tap_login(self):
        element = MOBILE_ELEMENTS["welcome_login_button"][self.session.platform]
        self.session.tap(element)


class LoginScreen:
    def __init__(self, session: MobileSession):
        self.session = session

    def login(self, email: str, password: str):
        self.session.enter_text(
            MOBILE_ELEMENTS["email_input"][self.session.platform],
            email
        )
        self.session.enter_text(
            MOBILE_ELEMENTS["password_input"][self.session.platform],
            password
        )
        self.session.tap(
            MOBILE_ELEMENTS["submit_login"][self.session.platform]
        )


class LiveStreamScreen:
    def __init__(self, session: MobileSession):
        self.session = session

    def is_loaded(self) -> bool:
        return self.session.get_current_screen() == "live_stream"
