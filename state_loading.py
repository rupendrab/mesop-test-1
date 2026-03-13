import time
import asyncio

import mesop as me


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


@me.page(path="/loading")
def main():
  state = me.state(State)
  if state.is_loading:
    me.progress_spinner()
  me.text(state.data)
  me.button("Call API", on_click=button_click)
