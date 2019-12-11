from ..iodevice import *

pin = 16
p = InputOutputDevice(pin, IOState.Float)
v = p.value

print('Pin {0} In = {0}'.format(pin,v))

p.outputMode()
p.high()

print('Pin {0} is high'.format(pin))

p.low()

print('Pin {0} is low'.format(pin))

p.close()

print('float')


