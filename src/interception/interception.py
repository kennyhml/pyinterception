from ctypes import Array, c_void_p, windll
from typing import Final

from .device import Device
from .strokes import Stroke

MAX_DEVICES: Final = 20
MAX_KEYBOARD: Final = 10
MAX_MOUSE: Final = 10

k32 = windll.LoadLibrary("kernel32")


class Interception:
    def __init__(self) -> None:
        self._context: list[Device] = []
        self._c_events: Array[c_void_p] = (c_void_p * MAX_DEVICES)()
        self._mouse = 11
        self._keyboard = 1

        try:
            self.build_handles()
        except Exception as e:
            self.destroy()
            raise e

    @property
    def mouse(self) -> int:
        return self._mouse

    @mouse.setter
    def mouse(self, num: int) -> None:
        if self.is_invalid(num) or not self.is_mouse(num):
            raise ValueError(f"{num} is not a valid mouse number (10 <= mouse <= 19).")
        self._mouse = num

    @property
    def keyboard(self) -> int:
        return self._keyboard

    @keyboard.setter
    def keyboard(self, num: int) -> None:
        if self.is_invalid(num) or not self.is_keyboard(num):
            raise ValueError(
                f"{num} is not a valid keyboard number (0 <= keyboard <= 9)."
            )
        self._keyboard = num

    def build_handles(self) -> None:
        """Creates handles and events for all interception devices.

        Iterates over all interception devices and creates a `Device` object for each one.
        A `Device` object represents an interception device and includes a handle to the device,
        an event that can be used to wait for input on the device, and a flag indicating whether
        the device is a keyboard or a mouse.

        The handle is created using the `create_device_handle()` method, which calls the Windows API
        function `CreateFileA()` with the appropriate parameters.

        The event is created using the Windows API function `CreateEventA()`, which creates a
        synchronization event that can be signaled when input is available on the device.

        The `is_keyboard()` method is called to determine whether the device is a keyboard or a mouse.
        This is used to set the `is_keyboard` flag on the Device object.

        The created Device objects are added to the context list and the corresponding event
        handle is added to the c_events dictionary.

        Raises:
            IOError: If a device handle cannot be created.
        """
        for device_num in range(MAX_DEVICES):
            device = Device(
                self.create_device_handle(device_num),
                k32.CreateEventA(0, 1, 0, 0),
                is_keyboard=self.is_keyboard(device_num),
            )
            self._context.append(device)
            self._c_events[device_num] = device.event

    def wait(self, milliseconds: int = -1):
        """Waits for input on any interception device.

        Calls the `WaitForMultipleObjects()` Windows API function to wait for input on any of the
        interception devices. The function will block until input is available on one of the devices
        or until the specified timeout period (in milliseconds) has elapsed. If `milliseconds` is
        not specified or is negative, the function will block indefinitely until input is available.

        If input is available on a device, the function will return the index of the device in the
        `_c_events` dictionary, indicating which device received input. If the timeout period
        elapses before input is available, the function will return 0. If an error occurs, the function
        will raise an OSError.

        Raises:
            OSError: If an error occurs while waiting for input.
        """
        result = k32.WaitForMultipleObjects(
            MAX_DEVICES, self._c_events, 0, milliseconds
        )
        if result in [-1, 0x102]:
            return 0
        return result

    def get_HWID(self, device: int):
        """Returns the HWID of a device in the context"""
        if self.is_invalid(device):
            return ""
        try:
            return self._context[device].get_HWID().decode("utf-16")
        except:
            return ""

    def receive(self, device: int):
        if not self.is_invalid(device):
            return self._context[device].receive()

    def send(self, device: int, stroke: Stroke) -> None:
        self._context[device].send(stroke)

    def send_key(self, stroke: Stroke) -> None:
        self._context[self._keyboard].send(stroke)

    def send_mouse(self, stroke: Stroke) -> None:
        self._context[self._mouse].send(stroke)

    def set_filter(self, predicate, filter):
        for i in range(MAX_DEVICES):
            if predicate(i):
                result = self._context[i].set_filter(filter)

    @staticmethod
    def is_keyboard(device):
        return device + 1 > 0 and device + 1 <= MAX_KEYBOARD

    @staticmethod
    def is_mouse(device):
        return device + 1 > MAX_KEYBOARD and device + 1 <= MAX_KEYBOARD + MAX_MOUSE

    @staticmethod
    def is_invalid(device):
        return device + 1 <= 0 or device + 1 > (MAX_KEYBOARD + MAX_MOUSE)

    @staticmethod
    def create_device_handle(device_num: int):
        """Creates a handle to a specified device.

        Access mode for the device is `GENERIC_READ | GENERIC_WRITE`, allows the
        handle to read and write to the device.

        Sharing mode for the device is `FILE_SHARE_READ | FILE_SHARE_WRITE`, which
        allows other processes to read from and write to the device while it is open.

        Creation disposition for the device is `OPEN_EXISTING`, indicating that the device
        should be opened if it already exists.

        Flags and attributes for the device are not used in this case.
        """
        device_name = f"\\\\.\\interception{device_num:02d}".encode()
        return k32.CreateFileA(device_name, 0x80000000, 0, 0, 3, 0, 0)

    def destroy(self) -> None:
        for device in self._context:
            device.destroy()
