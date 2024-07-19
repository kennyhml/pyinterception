from __future__ import annotations

import ctypes

from dataclasses import dataclass, field
from typing import Optional, Type
from .strokes import KeyStroke, MouseStroke, Stroke
from . import _ioctl


@dataclass
class DeviceIOResult:
    """Represents the result of an IO operation on a `Device`."""

    result: int
    data: Optional[ctypes.Array]
    data_bytes: bytes = field(init=False, repr=False)

    def __post_init__(self):
        if self.data is not None:
            self.data_bytes = bytes(self.data)


class Device:
    def __init__(self, handle, event, *, is_keyboard: bool):
        self.is_keyboard = is_keyboard
        self._parser: Type[KeyStroke] | Type[MouseStroke]
        if is_keyboard:
            self._c_recv_buffer = (ctypes.c_ubyte * 12)()
            self._parser = KeyStroke
        else:
            self._c_recv_buffer = (ctypes.c_ubyte * 24)()
            self._parser = MouseStroke

        if handle == -1 or event == 0:
            raise Exception("Can't create device!")

        self.handle = handle
        self.event = event

        self._bytes_returned = (ctypes.c_uint32 * 1)(0)
        self._hwid_buffer = (ctypes.c_byte * 500)()
        self._event_handle = (ctypes.c_int * 2)()
        self._filter_buffer = (ctypes.c_ushort * 1)()
        self._prdc_buffer = (ctypes.c_int * 1)()

        if self._device_set_event().result == 0:
            raise Exception("Can't communicate with driver")

    def __str__(self) -> str:
        return f"Device(handle={self.handle}, event={self.event}, is_keyboard: {self.is_keyboard})"

    def __repr__(self) -> str:
        return f"Device(handle={self.handle}, event={self.event}, is_keyboard: {self.is_keyboard})"

    def destroy(self):
        if self.handle != -1:
            ctypes.windll.kernel32.CloseHandle(self.handle)

        if self.event:
            ctypes.windll.kernel32.CloseHandle(self.event)

    def receive(self) -> Stroke:
        data = self._receive().data_bytes
        return self._parser.parse(data)

    def send(self, stroke: Stroke) -> DeviceIOResult:
        if not isinstance(stroke, self._parser):
            raise ValueError(f"Can't parse {stroke} with {self._parser.__name__}!")
        return self._send(stroke)

    def get_precedence(self) -> DeviceIOResult:
        return self._device_io_control(
            _ioctl.IOCTL_GET_PRECEDENCE, None, self._prdc_buffer
        )

    def set_precedence(self, precedence: int) -> DeviceIOResult:
        self._prdc_buffer[0] = precedence
        return self._device_io_control(
            _ioctl.IOCTL_SET_PRECEDENCE, self._prdc_buffer, None
        )

    def get_filter(self) -> DeviceIOResult:
        return self._device_io_control(
            _ioctl.IOCTL_GET_FILTER, None, self._filter_buffer
        )

    def set_filter(self, filter) -> DeviceIOResult:
        self._filter_buffer[0] = filter
        return self._device_io_control(
            _ioctl.IOCTL_SET_FILTER, self._filter_buffer, None
        )

    def get_HWID(self) -> str:
        data = self._get_HWID().data_bytes
        return data[0 : self._bytes_returned[0]].decode("utf-16")

    def _get_HWID(self) -> DeviceIOResult:
        return self._device_io_control(
            _ioctl.IOCTL_GET_HARDWARE_ID, None, self._hwid_buffer
        )

    def _receive(self) -> DeviceIOResult:
        return self._device_io_control(_ioctl.IOCTL_READ, None, self._c_recv_buffer)

    def _send(self, stroke: Stroke) -> DeviceIOResult:
        ctypes.memmove(self._c_recv_buffer, stroke.data, len(self._c_recv_buffer))
        return self._device_io_control(_ioctl.IOCTL_WRITE, self._c_recv_buffer, None)

    def _device_set_event(self) -> DeviceIOResult:
        self._event_handle[0] = self.event
        return self._device_io_control(_ioctl.IOCTL_SET_EVENT, self._event_handle, None)

    def _device_io_control(
        self,
        command: int,
        inbuffer: Optional[ctypes.Array] = None,
        outbuffer: Optional[ctypes.Array] = None,
    ) -> DeviceIOResult:
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
