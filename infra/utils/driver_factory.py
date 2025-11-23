from appium import webdriver
from appium.options.android import UiAutomator2Options
from config import Config


class DriverFactory:
    @staticmethod
    def get_driver():
        options = UiAutomator2Options()
        options.platform_name = Config.PLATFORM_NAME
        options.device_name = Config.DEVICE_NAME
        options.app_package = Config.APP_PACKAGE
        options.app_activity = Config.APP_ACTIVITY
        options.automation_name = Config.AUTOMATION_NAME
        options.no_reset = True  # Don't reset app state

        driver = webdriver.Remote(
            Config.APPIUM_SERVER,
            options=options
        )
        driver.implicitly_wait(Config.IMPLICIT_WAIT)
        return driver