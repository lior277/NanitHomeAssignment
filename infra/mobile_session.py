from dataclasses import dataclass


@dataclass
class MobileSession:
    """Mocked session that simulates a mobile app test driver.
    No real Appium calls—purely a fake state machine.
    """

    platform: str  # "ios" or "android"
    app_launched: bool = False
    logged_in: bool = False
    current_screen: str = "welcome"

    def launch_app(self):
        self.app_launched = True
        self.current_screen = "welcome"

    def tap(self, element_id: str):
        if self.current_screen == "welcome" and "login_button" in element_id:
            self.current_screen = "login"
        elif self.current_screen == "login" and "login_button" in element_id:
            self.logged_in = True
            self.current_screen = "live_stream"

    def enter_text(self, element_id: str, text: str):
        pass  # no-op mock

    def get_current_screen(self) -> str:
        return self.current_screen

    def is_logged_in(self) -> bool:
        return self.logged_in
