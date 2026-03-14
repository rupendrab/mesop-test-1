import time
import asyncio

import mesop as me

from app_shell import render_app_shell


async def slow_blocking_api_call():
    await asyncio.sleep(2)
    return "API call complete!"


@me.stateclass
class State:
    data: str
    is_loading: bool


async def button_click(event: me.ClickEvent):
    state = me.state(State)
    state.is_loading = True
    yield
    data = await slow_blocking_api_call()
    state.data = data
    state.is_loading = False
    yield


def page_content():
    state = me.state(State)
    with me.box(
        style=me.Style(
            padding=me.Padding.all(24),
            background="#f8fafc",
            min_height="100vh",
            box_sizing="border-box",
        )
    ):
        me.text(
            "Loading",
            type="headline-4",
            style=me.Style(margin=me.Margin(bottom=12)),
        )
        if state.is_loading:
            me.progress_spinner()
        me.text(state.data)
        me.button("Call API", on_click=button_click)


@me.page(path="/loading")
def main():
    render_app_shell("loading", page_content)
