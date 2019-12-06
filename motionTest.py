from motion import motion
from signal import pause


def on():
    print('A')

def off():
    print('B')

m = motion()

m.when_motion = on
m.when_no_motion = off

pause()