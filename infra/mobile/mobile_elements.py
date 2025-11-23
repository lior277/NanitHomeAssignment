"""Cross-platform mobile element locator mapping.

This module defines a central mapping of logical element names to platform
specific identifiers (iOS / Android). In a real project, these would map
to accessibility IDs or resource IDs used by Appium.
"""

from __future__ import annotations

from typing import Dict


MOBILE_ELEMENTS: Dict[str, Dict[str, str]] = {
    "welcome_login_button": {
        "ios": "login_button_ios",
        "android": "login_button_android",
    },
    "email_input": {
        "ios": "email_input_ios",
        "android": "email_input_android",
    },
    "password_input": {
        "ios": "password_input_ios",
        "android": "password_input_android",
    },
    "submit_login": {
        "ios": "login_button_ios",
        "android": "login_button_android",
    },
}
