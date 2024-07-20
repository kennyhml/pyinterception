import ctypes

from typing import Callable, Final, Optional

from .strokes import Stroke
from .device import Device

MAX_DEVICES: Final = 20
MAX_KEYBOARD: Final = 10
MAX_MOUSE: Final = 10

GENERIC_READ: Final = 0x80000000
OPEN_EXISTING: Final = 0x3
WAIT_TIMEOUT: Final = 0x102
WAIT_FAILED: Final = 0xFFFFFFFF


class Interception:
    """Represents an interception context.

    Encapsulating the environment into a class context is useful in order to
    allow the quick creation of different contexts (e.g a filter context).

    Properties
    ----------
    mouse :class:`int`:
        The mouse device number the context is currently using

    keyboard :class:`int`:
        The keyboard device number the context is currently using.

    devices :class:`list[Device]`:
        A list containing all 20 devices the context is managing
    """

    def __init__(self) -> None:
        self._devices: list[Device] = []
        self._event_handles = (ctypes.c_void_p * MAX_DEVICES)()
        self._using_mouse = 11
        self._using_keyboard = 1

        try:
            self.get_handles()
        except Exception:
            self.destroy()
            raise

    @property
    def mouse(self) -> int:
        return self._using_mouse

    @mouse.setter
    def mouse(self, num: int) -> None:
        if is_invalid(num) or not is_mouse(num):
            raise ValueError(f"{num} mouse number does not match (10 <= num <= 19).")
        self._using_mouse = num

    @property
    def keyboard(self) -> int:
        return self._using_keyboard

    @keyboard.setter
    def keyboard(self, num: int) -> None:
        if is_invalid(num) or not is_keyboard(num):
            raise ValueError(f"{num} keyboard number does not match (0 <= num <= 9).")
        self._using_keyboard = num

    @property
    def devices(self) -> list[Device]:
        return self._devices

    def destroy(self) -> None:
        for device in self._devices:
            device.destroy()

    def get_handles(self) -> None:
        """Opens handles to all 20 interception devices and events.

        See:
        https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea
        https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createeventa
        """
        for num in range(MAX_DEVICES):
            device_name = f"\\\\.\\interception{num:02d}".encode()
            hdevice = ctypes.windll.kernel32.CreateFileA(
                device_name, GENERIC_READ, 0, 0, OPEN_EXISTING, 0, 0
            )
            hevent = ctypes.windll.kernel32.CreateEventA(0, 1, 0, 0)

            device = Device(hdevice, hevent, is_keyboard=is_keyboard(num))
            self._devices.append(device)
            self._event_handles[num] = hevent

    def await_input(self, timeout_milliseconds: int = -1) -> Optional[int]:
        """Waits until any of the devices received an input or the timeout has
        expired (if it is non-negative).

        Once an input was received, the number of the device that received the input
        is returned.
        """
        result = ctypes.windll.kernel32.WaitForMultipleObjects(
            MAX_DEVICES, self._event_handles, 0, timeout_milliseconds
        )
        return None if result in [-1, WAIT_TIMEOUT, WAIT_FAILED] else result

    def set_filter(self, condition: Callable[[int], bool], filter: int):
        for i in range(MAX_DEVICES):
            if condition(i):
                self._devices[i].set_filter(filter)

    def send(self, device: int, stroke: Stroke):
        return self._devices[device].send(stroke)


def is_keyboard(device: int):
    """Determines whether a device is a keyboard based on it's index"""
    return 0 <= device <= MAX_KEYBOARD - 1


def is_mouse(device: int):
    """Determines whether a device is a mouse based on it's index"""
    return MAX_KEYBOARD <= device <= (MAX_KEYBOARD + MAX_MOUSE) - 1


def is_invalid(device: int):
    """Determines whether a device is invalid based on it's index"""
    return not 0 <= device <= 19
