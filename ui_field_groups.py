from dataclasses import field
import json
import re
import logging
import asyncio
from collections import deque

import mesop as me

from field_groups_process import process_field_group

ROW_GAP = 4
FIELD_NAME_WIDTH = "260px"
ACTION_WIDTH = "90px"
BUTTON_WIDTH = "44px"
FIELD_HEIGHT = "36px"
BUTTON_HEIGHT = "36px"

LABEL_STYLE = me.Style(
    font_size=14,
    font_weight=500,
    margin=me.Margin(bottom=4),
)

INPUT_STYLE = me.Style(
    font_size=13,
    line_height="1.0",
)

BUTTON_STYLE = me.Style(
    width=BUTTON_WIDTH,
    min_width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    border_radius=10,
    padding=me.Padding.symmetric(horizontal=0, vertical=0),
)


@me.stateclass
class PageState:
    field_group_name: str = ""
    replace: bool = False
    rows: list[dict[str, str]] = field(
        default_factory=lambda: [{"field_name": "", "action": "A"}]
    )
    pasted_fields: str = ""
    submitted_json: str = ""
    result_json: str = ""
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


def get_state() -> PageState:
    return me.state(PageState)


def show_logs(lines: list[str]):
    with me.box(
        style=me.Style(
            border=me.Border.all(me.BorderSide(color="#4d98e4", width=1)),
            border_radius=8,
            padding=me.Padding.all(12),
            height=100,
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


@me.page(
    path="/field-group",
    title="Field Group",
    stylesheets=["/static/overrides.css"],
)
def page():
    s = get_state()
    if s.logs is None or len(s.logs) == 0:
        s.logs = ["Process logs, waiting to start..."]
    if s.running is None:
        s.running = 0

    with me.box(
        style=me.Style(
            margin=me.Margin.symmetric(horizontal="auto"),
            padding=me.Padding.all(24),
            width="min(760px, 100%)",
            box_sizing="border-box",
        )
    ):
        with me.box(
            style=me.Style(
                display="flex",
                flex_direction="row",
                align_items="end",
                gap=16,
            )
        ):
            with me.box(style=me.Style(width=FIELD_NAME_WIDTH)):
                me.text("Field Group Name", style=LABEL_STYLE)
                me.input(
                    value=s.field_group_name,
                    on_blur=on_field_group_name_blur,
                    appearance="outline",
                    style=me.Style(
                        padding=me.Padding.all(0),
                        box_sizing="border-box",
                        width="100%",
                        font_size=13,
                        line_height="1.2",
                    ),
                )
            me.checkbox(
                "Replace",
                checked=(1 if s.replace else 0),
                on_change=on_replace_change,
                style=me.Style(margin=me.Margin(bottom=4)),
            )

        me.box(style=me.Style(height="20px"))

        render_rows()

        me.box(style=me.Style(height="20px"))

        me.text("Fields as raw delimited text", style=LABEL_STYLE)
        me.textarea(
            value=s.pasted_fields,
            on_blur=on_pasted_fields_blur,
            appearance="outline",
            rows=4,
            placeholder="Paste a list of fields from your clipboard",
            style=me.Style(
                width="100%",
                font_size=13,
                line_height="1.2",
            ),
        )

        me.box(style=me.Style(height="12px"))

        me.button(
            "Import Fields from delimited text",
            on_click=on_paste_fields,
            type="stroked",
            style=me.Style(
                border_radius=999,
                padding=me.Padding.symmetric(horizontal=18, vertical=8),
            ),
            disabled=s.running,
        )

        me.box(style=me.Style(height="20px"))

        me.button(
            "Submit",
            on_click=on_submit,
            type="stroked",
            style=me.Style(
                border_radius=999,
                padding=me.Padding.symmetric(horizontal=18, vertical=8),
            ),
            disabled=s.running,
        )

        me.box(style=me.Style(margin=me.Margin(top=16, bottom=16)))
        me.divider()
        show_logs(s.logs)

        if s.result_json:
            with me.box(
                style=me.Style(
                    margin=me.Margin(top=16),
                    background="#b6d4f3",
                ),
            ):
                me.text(
                    "Results", 
                    type="headline-5",
                    style=me.Style(margin=me.Margin(bottom=8))
                )
            me.code(s.result_json)


def render_rows():
    s = get_state()

    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="row",
            gap=ROW_GAP,
            align_items="end",
            margin=me.Margin(bottom=0),
        )
    ):
        with me.box(style=me.Style(width=FIELD_NAME_WIDTH)):
            me.text("Field Name", style=LABEL_STYLE)

        with me.box(style=me.Style(width=ACTION_WIDTH)):
            me.text("A/D", style=LABEL_STYLE)

        with me.box(style=me.Style(width=BUTTON_WIDTH)):
            me.text("")

        with me.box(style=me.Style(width=BUTTON_WIDTH)):
            me.text("")

    for i, row in enumerate(s.rows):
        render_row(i, row)


def render_row(index: int, row: dict[str, str]):
    s = get_state()
    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="row",
            gap=ROW_GAP,
            align_items="center",
            margin=me.Margin(top=2),
        )
    ):
        with me.box(style=me.Style(width=FIELD_NAME_WIDTH)):
            me.input(
                key=f"field_name_{index}",
                value=row["field_name"],
                on_blur=on_field_name_blur,
                appearance="outline",
                style=me.Style(
                    width="100%",
                    font_size=13,
                    line_height="1.0"
                ),
            )

        with me.box(style=me.Style(width=ACTION_WIDTH)):
            me.select(
                key=f"action_{index}",
                value=row["action"],
                options=[
                    me.SelectOption(label="A", value="A"),
                    me.SelectOption(label="D", value="D"),
                ],
                on_selection_change=on_action_change,
                disabled=s.replace,
                appearance="outline",
                style=me.Style(
                    width="100%",
                    font_size=13,
                    line_height="1.0"
                ),
            )

        with me.box(style=me.Style(width=BUTTON_WIDTH)):
            me.button(
                "+",
                key=f"add_{index}",
                on_click=on_add_row,
                type="stroked",
                style=BUTTON_STYLE,
            )

        with me.box(style=me.Style(width=BUTTON_WIDTH)):
            me.button(
                "x",
                key=f"delete_{index}",
                on_click=on_delete_row,
                type="stroked",
                style=BUTTON_STYLE,
            )


def on_field_group_name_blur(e: me.InputBlurEvent):
    s = get_state()
    s.field_group_name = e.value


def on_pasted_fields_blur(e: me.InputBlurEvent):
    s = get_state()
    s.pasted_fields = e.value


def on_replace_change(e: me.CheckboxChangeEvent):
    s = get_state()
    s.replace = e.checked
    if e.checked:
        s.rows = [
            {"field_name": row["field_name"], "action": "A"}
            for row in s.rows
        ]


def on_field_name_input(e: me.InputEvent):
    s = get_state()
    index = int(e.key.split("_")[-1])

    new_rows = list(s.rows)
    new_row = dict(new_rows[index])
    new_row["field_name"] = e.value
    new_rows[index] = new_row
    s.rows = new_rows

def on_field_name_blur(e: me.InputBlurEvent):
    s = get_state()
    index = int(e.key.split("_")[-1])

    new_rows = list(s.rows)
    new_row = dict(new_rows[index])
    new_row["field_name"] = e.value
    new_rows[index] = new_row
    s.rows = new_rows
    
def on_action_change(e: me.SelectSelectionChangeEvent):
    s = get_state()
    if s.replace:
        return
    index = int(e.key.split("_")[-1])

    new_rows = list(s.rows)
    new_row = dict(new_rows[index])
    new_row["action"] = e.value
    new_rows[index] = new_row
    s.rows = new_rows

def on_add_row(e: me.ClickEvent):
    s = get_state()
    s.rows.append({"field_name": "", "action": "A"})


def on_delete_row(e: me.ClickEvent):
    s = get_state()
    index = int(e.key.split("_")[-1])

    if len(s.rows) == 1:
        s.rows[0] = {"field_name": "", "action": "A"}
    else:
        s.rows.pop(index)


def on_paste_fields(e: me.ClickEvent):
    s = get_state()
    field_names = [
        token for token in re.split(r"[^0-9A-Za-z\-_]+", s.pasted_fields) if token
    ]

    if field_names:
        s.rows = [{"field_name": field_name, "action": "A"} for field_name in field_names]
    else:
        s.rows = [{"field_name": "", "action": "A"}]


async def on_submit(e: me.ClickEvent):
    s = get_state()

    adds = []
    deletes = []

    for row in s.rows:
        field_name = row["field_name"].strip()
        if not field_name:
            continue

        if row["action"] == "A":
            adds.append(field_name)
        else:
            deletes.append(field_name)

    payload = {
        "field_group_name": s.field_group_name.strip(),
        "replace": s.replace,
        "adds": adds,
        "deletes": deletes,
    }

    # state = me.state(State)
    s.running = 1
    s.logs = []
    s.result_json = ""

    sink = deque()
    handler = BufferLogHandler(sink)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    root_logger = logging.getLogger()
    old_level = root_logger.level

    # Make sure INFO logs are not filtered out
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    try:
        s.result_json = ""
        task = asyncio.create_task(process_field_group(payload))

        while not task.done():
            if sink:
                s.logs = list(sink)
                yield
            await asyncio.sleep(0.2)

        result = await task
        s.logs = list(sink)
        s.result_json = json.dumps(result, indent=2)
        yield
    finally:
        root_logger.removeHandler(handler)
        root_logger.setLevel(old_level)
        s.running = 0
        yield
