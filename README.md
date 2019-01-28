# interception_py
This is a port (not a [wrapper][wrp]) of [interception][c_ception] dll to python, it communicates directly with interception's driver

### why not using the wrapper?
* it's very slow and some strokes are lost
* fast strokes made python crash (some heap allocation errors)

To make it run you should install the driver from [c-interception][c_ception]

### example
```py

from interception import  *

if __name__ == "__main__":
    c = interception()
    c.set_filter(interception.is_keyboard,interception_filter_key_state.INTERCEPTION_FILTER_KEY_UP.value)
    while True:
        device = c.wait()
        stroke = c.receive(device)
        if type(stroke) is key_stroke:
            print(stroke.code)
        c.send(device,stroke)
```


[wrp]: https://github.com/cobrce/interception_wrapper
[c_ception]: https://github.com/oblitum/Interception
