import struct
from typing import Protocol


class Stroke(Protocol):

    @classmethod
    def parse(cls, self):
        ...

    @classmethod
    def parse_raw(cls, self):
        ...

    @property
    def data(self):
        ...

    @property
    def raw_data(self):
        ...


class MouseStroke:
    fmt = "HHhiiI"
    fmt_raw = "HHHHIiiI"

    def __init__(self, state, flags, rolling, x, y, information):
        self.state = state
        self.flags = flags
        self.rolling = rolling
        self.x = x
        self.y = y
        self.information = information

    @classmethod
    def parse(cls, data):
        return cls(*struct.unpack(cls.fmt, data))

    @classmethod
    def parse_raw(cls, data):
        unpacked = struct.unpack(cls.fmt_raw, data)
        return cls(**(unpacked[i] for i in (2, 1, 3, 5, 6, 7)))

    @property
    def data(self) -> bytes:
        return struct.pack(
            self.fmt,
            self.state,
            self.flags,
            self.rolling,
            self.x,
            self.y,
            self.information,
        )

    @property
    def raw_data(self) -> bytes:
        return struct.pack(
            self.fmt_raw,
            0,
            self.flags,
            self.state,
            self.rolling,
            0,
            self.x,
            self.y,
            self.information,
        )


class KeyStroke:
    fmt = "HHI"
    fmt_raw = "HHHHI"

    def __init__(self, code, state, information):
        self.code = code
        self.state = state
        self.information = information

    @classmethod
    def parse(cls, data):
        return cls(*struct.unpack(cls.fmt, data))

    @classmethod
    def parse_raw(cls, data):
        unpacked = struct.unpack(cls.fmt_raw, data)
        return cls(unpacked[1], unpacked[2], unpacked[4])

    @property
    def data(self):
        data = struct.pack(self.fmt, self.code, self.state, self.information)
        return data

    @property
    def raw_data(self):
        data = struct.pack(self.fmt_raw, 0, self.code, self.state, 0, self.information)
        return data
