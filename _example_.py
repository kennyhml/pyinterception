from interception import  *
from consts import *

if __name__ == "__main__":
    c = interception()
    c.set_filter(interception.is_mouse ,interception_filter_mouse_state.INTERCEPTION_FILTER_MOUSE_BUTTON_5_DOWN.value)
    while True:
        device = c.wait()
        print(device)
        stroke = c.receive(device)
        if type(stroke) is key_stroke:
            print(stroke.code)
        c.send(device,stroke)
        # hwid = c.get_HWID(device)
        # print(u"%s" % hwid)
    