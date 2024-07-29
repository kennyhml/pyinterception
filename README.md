# pyinterception
This is a python **port and wrapper** for [interception][c_ception], a low level input device driver.

> The Interception API aims to build a portable programming interface that allows one to intercept and control a range of input devices.

## Installing
Pyinterception is available on PyPi under the name `interception-python`, so simply `pip install interception-python`.

## Why use interception?
Did you ever try to send inputs to an application and, well, nothing happened? Yes, in alot of cases this is resolved by running your code with higher or same privileges as the target process, but that is not always the case.

Some people are actually under the impression that windows doesnt differentiate between *fake* inputs and *real* inputs, but that is **wrong**!

Take the popular remote software `Parsec` as example, if you play around with it you will notice that you wont have any success sending inputs to it. But obviously inputs from our mouse and keywords work, so how can it tell the difference?

If you take a look at [KBDLLHOOKSTRUCT][kbdllhook], specifically the `flags` field:
> Testing LLKHF_INJECTED (bit 4) will tell you whether the event was injected. If it was, then testing LLKHF_LOWER_IL_INJECTED (bit 1) will tell you whether or not the event was injected from a process running at lower integrity level.

This flag will **always** be set when sending an input through the windows API and there is nothing you can do about it. Programs may not pick up on this flag through the `KBDLLHOOKSTRUCT`, but it certainly proves that the OS clearly differentiates between inputs. 

Why is this an issue? Well, it's isnt always one. If whatever you're sending inputs to currently works fine, and you are not worried about getting flagged by some sort of anti-cheat, then by all means its totally fine to stick to pyautogui / pydirectinput.
At this point it is worth noting that alot of the more advanced anti-cheats including vanguard and some versions of EAC **will not boot** while the driver is loaded on your system, it is a very well known piece of software after all.
And if you're going to ask me how to bypass that detection - write your own driver.

## Why use this port?
- Very simple interface inspired by pyautogui / pydirectinput, all the complicated interception communication is abstracted away.
- Automatically adjusts the keyboard scancodes based on your current keyboard layout.
- Very well documented if you ever want to try and implement additional functionality yourself.
- Completely self-contained, no dependencies required!
## Todo list:
- Add support for **extended** keys
- Add optional 'human' mouse movement (bezier curves?)

Feel free to contribute, just make sure you try to stick to the current code style of the project :) 

## How to use?
First of all, you absolutely need to install the [interception-driver][c_ception], otherwise none of this will work. It's a very simple install.

Now, once you have all of that set up, you can go ahead and import `interception`. 

The first thing you are always going to want to call is `interception.auto_capture_devices()` in order for the library to get the correct device handles.
Explaining why would blow the scope of this introduction and you shouldn't have to worry about, just call the function and let it do it's thing!

Now you can begin to send inputs, just like you are used to it from pyautogui or pydirectinput!
```py
interception.move_to(960, 540)

with interception.hold_key("shift"):
    interception.press("a")

interception.click(120, 160, button="right", delay=1)
```
Thank you for taking your time to read the introduction o7

[c_ception]: https://github.com/oblitum/Interception
[kbdllhook]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct?redirectedfrom=MSDN
