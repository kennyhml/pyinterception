from interception import *
from consts import *

SCANCODE_ESC = 0x01

if __name__ == "__main__":
    c = interception()
    c.set_filter(interception.is_keyboard,interception_filter_key_state.INTERCEPTION_FILTER_KEY_UP.value | interception_filter_key_state.INTERCEPTION_FILTER_KEY_DOWN.value)
    c.set_filter(interception.is_mouse,interception_filter_mouse_state.INTERCEPTION_FILTER_MOUSE_LEFT_BUTTON_DOWN.value)
    while True:
        device = c.wait()
        stroke = c.receive(device)
        c.send(device,stroke)
        if stroke is None or (interception.is_keyboard(device) and stroke.code == SCANCODE_ESC):
            break
        print(c.get_HWID(device))
    c._destroy_context()
