"""
MobileSession - Mock Appium driver session for Stage 2

This is a MOCK implementation - does not use real Appium or devices.
The goal is to demonstrate design patterns and architecture for mobile testing.
"""

import logging
import time
from typing import Dict, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported mobile platforms"""
    IOS = "iOS"
    ANDROID = "Android"


class MobileSession:
    """
    Mock mobile session that simulates an Appium driver

    This class simulates mobile app interactions without requiring
    real devices, emulators, or Appium server.
    """

    def __init__(self, platform: str = "Android", app_name: str = "Nanit"):
        """
        Initialize mock mobile session

        Args:
            platform: Platform name (iOS or Android)
            app_name: Application name
        """
        self.platform = Platform.ANDROID if platform == "Android" else Platform.IOS
        self.app_name = app_name
        self.current_screen = None
        self.is_app_launched = False
        self.session_id = f"mock_session_{int(time.time())}"

        # Simulated state
        self.logged_in = False
        self.current_user = None

        logger.info(f"Mock MobileSession created: platform={self.platform.value}, app={app_name}")

    def launch_app(self) -> bool:
        """
        Launch the mobile application

        Returns:
            bool: True if app launched successfully
        """
        logger.info(f"Launching {self.app_name} app...")
        time.sleep(0.1)  # Simulate launch delay

        self.is_app_launched = True
        self.current_screen = "welcome"

        logger.info(f"✓ {self.app_name} app launched successfully")
        logger.info(f"  Current screen: {self.current_screen}")

        return True

    def is_element_visible(self, element_id: str) -> bool:
        """
        Check if an element is visible on current screen

        Args:
            element_id: Element identifier

        Returns:
            bool: True if element is visible
        """
        # Simulate element visibility based on current screen and platform
        screen_elements = self._get_screen_elements()

        is_visible = element_id in screen_elements
        logger.info(f"Element '{element_id}' visible: {is_visible}")

        return is_visible

    def click(self, element_id: str) -> bool:
        """
        Click on an element

        Args:
            element_id: Element identifier

        Returns:
            bool: True if click was successful
        """
        if not self.is_element_visible(element_id):
            logger.warning(f"Cannot click: Element '{element_id}' not visible")
            return False

        logger.info(f"Clicking on: {element_id}")
        time.sleep(0.05)  # Simulate click delay

        # Simulate navigation based on element clicked
        self._handle_navigation(element_id)

        logger.info(f"✓ Clicked successfully")
        return True

    def send_keys(self, element_id: str, text: str) -> bool:
        """
        Send text to an input element

        Args:
            element_id: Element identifier
            text: Text to send

        Returns:
            bool: True if text was sent successfully
        """
        if not self.is_element_visible(element_id):
            logger.warning(f"Cannot send keys: Element '{element_id}' not visible")
            return False

        logger.info(f"Sending keys to '{element_id}': {text}")
        time.sleep(0.05)  # Simulate typing delay

        # Store credentials if this is a login field
        if "email" in element_id.lower():
            self.current_user = {"email": text}
        elif "password" in element_id.lower():
            if self.current_user:
                self.current_user["password"] = text

        logger.info(f"✓ Keys sent successfully")
        return True

    def check_checkbox(self, element_id: str) -> bool:
        """
        Check a checkbox element

        Args:
            element_id: Checkbox element identifier

        Returns:
            bool: True if checkbox was checked
        """
        if not self.is_element_visible(element_id):
            logger.warning(f"Cannot check: Checkbox '{element_id}' not visible")
            return False

        logger.info(f"Checking checkbox: {element_id}")
        time.sleep(0.05)

        logger.info(f"✓ Checkbox checked")
        return True

    def get_current_screen(self) -> str:
        """
        Get the current screen name

        Returns:
            str: Current screen identifier
        """
        return self.current_screen

    def login_screen_visible(self) -> bool:
        """
        Check if login screen is visible

        Returns:
            bool: True if on login screen
        """
        return self.current_screen == "login"

    def welcome_screen_visible(self) -> bool:
        """
        Check if welcome screen is visible

        Returns:
            bool: True if on welcome screen
        """
        return self.current_screen == "welcome"

    def live_stream_visible(self) -> bool:
        """
        Check if live stream screen is visible

        Returns:
            bool: True if on live stream screen
        """
        return self.current_screen == "live_stream"

    def perform_login(self, email: str, password: str, accept_terms: bool = True) -> bool:
        """
        Perform complete login flow

        Args:
            email: User email
            password: User password
            accept_terms: Whether to accept terms and conditions

        Returns:
            bool: True if login successful
        """
        logger.info(f"Performing login for: {email}")

        # Navigate to login screen if needed
        if self.current_screen == "welcome":
            login_button = self._get_element_id("login_button")
            self.click(login_button)

        # Fill in credentials
        email_input = self._get_element_id("email_input")
        password_input = self._get_element_id("password_input")

        self.send_keys(email_input, email)
        self.send_keys(password_input, password)

        # Accept terms if needed
        if accept_terms:
            terms_checkbox = self._get_element_id("terms_and_conditions_check_box")
            self.check_checkbox(terms_checkbox)

        # Click login button
        login_button = self._get_element_id("login_button")
        self.click(login_button)

        # Simulate login processing
        time.sleep(0.2)

        # Check if credentials are valid
        if email == "demo_app@nanit.com" and password == "12341234":
            self.logged_in = True
            self.current_screen = "live_stream"
            logger.info("✓ Login successful")
            return True
        else:
            logger.warning("✗ Login failed: Invalid credentials")
            return False

    def get_stream_status(self) -> str:
        """
        Get the current stream status

        Returns:
            str: Stream status (e.g., "streaming", "offline")
        """
        if self.current_screen == "live_stream" and self.logged_in:
            return "streaming"
        return "offline"

    def quit(self):
        """Close the mobile session"""
        logger.info(f"Closing mock mobile session: {self.session_id}")
        self.is_app_launched = False
        self.current_screen = None
        self.logged_in = False

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _get_element_id(self, base_name: str) -> str:
        """
        Get platform-specific element ID

        Args:
            base_name: Base element name

        Returns:
            str: Platform-specific element ID
        """
        suffix = "_ios" if self.platform == Platform.IOS else "_android"
        return f"{base_name}{suffix}"

    def _get_screen_elements(self) -> list:
        """
        Get list of visible elements for current screen

        Returns:
            list: Element IDs visible on current screen
        """
        elements_map = {
            "welcome": [
                self._get_element_id("login_button")
            ],
            "login": [
                self._get_element_id("email_input"),
                self._get_element_id("password_input"),
                self._get_element_id("login_button"),
                self._get_element_id("terms_and_conditions_check_box")
            ],
            "live_stream": [
                self._get_element_id("live_stream_container"),
                self._get_element_id("stream_status_label")
            ]
        }

        return elements_map.get(self.current_screen, [])

    def _handle_navigation(self, element_id: str):
        """
        Handle screen navigation based on element clicked

        Args:
            element_id: Element that was clicked
        """
        # Welcome screen -> Login screen
        if self.current_screen == "welcome" and "login_button" in element_id:
            self.current_screen = "login"
            logger.info(f"  Navigated to: {self.current_screen}")

        # Login screen -> Live stream (if logged in)
        elif self.current_screen == "login" and "login_button" in element_id:
            if self.logged_in or (self.current_user and
                                  self.current_user.get("email") == "demo_app@nanit.com"):
                self.current_screen = "live_stream"
                self.logged_in = True
                logger.info(f"  Navigated to: {self.current_screen}")

    def __repr__(self) -> str:
        """String representation"""
        return (f"MobileSession(platform={self.platform.value}, "
                f"app={self.app_name}, "
                f"screen={self.current_screen}, "
                f"logged_in={self.logged_in})")