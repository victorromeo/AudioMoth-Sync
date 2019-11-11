from gpiozero import MotionSensor
from signal import pause

pir = MotionSensor(26)

def on_no_motion():
    print("n")

def on_motion():
    print('y')

pir.when_no_motion = on_no_motion
pir.when_motion = on_motion

pause()
