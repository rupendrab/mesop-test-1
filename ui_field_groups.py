from dataclasses import field
import json
import mesop as me

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
    rows: list[dict[str, str]] = field(
        default_factory=lambda: [{"field_name": "", "action": "A"}]
    )
    submitted_json: str = ""


def get_state() -> PageState:
    return me.state(PageState)


@me.page(
    path="/field-group",
    title="Field Group",
    stylesheets=["/static/overrides.css"],
)
def page():
    s = get_state()

    with me.box(
        style=me.Style(
            margin=me.Margin.symmetric(horizontal="auto"),
            padding=me.Padding.all(24),
            width="min(760px, 100%)",
            box_sizing="border-box",
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

        me.box(style=me.Style(height="20px"))

        render_rows()

        me.box(style=me.Style(height="20px"))

        me.button(
            "Submit",
            on_click=on_submit,
            type="stroked",
            style=me.Style(
                border_radius=999,
                padding=me.Padding.symmetric(horizontal=18, vertical=8),
            ),
        )

        me.box(style=me.Style(margin=me.Margin(top=16, bottom=16)))
        me.divider()

        if s.submitted_json:
            me.text("Submitted payload")
            me.code(s.submitted_json)


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


def on_submit(e: me.ClickEvent):
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
        "adds": adds,
        "deletes": deletes,
    }

    s.submitted_json = json.dumps(payload, indent=2)
