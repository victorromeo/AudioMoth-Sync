import iostate
from gpiozero import DigitalInputDevice, DigitalOutputDevice

class iodevice:
    def __init__(self, pin: int, mode: iostate, pin_factory = None, pull_up_in: bool = False, active_state_in = None, bounce_time_in = None, active_high_out : bool = True, initial_value_out = False):
        self.pin = pin
        self.mode = mode
        self.device = None
        self.current_value = initial_value_out
        self.pin_factory = pin_factory
        self.active_state_in = active_state_in
        self.bounce_time_in = None
        self.active_high_out = active_high_out
        self.pull_up_in = pull_up_in

        if (mode == iostate.iostate.Input):
            self.device = DigitalInputDevice(self.pin, pin_factory = self.pin_factory)
        elif (mode == iostate.iostate.Output):
            self.device = DigitalOutputDevice(self.pin, active_high = True, initial_value = self.current_value, pin_factory = self.pin_factory)

    def value(self):
        if (self.mode == iostate.iostate.Output):
            return self.current_value

        if (self.mode == iostate.iostate.Input):
            return self.device.value

        return None

    def high(self):
        if (self.mode == iostate.iostate.Output):
            self.current_value = True
            self.device.on()
        else:
            print("Output failed. Not in Output state")

    def low(self):
        if (self.mode == iostate.iostate.Output):
            self.current_value = False
            self.device.off()
        else:
           print("Output failed. Not in Output state")

    def set(self, value: bool):
        if (value):
            self.high()
        else:
            self.low()

    def inputMode(self):
        if (self.mode == iostate.iostate.Input):
           return

        if (self.mode == iostate.iostate.Output):
            self.device.close()
            self.device = None

        self.device = DigitalInputDevice(self.pin, pull_up = self.pull_up_in, active_state = self.active_state_in, bounce_time = self.bounce_time_in, pin_factory = self.pin_factory)
        self.current_value = self.device.value
        self.mode = iostate.iostate.Input

    def outputMode(self, initial_value: bool = None):
        if (self.mode == iostate.iostate.Output):
            if (initial_value != None):
                self.current_value = initial_value
            self.set(self.current_value)
            return

        if (self.mode == iostate.iostate.Input):
            self.device.close()
            self.device = None

        self.device = DigitalOutputDevice(self.pin, active_high = self.active_high_out, initial_value = initial_value, pin_factory = self.pin_factory)
        self.current_value = initial_value
        self.mode = iostate.iostate.Output

    def close(self):
        if (self.mode == iostate.iostate.Input or self.mode == iostate.iostate.Output):
            self.device.close()
            self.device = None
            self.mode = iostate.iostate.Float
            self.current_value = None

    def blink(self, on_time=1, off_time=0, n=None, background=True):
        self.outputMode()
        value = self.current_value
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
