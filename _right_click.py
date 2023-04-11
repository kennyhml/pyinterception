import time

import pyautogui
from interception import *
from win32api import GetSystemMetrics

# get screen size
screen_width = GetSystemMetrics(0)
screen_height = GetSystemMetrics(1)

# create a context for interception to use to send strokes, in this case
# we won't use filters, we will manually search for the first found mouse
context = interception()

# loop through all devices and check if they correspond to a mouse
mouse = 0
for i in range(MAX_DEVICES):
    if interception.is_mouse(i):
        mouse = i
        break

# no mouse we quit
if mouse == 0:
    print("No mouse found")
    exit(0)

_screen_width = GetSystemMetrics(0)
_screen_height = GetSystemMetrics(1)

def to_hexadecimal(screen_size: int, i: int):
    return int((0xFFFF / screen_size) * i)

x, y = 1439,230
# we create a new mouse stroke, initially we use set right button down, we also use absolute move,
# and for the coordinate (x and y) we use center screen
mstroke = mouse_stroke(
    0,
    interception_mouse_flag.INTERCEPTION_MOUSE_MOVE_ABSOLUTE.value,
    0,
    to_hexadecimal(_screen_width, x),
    to_hexadecimal(_screen_height, y),
    0,
)

context.send(13, mstroke)  # we send the key stroke, now the right button is down

time.sleep(1)


mstroke.state = (
    interception_mouse_state.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP.value
)  # update the stroke to release the button
context.send(15, mstroke)  # button right is up
