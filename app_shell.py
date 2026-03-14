from collections.abc import Callable

import mesop as me


SIDEBAR_WIDTH = 220

MENU_ITEMS = (
    ("starter", "Starter Kit", "/starter_kit", None),
    ("loading", "Loading", "/loading", None),
    ("logs", "Logging", "/logs", {"view": "logs"}),
    ("hello", "Hello", "/logs", {"view": "hello"}),
)

MENU_ITEM_MAP = {
    item_id: {"url": url, "query_params": query_params}
    for item_id, _label, url, query_params in MENU_ITEMS
}


def render_app_shell(active_item: str, content: Callable[[], None]):
    is_mobile = me.viewport_size().width < 720
    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="column" if is_mobile else "row",
            min_height="100vh",
        )
    ):
        _sidebar_menu(active_item)
        with me.box(
            style=me.Style(
                flex_grow=1,
                min_height="100vh",
            )
        ):
            content()


def _sidebar_menu(active_item: str):
    with me.box(
        style=me.Style(
            width=SIDEBAR_WIDTH,
            min_height="100vh",
            background="#0f172a",
            padding=me.Padding.all(20),
            box_sizing="border-box",
        )
    ):
        me.text(
            "Menu",
            style=me.Style(
                color="#cbd5e1",
                font_size=14,
                font_weight=600,
                margin=me.Margin(bottom=16),
                text_transform="uppercase",
                letter_spacing="0.08em",
            ),
        )
        for item_id, label, url, query_params in MENU_ITEMS:
            _sidebar_item(
                item_id=item_id,
                label=label,
                is_active=active_item == item_id,
            )


def _sidebar_item(item_id: str, label: str, is_active: bool):
    with me.box(
        key=item_id,
        on_click=_handle_sidebar_click,
        style=me.Style(
            background="#1d4ed8" if is_active else "#1e293b",
            color="#ffffff" if is_active else "#cbd5e1",
            padding=me.Padding.symmetric(horizontal=14, vertical=12),
            border_radius=10,
            cursor="pointer",
            margin=me.Margin(bottom=10),
        ),
    ):
        me.text(
            label,
            style=me.Style(
                color="inherit",
                font_weight=600,
            ),
        )


def _handle_sidebar_click(e: me.ClickEvent):
    menu_item = MENU_ITEM_MAP.get(e.key)
    if menu_item is None:
        return

    if menu_item["query_params"] is None:
        me.navigate(menu_item["url"])
    else:
        me.navigate(menu_item["url"], query_params=menu_item["query_params"])
