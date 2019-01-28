from interception import  *
from consts import *

if __name__ == "__main__":
    c = interception()
    c.set_filter(interception.is_keyboard,interception_filter_key_state.INTERCEPTION_FILTER_KEY_UP.value)
    while True:
        device = c.wait()
        stroke = c.receive(device)
        if type(stroke) is key_stroke:
            print(stroke.code)
        c.send(device,stroke)
        # hwid = c.get_HWID(device)
        # print(u"%s" % hwid)
    