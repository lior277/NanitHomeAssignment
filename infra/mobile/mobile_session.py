from dataclasses import dataclass, field
import os
import logging

logger = logging.getLogger(__name__)

@dataclass
class MobileSession:
    """
    Mocked mobile test session (no real Appium).
    FAST_MODE skips heavy logic but preserves navigation state.
    """

    platform: str
    app_launched: bool = False
    logged_in: bool = False
    current_screen: str = "welcome"
    fast_mode: bool = field(default_factory=lambda: os.getenv("FAST_MODE", "false").lower() == "true")

    def launch_app(self):
        logger.info(f"Launching mock app on platform={self.platform}")
        self.app_launched = True
        self.current_screen = "welcome"

    def tap(self, element_id: str):
        logger.debug(f"Tap: {element_id} on {self.current_screen}")

        # ---------- FAST MODE (simulate flow) ----------
        if self.fast_mode:
            logger.debug("FAST_MODE: logical navigation only")
            if self.current_screen == "welcome":
                self.current_screen = "login"
            elif self.current_screen == "login":
                self.logged_in = True
                self.current_screen = "live_stream"
            return

        # ---------- REAL MODE ----------
        if self.current_screen == "welcome" and "login_button" in element_id:
            self.current_screen = "login"

        elif self.current_screen == "login" and "login_button" in element_id:
            self.logged_in = True
            self.current_screen = "live_stream"

    def enter_text(self, element_id: str, text: str):
        logger.debug(f"enter_text: {element_id}='{text}' (fast_mode={self.fast_mode})")

    def get_current_screen(self) -> str:
        return self.current_screen

    def is_logged_in(self) -> bool:
        return self.logged_in

    def reset(self):
        logger.info("Resetting mock mobile session")
        self.app_launched = False
        self.logged_in = False
        self.current_screen = "welcome"
