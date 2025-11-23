"""
Cross-platform mobile element locator mapping.

This file holds a unified selector dictionary used by the mocked MobileSession and
screen objects. In a real project, this would map to platform-specific accessibility
identifiers, resource IDs, or XPath selectors.
"""

from __future__ import annotations
from typing import Dict


# Central lookup table used by screen objects
MOBILE_ELEMENTS = {
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


def get_selector(element_name: str, platform: str) -> str:
    """
    Return the platform-specific selector from MOBILE_ELEMENTS.

    Args:
        element_name: logical key, e.g. "email_input"
        platform: mobile platform ("ios" | "android")

    Returns:
        str: The selector string for this element/platform.

    Raises:
        KeyError: If the element or platform is not defined.
    """
    platform = platform.lower()

    if element_name not in MOBILE_ELEMENTS:
        raise KeyError(f"Unknown element key: {element_name}")

    if platform not in MOBILE_ELEMENTS[element_name]:
        raise KeyError(
            f"Platform '{platform}' not supported for element '{element_name}'."
        )

    return MOBILE_ELEMENTS[element_name][platform]
