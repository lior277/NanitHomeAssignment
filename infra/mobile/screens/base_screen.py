# infra/mobile/screens/base_screen.py
from infra.mobile.mobile_session import MobileSession


class BaseScreen:
    def __init__(self, session: MobileSession) -> None:
        self.session = session
