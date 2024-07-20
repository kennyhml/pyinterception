from __future__ import annotations

import ctypes
from ctypes.wintypes import HANDLE

from dataclasses import dataclass, field
from typing import Optional, Type
from .strokes import KeyStroke, MouseStroke, Stroke
from . import _ioctl


@dataclass
class DeviceIOResult:
    """Represents the result of a `DeviceIoControl` call.

    Parameters
    ----------
    succeeded :class:`bool`:
        Whether the DeviceIoControl call completed successfully

    outbuffer :class:`Optional[Array]`:
        The outbuffer passed to the DeviceIoControl call, or `None`

    Attributes
    ----------
    data_bytes :class:`Optional[bytes]`:
        The data as bytes if data is not `None`
    """

    succeeded: bool
    outbuffer: Optional[ctypes.Array]
    data: Optional[bytes] = field(init=False, repr=False)

    def __post_init__(self):
        self.data = None if self.outbuffer is None else bytes(self.outbuffer)


class Device:
    """Represents a windows IO mouse / keyboard device.

    Parameters
    ----------
    handle :class:`HANDLE`:
        The handle to the I/O device obtained through creation with `CreateFileA`

    event :class:`HANDLE`:
        The handle to the event object responsible for synchronization

    is_keyboard :class:`bool`:
        Whether the device is a keyboard device (otherwise mouse)

    To communicate with `DeviceIoControl`, buffers for the respective operations
    are created - but meant for internal use only.

    Raises
    ------
    `Exception`:
        If the device or event handle are invalid or the event could not synchronize.
    """

    def __init__(self, handle: HANDLE, event: HANDLE, *, is_keyboard: bool):
        if handle == -1 or event == 0:
            raise Exception("Handle and event must be valid to create device!")

        self.is_keyboard = is_keyboard
        self._parser: Type[KeyStroke] | Type[MouseStroke]
        if is_keyboard:
            self._stroke_buffer = (ctypes.c_ubyte * 12)()
            self._parser = KeyStroke
        else:
            self._stroke_buffer = (ctypes.c_ubyte * 24)()
            self._parser = MouseStroke

        self.handle = handle
        self.event = event

        # preferring personal buffers over shared buffers for thread safety
        self._bytes_returned = (ctypes.c_uint32 * 1)(0)
        self._hwid_buffer = (ctypes.c_byte * 500)()
        self._event_buffer = (ctypes.c_void_p * 2)()
        self._filter_buffer = (ctypes.c_ushort * 1)()
        self._prdc_buffer = (ctypes.c_int * 1)()

        if not self._device_set_event().succeeded:
            raise Exception("Can't communicate with driver")

    def __str__(self) -> str:
        return f"Device(handle={self.handle}, event={self.event}, is_keyboard: {self.is_keyboard})"

    def __repr__(self) -> str:
        return f"Device(handle={self.handle}, event={self.event}, is_keyboard: {self.is_keyboard})"

    def __del__(self) -> None:
        self.destroy()

    def destroy(self):
        """Closes the handles to the device, must be called before destruction
        in order to prevent handle leakage.
        """
        if self.handle != -1:
            ctypes.windll.kernel32.CloseHandle(self.handle)
            self.handle = -1

        if self.event:
            ctypes.windll.kernel32.CloseHandle(self.event)
            self.handle = 0

    def receive(self) -> Optional[Stroke]:
        """Receives the keystroke sent from this device.

        Must be the resulting device of a kernel32 `WaitForMultipleObjects` call to
        ensure that there is a valid input to be received.

        If no stroke could be received, `None` is returned instead.
        """
        data = self._receive().data
        return None if data is None else self._parser.parse(data)

    def send(self, stroke: Stroke) -> DeviceIOResult:
        """Sends the given stroke from this device.

        The `Stroke` must be compatible with the device type parser, i.e a mouse device
        is unable to send a `KeyStroke`.

        Raises
        ------
        `ValueError`:
            If the provided stroke is of an incompatible type for this device.
        """
        if not isinstance(stroke, self._parser):
            raise ValueError(
                f"Unable to send {type(stroke).__name__} with '{self._parser.__name__}' parser!"
            )
        return self._send(stroke)

    def get_precedence(self) -> DeviceIOResult:
        """Gets the device precedence"""
        return self._device_io_control(
            _ioctl.IOCTL_GET_PRECEDENCE, None, self._prdc_buffer
        )

    def set_precedence(self, precedence: int) -> DeviceIOResult:
        """Sets the device precedence"""
        self._prdc_buffer[0] = precedence
        return self._device_io_control(
            _ioctl.IOCTL_SET_PRECEDENCE, self._prdc_buffer, None
        )

    def get_filter(self) -> DeviceIOResult:
        """Retrieves the input filter for this device.

        TODO: Automatically parse it from the `DeviceIOResult`
        """
        return self._device_io_control(
            _ioctl.IOCTL_GET_FILTER, None, self._filter_buffer
        )

    def set_filter(self, filter: int) -> DeviceIOResult:
        """Sets the input filter for this device.

        The filter is a bitfield of Filter flags found in `_consts.py`
        """
        self._filter_buffer[0] = filter
        return self._device_io_control(
            _ioctl.IOCTL_SET_FILTER, self._filter_buffer, None
        )

    def get_HWID(self) -> Optional[str]:
        """Gets the Hardware ID of this device as a string.

        If the device is invalid, `None` is returned instead.
        """
        data = self._get_HWID().data
        size: int = self._bytes_returned[0]
        return None if data is None or not size else data[:size].decode("utf-16")

    def _get_HWID(self) -> DeviceIOResult:
        """Makes a low-level call to `DeviceIoControl` to get the hardware ID"""
        return self._device_io_control(
            _ioctl.IOCTL_GET_HARDWARE_ID, None, self._hwid_buffer
        )

    def _receive(self) -> DeviceIOResult:
        """Makes a low-level call to `DeviceIoControl` to read the device input"""
        return self._device_io_control(_ioctl.IOCTL_READ, None, self._stroke_buffer)

    def _send(self, stroke: Stroke) -> DeviceIOResult:
        """Makes a low-level call to `DeviceIoControl` to write to the device output."""
        ctypes.memmove(self._stroke_buffer, stroke.data, len(self._stroke_buffer))
        return self._device_io_control(_ioctl.IOCTL_WRITE, self._stroke_buffer, None)

    def _device_set_event(self) -> DeviceIOResult:
        """Makes a low-level call to `DeviceIoControl` to synchronize the event object"""
        self._event_buffer[0] = self.event
        return self._device_io_control(_ioctl.IOCTL_SET_EVENT, self._event_buffer, None)

    def _device_io_control(
        self,
        command: int,
        inbuffer: Optional[ctypes.Array] = None,
        outbuffer: Optional[ctypes.Array] = None,
    ) -> DeviceIOResult:
        """The heart of the device operations, makes a call to `DeviceIoControl` with
        the provided arguments.

        Parameters
        ----------
        command :class:`int`:
            An IOCTL (I/O Control) command value that specifies the operation, see `_ioctl.py`

        inbuffer :class:`Optional[Array]`:
            A buffer containing the data to send to the operation, should it require input data.

        outbuffer :class:`Optional[Array]`:
            A buffer to hold the data of the operation, should it require an output buffer.

        See: https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-deviceiocontrol
        """
        res = ctypes.windll.kernel32.DeviceIoControl(
            self.handle,
            command,
            inbuffer,
            len(bytes(inbuffer)) if inbuffer is not None else 0,
            outbuffer,
            len(bytes(outbuffer)) if outbuffer is not None else 0,
            self._bytes_returned,
            0,
        )
        return DeviceIOResult(res, outbuffer)
