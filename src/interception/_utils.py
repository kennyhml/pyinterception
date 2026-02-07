from contextlib import contextmanager
from typing import Optional
import functools
from threading import Thread
import win32api  # type: ignore
import ctypes

SPI_GETMOUSE = 0x003
SPI_SETMOUSE = 0x004
SPIF_SENDCHANGE = 0x002

SystemParametersInfoA = ctypes.windll.user32.SystemParametersInfoA


def normalize(x: int | tuple[int, int], y: Optional[int] = None) -> tuple[int, int]:
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


def to_interception_coordinate(x: int, y: int) -> tuple[int, int]:
    """Scales a "normal" coordinate to the respective point in the interception
    coordinate system.

    The interception coordinate system covers all 16-bit unsigned integers,
    ranging from `0x0` to `0xFFFF (65535)`.

    To arrive at the formula, we first have to realize the following:
        - The maximum value in the 16-bit system is so `0xFFFF (~65535)`
        - The maximum value, depending on your monitor, would for example be `1920`
        - To calculate the factor, we can calculate `65535 / 1920 = ~34.13`.
        - Thus we found out, that `scaled x = factor * original x` and `factor = 0xFFFF / axis`

    So, to bring it to code:
    ```py
    xfactor = 0xFFFF / screen_width
    yfactor = 0xFFFF / screen_height
    ```

    Now, using that factor, we can calculate the position of our coordinate as such:
    ```py
    interception_x = round(xfactor * x)
    interception_y = round(yfactor * y)
    """

    def scale(metric_index: int, point: int) -> int:
        scale: float = 0xFFFF / win32api.GetSystemMetrics(metric_index)
        return round(point * scale)

    return scale(0, x), scale(1, y)


def get_cursor_pos() -> tuple[int, int]:
    """Gets the current position of the cursor using `GetCursorPos`"""
    return win32api.GetCursorPos()


def threaded(name: str):
    """Threads a function, beware that it will lose its return values"""

    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            def run():
                func(*args, **kwargs)

            thread = Thread(target=run, name=name)
            thread.start()

        return inner

    return outer


def set_win32_mouse_acceleration(enabled: bool):

    # buffer storing the mouse state. The last element is the acceleration
    mouse_params = (ctypes.c_int * 3)()

    SystemParametersInfoA(SPI_GETMOUSE, 0, mouse_params, 0)
    mouse_params[2] = int(enabled)
    SystemParametersInfoA(SPI_SETMOUSE, 0, mouse_params, SPIF_SENDCHANGE)


def get_win32_mouse_acceleration() -> bool:

    # buffer storing the mouse state. The last element is the acceleration
    mouse_params = (ctypes.c_int * 3)()
    SystemParametersInfoA(SPI_GETMOUSE, 0, mouse_params, 0)
    return bool(mouse_params[2])


@contextmanager
def disable_mouse_acceleration():
    original = get_win32_mouse_acceleration()
    set_win32_mouse_acceleration(False)
    try:
        yield
    finally:
        set_win32_mouse_acceleration(original)
