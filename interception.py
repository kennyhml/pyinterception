from ctypes import *
from stroke import  *
from consts import *

MAX_DEVICES = 20
MAX_KEYBOARD = 10
MAX_MOUSE  = 10

k32 = windll.LoadLibrary('kernel32')

class interception():
    _context = []
    k32 = None
    _c_events = (c_void_p * MAX_DEVICES)()

    def __init__(self):
        try:
            for i in range(MAX_DEVICES):
                _device = device(k32.CreateFileA(b'\\\\.\\interception%02d' % i,
                                        0x80000000,0,0,3,0,0),
                                 k32.CreateEventA(0, 1, 0, 0),
                                 interception.is_keyboard(i))
                self._context.append(_device)
                self._c_events[i] = _device.event

        except Exception as e:
            self._destroy_context()
            raise e
    
    def wait(self,milliseconds =-1):

        result = k32.WaitForMultipleObjects(MAX_DEVICES,self._c_events,0,milliseconds)
        if result == -1 or result  == 0x102:
            return 0
        else:
            return result
    
    def set_filter(self,predicate,filter):
        for i in range(MAX_DEVICES):
            if predicate(i):
                result = self._context[i].set_filter(filter)

    def get_HWID(self,device:int):
        if not interception.is_invalid(device):
            try:
                return self._context[device].get_HWID().decode("utf-16")
            except:
                pass
        return ""

    def receive(self,device:int):
        if not interception.is_invalid(device):
            return self._context[device].receive()

    def send(self,device: int,stroke : stroke):
        if not interception.is_invalid(device):
            self._context[device].send(stroke)
    
    @staticmethod
    def is_keyboard(device):
        return  device+1 > 0 and device+1 <= MAX_KEYBOARD
    
    @staticmethod
    def is_mouse(device):
        return device+1 > MAX_KEYBOARD and device+1 <= MAX_KEYBOARD + MAX_MOUSE
    
    @staticmethod
    def is_invalid(device):
        return device+1 <= 0 or device+1 > (MAX_KEYBOARD + MAX_MOUSE)

    def _destroy_context(self):
        for device in self._context:
            device.destroy()

class device_io_result:
    result = 0
    data = None
    data_bytes = None
    def  __init__(self,result,data):
        self.result = result
        if data!=None:
            self.data = list(data)
            self.data_bytes = bytes(data)


def device_io_call(decorated):
    def decorator(device,*args,**kwargs):
        command,inbuffer,outbuffer = decorated(device,*args,**kwargs)
        return  device._device_io_control(command,inbuffer,outbuffer)
    return decorator

class device():
    handle=0
    event=0
    is_keyboard = False    
    _parser = None
    _bytes_returned = (c_int * 1)(0)
    _c_byte_500 = (c_byte * 500)()
    _c_int_2 = (c_int * 2)()
    _c_ushort_1 = (c_ushort * 1)()
    _c_int_1 = (c_int * 1)()
    _c_recv_buffer = None
    
    def __init__(self, handle, event,is_keyboard:bool):
        self.is_keyboard = is_keyboard
        if is_keyboard:
            self._c_recv_buffer = (c_byte * 12)()
            self._parser = key_stroke
        else:
            self._c_recv_buffer = (c_byte * 24)()
            self._parser = mouse_stroke

        if handle == -1 or event == 0:
            raise Exception("Can't create device")
        self.handle=handle
        self.event =event

        if self._device_set_event().result == 0:
            raise Exception("Can't communicate with driver")

    def destroy(self):
        if self.handle != -1:
            k32.CloseHandle(self.handle)
        if self.event!=0:
            k32.CloseHandle(self.event)
    
    @device_io_call
    def get_precedence(self):
        return  0x222008,0,self._c_int_1
    
    @device_io_call
    def set_precedence(self,precedence : int):
        self._c_int_1[0] = precedence
        return  0x222004,self._c_int_1,0

    @device_io_call
    def get_filter(self):
        return  0x222020,0,self._c_ushort_1

    @device_io_call
    def set_filter(self,filter):
        self._c_ushort_1[0] = filter
        return 0x222010,self._c_ushort_1,0

    @device_io_call
    def _get_HWID(self):
        return 0x222200,0,self._c_byte_500
    
    def get_HWID(self):
        data = self._get_HWID().data_bytes
        return data[:self._bytes_returned[0]]
    
    @device_io_call
    def _receive(self):
        return 0x222100,0,self._c_recv_buffer

    def receive(self):
        data = self._receive().data_bytes
        return self._parser.parse_raw(data)
    
    def send(self,stroke:stroke):
        if type(stroke) == self._parser:
            self._send(stroke)

    @device_io_call
    def _send(self,stroke:stroke):
        memmove(self._c_recv_buffer,stroke.data_raw,len(self._c_recv_buffer))
        return 0x222080,self._c_recv_buffer,0

    @device_io_call
    def _device_set_event(self):
        self._c_int_2[0] = self.event
        return 0x222040,self._c_int_2,0

    def _device_io_control(self,command,inbuffer,outbuffer)->device_io_result:
        res = k32.DeviceIoControl(self.handle,command,inbuffer,
                                  len(bytes(inbuffer)) if inbuffer != 0 else  0,
                                  outbuffer,
                                  len(bytes(outbuffer)) if outbuffer !=0 else 0,
                                  self._bytes_returned,0)

        return device_io_result(res,outbuffer if outbuffer !=0 else None) 