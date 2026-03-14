import mesop as me

import capture_log
import starter
import state_loading


__all__ = ["capture_log", "starter", "state_loading"]


@me.page(path="/")
def home():
    me.navigate("/starter_kit")
