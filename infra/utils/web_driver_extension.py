"""
Mobile Driver Extension - Element interaction utilities
Converted from web DriverEX pattern to mobile automation
"""
from time import sleep
from typing import Any, List, Optional, Tuple

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    ElementNotVisibleException,  # kept for backward compat; may be absent in some selenium builds
    ElementNotSelectableException,
    InvalidSelectorException,
    NoSuchFrameException,
    WebDriverException,
    TimeoutException,
)

from appium.webdriver.common.appiumby import AppiumBy
from config import Config


def ignore_exception_types():
    # Broad but safe ignore list for polling; we still surface the last exception on timeout
    return [
        NoSuchElementException,
        ElementNotInteractableException,
        ElementNotVisibleException,
        ElementNotSelectableException,
        InvalidSelectorException,
        NoSuchFrameException,
        WebDriverException,
        StaleElementReferenceException
    ]


# ---------- Internal mobile helpers (kept private; API unchanged) ----------

def _screen_size(driver) -> Tuple[int, int]:
    size = driver.get_window_size()
    return size["width"], size["height"]


def _scroll_gesture(driver, direction: str = "down", percent: float = 0.8) -> bool:
    """
    Best-effort scroll using W3C mobile gesture with fallback to deprecated driver.swipe.
    """
    try:
        w, h = _screen_size(driver)
        # use near-fullscreen rect for scroll
        rect = {"left": 0, "top": 0, "width": w, "height": h}
        return bool(driver.execute_script(
            "mobile: scrollGesture",
            {"elementId": None, **rect, "direction": direction, "percent": percent}
        ))
    except Exception:
        # Fallback to swipe if driver doesn't support scrollGesture
        try:
            start_x = w // 2
            if direction.lower() == "down":
                start_y, end_y = int(h * 0.8), int(h * 0.2)
            else:
                start_y, end_y = int(h * 0.2), int(h * 0.8)
            driver.swipe(start_x, start_y, start_x, end_y, 800)
            return True
        except Exception:
            return False


def _click_gesture(driver, element: WebElement) -> bool:
    """
    Try a low-level tap if normal click gets intercepted.
    """
    try:
        driver.execute_script("mobile: clickGesture", {"elementId": element.id})
        return True
    except Exception:
        try:
            element.click()
            return True
        except Exception:
            return False


# ---------- Waitable callables (unchanged public names) ----------

class SearchElement:
    def __init__(self, by: tuple):
        self.by = by
        self.last_exception = None

    def __call__(self, driver) -> Optional[WebElement]:
        try:
            element = driver.find_element(*self.by)
            if element is not None:
                # Some widgets return True for enabled but are off-screen; try to ensure displayed
                if element.is_displayed() and element.is_enabled():
                    return element
            return None
        except StaleElementReferenceException:
            sleep(0.3)
            return None
        except Exception as e:
            self.last_exception = e
            return None


class SearchElements:
    def __init__(self, by: tuple):
        self.by = by
        self.last_exception = None
        self.elements_found = False

    def __call__(self, driver) -> Optional[List[WebElement]]:
        try:
            elements = driver.find_elements(*self.by)
            self.elements_found = True
            return elements
        except StaleElementReferenceException:
            sleep(0.3)
            self.last_exception = Exception(
                f"StaleElementReferenceException when finding elements with locator: {self.by}"
            )
            return None
        except Exception as e:
            self.last_exception = Exception(f"Error in SearchElements: {str(e)} for locator: {self.by}")
            return None


class ScrollToElement:
    def __init__(self, by: tuple = None, text: str = None):
        self.by = by
        self.text = text
        self.last_exception = None

    def __call__(self, driver) -> Any:
        try:
            # 1) Text-based fast path via UiAutomator selector
            if self.text:
                try:
                    driver.find_element(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(text("{self.text}"))'
                    )
                    sleep(0.3)
                    return True
                except Exception:
                    # Fallback: repeated scroll-then-find cycles
                    for _ in range(6):
                        _scroll_gesture(driver, "down", 0.85)
                        sleep(0.2)
                        try:
                            el = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'text("{self.text}")')
                            if el.is_displayed():
                                return el
                        except Exception:
                            pass
                    return None

            # 2) Locator-based: try simple find, else scroll until found or exhausted
            if self.by:
                try:
                    el = driver.find_element(*self.by)
                    if el.is_displayed():
                        return el
                except Exception:
                    pass

                for _ in range(6):
                    _scroll_gesture(driver, "down", 0.85)
                    sleep(0.2)
                    try:
                        el = driver.find_element(*self.by)
                        if el.is_displayed():
                            return el
                    except Exception:
                        continue
            return None
        except Exception as e:
            self.last_exception = e
            return None


class ForceClick:
    def __init__(self, by: tuple = None, element: WebElement = None):
        self.by = by
        self.element = element
        self.last_exception = None

    def __call__(self, driver) -> Optional[WebElement]:
        try:
            if self.element is not None:
                element = self.element
            elif self.by is not None:
                element = driver.find_element(*self.by)
            else:
                raise ValueError("Either 'by' or 'element' must be provided.")

            if not (element.is_displayed() and element.is_enabled()):
                # Try to bring it into view
                if self.by:
                    ScrollToElement(self.by)(driver)
                else:
                    _scroll_gesture(driver, "down", 0.85)
                sleep(0.2)

            try:
                element.click()
            except ElementClickInterceptedException:
                # Scroll a bit and retry
                if self.by:
                    ScrollToElement(self.by)(driver)
                _click_gesture(driver, element)

            return element

        except StaleElementReferenceException:
            sleep(0.3)
            return None
        except ElementClickInterceptedException:
            try:
                if self.by:
                    el = driver.find_element(*self.by)
                    if _click_gesture(driver, el):
                        return el
            except Exception:
                pass
            return None
        except Exception as e:
            self.last_exception = e
            return None


class GetElementText:
    def __init__(self, by: tuple):
        self.by = by
        self.last_exception = None

    def __call__(self, driver) -> str:
        try:
            element = driver.find_element(*self.by)
            # Prefer text attribute; fallback to content-desc for accessibility labels
            text = element.text or element.get_attribute("text") or element.get_attribute("content-desc") or ""
            return text.strip()
        except StaleElementReferenceException:
            sleep(0.3)
            return ""
        except Exception as e:
            self.last_exception = e
            return ""


class SendKeysAuto:
    def __init__(self, by: tuple, input_text: str):
        self.by = by
        self.input_text = input_text
        self.last_exception = None

    def __call__(self, driver) -> bool:
        try:
            element = DriverEX.search_element(driver, self.by)
            # Sometimes .text is empty while "text" attribute carries value on Android
            existing_text = (element.text or element.get_attribute("text") or "").strip()

            if self.input_text != existing_text:
                # Some OEMs fail on clear(); use fallback sequence if needed
                try:
                    element.clear()
                except Exception:
                    # Select-all & delete (Android keycode: 29=A, 113=CTRL_LEFT, 67=DEL) via actions is complex; keep simple
                    pass
                element.send_keys(self.input_text)
                return False  # returning False means "keep waiting until condition stabilizes"
            return True
        except StaleElementReferenceException:
            sleep(0.1)
            return False
        except Exception as e:
            self.last_exception = e
            return False


class PressKeycode:
    """Mobile-specific: Press Android keycode"""
    def __init__(self, keycode: int):
        self.keycode = keycode
        self.last_exception = None

    def __call__(self, driver) -> bool:
        try:
            # Appium AndroidDriver still supports press_keycode
            driver.press_keycode(self.keycode)
            return True
        except Exception as e:
            self.last_exception = e
            return False


class MobileSwipe:
    """Mobile-specific: Swipe gesture"""
    def __init__(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 800):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.duration = duration
        self.last_exception = None

    def __call__(self, driver) -> bool:
        try:
            # Try modern swipeGesture with distance calculated from coords
            try:
                # Convert to direction + percent if possible; else use fallback swipe
                direction = "down" if self.end_y < self.start_y else "up"
                # emulate by small percent if the vector is tiny; otherwise ~80%
                percent = 0.8
                w, h = _screen_size(driver)
                rect = {"left": 0, "top": 0, "width": w, "height": h}
                driver.execute_script("mobile: swipeGesture", {**rect, "direction": direction, "percent": percent})
                return True
            except Exception:
                driver.swipe(self.start_x, self.start_y, self.end_x, self.end_y, self.duration)
                return True
        except Exception as e:
            self.last_exception = e
            return False


class DriverEX:
    """Mobile automation helper - matches web DriverEX pattern"""

    @staticmethod
    def search_element(driver, by: tuple) -> WebElement:
        """
        Wait for element to be present and interactable
        """
        search = SearchElement(by)
        try:
            return WebDriverWait(
                driver,
                Config.EXPLICIT_WAIT,
                ignored_exceptions=ignore_exception_types()
            ).until(search)
        except TimeoutException:
            if search.last_exception:
                raise search.last_exception
            raise

    @staticmethod
    def send_keys_auto(driver, by: tuple, input_text: str) -> None:
        """
        Send keys to element with automatic retry
        """
        send_keys = SendKeysAuto(by, input_text)
        try:
            WebDriverWait(
                driver,
                Config.EXPLICIT_WAIT,
                ignored_exceptions=ignore_exception_types()
            ).until(send_keys)
        except TimeoutException:
            if send_keys.last_exception:
                raise send_keys.last_exception
            raise

    @staticmethod
    def search_elements(driver, by: tuple, wait_if_empty=False) -> List[WebElement]:
        """
        Find multiple elements
        """
        search = SearchElements(by)

        if not wait_if_empty:
            return driver.find_elements(*by)

        try:
            elements = WebDriverWait(
                driver,
                Config.EXPLICIT_WAIT,
                ignored_exceptions=ignore_exception_types()
            ).until(search)
            return elements if elements is not None else []
        except TimeoutException:
            if search.elements_found:
                return []
            if search.last_exception:
                # Helpful context for debugging locator mismatches
                try:
                    print(f"Detailed error when searching for elements: {str(search.last_exception)}")
                    print(f"Current activity: {getattr(driver, 'current_activity', '<n/a>')}")
                    print(f"Current package: {getattr(driver, 'current_package', '<n/a>')}")
                except Exception:
                    pass
            return []

    @staticmethod
    def force_click(driver, by: tuple = None, element: WebElement = None) -> bool:
        """
        Click on element with wait and retry
        """
        if not by and not element:
            raise ValueError("Either 'by' or 'element' must be provided.")

        click = ForceClick(by, element)
        try:
            el = WebDriverWait(
                driver,
                Config.EXPLICIT_WAIT,
                ignored_exceptions=ignore_exception_types()
            ).until(click)
            return el is not None
        except TimeoutException:
            if click.last_exception:
                raise click.last_exception
            raise

    @staticmethod
    def get_element_text(driver, by: tuple) -> str:
        """
        Get text from element
        """
        get_text = GetElementText(by)
        try:
            return WebDriverWait(
                driver,
                Config.EXPLICIT_WAIT,
                ignored_exceptions=ignore_exception_types()
            ).until(get_text)
        except TimeoutException:
            if get_text.last_exception:
                raise get_text.last_exception
            raise

    @staticmethod
    def scroll_to_element(driver, by: tuple = None, text: str = None) -> Any:
        """
        Scroll to element by locator or text
        """
        scroll = ScrollToElement(by, text)
        try:
            return WebDriverWait(
                driver,
                Config.EXPLICIT_WAIT,
                ignored_exceptions=ignore_exception_types()
            ).until(scroll)
        except TimeoutException:
            if scroll.last_exception:
                raise scroll.last_exception
            raise

    @staticmethod
    def press_keycode(driver, keycode: int) -> bool:
        """
        Press Android keycode (e.g., 66 for Enter, 4 for Back)
        """
        press = PressKeycode(keycode)
        try:
            return WebDriverWait(
                driver,
                Config.EXPLICIT_WAIT,
                ignored_exceptions=ignore_exception_types()
            ).until(press)
        except TimeoutException:
            if press.last_exception:
                raise press.last_exception
            raise

    @staticmethod
    def swipe(driver, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 800) -> bool:
        """
        Perform swipe gesture
        """
        swipe = MobileSwipe(start_x, start_y, end_x, end_y, duration)
        try:
            return WebDriverWait(
                driver,
                Config.EXPLICIT_WAIT,
                ignored_exceptions=ignore_exception_types()
            ).until(swipe)
        except TimeoutException:
            if swipe.last_exception:
                raise swipe.last_exception
            raise
