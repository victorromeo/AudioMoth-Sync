import audiomoth
import iodevice

# (self, swdio, rst, swo, clk)

moth = audiomoth.audiomoth(16, 19, 18, 17)

print("About to mount AudioMoth")
moth.mountMoth()
print("Moth Mounted")

print("About to unmount AudioMoth")
moth.unmountMoth()
print("Moth Unmounted")
