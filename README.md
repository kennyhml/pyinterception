# pyinterception
This is a greatly reworked version of [interception_py][wrp], a python port for [interception][c_ception], which is now obsolete and points here instead.

The Interception API aims to build a portable programming interface that allows one to intercept and control a range of input devices.

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

## Why use this fork?
- I aim to make this port as simple to use as possible
- Comparable to things like pyautogui or pydirectinput
- The codebase has been refactored in a much more readable fashion
- I work with loads of automation first hand so there is alot of QoL features.

Unfortunately, the original repository is entirely undocumented and stuffed into one file for the most part,
which made some things pretty hard to decipher and understand.


## How to use?
First of all, you absolutely need to install the [interception-driver][c_ception], otherwise none of this will work. It's a very simple install.

Now, once you have all of that set up, you can go ahead and import `interception`. Let's start by identifying your used devices!

```py
import interception

kdevice = interception.listen_to_keyboard()
mdevice = interception.listen_to_mouse()
```
You will get two integers back, those integers are the number of the device you just used. Let's set this device in interception to ensure it sends events from the correct one!
```py
interception.inputs.keyboard = kdevice
interception.inputs.mouse = mdevice
```

So, now you can begin to send inputs, just like you are used to it from pyautogui or pydirectinput!
```py
interception.move_to(960, 540)

with interception.key_down("shift"):
    interception.press("a")

interception.click(120, 160, button="right", delay=1)
```

Have fun :D

[wrp]: https://github.com/cobrce/interception_py
[c_ception]: https://github.com/oblitum/Interception
