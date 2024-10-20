from ctypes import windll, wintypes
from dataclasses import dataclass
import functools

from .exceptions import UnknownKeyError


@dataclass
class KeyData:
    vk_code: int = -1
    scan_code: int = -1

    shift: bool = False
    ctrl: bool = False
    alt: bool = False
    is_extended: bool = False


_KEYBOARD_KEYS: list[str] = [
    "\t",
    "\n",
    "\r",
    " ",
    "!",
    '"',
    "#",
    "$",
    "%",
    "&",
    "'",
    "(",
    ")",
    "*",
    "+",
    ",",
    "-",
    ".",
    "/",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    ":",
    ";",
    "<",
    "=",
    ">",
    "?",
    "@",
    "[",
    "\\",
    "]",
    "^",
    "_",
    "`",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "{",
    "|",
    "}",
    "~",
    "accept",
    "add",
    "alt",
    "altleft",
    "altright",
    "apps",
    "backspace",
    "browserback",
    "browserfavorites",
    "browserforward",
    "browserhome",
    "browserrefresh",
    "browsersearch",
    "browserstop",
    "capslock",
    "clear",
    "convert",
    "ctrl",
    "ctrlleft",
    "ctrlright",
    "decimal",
    "del",
    "delete",
    "divide",
    "down",
    "end",
    "enter",
    "esc",
    "escape",
    "execute",
    "f1",
    "f10",
    "f11",
    "f12",
    "f13",
    "f14",
    "f15",
    "f16",
    "f17",
    "f18",
    "f19",
    "f2",
    "f20",
    "f21",
    "f22",
    "f23",
    "f24",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "final",
    "fn",
    "hanguel",
    "hangul",
    "hanja",
    "help",
    "home",
    "insert",
    "junja",
    "kana",
    "kanji",
    "launchapp1",
    "launchapp2",
    "launchmail",
    "launchmediaselect",
    "left",
    "modechange",
    "multiply",
    "nexttrack",
    "nonconvert",
    "num0",
    "num1",
    "num2",
    "num3",
    "num4",
    "num5",
    "num6",
    "num7",
    "num8",
    "num9",
    "numlock",
    "pagedown",
    "pageup",
    "pause",
    "pgdn",
    "pgup",
    "playpause",
    "prevtrack",
    "printscreen",
    "prntscrn",
    "prtsc",
    "prtscr",
    "return",
    "right",
    "scrolllock",
    "select",
    "separator",
    "shift",
    "shiftleft",
    "shiftright",
    "sleep",
    "space",
    "stop",
    "subtract",
    "tab",
    "up",
    "volumedown",
    "volumemute",
    "volumeup",
    "win",
    "winleft",
    "winright",
    "yen",
    "command",
    "option",
    "optionleft",
    "optionright",
]

_MAPPING: dict[str, int] = {key: -1 for key in _KEYBOARD_KEYS}
_MAPPING.update(
    {
        "backspace": 0x08,  # VK_BACK
        "\b": 0x08,  # VK_BACK
        "super": 0x5B,  # VK_LWIN
        "tab": 0x09,  # VK_TAB
        "\t": 0x09,  # VK_TAB
        "clear": 0x0C,  # VK_CLEAR
        "enter": 0x0D,  # VK_RETURN
        "\n": 0x0D,  # VK_RETURN
        "return": 0x0D,  # VK_RETURN
        "shift": 0x10,  # VK_SHIFT
        "ctrl": 0x11,  # VK_CONTROL
        "alt": 0x12,  # VK_MENU
        "pause": 0x13,  # VK_PAUSE
        "capslock": 0x14,  # VK_CAPITAL
        "kana": 0x15,  # VK_KANA
        "hanguel": 0x15,  # VK_HANGUEL
        "hangul": 0x15,  # VK_HANGUL
        "junja": 0x17,  # VK_JUNJA
        "final": 0x18,  # VK_FINAL
        "hanja": 0x19,  # VK_HANJA
        "kanji": 0x19,  # VK_KANJI
        "esc": 0x1B,  # VK_ESCAPE
        "escape": 0x1B,  # VK_ESCAPE
        "convert": 0x1C,  # VK_CONVERT
        "nonconvert": 0x1D,  # VK_NONCONVERT
        "accept": 0x1E,  # VK_ACCEPT
        "modechange": 0x1F,  # VK_MODECHANGE
        " ": 0x20,  # VK_SPACE
        "space": 0x20,  # VK_SPACE
        "pgup": 0x21,  # VK_PRIOR
        "pgdn": 0x22,  # VK_NEXT
        "pageup": 0x21,  # VK_PRIOR
        "pagedown": 0x22,  # VK_NEXT
        "end": 0x23,  # VK_END
        "home": 0x24,  # VK_HOME
        "left": 0x25,  # VK_LEFT
        "up": 0x26,  # VK_UP
        "right": 0x27,  # VK_RIGHT
        "down": 0x28,  # VK_DOWN
        "select": 0x29,  # VK_SELECT
        "print": 0x2A,  # VK_PRINT
        "execute": 0x2B,  # VK_EXECUTE
        "prtsc": 0x2C,  # VK_SNAPSHOT
        "prtscr": 0x2C,  # VK_SNAPSHOT
        "prntscrn": 0x2C,  # VK_SNAPSHOT
        "printscreen": 0x2C,  # VK_SNAPSHOT
        "insert": 0x2D,  # VK_INSERT
        "del": 0x2E,  # VK_DELETE
        "delete": 0x2E,  # VK_DELETE
        "help": 0x2F,  # VK_HELP
        "win": 0x5B,  # VK_LWIN
        "winleft": 0x5B,  # VK_LWIN
        "winright": 0x5C,  # VK_RWIN
        "apps": 0x5D,  # VK_APPS
        "sleep": 0x5F,  # VK_SLEEP
        "num0": 0x60,  # VK_NUMPAD0
        "num1": 0x61,  # VK_NUMPAD1
        "num2": 0x62,  # VK_NUMPAD2
        "num3": 0x63,  # VK_NUMPAD3
        "num4": 0x64,  # VK_NUMPAD4
        "num5": 0x65,  # VK_NUMPAD5
        "num6": 0x66,  # VK_NUMPAD6
        "num7": 0x67,  # VK_NUMPAD7
        "num8": 0x68,  # VK_NUMPAD8
        "num9": 0x69,  # VK_NUMPAD9
        "multiply": 0x6A,  # VK_MULTIPLY  ??? Is this the numpad *?
        "add": 0x6B,  # VK_ADD  ??? Is this the numpad +?
        "separator": 0x6C,  # VK_SEPARATOR  ??? Is this the numpad enter?
        "subtract": 0x6D,  # VK_SUBTRACT  ??? Is this the numpad -?
        "decimal": 0x6E,  # VK_DECIMAL
        "divide": 0x6F,  # VK_DIVIDE
        "f1": 0x70,  # VK_F1
        "f2": 0x71,  # VK_F2
        "f3": 0x72,  # VK_F3
        "f4": 0x73,  # VK_F4
        "f5": 0x74,  # VK_F5
        "f6": 0x75,  # VK_F6
        "f7": 0x76,  # VK_F7
        "f8": 0x77,  # VK_F8
        "f9": 0x78,  # VK_F9
        "f10": 0x79,  # VK_F10
        "f11": 0x7A,  # VK_F11
        "f12": 0x7B,  # VK_F12
        "f13": 0x7C,  # VK_F13
        "f14": 0x7D,  # VK_F14
        "f15": 0x7E,  # VK_F15
        "f16": 0x7F,  # VK_F16
        "f17": 0x80,  # VK_F17
        "f18": 0x81,  # VK_F18
        "f19": 0x82,  # VK_F19
        "f20": 0x83,  # VK_F20
        "f21": 0x84,  # VK_F21
        "f22": 0x85,  # VK_F22
        "f23": 0x86,  # VK_F23
        "f24": 0x87,  # VK_F24
        "numlock": 0x90,  # VK_NUMLOCK
        "scrolllock": 0x91,  # VK_SCROLL
        "shiftleft": 0xA0,  # VK_LSHIFT
        "shiftright": 0xA1,  # VK_RSHIFT
        "ctrlleft": 0xA2,  # VK_LCONTROL
        "ctrlright": 0xA3,  # VK_RCONTROL
        "altleft": 0xA4,  # VK_LMENU
        "altright": 0xA5,  # VK_RMENU
        "browserback": 0xA6,  # VK_BROWSER_BACK
        "browserforward": 0xA7,  # VK_BROWSER_FORWARD
        "browserrefresh": 0xA8,  # VK_BROWSER_REFRESH
        "browserstop": 0xA9,  # VK_BROWSER_STOP
        "browsersearch": 0xAA,  # VK_BROWSER_SEARCH
        "browserfavorites": 0xAB,  # VK_BROWSER_FAVORITES
        "browserhome": 0xAC,  # VK_BROWSER_HOME
        "volumemute": 0xAD,  # VK_VOLUME_MUTE
        "volumedown": 0xAE,  # VK_VOLUME_DOWN
        "volumeup": 0xAF,  # VK_VOLUME_UP
        "nexttrack": 0xB0,  # VK_MEDIA_NEXT_TRACK
        "prevtrack": 0xB1,  # VK_MEDIA_PREV_TRACK
        "stop": 0xB2,  # VK_MEDIA_STOP
        "playpause": 0xB3,  # VK_MEDIA_PLAY_PAUSE
        "launchmail": 0xB4,  # VK_LAUNCH_MAIL
        "launchmediaselect": 0xB5,  # VK_LAUNCH_MEDIA_SELECT
        "launchapp1": 0xB6,  # VK_LAUNCH_APP1
        "launchapp2": 0xB7,  # VK_LAUNCH_APP2
    }
)

extended_keys = {
    0xa5, # VK_RMENU
    0x2e, # VK_DELETE
    0x2d, # VK_INSERT
    0x22, # VK_NEXT
    0x21, # VK_PRIOR
    0x24, # VK_HOME
    0x23, # VK_END
    0x25, # VK_LEFT
    0x27, # VK_RIGHT
    0x26, # VK_UP
    0x28, # VK_DOWN
}

SHIFT_FLAG = 1
ALT_FLAG = 2
CTRL_FLAG = 4

MAPVK_VK_TO_VSC_EX = 4

# ascii characters from 32 (space) to 126 (~), see https://www.asciitable.com/
# these are constants, but its easier to just map them like this than maintaining
# an even bigger table.
for c in range(32, 127):
    _MAPPING[chr(c)] = windll.user32.VkKeyScanA(wintypes.WCHAR(chr(c)))


@functools.cache
def get_key_information(key: str) -> KeyData:
    if key not in _MAPPING:
        raise UnknownKeyError(key)

    res = KeyData()

    # Split the modifiers (high byte) from the virtual code (low byte)
    # That way we can check whether we have to include shift / ctrl / alt for this key
    vk = _MAPPING[key]
    modifiers, res.vk_code = divmod(vk, 0x100)

    res.shift |= bool(modifiers & SHIFT_FLAG)
    res.ctrl |= bool(modifiers & CTRL_FLAG)
    res.alt |= bool(modifiers & ALT_FLAG)

    # Use MAPVK_VK_TO_VSC_EX, see https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mapvirtualkeya
    # If it is a virtual-key code that does not distinguish between left- and right-hand keys,
    # the left-hand scan code is returned. If the scan code is an extended scan code, the high
    # byte of the returned value will contain either 0xe0 or 0xe1 to specify the extended scan
    # code. If there is no translation, the function returns 0.
    scan_code = windll.user32.MapVirtualKeyA(res.vk_code, MAPVK_VK_TO_VSC_EX)
    res.scan_code = scan_code & 0xFF
    res.is_extended = bool(((scan_code >> 8) & 0xFF) & 0xE0) or res.vk_code in extended_keys

    return res
