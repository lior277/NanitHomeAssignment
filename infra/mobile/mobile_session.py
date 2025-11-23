"""Mocked mobile session implementation.

This module provides :class:`MobileSession`, a lightweight state machine that
simulates a mobile app driver session (no real Appium calls). It supports both
normal mode and FAST_MODE for accelerating tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import os

LOGGER = logging.getLogger(__name__)


@dataclass
class MobileSession:  # pylint: disable=too-few-public-methods
    """Mocked mobile app session.

    Attributes:
        platform: Target platform, either ``"ios"`` or ``"android"``.
        app_launched: Whether the app has been launched in this session.
        logged_in: Whether the user is considered logged in.
        current_screen: Logical screen name (e.g. ``"welcome"``, ``"login"``,
            ``"live_stream"``).
        fast_mode: When True, simulates navigation without heavy delays.
    """

    platform: str
    app_launched: bool = False
    logged_in: bool = False
    current_screen: str = "welcome"
    fast_mode: bool = field(
        default_factory=lambda: os.getenv("FAST_MODE", "false").lower() == "true",
    )

    def launch_app(self) -> None:
        """Simulate launching the app."""
        LOGGER.info("Launching mock app on platform=%s", self.platform)
        self.app_launched = True
        self.current_screen = "welcome"

    def tap(self, element_id: str) -> None:
        """Simulate tapping a UI element by its identifier."""
        LOGGER.debug(
            "Tap on element '%s' at screen '%s' (fast_mode=%s)",
            element_id,
            self.current_screen,
            self.fast_mode,
        )

        if self.fast_mode:
            LOGGER.debug("FAST_MODE: logical navigation only")
            if self.current_screen == "welcome":
                self.current_screen = "login"
            elif self.current_screen == "login":
                self.logged_in = True
                self.current_screen = "live_stream"
            return

        if self.current_screen == "welcome" and "login_button" in element_id:
            self.current_screen = "login"
            return

        if self.current_screen == "login" and "login_button" in element_id:
            self.logged_in = True
            self.current_screen = "live_stream"

    def enter_text(self, element_id: str, text: str) -> None:
        """Simulate entering text into a field."""
        LOGGER.debug(
            "enter_text on '%s' with value '%s' (fast_mode=%s)",
            element_id,
            text,
            self.fast_mode,
        )

    def get_current_screen(self) -> str:
        """Return the current logical screen name."""
        return self.current_screen

    def is_logged_in(self) -> bool:
        """Return True if the user is considered logged in."""
        return self.logged_in

    def reset(self) -> None:
        """Reset the session state to initial values."""
        LOGGER.info("Resetting mock mobile session")
        self.app_launched = False
        self.logged_in = False
        self.current_screen = "welcome"
