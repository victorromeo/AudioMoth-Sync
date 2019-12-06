# This operation requires that udev has a custom rule to create a symbolic link when the AudioMoth is detected
# To Add the required udev rule, run the following command
#    nano /etc/udev/rules.d/10-local.rules
# And then type following
#      ACTION=="add", ATTRS{model}=="EFM32 MSD Device", SUBSYSTEMS=="scsi", SYMLINK+="moth%n"
#

from iodevice import IOState, InputOutputDevice
import time
import os
from shell import output_shell

# Command to fetch the device name of the AudioMoth
getMothDeviceNameCommand = "ls -la /dev/moth* | grep 'sd.[0-9]' | awk 'NF>1{print $NF}'"
getMothMountPathCommand = "mount | grep -F '{0}' | cut -d \" \" -f 3"
unmountCommand = "umount -l {0}"
path_to_watch = "/dev"

class audiomoth:

    def __init__(self, swdio, rst, swo, clk):
        self.swdio = InputOutputDevice(swdio,IOState.Float)
        self.rst = InputOutputDevice(rst,IOState.Float)
        self.swo = InputOutputDevice(swo,IOState.Float)
        self.clk = InputOutputDevice(clk,IOState.Float)

        self.mount_path = None
        self.device_name = None
        self.device_path = None



    def getMothDeviceName(self):
        # print(getMothDeviceNameCommand)
        moth_device_name, success = output_shell(getMothDeviceNameCommand)

        self.device_name = moth_device_name[:-1] if (success and len(moth_device_name) > 3) else None
        self.device_path = path_to_watch + '/' + moth_device_name[:-1] if (success and len(moth_device_name) > 3) else None

        return self.device_name

    def getMothMountPath(self):
        command = getMothMountPathCommand.format(self.device_path)
        # print(command)
        mount_path, success = output_shell(command)
        self.mount_path = mount_path[:-1] if (success and len(mount_path) > 3) else None

        return self.mount_path

    def is_detected(self):
        self.getMothDeviceName()
        detected = self.device_name is not None and len(self.device_name) > 3;

        if detected:
            print("AudioMoth device detected at {0}".format(self.device_path))
        else:
            print("AudioMoth device not detected")

        return detected

    def is_mounted(self):

        self.getMothMountPath()
        mounted = self.mount_path is not None and len(self.mount_path) > 3;

        if mounted:
            print("AudioMoth device mounted at {0}".format(self.mount_path))
        else:
            print("AudioMoth device not mounted")

        return mounted

    def usbModeOn(self):
        self.swdio.outputMode()
        self.swdio.low()

    def usbModeOff(self):
        self.swdio.outputMode()
        self.swdio.high()
        time.sleep(1)

        self.swdio.close()

    def resetMoth(self):
        print("AudioMoth restarting")

        # Pulling the RST pin to ground forces the AudioMoth to restart
        self.rst.outputMode()
        self.rst.low()
        time.sleep(1)

        # Pulling up the RST pin before closing the output device ensures the pin doesn't stay low
        self.rst.high()
        time.sleep(1)

        # Close the pin to allow RST to complete
        self.rst.close()

    def mountMoth(self):

        mTimeout = 30
        mPoll = 1
        dTimeout = 30
        dPoll = 1

        detected = self.is_detected()
        mounted = self.is_mounted()

        if (detected and mounted):
            return

        before = dict ([(f, None) for f in os.listdir (path_to_watch)])

        while (detected and not mounted):

            # Pull the SWDIO pin low, so that when the AudioMoth has restarted, it will start in USB mode
            self.usbModeOn()
            self.resetMoth()
            time.sleep (5)

            dTimeout = 30

            detected = self.is_detected()
            while not detected and dTimeout > 0:
                self.usbModeOn()
                time.sleep(dPoll)
                detected = self.is_detected()
                dTimeout -= dPoll

            if not detected:
                raise Exception("Failed to detected device via reset")

            mounted = self.is_mounted()
            while not mounted and mTimeout > 0:
                time.sleep(mPoll)
                mounted = self.is_mounted()
                mTimeout -= mPoll

            if not mounted:
                raise Exception("Failed to mount device via reset")

        if not detected:
            # Pull the SWDIO pin low, and wait to detect
            self.usbModeOn()
            time.sleep (5)

            detected = self.is_detected()
            while not detected and dTimeout > 0:
                self.usbModeOn()
                time.sleep(dPoll)
                detected = self.is_detected()
                dTimeout -= dPoll

            if not detected:
                raise Exception("Failed to detected device. Check AudioMoth is connected")

        while not mounted and mTimeout > 0:
            time.sleep(mPoll)
            mounted = self.is_mounted()
            mTimeout -= mPoll

        if not mounted:
            raise Exception("Failed to mount device. Check for SD card and filesystem on SD Card")

        # # Detect changes in the device 'dev' folder, and wait for the Moth to be found
        # moth_found = False
        # while not moth_found:
        #     time.sleep (10)
        #     after = dict ([(f, None) for f in os.listdir (path_to_watch)])
        #     added = [f for f in after if not f in before]
        #     removed = [f for f in before if not f in after]
        #
        #     if added: print ("Added: ", ", ".join (added))
        #     if removed: print ("Removed: ", ", ".join (removed))
        #
        #     moth_found = 'moth' in added
        #     before = after

        # Get the Mount Path
        # self.device_name = self.getMothDeviceName()
        # if (self.device_name == None):
        #     print('Failed to find AudioMoth - AudioMoth not mounted')
        #     raise Exception('Failed to find AudioMoth - AudioMoth not mounted')
        #
        # self.device_path = '/dev/' + self.device_name
        # self.getMothMountPath()
        #


        print(self.mount_path)
        print("Moth successfully mounted")

        return

    def unmountMoth(self):

        mTimeout = 30
        mPoll    = 2
        dTimeout = 10
        dPoll    = 1

        if not self.is_detected():
            return

        # Get the folder content
        before = dict ([(f, None) for f in os.listdir (path_to_watch)])

        if self.is_mounted():
            print("Moth currently mounted")

            # Umount the filesystem mount point (Lazily)
            command = unmountCommand.format(self.device_path)
            print(command)
            output_shell(command)
            time.sleep(10)

            # Report failure
            while self.is_mounted() and mTimeout > 0:
                # Lift the SWDIO pin, to cause the AudioMoth to remove the USB MSD protocol support
                self.usbModeOff()
                time.sleep(mPoll)
                mTimeout -= mPoll

            if self.is_mounted():
                print("Moth failed to unmount")
                raise Exception("Failed to unmount")
                return

        # Turn off the AudioMoth usb support
        while self.is_detected() and dTimeout > 0:
            self.usbModeOff()
            time.sleep(dPoll)
            dTimeout -= dPoll

        if self.is_detected():
            print("Moth failed to disable USB MSD within expeced timeout (30s). Resetting")
            self.usbModeOff()
            self.resetMoth()
            time.sleep(10)

        if self.is_detected():
            print("Moth failed to remove device")
            raise Exception("Failed to remove device")
            return

        print ("Moth successfully unmounted")
        self.device_name = None
        self.device_path = None
        self.mount_path = None

                # moth_found = True
                #
                # while moth_found:
                #     time.sleep (10)
                #     after = dict ([(f, None) for f in os.listdir (path_to_watch)])
                #     added = [f for f in after if not f in before]
                #     removed = [f for f in before if not f in after]
                #
                #     if added: print ("Added: ", ", ".join (added))
                #     if removed: print ("Removed: ", ", ".join (removed))
                #
                #     moth_found = 'moth' in removed
                #     before = after
