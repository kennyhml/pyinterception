import time
from contextlib import contextmanager
from typing import Literal, Optional

from win32api import GetSystemMetrics  # type:ignore[import]

from ._consts import *
from ._keycodes import KEYBOARD_MAPPING
from .interception import Interception
from .strokes import KeyStroke, MouseStroke

interception = Interception()

_screen_width = GetSystemMetrics(0)
_screen_height = GetSystemMetrics(1)

MOUSE_BUTTON_MAPPING = {
    "left": (MouseState.MOUSE_LEFT_BUTTON_DOWN, MouseState.MOUSE_LEFT_BUTTON_UP),
    "right": (MouseState.MOUSE_RIGHT_BUTTON_DOWN, MouseState.MOUSE_RIGHT_BUTTON_UP),
    "middle": (MouseState.MOUSE_MIDDLE_BUTTON_DOWN, MouseState.MOUSE_MIDDLE_BUTTON_UP),
    "mouse4": (MouseState.MOUSE_BUTTON_4_DOWN, MouseState.MOUSE_BUTTON_4_UP),
    "mouse5": (MouseState.MOUSE_BUTTON_5_DOWN, MouseState.MOUSE_BUTTON_5_UP),
}


def _normalize(x: int | tuple[int, int], y: Optional[int] = None) -> tuple[int, int]:
    if isinstance(x, tuple):
        if len(x) == 2:
            x, y = x
        elif len(x) == 4:
            x, y, *_ = x
        else:
            raise ValueError(f"Cant normalize tuple of length {len(x)}: {x}")
    else:
        assert y is not None

    return int(x), int(y)


def _to_hexadecimal(screen_size: int, i: int):
    return int((0xFFFF / screen_size) * i) + 1


def _to_interception_point(x: int, y: int) -> tuple[int, int]:
    return (
        _to_hexadecimal(_screen_width, x),
        _to_hexadecimal(_screen_height, y),
    )


def move_to(x: int | tuple[int, int], y: Optional[int] = None) -> None:
    x, y = _normalize(x, y)
    x, y = _to_interception_point(x, y)

    stroke = MouseStroke(0, MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, x, y, 0)
    interception.send(14, stroke)


def click(
    x: Optional[int | tuple[int, int]] = None,
    y: Optional[int] = None,
    button: Literal["left", "right", "middle", "mouse4", "mouse5"] = "left",
    clicks: int = 1,
    interval: int | float = 0.1,
    delay: int | float = 0.1,
) -> None:
    if x is not None:
        move_to(x, y)

    time.sleep(delay)

    for _ in range(clicks):
        mouse_down(button)
        mouse_up(button)

        if clicks > 1:
            time.sleep(interval)


def press(key: str, presses: int = 1, interval: int | float = 0.1) -> None:
    for _ in range(presses):
        try:
            key_down(key)
            key_up(key)
        except KeyError:
            raise ValueError(f"Unsupported key, {key}")
        if presses > 1:
            time.sleep(interval)


def write(term: str, interval: int | float = 0.05) -> None:
    for c in term.lower():
        press(c)
        time.sleep(interval)


def key_down(key: str) -> None:
    stroke = KeyStroke(KEYBOARD_MAPPING[key], KeyState.KEY_DOWN, 0)
    interception.send(1, stroke)
    time.sleep(0.025)


def key_up(key: str) -> None:
    stroke = KeyStroke(KEYBOARD_MAPPING[key], KeyState.KEY_UP, 0)
    interception.send(1, stroke)
    time.sleep(0.025)


def mouse_down(button: Literal["left", "right", "middle", "mouse4", "mouse5"]) -> None:
    down, _ = MOUSE_BUTTON_MAPPING[button]

    stroke = MouseStroke(down, MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, 0, 0, 0)
    interception.send(14, stroke)
    time.sleep(0.025)


def mouse_up(button: Literal["left", "right", "middle", "mouse4", "mouse5"]) -> None:
    _, up = MOUSE_BUTTON_MAPPING[button]

    stroke = MouseStroke(up, MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, 0, 0, 0)
    interception.send(14, stroke)
    time.sleep(0.025)


@contextmanager
def hold_mouse(button: Literal["left", "right", "middle", "mouse4", "mouse5"]):
    mouse_down(button=button)
    try:
        yield
    finally:
        mouse_up(button=button)


@contextmanager
def hold_key(key: str):
    key_down(key)
    try:
        yield
    finally:
        key_up(key)
