class Config:
    APPIUM_SERVER = "http://127.0.0.1:4723"

    PLATFORM_NAME = "Android"
    # config/config.py
    UDID = "192.168.1.206:44421"

    DEVICE_NAME = "Pixel"  # label only

    APP_PACKAGE = "com.google.android.apps.tasks"
    APP_ACTIVITY = "com.google.android.apps.tasks.ui.TaskListsActivity"
    AUTOMATION_NAME = "UiAutomator2"

    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 20
