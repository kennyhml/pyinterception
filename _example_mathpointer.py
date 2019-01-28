from interception import *
from consts import *
from math import *
from win32api import GetSystemMetrics
from datetime import datetime
from time import  sleep

esc   = 0x01
num_0 = 0x0B
num_1 = 0x02
num_2 = 0x03
num_3 = 0x04
num_4 = 0x05
num_5 = 0x06
num_6 = 0x07
num_7 = 0x08
num_8 = 0x09
num_9 = 0x0A
scale = 15
screen_width = GetSystemMetrics(0)
screen_height = GetSystemMetrics(1)

def delay():
    sleep(0.001)

class point():
    x = 0
    y = 0
    def __init__(self,x,y):
        self.x = x
        self.y = y

def circle(t):
    f = 10
    return point(scale  * f * cos(t), scale * f *sin(t))

def mirabilis(t):
    f= 1 / 2
    k = 1 / (2 * pi)

    return point(scale * f * (exp(k * t) * cos(t)),
                 scale * f * (exp(k * t) * sin(t)))

def epitrochoid(t):
    f = 1
    R = 6
    r = 2
    d = 1
    c = R + r

    return point(scale * f * (c * cos(t) - d * cos((c * t) / r)),
                 scale * f * (c * sin(t) - d * sin((c * t) / r)))

def hypotrochoid(t):
    f = 10 / 7
    R = 5
    r = 3
    d = 5
    c = R - r

    return point(scale * f * (c * cos(t) + d * cos((c * t) / r)),
                 scale * f * (c * sin(t) - d * sin((c * t) / r)))

def hypocycloid(t):
    f = 10 / 3
    R = 3
    r = 1
    c = R - r

    return point(scale * f * (c * cos(t) + r * cos((c * t) / r)),
                 scale * f * (c * sin(t) - r * sin((c * t) / r)))

def bean(t):
    f = 10
    c = cos(t)
    s = sin(t)

    return point(scale * f * ((pow(c, 3) + pow(s, 3)) * c),
                 scale * f * ((pow(c, 3) + pow(s, 3)) * s))

def Lissajous(t):
    f = 10
    a = 2
    b = 3

    return point(scale * f * (sin(a * t)), scale * f * (sin(b * t)))

def epicycloid(t):
    f = 10 / 42
    R = 21
    r = 10
    c = R + r

    return point(scale * f * (c * cos(t) - r * cos((c * t) / r)),
                 scale * f * (c * sin(t) - r * sin((c * t) / r)))

def rose(t):
    f = 10
    R = 1
    k = 2 / 7

    return point(scale * f * (R * cos(k * t) * cos(t)),
                 scale * f * (R * cos(k * t) * sin(t)))

def butterfly(t):
    f = 10 / 4
    c = exp(cos(t)) - 2 * cos(4 * t) + pow(sin(t / 12), 5)

    return point(scale * f * (sin(t) * c), scale * f * (cos(t) * c))

def math_track(context:interception, mouse : int,
                center,curve, t1, t2, # changed params order
                partitioning):
    delta = t2 - t1
    position = curve(t1)
    mstroke = mouse_stroke(interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_UP.value,
                           interception_mouse_flag.INTERCEPTION_MOUSE_MOVE_ABSOLUTE.value,
                           0,
                           int((0xFFFF * center.x) / screen_width),
                           int((0xFFFF * center.y) / screen_height),
                           0)

    context.send(mouse,mstroke)

    mstroke.state = 0
    mstroke.x = int((0xFFFF * (center.x + position.x)) / screen_width)
    mstroke.y = int((0xFFFF * (center.y - position.y)) / screen_height)

    context.send(mouse,mstroke)

    j = 0
    for i in range(partitioning+2):
        if (j % 250 == 0):
            delay()
            mstroke.state = interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_UP.value
            context.send(mouse,mstroke)

            delay()
            mstroke.state = interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN.value
            context.send(mouse,mstroke)
            if i > 0:
                i = i-2

        position = curve(t1 + (i * delta)/partitioning)
        mstroke.x = int((0xFFFF * (center.x + position.x)) / screen_width)
        mstroke.y = int((0xFFFF * (center.y - position.y)) / screen_height)
        context.send(mouse,mstroke)
        delay()
        j = j + 1

    delay()
    mstroke.state = interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN.value
    context.send(mouse,mstroke)

    delay()
    mstroke.state = interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_UP.value
    context.send(mouse,mstroke)

    delay()
    mstroke.state = 0
    mstroke.x = int((0xFFFF * center.x) / screen_width)
    mstroke.y = int((0xFFFF * center.y) / screen_height)
    context.send(mouse,mstroke)

curves = {  num_0 : (circle,0,2*pi,200),
            num_1 : (mirabilis,-6*pi,6*pi,200),
            num_2 : (epitrochoid,0, 2 * pi, 200),
            num_3 : (hypotrochoid, 0, 6 * pi, 200),
            num_4 : (hypocycloid,0, 2 * pi, 200),
            num_5 : (bean, 0, pi, 200),
            num_6 : (Lissajous, 0, 2 * pi, 200),
            num_7 : (epicycloid, 0, 20 * pi, 1000),
            num_8 : (rose,0, 14 * pi, 500),
            num_9 : (butterfly, 0, 21 * pi, 2000),
            }


notice = '''NOTICE: This example works on real machines.
Virtual machines generally work with absolute mouse
positioning over the screen, which this samples isn't\n"
prepared to handle.

Now please, first move the mouse that's going to be impersonated.
'''

steps = '''Impersonating mouse %d
Now:
  - Go to Paint (or whatever place you want to draw)
  - Select your pencil
  - Position your mouse in the drawing board
  - Press any digit (not numpad) on your keyboard to draw an equation
  - Press ESC to exit.'''

def main():

    mouse = 0
    position = point(screen_width // 2, screen_height // 2)
    context = interception()
    context.set_filter(interception.is_keyboard,
                       interception_filter_key_state.INTERCEPTION_FILTER_KEY_DOWN.value |
                       interception_filter_key_state.INTERCEPTION_FILTER_KEY_UP.value)
    context.set_filter(interception.is_mouse,
                       interception_filter_mouse_state.INTERCEPTION_FILTER_MOUSE_MOVE.value )

    print(notice)

    while True:

        device = context.wait()
        if interception.is_mouse(device):
            if mouse == 0:
                mouse = device
                print( steps % (device - 10))

            mstroke = context.receive(device)

            position.x += mstroke.x
            position.y += mstroke.y
            
            if position.x < 0:
                position.x = 0
            if position.x > screen_width - 1:
                position.x = screen_width -1
            
            if position.y <0 :
                position.y = 0
            if position.y > screen_height - 1:
                position.y = screen_height -1
            
            mstroke.flags = interception_mouse_flag.INTERCEPTION_MOUSE_MOVE_ABSOLUTE.value
            mstroke.x = int((0xFFFF * position.x) / screen_width)
            mstroke.y = int((0xFFFF * position.y) / screen_height)
            
            context.send(device,mstroke)
        
        if mouse and interception.is_keyboard(device):
            kstroke = context.receive(device)

            if kstroke.code == esc:
                return

            if kstroke.state == interception_key_state.INTERCEPTION_KEY_DOWN.value:     
                if kstroke.code in curves:
                    math_track(context,mouse,position,*curves[kstroke.code])
                else:
                    context.send(device,kstroke)

            elif kstroke.state == interception_key_state.INTERCEPTION_KEY_UP.value:
                if not kstroke.code in curves:
                    context.send(device,kstroke)
            else:
                context.send(device,kstroke)


if __name__ == "__main__":
    main()