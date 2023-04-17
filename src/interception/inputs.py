import ctypes
import time
from contextlib import contextmanager
from ctypes import wintypes
from typing import Literal, Optional

from win32api import GetSystemMetrics  # type:ignore[import]

from ._consts import *
from ._keycodes import KEYBOARD_MAPPING
from .interception import Interception
from .strokes import KeyStroke, MouseStroke

try:
    interception = Interception()
except Exception:
    print("Failed to initialize Interception.")

_screen_width = GetSystemMetrics(0)
_screen_height = GetSystemMetrics(1)

keyboard = 1
mouse = 11

MOUSE_BUTTON_MAPPING = {
    "left": (MouseState.MOUSE_LEFT_BUTTON_DOWN, MouseState.MOUSE_LEFT_BUTTON_UP),
    "right": (MouseState.MOUSE_RIGHT_BUTTON_DOWN, MouseState.MOUSE_RIGHT_BUTTON_UP),
    "middle": (MouseState.MOUSE_MIDDLE_BUTTON_DOWN, MouseState.MOUSE_MIDDLE_BUTTON_UP),
    "mouse4": (MouseState.MOUSE_BUTTON_4_DOWN, MouseState.MOUSE_BUTTON_4_UP),
    "mouse5": (MouseState.MOUSE_BUTTON_5_DOWN, MouseState.MOUSE_BUTTON_5_UP),
}


def _normalize(x: int | tuple[int, int], y: Optional[int] = None) -> tuple[int, int]:
    """Normalizes an x, y position to allow passing them seperately or as tuple."""
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
    """Converts a coordinate from the usual system to a coordinate interception
    can understand and move to."""
    return int((0xFFFF / screen_size) * i) + 1


def _to_interception_point(x: int, y: int) -> tuple[int, int]:
    """Converts a point (x, y) from the usual system to a point interception
    can understand and move to."""
    return (
        _to_hexadecimal(_screen_width, x),
        _to_hexadecimal(_screen_height, y),
    )


def _get_cursor_pos() -> tuple[int, int]:
    """Gets the current position of the cursor using `GetCursorPos`"""
    cursor = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
    return (int(cursor.x), int(cursor.y))


def capture_keyboard() -> int:
    """Captures keyboard keypresses until the `Escape` key is pressed.

    Filters out non `KEY_DOWN` events to not post the same capture twice.
    """
    context = Interception()
    context.set_filter(context.is_keyboard, FilterKeyState.FILTER_KEY_DOWN)

    print("Capturing keyboard presses, press ESC to quit.")
    try:
        while True:
            device = context.wait()
            stroke = context.receive(device)

            if stroke.code == 0x01:
                print("ESC pressed, exited.")
                return device

            print(f"Received stroke {stroke} on keyboard device {device}")
            context.send(device, stroke)
    finally:
        context._destroy_context()


def capture_mouse() -> int:
    """Captures mouse left clicks until the `Escape` key is pressed.

    Filters out non `LEFT_BUTTON_DOWN` events to not post the same capture twice.
    """
    context = Interception()
    context.set_filter(context.is_mouse, FilterMouseState.FILTER_MOUSE_LEFT_BUTTON_DOWN)
    context.set_filter(context.is_keyboard, FilterKeyState.FILTER_KEY_DOWN)

    print("Capturing mouse left clicks, press ESC to quit.")
    try:
        while True:
            device = context.wait()
            stroke = context.receive(device)

            if context.is_keyboard(device) and stroke.code == 0x01:
                print("ESC pressed, exited.")
                return device

            elif not context.is_keyboard(device):
                print(f"Received stroke {stroke} on mouse device {device}")

            context.send(device, stroke)
    finally:
        context._destroy_context()


def listen_to_keyboard() -> int:
    """Captures keyboard keypresses until the `Escape` key is pressed.

    Doesn't filter out any events at all.
    """
    context = Interception()
    context.set_filter(context.is_keyboard, FilterKeyState.FILTER_KEY_ALL)

    print("Listenting to keyboard, press ESC to quit.")
    try:
        while True:
            device = context.wait()
            stroke = context.receive(device)

            if stroke.code == 0x01:
                print("ESC pressed, exited.")
                return device

            print(f"Received stroke {stroke} on keyboard device {device}")
            context.send(device, stroke)
    finally:
        context._destroy_context()


def listen_to_mouse() -> int:
    """Captures mouse movements / clicks until the `Escape` key is pressed.

    Doesn't filter out any events at all.
    """
    context = Interception()
    context.set_filter(context.is_mouse, FilterMouseState.FILTER_MOUSE_ALL)
    context.set_filter(context.is_keyboard, FilterKeyState.FILTER_KEY_DOWN)

    print("Listenting to mouse, press ESC to quit.")
    try:
        while True:
            device = context.wait()
            stroke = context.receive(device)

            if context.is_keyboard(device) and stroke.code == 0x01:
                print("ESC pressed, exited.")
                return device

            elif not context.is_keyboard(device):
                print(f"Received stroke {stroke} on mouse device {device}")

            context.send(device, stroke)
    finally:
        context._destroy_context()


def move_to(x: int | tuple[int, int], y: Optional[int] = None) -> None:
    """Moves to a given position."""
    x, y = _normalize(x, y)
    x, y = _to_interception_point(x, y)

    stroke = MouseStroke(0, MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, x, y, 0)
    interception.send(mouse, stroke)


def move_relative(x: int = 0, y: int = 0) -> None:
    """Moves relatively to a given position."""
    curr = _get_cursor_pos()
    move_to(curr[0] + x, curr[1] + y)


def position() -> tuple[int, int]:
    """Returns the position of the cursor on the monitor."""
    return _get_cursor_pos()


def click(
    x: Optional[int | tuple[int, int]] = None,
    y: Optional[int] = None,
    button: Literal["left", "right", "middle", "mouse4", "mouse5"] = "left",
    clicks: int = 1,
    interval: int | float = 0.1,
    delay: int | float = 0.3,
) -> None:
    """Clicks at a given position.

    Parameters
    ----------
    button :class:`Literal["left", "right", "middle", "mouse4", "mouse5"]`:
        The button to click once moved to the location (if passed), default "left".

    clicks :class:`int`:
        The amount of mouse clicks to perform with the given button

    interval :class:`int | float`:
        The interval between multiple clicks, only applies if clicks > 1

    delay :class:`int | float`:
        The delay between moving and clicking.
    """
    if x is not None:
        move_to(x, y)

    time.sleep(delay)

    for _ in range(clicks):
        mouse_down(button)
        mouse_up(button)

        if clicks > 1:
            time.sleep(interval)


def left_click(clicks: int = 1, interval: int | float = 0.1) -> None:
    """Left clicks at the current position."""
    click(button="left", clicks=clicks, interval=interval)


def right_click(clicks: int = 1, interval: int | float = 0.1) -> None:
    """Right cicks at the current position."""
    click(button="right", clicks=clicks, interval=interval)


def press(key: str, presses: int = 1, interval: int | float = 0.1) -> None:
    """Presses a key.

    Parameters
    ----------
    key :class:`str`:
        The key to press.

    presses :class:`int`:
        The amount of presses to perform with the given key.

    interval :class:`int | float`:
        The interval between multiple presses, only applies if presses > 1.
    """
    for _ in range(presses):
        try:
            key_down(key)
            key_up(key)
        except KeyError:
            raise ValueError(f"Unsupported key, {key}")
        if presses > 1:
            time.sleep(interval)


def write(term: str, interval: int | float = 0.05) -> None:
    """Writes a term by sending each key one after another.

    Parameters
    ----------
    term :class:`str`:
        The term to write.

    interval :class:`int | float`:
        The interval between pressing of the different characters.
    """
    for c in term.lower():
        press(c)
        time.sleep(interval)


def scroll(direction: Literal["up", "down"]) -> None:
    """Scrolls the mouse wheel one unit in a given direction."""
    amount = (
        MouseRolling.MOUSE_WHEEL_UP
        if direction == "up"
        else MouseRolling.MOUSE_WHEEL_DOWN
    )

    stroke = MouseStroke(
        MouseState.MOUSE_WHEEL, MouseFlag.MOUSE_MOVE_RELATIVE, amount, 0, 0, 0
    )
    interception.send(mouse, stroke)
    time.sleep(0.025)


def key_down(key: str) -> None:
    """Holds a key down, will not be released automatically.

    If you want to hold a key while performing an action, please use
    `hold_key`, which offers a context manager.
    """
    stroke = KeyStroke(KEYBOARD_MAPPING[key], KeyState.KEY_DOWN, 0)
    interception.send(keyboard, stroke)
    time.sleep(0.025)


def key_up(key: str) -> None:
    """Releases a key."""
    stroke = KeyStroke(KEYBOARD_MAPPING[key], KeyState.KEY_UP, 0)
    interception.send(keyboard, stroke)
    time.sleep(0.025)


def mouse_down(button: Literal["left", "right", "middle", "mouse4", "mouse5"]) -> None:
    """Holds a mouse button down, will not be released automatically.

    If you want to hold a mouse button while performing an action, please use
    `hold_mouse`, which offers a context manager.
    """
    down, _ = MOUSE_BUTTON_MAPPING[button]

    stroke = MouseStroke(down, MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, 0, 0, 0)
    interception.send(mouse, stroke)
    time.sleep(0.03)


def mouse_up(button: Literal["left", "right", "middle", "mouse4", "mouse5"]) -> None:
    """Releases a mouse button."""
    _, up = MOUSE_BUTTON_MAPPING[button]

    stroke = MouseStroke(up, MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, 0, 0, 0)
    interception.send(mouse, stroke)
    time.sleep(0.03)


@contextmanager
def hold_mouse(button: Literal["left", "right", "middle", "mouse4", "mouse5"]):
    """A context manager to hold a mouse button while performing another action.

    Example:
    ```py
    with interception.hold_mouse("left"):
        interception.move_to(300, 300)
    """
    mouse_down(button=button)
    try:
        yield
    finally:
        mouse_up(button=button)


@contextmanager
def hold_key(key: str):
    """A context manager to hold a mouse button while performing another action.

    Example:
    ```py
    with interception.hold_key("ctrl"):
        interception.press("c")
    """
    key_down(key)
    try:
        yield
    finally:
        key_up(key)
