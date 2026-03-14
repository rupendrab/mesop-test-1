import asyncio
import logging
from collections import deque

import mesop as me

from app_shell import render_app_shell


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
    for i in range(20):
        logging.info("Processing step %s", i + 1)
        await asyncio.sleep(2)
    logging.info("Done")


def show_logs(lines: list[str]):
    with me.box(
        style=me.Style(
            border=me.Border.all(me.BorderSide(color="#4d98e4", width=1)),
            border_radius=8,
            padding=me.Padding.all(12),
            height=300,
            overflow_y="auto",
            background="#b6d4f3",
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


def logging_content(state: State):
    with me.box(
        style=me.Style(
            padding=me.Padding.all(24),
            background="#f8fafc",
            min_height="100vh",
            box_sizing="border-box",
        )
    ):
        me.text(
            "Logging",
            type="headline-4",
            style=me.Style(margin=me.Margin(bottom=12)),
        )
        me.button("Run", on_click=run_task, disabled=state.running)
        show_logs(state.logs)


def hello_content():
    with me.box(
        style=me.Style(
            padding=me.Padding.all(24),
            background="#f8fafc",
            min_height="100vh",
            box_sizing="border-box",
        )
    ):
        me.text(
            "Hello",
            type="headline-4",
            style=me.Style(margin=me.Margin(bottom=12)),
        )
        me.text(
            "Hello world",
            style=me.Style(
                font_size=18,
                color="#0f172a",
            ),
        )


@me.page(path="/logs")
def page():
    state = me.state(State)
    if state.logs is None or len(state.logs) == 0:
        state.logs = ["Waiting to start..."]
    if state.running is None:
        state.running = 0
    active_view = me.query_params.get("view", "logs")
    if active_view not in {"logs", "hello"}:
        active_view = "logs"
    render_app_shell(
        active_view,
        hello_content if active_view == "hello" else lambda: logging_content(state),
    )


async def run_task(e: me.ClickEvent):
    print("Starting long task...")
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
