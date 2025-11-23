"""Mocked mobile driver session used for the Nanit assignment.

This class simulates a minimal Appium-like session without real devices.
It is intentionally simple and state-based for test design purposes.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MobileSession:
    """Mock session that simulates a mobile app driver."""

    platform: str  # "ios" or "android"
    app_launched: bool = False
    logged_in: bool = False
    current_screen: str = "welcome"
    fast_mode: bool = False

    def __post_init__(self) -> None:
        """Initialize FAST_MODE from environment."""
        self.fast_mode = os.getenv("FAST_MODE", "false").lower() == "true"
        if self.fast_mode:
            logger.warning(
                "FAST_MODE enabled for MobileSession on platform %s",
                self.platform,
            )

    def launch_app(self) -> None:
        """Simulate launching the Nanit app."""
        self.app_launched = True
        self.current_screen = "welcome"
        logger.info("App launched on platform %s", self.platform)

    def tap(self, element_id: str) -> None:
        """Simulate tapping an element by id."""
        logger.info(
            "Tap on element %s in screen %s",
            element_id,
            self.current_screen,
        )

        if self.fast_mode:
            logger.warning(
                "FAST_MODE: tap() shortcut enabled on screen %s",
                self.current_screen,
            )

        if self.current_screen == "welcome" and "login_button" in element_id:
            self.current_screen = "login"
            logger.debug("Navigated to login screen")
        elif self.current_screen == "login" and "login_button" in element_id:
            self.logged_in = True
            self.current_screen = "live_stream"
            logger.debug("Login simulated, navigated to live_stream screen")

    def enter_text(self, element_id: str, text: str) -> None:
        """Simulate entering text into an input."""
        logger.debug(
            "Enter text into %s on screen %s",
            element_id,
            self.current_screen,
        )
        # No-op in mock session

    def get_current_screen(self) -> str:
        """Return logical current screen."""
        return self.current_screen

    def is_logged_in(self) -> bool:
        """Return whether the user is considered logged in."""
        return self.logged_in
