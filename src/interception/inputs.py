import functools
import time
from contextlib import contextmanager
from typing import Literal, Optional, TypeAlias

from . import _keycodes, _utils, beziercurve, exceptions
from .constants import (
    FilterKeyFlag,
    FilterMouseButtonFlag,
    KeyFlag,
    MouseButtonFlag,
    MouseFlag,
    MouseRolling,
)
from .interception import Interception
from .strokes import KeyStroke, MouseStroke

# try to initialize interception, if it fails simply remember that it failed to initalize.
# I want to avoid raising the error on import and instead raise it when attempting to call
# functionality that relies on the driver, this also still allows access to non driver stuff
try:
    interception = Interception()
    INTERCEPTION_INSTALLED = True
except Exception:
    INTERCEPTION_INSTALLED = False

MouseButton: TypeAlias = Literal["left", "right", "middle", "mouse4", "mouse5"]

MOUSE_BUTTON_DELAY = 0.03
KEY_PRESS_DELAY = 0.025


def requires_driver(func):
    """Wraps any function that requires the interception driver to be installed
    such that, if it is not installed, a `DriverNotFoundError` is raised"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not INTERCEPTION_INSTALLED:
            raise exceptions.DriverNotFoundError
        return func(*args, **kwargs)

    return wrapper


@requires_driver
def move_to(
    x: int | tuple[int, int],
    y: Optional[int] = None,
    curve_params: Optional[beziercurve.BezierCurveParams] = None,
    *,
    overrule_global_curve: bool = False,
) -> None:
    """Moves to a given absolute (x, y) location on the screen.

    Parameters
    ----------
    curve_params :class:`Optional[HumanCurve]`:
        An optional container to define the curve parameters, pyclick is required.

    overrule_global_curve :class:`bool`:
        Whether a global curve should not be used despite being set. False by default.

    The coordinates can be passed as a tuple-like `(x, y)` coordinate or
    seperately as `x` and `y` coordinates, it will be parsed accordingly.

    ### Examples:
    ```py
    # passing x and y seperately, typical when manually calling the function
    interception.move_to(800, 1200)

    # passing a tuple-like coordinate, typical for dynamic operations.
    # simply avoids having to unpack the arguments.
    target_location = (1200, 300)
    interception.move_to(target_location)
    ```
    """

    if curve_params is None:
        x, y = _utils.to_interception_coordinate(*_utils.normalize(x, y))
        stroke = MouseStroke(MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, 0, x, y)
        interception.send(interception.mouse, stroke)
        return

    curve = beziercurve.HumanCurve(mouse_position(), _utils.normalize(x, y))
    for point in curve.points:
        # Tempts to use recursion, but recursion stack limit would not allow it.
        # Iterative solution is harder to read than this imo.
        x, y = _utils.to_interception_coordinate(*_utils.normalize(point))
        stroke = MouseStroke(MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, 0, x, y)
        interception.send(interception.mouse, stroke)
        time.sleep(0.01)


@requires_driver
def move_relative(x: int = 0, y: int = 0) -> None:
    """Moves relatively from the current cursor position by the given amounts.

    Due to conversion to the coordinate system the interception driver
    uses, an offset of 1 pixel in either x or y axis may occur or not.

    ### Example:
    ```py
    interception.mouse_position()
    >>> 300, 400

    # move the mouse by 100 pixels on the x-axis and 0 in y-axis
    interception.move_relative(100, 0)
    interception.mouse_position()
    >>> 400, 400
    """
    stroke = MouseStroke(MouseFlag.MOUSE_MOVE_RELATIVE, 0, 0, x, y)
    interception.send(interception.mouse, stroke)


def mouse_position() -> tuple[int, int]:
    """Returns the current position of the cursor as `(x, y)` coordinate.

    This does nothing special like other conventional mouse position functions.
    """
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
    """Presses a mouse button at a specific location (if given).

    Parameters
    ----------
    button :class:`Literal["left", "right", "middle", "mouse4", "mouse5"] | str`:
        The button to click once moved to the location (if passed), default "left".

    clicks :class:`int`:
        The amount of mouse clicks to perform with the given button, default 1.

    interval :class:`int | float`:
        The interval between multiple clicks, only applies if clicks > 1, default 0.1.

    delay :class:`int | float`:
        The delay between moving and clicking, default 0.3.
    """
    if x is not None:
        move_to(x, y)
        time.sleep(delay)

    for _ in range(clicks):
        mouse_down(button)
        mouse_up(button)

        if clicks > 1:
            time.sleep(interval)


# decided against using functools.partial for left_click and right_click
# because it makes it less clear that the method attribute is a function
# and might be misunderstood. It also still allows changing the button
# argument afterall - just adds the correct default.
@requires_driver
def left_click(clicks: int = 1, interval: int | float = 0.1) -> None:
    """Thin wrapper for the `click` function with the left mouse button."""
    click(button="left", clicks=clicks, interval=interval)


@requires_driver
def right_click(clicks: int = 1, interval: int | float = 0.1) -> None:
    """Thin wrapper for the `click` function with the right mouse button."""
    click(button="right", clicks=clicks, interval=interval)


@requires_driver
def press(key: str, presses: int = 1, interval: int | float = 0.1) -> None:
    """Presses a given key, for mouse buttons use the`click` function.

    Parameters
    ----------
    key :class:`str`:
        The key to press, not case sensitive.

    presses :class:`int`:
        The amount of presses to perform with the given key, default 1.

    interval :class:`int | float`:
        The interval between multiple presses, only applies if presses > 1, defaul 0.1.
    """
    for _ in range(presses):
        key_down(key)
        key_up(key)
        if presses > 1:
            time.sleep(interval)


@requires_driver
def write(term: str, interval: int | float = 0.05) -> None:
    """Writes a term by sending each key one after another.

    Uppercase characters are not currently supported, the term will
    come out as lowercase.

    Parameters
    ----------
    term :class:`str`:
        The term to write.

    interval :class:`int | float`:
        The interval between the different characters, default 0.05.
    """
    for c in term:
        press(c)
        time.sleep(interval)


@requires_driver
def scroll(direction: Literal["up", "down"]) -> None:
    """Scrolls the mouse wheel one unit in a given direction."""
    if direction == "up":
        button_data = MouseRolling.MOUSE_WHEEL_UP
    else:
        button_data = MouseRolling.MOUSE_WHEEL_DOWN

    stroke = MouseStroke(
        MouseFlag.MOUSE_MOVE_RELATIVE, MouseButtonFlag.MOUSE_WHEEL, button_data, 0, 0
    )
    interception.send(interception.mouse, stroke)
    time.sleep(0.025)


def _send_with_mods(stroke: KeyStroke, **kwarg_mods) -> None:

    mods: list[str] = [key for key, v in kwarg_mods.items() if v]

    for mod in mods:
        key_down(mod, 0)

    interception.send(interception.keyboard, stroke)

    for mod in mods:
        key_up(mod, 0)


@requires_driver
def key_down(key: str, delay: Optional[float | int] = None) -> None:
    """Updates the state of the given key to be `down`.

    To release the key automatically, consider using the `hold_key` contextmanager.

    ### Parameters:
    ----------
    key :class: `str`:
        The key to hold down.

    delay :class: `Optional[float | int]`:
        The amount of time to wait after updating the key state.

    ### Raises:
    `UnknownKeyError` if the given key is not supported.
    """
    data = _keycodes.get_key_information(key)

    stroke = KeyStroke(data.scan_code, KeyFlag.KEY_DOWN)
    if data.is_extended:
        stroke.flags |= KeyFlag.KEY_E0

    _send_with_mods(stroke, ctrl=data.ctrl, alt=data.alt, shift=data.shift)
    time.sleep(delay if delay is not None else KEY_PRESS_DELAY)


@requires_driver
def key_up(key: str, delay: Optional[float | int] = None) -> None:
    """Updates the state of the given key to be `up`.

    ### Parameters:
    ----------
    key :class: `str`:
        The key to release.

    delay :class: `Optional[float | int]`:
        The amount of time to wait after updating the key state.

    ### Raises:
    `UnknownKeyError` if the given key is not supported.
    """
    data = _keycodes.get_key_information(key)

    stroke = KeyStroke(data.scan_code, KeyFlag.KEY_UP)
    if data.is_extended:
        stroke.flags |= KeyFlag.KEY_E0

    _send_with_mods(stroke, ctrl=data.ctrl, alt=data.alt, shift=data.shift)
    time.sleep(delay if delay is not None else KEY_PRESS_DELAY)


@requires_driver
def mouse_down(button: MouseButton, delay: Optional[float] = None) -> None:
    """Holds a mouse button down, will not be released automatically.

    If you want to hold a mouse button while performing an action, please use
    `hold_mouse`, which offers a context manager.
    """
    button_state = _get_button_states(button, down=True)
    stroke = MouseStroke(MouseFlag.MOUSE_MOVE_ABSOLUTE, button_state, 0, 0, 0)
    interception.send(interception.mouse, stroke)
    time.sleep(delay or MOUSE_BUTTON_DELAY)


@requires_driver
def mouse_up(button: MouseButton, delay: Optional[float] = None) -> None:
    """Releases a mouse button."""
    button_state = _get_button_states(button, down=False)
    stroke = MouseStroke(MouseFlag.MOUSE_MOVE_ABSOLUTE, button_state, 0, 0, 0)
    interception.send(interception.mouse, stroke)
    time.sleep(delay or MOUSE_BUTTON_DELAY)


@requires_driver
@contextmanager
def hold_mouse(button: MouseButton):
    """Holds a mouse button down while performing another action.

    ### Example:
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
    """Hold a key down while performing another action.

    ### Example:
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
def capture_keyboard() -> None:
    """Captures keyboard keypresses until the `Escape` key is pressed.

    Filters out non `KEY_DOWN` events to not post the same capture twice.
    """
    context = Interception()
    context.set_filter(context.is_keyboard, FilterKeyFlag.FILTER_KEY_DOWN)
    print("Capturing keyboard presses, press ESC to quit.")

    _listen_to_events(context, "esc")
    print("No longer intercepting keyboard events.")


@requires_driver
def capture_mouse() -> None:
    """Captures mouse left clicks until the `Escape` key is pressed.

    Filters out non `LEFT_BUTTON_DOWN` events to not post the same capture twice.
    """
    context = Interception()
    context.set_filter(
        context.is_mouse, FilterMouseButtonFlag.FILTER_MOUSE_LEFT_BUTTON_DOWN
    )
    context.set_filter(context.is_keyboard, FilterKeyFlag.FILTER_KEY_DOWN)
    print("Intercepting mouse left clicks, press ESC to quit.")

    _listen_to_events(context, "esc")
    print("No longer intercepting mouse events.")


@requires_driver
def auto_capture_devices(
    *, keyboard: bool = True, mouse: bool = True, verbose: bool = False
) -> None:
    """Uses pynputs keyboard and mouse listener to check whether a device
    number will send a valid input. During this process, each possible number
    for the device is tried - once a working number is found, it is assigned
    to the context and the it moves to the next device.

    ### Parameters:
    --------------
    keyboard :class:`bool`:
        Capture the keyboard number.

    mouse :class:`bool`:
        Capture the mouse number.

    verbose :class:`bool`:
        Provide output regarding the tested numbers.
    """

    def log(info: str) -> None:
        if verbose:
            print(info)

    num = 0 if keyboard else 10
    while num < 20:
        hwid: Optional[str] = interception.devices[num].get_HWID()
        if hwid is None:
            log(f"{num}: None")
            num += 1
            continue

        log(f"{num}: {hwid[:60]}...")
        if interception.is_keyboard(num):
            interception.keyboard = num
            num += 1
            if not mouse:
                break
            continue
        interception.mouse = num
        num += 1

    log(f"Devices set. Mouse: {interception.mouse}, keyboard: {interception.keyboard}")


@requires_driver
def set_devices(keyboard: Optional[int] = None, mouse: Optional[int] = None) -> None:
    """Sets the devices on the current context. Keyboard devices should be from 0 to 10
    and mouse devices from 10 to 20 (both non-inclusive).

    If a device out of range is passed, the context will raise a `ValueError`.
    """
    if keyboard is not None:
        interception.keyboard = keyboard

    if mouse is not None:
        interception.mouse = mouse


@requires_driver
def get_mouse() -> int:
    return interception.mouse


@requires_driver
def get_keyboard() -> int:
    return interception.keyboard


def _listen_to_events(context: Interception, stop_button: str) -> None:
    """Listens to a given interception context. Stops when the `stop_button` is
    the event key.

    Remember to destroy the context in any case afterwards. Otherwise events
    will continue to be intercepted!"""
    stop = _keycodes.get_key_information(stop_button).scan_code
    try:
        while True:
            device = context.await_input()
            if device is None:
                continue

            stroke = context.devices[device].receive()
            if stroke is None:
                continue

            if isinstance(stroke, KeyStroke) and stroke.code == stop:
                return

            print(f"Received stroke {stroke} on device {device}")
            context.send(device, stroke)
    finally:
        context.destroy()


def _get_button_states(button: str, *, down: bool) -> int:
    try:
        states = MouseButtonFlag.from_string(button)
        return states[not down]  # first state is down, second state is up
    except KeyError:
        raise exceptions.UnknownButtonError(button)
