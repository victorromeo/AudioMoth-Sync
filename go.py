from lib.device import *

pprint(states)
pprint(transitions)

# Start the Device
d = Device()
print(d.state)

#Configure the Device
d.setup()
print(d.state)