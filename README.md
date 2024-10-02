# pyinterception
This is a python **port and wrapper** for [interception][c_ception], a low level input device driver.

> The Interception API aims to build a portable programming interface that allows one to intercept and control a range of input devices.

## Installing
Pyinterception is available on PyPi as `interception-python`, so simply `pip install interception-python`.

## Why use the interception device driver?
Some people are under the impression that windows doesnt differentiate between *fake* inputs and *real* inputs, but that is **wrong**!

Take a look at [KBDLLHOOKSTRUCT][kbdllhook], specifically the `flags` field:
> Testing LLKHF_INJECTED (bit 4) will tell you whether the event was injected. If it was, then testing LLKHF_LOWER_IL_INJECTED (bit 1) will tell you whether or not the event was injected from a process running at lower integrity level.

This flag will **always** be set when sending an input through the windows API and there is nothing you can do about it. Programs may not pick up on this flag through the `KBDLLHOOKSTRUCT`, but it certainly proves that the OS clearly differentiates between inputs. 

If whatever you're sending inputs to currently works fine, and you are not worried about getting flagged by heuristic input detection, then by all means its totally fine to stick to pyautogui / pydirectinput.
At this point it is worth noting that alot of the more advanced anti-cheats including vanguard and some versions of EAC **will not boot** while the driver is loaded on your system, it is a very well known piece of software after all.
And if you're going to ask me how to bypass that detection - write your own driver.

## Why use this port?
- Very simple interface inspired by pyautogui / pydirectinput, the low-level communication is abstracted away.
- Dynamically obtains scancodes, thus doesnt depend on the order of your keyboard layout.
- Well documented for anyone who is interested in implementing any functionality themselves.
- Completely self-contained, no dependencies are required to use the library other than the driver itself!
- Supports keys that are extended or require a shift / alt / ctrl modifier to work.
- Supports 'human' movement by generating configurable [Bezier Curves][curve] - requires [PyClick][pyclick] to be installed.

## How is it used?
First of all, you absolutely need to install the [interception-driver][c_ception], otherwise none of this will work.

The first thing you are always going to want to call is `interception.auto_capture_devices()` in order for the library to get the correct device handles.
Explaining why would blow the scope of this introduction and you shouldn't have to worry about, just call the function and let it do it's thing!

Now you can begin to send inputs, just like you are used to it from pyautogui or pydirectinput!
```py
interception.move_to(960, 540)

with interception.hold_key("shift"):
    interception.press("a")

interception.click(120, 160, button="right", delay=1)
```

## Human Mouse Movement
Some people may need the library to move the mouse in a more 'human' fashion to be less vulnerable to heuristic input detection.

[PyClick][pyclick] already offers a great way to create custom Bezier Curves, so the library just makes use of that. To avoid bloat for the people who
do not care about this functionality, PyClick must be installed manually if you want to use it.

First create your Bezier Curve parameters container. You can either pass the params to `move_to` calls individually, or set them globally.
```py
from interception import beziercurve

curve_params = beziercurve.BezierCurveParams()

# Uses a bezier curve created with the specified parameters
interception.move_to(960, 540, params)

# Does not use a bezier curve, instead 'warps' to the location
interception.move_to(960, 540)

beziercurve.set_default_params(params)

# Uses the bezier curve parameters we just declared as default
interception.move_to(960, 540)

# Overrules the default bezier curve parameters and 'warps' instead
interception.move_to(960, 540, allow_global_params=False)
```

The resulting mouse movements look something like this (with the default curve parameters):
<p float="left">
  <img src="demo/curves.gif" width="650" height="245" />
</p>

[c_ception]: https://github.com/oblitum/Interception
[pyclick]: https://github.com/patrikoss/pyclick
[curve]: https://en.wikipedia.org/wiki/B%C3%A9zier_curve
[kbdllhook]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct?redirectedfrom=MSDN
