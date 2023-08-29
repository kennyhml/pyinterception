# pyinterception
This is a greatly reworked version of [interception_py][wrp], a python port for [interception][c_ception], which is now obsolete and points here instead.

The Interception API aims to build a portable programming interface that allows one to intercept and control a range of input devices.

## How to install
Pyinterception is now available on PyPi under the name `interception-python`! So simply `pip install interception-python`.


## Why use interception?
Did you ever try to send inputs to an application or game and, well, nothing happened? Sure, in alot of cases this is resolved by running your
code with administrative privileges, but this is not always the case.

Take parsec as example, you are entirely unable to send any simulated inputs to parsec, but it has no problems with real inputs, so why is this?

Long story short, injected inputs actually have a `LowLevelKeyHookInjected` (0x10) flag. This flag will **always** be set when sending an Input with `SendInput` or the even older `mouse_event` and `keyb_event`. This flag is not at all hard to pick up for programs, if you have python3.7 and pyHook installed, you can try it yourself using this code:

```py
import pyHook
import pythoncom

def keyb_event(event):

    if event.flags & 0x10:
        print("Injected input sent")
    else:
        print("Real input sent")

    return True

hm = pyHook.HookManager()
hm.KeyDown = keyb_event

hm.HookKeyboard()

pythoncom.PumpMessages()
```
You will quickly see that, no matter what conventional python library you try, all of them will be flagged as injected. Thats because in the end, they all either rely on `SendInput` or `keyb_event` | `mouse_event`.

Why is this bad? Well, it's not always bad. If whatever you're sending inputs to currently works fine, and you are not worried about getting flagged by some sort of anti-cheat, then by all means its totally fine to stick to pyautogui / pydirectinput.

Alright, enough about that, onto the important shit.

## Why use this port?
- Extremely simple interface, comparable to pyautogui / pydirectinput
- Dynamic keyboard adjustment for all kinds of layouts
- Refactored in a much more readable and documented fashion
- I work with loads of automation first hand so there is alot of QoL features.

## How to use?
First of all, you absolutely need to install the [interception-driver][c_ception], otherwise none of this will work. It's a very simple install.

Now, once you have all of that set up, you can go ahead and import `interception`. 
The first thing you need to understand is that you have 10 different numbers for keyboard / mouse, and any of them could be the device you are
using. You can observe this by running the following program:
```py
import interception

interception.capture_keyboard()
interception.capture_mouse()
```
You can cancel the capture by pressing the ESC key, but every time you press a key or click with the mouse, you can see the intercepted event in the terminal.
The event consists of different kinds of flags and states, but also of the number of your device we just talked about.

To make sure that interception can actively send inputs from the correct devices, you have to set the correct devices. You can do this by manually checking the output,
but that gets pretty annoying as they can and will change sometimes. To make this easier, pyinterception has a method that will automatically capture a working device:
```py
import interception

interception.auto_capture_devices(keyboard=True, mouse=True)
```
So, now you can begin to send inputs, just like you are used to it from pyautogui or pydirectinput!
```py
interception.move_to(960, 540)

with interception.hold_key("shift"):
    interception.press("a")

interception.click(120, 160, button="right", delay=1)
```

Have fun :D

[wrp]: https://github.com/cobrce/interception_py
[c_ception]: https://github.com/oblitum/Interception
