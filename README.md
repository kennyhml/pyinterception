# pyintercept
This is a greatly reworked fork of [interception_py][wrp], a python port for [interception][c_ception].

The Interception API aims to build a portable programming interface that allows one to intercept and control a range of input devices.


## Why use this fork instead of intercept_py?
- Interception_py has not been maintained in 4 years
- I made it as simple to use as things like pyautogui / pydirectinput
- I made it alot more clear and readable what is happening and where.
Unfortunately, the original repository is entirely undocumented and stuffed into one file for the most part.


## Requirements
You absolutely need to install the [interception-driver][c_ception], otherwise none of this will work.

Its as simple as running a .bat file and restarting your computer.

[wrp]: https://github.com/cobrce/interception_py
[c_ception]: https://github.com/oblitum/Interception
