from __future__ import annotations

import struct

from typing import Protocol, ClassVar, TypeVar, Type
from dataclasses import dataclass, field


T = TypeVar("T", bound="Stroke")


class Stroke(Protocol):
    """The Protocol any stroke (input) must implement.

    This essentially requires the strokes to deal with conversions of the stroke
    between the c-struct that interception expects and the python object we use.

    Another option would be to use ctypes.Structure together with _fields_
    attributes to get rid of the conversion through struct.pack / struct.unpack,
    but doing things that way we would lose alot of the type-checking and IDE
    support for variable access.

    To pack the struct, we need a format for the packer to use that knows the
    size of each fields in bytes, you can read more about the format here:
    https://docs.python.org/3/library/struct.html#format-characters
    """

    format: ClassVar[bytes]

    @classmethod
    def parse(cls: Type[T], data: bytes) -> T: ...

    @property
    def data(self) -> bytes: ...


@dataclass
class MouseStroke:
    """The data of a single interception mouse stroke.

    Reference: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawmouse#members

    Attributes
    ----------
    flags :class:`int`:
       Combinations of `MouseState`, equivalent to referenced `usFlags` of `RAWMOUSE`

    button_flags :class:`int`:
        Combination of `MouseButtonFlag`, equivalent to referenced `usButtonFlags` of `RAWMOUSE`

    button_data :class:`int`:
        If button_flags named a MOUSE_WHEEL, specifies the distance the wheel is rotated.

    x :class:`int`:
        Signed relative motion or absolute motion in x direction, depending on the value of `flags`.

    y :class:`int`:
        Signed relative motion or absolute motion in y direction, depending on the value of `flags`.

    information :class:`int`:
        Additional device-specific information for the event. See `ulExtraInformation`\n
        This field is receive-only, setting this yourself doesnt change anything.
    """

    format: ClassVar[bytes] = b"HHHHIiiI"

    flags: int
    button_flags: int
    button_data: int
    x: int
    y: int

    information: int = field(init=False, default=0)
    _unit_id: int = field(init=False, default=0, repr=False)
    _raw_buttons: int = field(init=False, default=0, repr=False)

    @classmethod
    def parse(cls: Type[MouseStroke], data: bytes) -> MouseStroke:
        unpacked: tuple[int, ...] = struct.unpack(cls.format, data)

        # The order of the MouseStroke initializer doesnt match the values
        # arrangement in the bytes struct, so we need to 'pick' them in order.
        # This is because many of the fields are useless to initialize ourselves
        # and only report information of a received event.
        instance = cls(*(unpacked[i] for i in (1, 2, 3, 5, 6)))

        instance.information = unpacked[7]
        instance._unit_id = unpacked[0]
        instance._raw_buttons = unpacked[4]

        return instance

    @property
    def data(self) -> bytes:
        return struct.pack(
            self.format,
            self._unit_id,
            self.flags,
            self.button_flags,
            self.button_data,
            self._raw_buttons,
            self.x,
            self.y,
            self.information,
        )


@dataclass
class KeyStroke:
    """The data of a single interception key stroke.

    Reference: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawkeyboard#members

    Attributes
    ----------
    format :class:`bytes`:
        The format this struct is stored in, 4x `USHORT` and one `ULONG` (12 bytes total)

    code :class:`int`:
       Specifies the scan code, equivalent to referenced `MakeCode` of `RAWKEYBOARD`

    flags :class:`int`:
        Flags for scan code information, equivalent to referenced `Flags` of `RAWKEYBOARD`
    """

    format: ClassVar[bytes] = b"HHHHI"

    code: int
    flags: int

    information: int = field(init=False, default=0)
    _unit_id: int = field(init=False, default=0, repr=False)
    _reserved: int = field(init=False, default=0, repr=False)

    @classmethod
    def parse(cls: Type[KeyStroke], data: bytes) -> KeyStroke:
        unpacked: tuple[int, ...] = struct.unpack(cls.format, data)

        # The order of the KeyStroke initializer doesnt match the values
        # arrangement in the bytes struct, so we need to 'pick' them in order.
        # This is because when we initialize it ourselves, we dont care about
        # 'information' or 'unit_id', they are receive-only fields.
        instance = cls(*unpacked[1:3])
        instance._unit_id, instance.information = data[0], data[4]
        return instance

    @property
    def data(self) -> bytes:
        data = struct.pack(
            self.format,
            self._unit_id,
            self.code,
            self.flags,
            self._reserved,
            self.information,
        )
        return data
