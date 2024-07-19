from __future__ import annotations
from enum import IntEnum


class KeyFlag(IntEnum):
    """
    Interception uses the key flag enums as defined per win32.

    See `Flags` member: https://learn.microsoft.com/de-de/windows/win32/api/winuser/ns-winuser-rawkeyboard#members
    """

    KEY_DOWN = 0x00
    KEY_UP = 0x01
    KEY_E0 = 0x02
    KEY_E1 = 0x04
    KEY_TERMSRV_SET_LED = 0x08
    KEY_TERMSRV_SHADOW = 0x10
    KEY_TERMSRV_VKPACKET = 0x20


class MouseButtonFlag(IntEnum):
    """
    Interception uses the mouse button flag enums as defined per win32.

    See usButtonFlags member: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawmouse#members
    """

    MOUSE_LEFT_BUTTON_DOWN = 0x001
    MOUSE_LEFT_BUTTON_UP = 0x002
    MOUSE_RIGHT_BUTTON_DOWN = 0x004
    MOUSE_RIGHT_BUTTON_UP = 0x008
    MOUSE_MIDDLE_BUTTON_DOWN = 0x010
    MOUSE_MIDDLE_BUTTON_UP = 0x020

    MOUSE_BUTTON_4_DOWN = 0x040
    MOUSE_BUTTON_4_UP = 0x080
    MOUSE_BUTTON_5_DOWN = 0x100
    MOUSE_BUTTON_5_UP = 0x200

    MOUSE_WHEEL = 0x400
    MOUSE_HWHEEL = 0x800

    @staticmethod
    def from_string(button: str) -> tuple[MouseButtonFlag, MouseButtonFlag]:
        return _MAPPED_MOUSE_BUTTONS[button]


class MouseFlag(IntEnum):
    """
    Interception uses the mouse state enums as defined per win32.

    See usFlags member: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawmouse#members
    """

    MOUSE_MOVE_RELATIVE = 0x000
    MOUSE_MOVE_ABSOLUTE = 0x001
    MOUSE_VIRTUAL_DESKTOP = 0x002
    MOUSE_ATTRIBUTES_CHANGED = 0x004
    MOUSE_MOVE_NOCOALESCE = 0x008
    MOUSE_TERMSRV_SRC_SHADOW = 0x100


class MouseRolling(IntEnum):
    """
    See: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawmouse#remarks

    The wheel rotation will be a multiple of WHEEL_DELTA, which is set at 120.
    This is the threshold for action to be taken, and one such action should occur for each delta.
    """

    MOUSE_WHEEL_UP = 0x78
    MOUSE_WHEEL_DOWN = 0xFF88


class FilterMouseButtonFlag(IntEnum):
    FILTER_MOUSE_NONE = 0x0000
    FILTER_MOUSE_ALL = 0xFFFF

    FILTER_MOUSE_LEFT_BUTTON_DOWN = MouseButtonFlag.MOUSE_LEFT_BUTTON_DOWN
    FILTER_MOUSE_LEFT_BUTTON_UP = MouseButtonFlag.MOUSE_LEFT_BUTTON_UP
    FILTER_MOUSE_RIGHT_BUTTON_DOWN = MouseButtonFlag.MOUSE_RIGHT_BUTTON_DOWN
    FILTER_MOUSE_RIGHT_BUTTON_UP = MouseButtonFlag.MOUSE_RIGHT_BUTTON_UP
    FILTER_MOUSE_MIDDLE_BUTTON_DOWN = MouseButtonFlag.MOUSE_MIDDLE_BUTTON_DOWN
    FILTER_MOUSE_MIDDLE_BUTTON_UP = MouseButtonFlag.MOUSE_MIDDLE_BUTTON_UP

    FILTER_MOUSE_BUTTON_4_DOWN = MouseButtonFlag.MOUSE_BUTTON_4_DOWN
    FILTER_MOUSE_BUTTON_4_UP = MouseButtonFlag.MOUSE_BUTTON_4_UP
    FILTER_MOUSE_BUTTON_5_DOWN = MouseButtonFlag.MOUSE_BUTTON_5_DOWN
    FILTER_MOUSE_BUTTON_5_UP = MouseButtonFlag.MOUSE_BUTTON_5_UP

    FILTER_MOUSE_WHEEL = MouseButtonFlag.MOUSE_WHEEL
    FILTER_MOUSE_HWHEEL = MouseButtonFlag.MOUSE_HWHEEL
    FILTER_MOUSE_MOVE = 0x1000


class FilterKeyFlag(IntEnum):
    FILTER_KEY_NONE = 0x0000
    FILTER_KEY_ALL = 0xFFFF
    FILTER_KEY_DOWN = KeyFlag.KEY_UP
    FILTER_KEY_UP = KeyFlag.KEY_UP << 1
    FILTER_KEY_E0 = KeyFlag.KEY_E0 << 1
    FILTER_KEY_E1 = KeyFlag.KEY_E1 << 1
    FILTER_KEY_TERMSRV_SET_LED = KeyFlag.KEY_TERMSRV_SET_LED << 1
    FILTER_KEY_TERMSRV_SHADOW = KeyFlag.KEY_TERMSRV_SHADOW << 1
    FILTER_KEY_TERMSRV_VKPACKET = KeyFlag.KEY_TERMSRV_VKPACKET << 1


_MAPPED_MOUSE_BUTTONS = {
    "left": (
        MouseButtonFlag.MOUSE_LEFT_BUTTON_DOWN,
        MouseButtonFlag.MOUSE_LEFT_BUTTON_UP,
    ),
    "right": (
        MouseButtonFlag.MOUSE_RIGHT_BUTTON_DOWN,
        MouseButtonFlag.MOUSE_RIGHT_BUTTON_UP,
    ),
    "middle": (
        MouseButtonFlag.MOUSE_MIDDLE_BUTTON_DOWN,
        MouseButtonFlag.MOUSE_MIDDLE_BUTTON_UP,
    ),
    "mouse4": (MouseButtonFlag.MOUSE_BUTTON_4_DOWN, MouseButtonFlag.MOUSE_BUTTON_4_UP),
    "mouse5": (MouseButtonFlag.MOUSE_BUTTON_5_DOWN, MouseButtonFlag.MOUSE_BUTTON_5_UP),
}
