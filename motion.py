from configuration import configuration as config
from gpiozero import MotionSensor
from time import time
from threading import Timer

class motion:

    motionSensors = []
    latest_motion = time()
    motion_detected = False

    when_motion = None
    when_no_motion = None

    def __init__(self):

        for pin in config.pir_pins:
            pir = MotionSensor(pin, queue_len = config.motion_queue_len)
            pir.when_motion = self._on_motion
            pir.when_no_motion = self._on_no_motion
            self.motionSensors.append(pir)

    def _on_motion(self):
        print('.')
      
        if not self.motion_detected:
            self.motion_detected = True
            self.latest_motion = time()

            if self.when_motion != None:
                self.when_motion()
        else:
            self.latest_motion = time()

    def _on_no_motion(self):
        print('-')

        t = Timer(config.motion_sec, self._on_no_motion_delay)
        t.start()

    def _on_no_motion_delay(self):

        now = time()

        if self.latest_motion != None and now - self.latest_motion >= config.motion_sec:
            if self.when_no_motion != None:
                self.when_no_motion()
            
            self.motion_detected = False

            

        