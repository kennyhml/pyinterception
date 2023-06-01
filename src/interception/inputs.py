import functools
import time
from contextlib import contextmanager
from typing import Literal, Optional

from . import _utils
from ._consts import *
from ._keycodes import KEYBOARD_MAPPING
from . import exceptions
from .interception import Interception
from .strokes import KeyStroke, MouseStroke
from .types import MouseButton

# try to initialize interception, if it fails simply remember that it failed to initalize.
# I want to avoid raising the error on import and instead raise it when attempting to call
# functioality that relies on the driver, this also still allows access to non driver functionality
# such as `mouse_position()`
try:
    interception = Interception()
    INTERCEPTION_INSTALLED = True
except Exception:
    INTERCEPTION_INSTALLED = False


MOUSE_BUTTON_DELAY = 0.03
KEY_PRESS_DELAY = 0.025

keyboard = 1
mouse = 11


def requires_driver(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not INTERCEPTION_INSTALLED:
            raise exceptions.InterceptionNotInstalled
        return func(*args, **kwargs)

    return wrapper


@requires_driver
def move_to(x: int | tuple[int, int], y: Optional[int] = None) -> None:
    """Moves to a given position."""
    x, y = _utils.normalize(x, y)
    x, y = _utils.to_interception_coordinate(x, y)
    stroke = MouseStroke(0, MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, x, y, 0)
    interception.send(mouse, stroke)


@requires_driver
def move_relative(x: int | tuple[int, int], y: Optional[int] = None) -> None:
    """Moves to a given position."""
    x, y = _utils.normalize(x, y)
    # x, y = _utils.to_interception_coordinate(x, y)

    stroke = MouseStroke(0, MouseFlag.MOUSE_MOVE_RELATIVE, 0, x, y, 0)
    interception.send(mouse, stroke)


def mouse_position() -> tuple[int, int]:
    """Returns the position of the cursor on the monitor."""
    return _utils.get_cursor_pos()


@requires_driver
def click(
    x: Optional[int | tuple[int, int]] = None,
    y: Optional[int] = None,
    button: MouseButton = "left",
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


@requires_driver
def left_click(clicks: int = 1, interval: int | float = 0.1) -> None:
    """Left clicks at the current position."""
    click(button="left", clicks=clicks, interval=interval)


@requires_driver
def right_click(clicks: int = 1, interval: int | float = 0.1) -> None:
    """Right cicks at the current position."""
    click(button="right", clicks=clicks, interval=interval)


@requires_driver
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
            raise exceptions.InvalidKeyRequested(key)
        if presses > 1:
            time.sleep(interval)


@requires_driver
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


@requires_driver
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


@requires_driver
def key_down(key: str, delay: Optional[float] = None) -> None:
    """Holds a key down, will not be released automatically.

    If you want to hold a key while performing an action, please use
    `hold_key`, which offers a context manager.
    """
    stroke = KeyStroke(KEYBOARD_MAPPING[key], KeyState.KEY_DOWN, 0)
    interception.send(keyboard, stroke)
    
    time.sleep(delay or KEY_PRESS_DELAY)


@requires_driver
def key_up(key: str, delay: Optional[float] = None) -> None:
    """Releases a key."""
    stroke = KeyStroke(KEYBOARD_MAPPING[key], KeyState.KEY_UP, 0)
    interception.send(keyboard, stroke)
    time.sleep(delay or KEY_PRESS_DELAY)


@requires_driver
def mouse_down(button: MouseButton, delay: Optional[float] = None) -> None:
    """Holds a mouse button down, will not be released automatically.

    If you want to hold a mouse button while performing an action, please use
    `hold_mouse`, which offers a context manager.
    """
    down, _ = MouseState.from_string(button)

    stroke = MouseStroke(down, MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, 0, 0, 0)
    interception.send(mouse, stroke)
    time.sleep(delay or MOUSE_BUTTON_DELAY)


@requires_driver
def mouse_up(button: MouseButton, delay: Optional[float] = None) -> None:
    """Releases a mouse button."""
    _, up = MouseState.from_string(button)

    stroke = MouseStroke(up, MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, 0, 0, 0)
    interception.send(mouse, stroke)
    time.sleep(delay or MOUSE_BUTTON_DELAY)


@requires_driver
@contextmanager
def hold_mouse(button: MouseButton):
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


@requires_driver
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


@requires_driver
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


@requires_driver
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


@requires_driver
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


@requires_driver
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
