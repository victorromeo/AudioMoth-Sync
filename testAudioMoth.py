import audiomoth
import iodevice

# (self, swdio, rst, swo, clk)

moth = audiomoth.audiomoth(20, 23, 22, 21)

print("About to mount AudioMoth")
moth.mountMoth()
print("Moth Mounted")

print("About to unmount AudioMoth")
moth.unmountMoth()
print("Moth Unmounted")
