# infra/mobile/elements_resolver.py
from infra.mobile.mobile_elements import MOBILE_ELEMENTS


class ElementResolver:
    def __init__(self, platform: str):
        self.platform = platform

    def locator(self, logical_name: str) -> str:
        try:
            return MOBILE_ELEMENTS[logical_name][self.platform]
        except KeyError:
            raise KeyError(f"Unknown locator '{logical_name}' for platform '{self.platform}'")
