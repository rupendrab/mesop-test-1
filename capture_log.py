import asyncio
import logging
from collections import deque

import mesop as me


@me.stateclass
class State:
    logs: list[str]
    running: int


class BufferLogHandler(logging.Handler):
    def __init__(self, sink: deque[str], max_lines: int = 200):
        super().__init__()
        self.sink = sink
        self.max_lines = max_lines

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.sink.append(msg)
        while len(self.sink) > self.max_lines:
            self.sink.popleft()


async def long_task():
    for i in range(5):
        logging.info("Processing step %s", i + 1)
        await asyncio.sleep(2)
    logging.info("Done")


def show_logs(lines: list[str]):
    with me.box(
        style=me.Style(
            border=me.Border.all(me.BorderSide(color="#d0d7de", width=1)),
            border_radius=8,
            padding=me.Padding.all(12),
            height=300,
            overflow_y="auto",
            background="#fafafa",
            margin=me.Margin(top=12),
        )
    ):
        for line in lines:
            me.text(
                line,
                style=me.Style(
                    font_family="monospace",
                    font_size=13,
                    margin=me.Margin(bottom=4),
                    white_space="pre-wrap",
                ),
            )

@me.page(path="/logs")
def page():
    state = me.state(State)
    if state.logs is None:
        state.logs = []
    if state.running is None:
        state.running = 0

    me.button("Run", on_click=run_task, disabled=state.running)
    show_logs(state.logs)


async def run_task(e: me.ClickEvent):
    state = me.state(State)
    state.running = 1
    state.logs = []

    sink = deque()
    handler = BufferLogHandler(sink)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    root_logger = logging.getLogger()
    old_level = root_logger.level

    # Make sure INFO logs are not filtered out
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    try:
        task = asyncio.create_task(long_task())

        while not task.done():
            if sink:
                state.logs = list(sink)
                yield
            await asyncio.sleep(0.2)

        await task
        state.logs = list(sink)
        yield
    finally:
        root_logger.removeHandler(handler)
        root_logger.setLevel(old_level)
        state.running = 0
        yield
