# infra/mobile/screens/live_stream_screen.py
from infra.mobile.screens.base_screen import BaseScreen


class LiveStreamScreen(BaseScreen):
    """Live stream page object."""

    def is_loaded(self) -> bool:
        return self.session.get_current_screen() == "live_stream"
