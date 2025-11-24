from __future__ import annotations
import logging

from infra.mobile.elements_resolver import ElementResolver

logger = logging.getLogger(__name__)


class MobileSession:
    """Mock mobile session implementing welcome → login → live_stream flow."""

    def __init__(self, platform: str) -> None:
        self.platform = platform
        self.app_launched = False
        self.logged_in = False
        self.live_stream_active = False
        self.current_screen = "welcome"

        # Resolve logical names → platform-specific IDs
        self.resolver = ElementResolver(platform)

    def launch_app(self) -> None:
        logger.info("Launching app on %s", self.platform)
        self.app_launched = True
        self.current_screen = "welcome"

    def close(self) -> None:
        logger.info("Closing session")
        self.app_launched = False
        self.logged_in = False
        self.live_stream_active = False
        self.current_screen = "welcome"

    def get_current_screen(self) -> str:
        return self.current_screen

    def is_logged_in(self) -> bool:
        return self.logged_in

    def enter_text(self, logical_name: str, value: str) -> None:
        resolved = self.resolver.locator(logical_name)
        logger.info("Enter text into %s = %s", resolved, value)

    def tap(self, logical_name: str) -> None:
        """Resolve element + route to correct handler based on active screen."""
        resolved = self.resolver.locator(logical_name)
        logger.info("Tap: %s (resolved=%s)", logical_name, resolved)

        handlers = {
            "welcome": self._handle_welcome,
            "login": self._handle_login,
            "live_stream": self._handle_stream,
        }

        handler = handlers.get(self.current_screen)
        if handler is not None:
            return handler(logical_name)

        logger.warning(
            "No handler for tap '%s' on screen '%s'",
            logical_name,
            self.current_screen,
        )
        return None

    def _handle_welcome(self, name: str) -> None:
        if name == "welcome_login_button":
            self.go_to_login()
            return

        logger.warning("Unhandled welcome action: %s", name)

    def _handle_login(self, name: str) -> None:
        if name == "submit_login":
            self._submit_login()
            return

        logger.warning("Unhandled login action: %s", name)

    def _handle_stream(self, name: str) -> None:
        if name == "start_stream":
            self.start_live_stream()
            return

        if name == "stop_stream":
            self.stop_live_stream()
            return

        logger.warning("Unhandled stream action: %s", name)

    def go_to_login(self) -> None:
        if not self.app_launched:
            raise RuntimeError("Cannot navigate: app not launched")
        logger.info("→ welcome → login")
        self.current_screen = "login"

    def enter_dashboard(self) -> None:
        if not self.logged_in:
            raise RuntimeError("Cannot enter dashboard: not logged in")
        logger.info("→ login → live_stream")
        self.current_screen = "live_stream"

    def _submit_login(self) -> None:
        logger.info("Submitting login")
        self.logged_in = True
        self.enter_dashboard()

    def start_live_stream(self) -> None:
        if not self.logged_in:
            raise RuntimeError("Cannot start stream: user not logged in")
        logger.info("Live stream started")
        self.live_stream_active = True
        self.current_screen = "live_stream"

    def stop_live_stream(self) -> None:
        logger.info("Live stream stopped")
        self.live_stream_active = False
