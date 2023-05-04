from __future__ import annotations

from ctypes import c_byte, c_int, c_ubyte, c_ushort, memmove, windll
from dataclasses import dataclass, field
from typing import Any, Type

from .strokes import KeyStroke, MouseStroke, Stroke

k32 = windll.LoadLibrary("kernel32")


def device_io_call(decorated):
    def decorator(device: Device, *args, **kwargs):
        command, inbuffer, outbuffer = decorated(device, *args, **kwargs)
        return device._device_io_control(command, inbuffer, outbuffer)

    return decorator


@dataclass
class DeviceIOResult:
    """Represents the result of an IO operation on a `Device`."""
    result: int
    data: Any
    data_bytes: bytes = field(init=False, repr=False)

    def __post_init__(self):
        if self.data is not None:
            self.data = list(self.data)
            self.data_bytes = bytes(self.data)


class Device:
    _bytes_returned = (c_int * 1)(0)
    _c_byte_500 = (c_byte * 500)()
    _c_int_2 = (c_int * 2)()
    _c_ushort_1 = (c_ushort * 1)()
    _c_int_1 = (c_int * 1)()

    def __init__(self, handle, event, *, is_keyboard: bool):
        self.is_keyboard = is_keyboard
        self._parser: Type[KeyStroke] | Type[MouseStroke]
        if is_keyboard:
            self._c_recv_buffer = (c_ubyte * 12)()
            self._parser = KeyStroke
        else:
            self._c_recv_buffer = (c_ubyte * 24)()
            self._parser = MouseStroke

        if handle == -1 or event == 0:
            raise Exception("Can't create device!")

        self.handle = handle
        self.event = event

        if self._device_set_event().result == 0:
            raise Exception("Can't communicate with driver")

    def __str__(self) -> str:
        return f"Device(handle={self.handle}, event={self.event}, is_keyboard: {self.is_keyboard})"

    def __repr__(self) -> str:
        return f"Device(handle={self.handle}, event={self.event}, is_keyboard: {self.is_keyboard})"

    def destroy(self):
        if self.handle != -1:
            k32.CloseHandle(self.handle)

        if self.event:
            k32.CloseHandle(self.event)

    @device_io_call
    def get_precedence(self):
        return 0x222008, 0, self._c_int_1

    @device_io_call
    def set_precedence(self, precedence: int):
        self._c_int_1[0] = precedence
        return 0x222004, self._c_int_1, 0

    @device_io_call
    def get_filter(self):
        return 0x222020, 0, self._c_ushort_1

    @device_io_call
    def set_filter(self, filter):
        self._c_ushort_1[0] = filter
        return 0x222010, self._c_ushort_1, 0

    @device_io_call
    def _get_HWID(self):
        return 0x222200, 0, self._c_byte_500

    def get_HWID(self):
        data = self._get_HWID().data_bytes
        return data[:self._bytes_returned[0]]

    @device_io_call
    def _receive(self):
        return 0x222100, 0, self._c_recv_buffer

    def receive(self):
        data = self._receive().data_bytes
        return self._parser.parse_raw(data)

    def send(self, stroke: Stroke):
        if not isinstance(stroke, self._parser):
            raise ValueError(
                f"Can't parse {stroke} with {self._parser.__name__} parser!"
            )
        self._send(stroke)

    @device_io_call
    def _send(self, stroke: Stroke):
        memmove(self._c_recv_buffer, stroke.raw_data, len(self._c_recv_buffer))
        return 0x222080, self._c_recv_buffer, 0

    @device_io_call
    def _device_set_event(self):
        self._c_int_2[0] = self.event
        return 0x222040, self._c_int_2, 0

    def _device_io_control(self, command, inbuffer, outbuffer) -> DeviceIOResult:
        res = k32.DeviceIoControl(
            self.handle,
            command,
            inbuffer,
            len(bytes(inbuffer)) if inbuffer else 0,
            outbuffer,
            len(bytes(outbuffer)) if outbuffer else 0,
            self._bytes_returned,
            0,
        )

        return DeviceIOResult(res, outbuffer if outbuffer else None)
