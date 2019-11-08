from enum import Enum, unique
from gpiozero import *

@unique
class IOState(Enum):
    Input = 0
    Output = 1
    Float = -1

class InputOutputDevice:
    def __init__(self, pin: int, mode: IOState, pin_factory = None, pull_up_in: bool = False, active_state_in = None, bounce_time_in = None, active_high_out : bool = True, initial_value_out = False):
        self.pin = pin
        self.mode = mode
        self.device = None
        self.value = initial_value_out
        self.pin_factory = pin_factory
        self.active_state_in = active_state_in
        self.bounce_time_in = None
        self.active_high_out = active_high_out

        if (mode == IOState.Input):
            self.device = DigitalInputDevice(self.pin, pin_factory = self.pin_factory)
        else:
            self.device = DigitalOutputDevice(self.pin, active_high = True, initial_value = self.value, pin_factory = self.pin_factory)

    def value(self):
        if (self.mode == IOState.Output):
            return self.value

        if (self.mode == IOState.Input):
            return self.device.value

        return None

    def high(self):
        if (self.mode == IOState.Output):
            self.value = True
            self.device.on()

    def low(self):
        if (self.mode == IOState.Output):
            self.value = False
            self.device.off()

    def set(value: bool):
        if (value):
            self.high()
        else:
            self.low()

    def inputMode(self):
        if (self.mode == IOState.Input):
           return

        if (self.mode == IOState.Output):
            self.device.close()
            self.device = None

        self.device = DigitalInputDevice(self.pin, pull_up = self.pull_up_in, active_state = self.active_state_in, bounce_time = self.bounce_time_in, pin_factory = self.pin_factory)
        self.value = self.device.value

    def outputMode(self, initial_value: bool = None):
        if (self.mode == IOState.Output):
            if (initial_value != None): 
                self.value = initial_value
            self.set(self.value)

        if (self.mode == IOState.Input):
            self.device.close()
            self.device = None

        self.device = DigitalOutputDevice(self.pin, active_high = self.active_high_out, initial_value = initial_value, pin_factory = self.pin_factory)
        self.value = initial_value

    def close(self):
        if (self.mode == IOState.Input or self.mode == IOState.Output):
            self.device.close()
            self.device = None
            self.mode = IOState.Float
            self.value = None

    def blink(self, on_time=1, off_time=0, n=None, background=True):
        self.outputMode()
        value = self.value
        self.device.blink(on_time,off_time,n,background)
        set(value)

    def wait_for_active(self, timeout = None):
        self.inputMode()
        self.device.wait_for_active(timeout)

    def wait_for_inactive(self, timeout = None):
        self.inputMode()
        self.device.wait_for_inactive(timeout)

    @property
    def active_time(self):
        self.inputMode()
        return self.device.active_time

    @property
    def inactive_time(self):
        self.inputMode()
        return self.device.inactive_time

    @property
    def when_activated(self):
        self.inputMode()
        return self.device.when_activated

    @when_activated.setter
    def when_activated(self, x):
        self.inputMode()
        self.device.when_activated = x

    @property
    def when_deactivated(self):
        self.inputMode()
        return self.device.when_deactivated

    @when_deactivated.setter
    def when_deactivated(self, x):
        self.inputMode()
        self.device.when_deactivated = x
