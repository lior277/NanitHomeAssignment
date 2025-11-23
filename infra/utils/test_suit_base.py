import logging
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from config.config import Config

PKG = "com.google.android.apps.tasks"
ACT = "com.google.android.apps.tasks.ui.TaskListsActivity"  # adjust if resolve-activity shows different

class TestSuitBase:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    @staticmethod
    def get_mobile_driver_options() -> UiAutomator2Options:
        opts = UiAutomator2Options()
        # Required caps (Appium v2+ uses appium: vendor prefix)
        opts.set_capability("platformName", Config.PLATFORM_NAME)
        opts.set_capability("appium:automationName", Config.AUTOMATION_NAME)
        opts.set_capability("appium:udid", Config.UDID)

        # App under test + launch waits
        opts.set_capability("appium:appPackage", PKG)
        opts.set_capability("appium:appActivity", ACT)
        opts.set_capability("appium:appWaitActivity", "com.google.android.apps.tasks.*")
        opts.set_capability("appium:appWaitForLaunch", True)
        opts.set_capability("appium:appWaitDuration", 20000)

        # QoL
        opts.set_capability("appium:noReset", True)
        opts.set_capability("appium:autoGrantPermissions", True)
        opts.set_capability("appium:newCommandTimeout", 300)
        opts.set_capability("appium:adbExecTimeout", 120000)
        return opts

    @staticmethod
    def get_driver() -> webdriver.Remote:
        """Create and return an Appium WebDriver."""
        options = TestSuitBase.get_mobile_driver_options()
        driver = webdriver.Remote(Config.APPIUM_SERVER, options=options)  # no /wd/hub
        driver.implicitly_wait(Config.IMPLICIT_WAIT)
        return driver

    @staticmethod
    def ensure_app_launched(driver, timeout: int = 15) -> None:
        """Bring the app to foreground and wait until focused."""
        try:
            driver.activate_app(PKG)
            driver.start_activity(app_package=PKG, app_activity=ACT)
        except Exception:
            # ignore; some devices already on the activity
            pass
        WebDriverWait(driver, timeout).until(lambda d: d.current_package == PKG)
        TestSuitBase.logger.info("Launched %s / %s", PKG, getattr(driver, "current_activity", "<unknown>"))

    @staticmethod
    def driver_dispose(driver: webdriver.Remote | None = None) -> None:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                TestSuitBase.logger.error("Error disposing driver: %s", e)
