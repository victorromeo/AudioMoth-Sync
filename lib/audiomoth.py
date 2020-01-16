from configuration import configuration as config
from log import logging

# This operation requires that udev has a custom rule to create a symbolic link when the AudioMoth is detected
# To Add the required udev rule, run the following command
#    nano /etc/udev/rules.d/10-local.rules
# And then type following
#      ACTION=="add", ATTRS{model}=="EFM32 MSD Device", SUBSYSTEMS=="scsi", SYMLINK+="moth%n"
#

from iostate import iostate
from iodevice import iodevice 
import time
import os
from shell import output_shell
from datetime import datetime, timezone
import math


# Command to fetch the device name of the AudioMoth
getMothDeviceNameCommand = "ls -la /dev/moth* | grep 'sd.[0-9]' | awk 'NF>1{print $NF}'"
getMothMountPathCommand = "mount | grep -F '{0}' | cut -d \" \" -f 3"
unmountCommand = "umount -l {0}"
path_to_watch = "/dev"

class audiomoth:

    def __init__(self, swdio:int = config.am_swdio_pin, rst:int = config.am_rst_pin, swo:int = config.am_swo_pin, clk: int = config.am_swclk_pin, pwr:int = config.am_pwr_pin):
        self.swdio_pin = swdio
        self.rst_pin = rst
        self.swo_pin = swo 
        self.clk_pin = clk
        self.pwr_pin = pwr

        self.mount_path = None
        self.device_name = None
        self.device_path = None

    def __enter__(self):
        self.swdio = iodevice(self.swdio_pin,iostate.Float)
        self.rst = iodevice(self.rst_pin,iostate.Float)
        self.swo = iodevice(self.swo_pin,iostate.Float)
        self.clk = iodevice(self.clk_pin,iostate.Float)
        self.pwr = iodevice(self.pwr_pin,iostate.Input, None, False)

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.pwr.close()
        self.clk.close()
        self.swo.close()
        self.rst.close()
        self.swdio.close()

    def detectMoth(self) -> bool:
        return bool(self.pwr.value())

    def getMothDeviceName(self):

        moth_device_name, success = output_shell(getMothDeviceNameCommand)

        self.device_name = moth_device_name[:-1] if (success and len(moth_device_name) > 3) else None
        self.device_path = path_to_watch + '/' + moth_device_name[:-1] if (success and len(moth_device_name) > 3) else None

        logging.debug("getMothDeviceName:{0}".format(self.device_name))
        return self.device_name

    def getMothMountPath(self):
        command = getMothMountPathCommand.format(self.device_path)

        mount_path, success = output_shell(command)
        self.mount_path = mount_path[:-1] if (success and len(mount_path) > 3) else None

        logging.debug("getMothMountPath:{0}".format(self.mount_path))
        return self.mount_path

    def is_detected(self):
        self.getMothDeviceName()
        detected = self.device_name is not None and len(self.device_name) > 3

        if detected:
            print("AudioMoth device detected at {0}".format(self.device_path))
        else:
            print("AudioMoth device not detected")

        logging.debug("is_detected:{0}".format(detected))
        return detected

    def is_mounted(self):

        self.getMothMountPath()
        mounted = self.mount_path is not None and len(self.mount_path) > 3

        if mounted:
            print("AudioMoth device mounted at {0}".format(self.mount_path))
        else:
            print("AudioMoth device not mounted")

        logging.debug("is_mounted:{0}".format(mounted))
        return mounted

    def usbModeOn(self):
        self.swdio.outputMode()
        self.swdio.low()
        logging.debug("usbModeOn")

    def usbModeOff(self):
        self.swdio.outputMode()
        self.swdio.high()
        time.sleep(1)

        self.swdio.close()
        logging.debug("usbModeOff")

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
        logging.debug("resetMoth")

    def mountMoth(self):

        mTimeout = 30
        mPoll = 1
        dTimeout = 30
        dPoll = 1

        detected = self.is_detected()
        mounted = self.is_mounted()

        if (detected and mounted):
            logging.debug("mountMoth: Already mounted")
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
                logging.error("mountMoth: failed to detect via reset")
                raise Exception("Failed to detected device via reset")

            mounted = self.is_mounted()
            while not mounted and mTimeout > 0:
                time.sleep(mPoll)
                mounted = self.is_mounted()
                mTimeout -= mPoll

            if not mounted:
                logging.error("mountMoth: failed to mount device via reset")
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
                logging.error("mountMoth: failed to detect moth")
                raise Exception("Failed to detected device. Check AudioMoth is connected")

        while not mounted and mTimeout > 0:
            time.sleep(mPoll)
            mounted = self.is_mounted()
            mTimeout -= mPoll

        if not mounted:
            logging.error("mountMoth: failed to mount moth filesystem")
            raise Exception("Failed to mount device. Check for SD card and filesystem on SD Card")

        print(self.mount_path)
        print("Moth successfully mounted")
        logging.debug("mountMoth: Complete")
        return

    def unmountMoth(self):

        mTimeout = 30
        mPoll    = 2
        dTimeout = 10
        dPoll    = 1

        if not self.is_detected():
            logging.warning("unmountMoth: not connected")
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
                logging.error("unmountMoth: failed to unmount")
                raise Exception("Failed to unmount moth")

        # Turn off the AudioMoth usb support
        while self.is_detected() and dTimeout > 0:
            self.usbModeOff()
            time.sleep(dPoll)
            dTimeout -= dPoll

        if self.is_detected():
            print("Moth failed to disable USB MSD within expected timeout (30s). Resetting")
            self.usbModeOff()
            self.resetMoth()
            time.sleep(10)

        if self.is_detected():
            print("Moth failed to remove device")
            logging.warning("unmountMoth: failed to remove device")
            raise Exception("Failed to remove device")

        print ("Moth successfully unmounted")
        logging.debug("unmountMoth: Complete")
        self.device_name = None
        self.device_path = None
        self.mount_path = None
    
    def dateToBuffer(self, buffer:[], offset, dateValue:datetime):
        timestamp = math.floor(dateValue.timestamp())
        print(timestamp)
        buffer[offset + 3] = (timestamp >> 24) & 0xff
        buffer[offset + 2] = (timestamp >> 16) & 0xff
        buffer[offset + 1] = (timestamp >> 8) & 0xff
        buffer[offset + 0] = (timestamp & 0xff)

    def bufferToDate(self, buffer, offset):
        timestamp = 0
        
        if len(buffer) > 3:
            timestamp |= (int(buffer[offset]) & 0xff) | ((int(buffer[offset + 1]) & 0xff) << 8) | ((int(buffer[offset + 2]) & 0xff) << 16) | ((int(buffer[offset + 3]) & 0xff) << 24)
            print(timestamp)

        #timestamp = ((buffer[offset] & 0xff) | (buffer[offset + 1] 0x0ff) | (buffer[offset + 2] & 0xff) | (buffer[offset + 3] & 0xff)) / 1000
        return datetime.fromtimestamp(timestamp)

    def setTime(self):
        buffer = [0x00, 0x02, 0x00, 0x00, 0x00, 0x00]
        self.dateToBuffer(buffer, 2, datetime.now(timezone.utc))
        setTimeCommand = "./apps/usbhidtool 0x10C4 0x0002 {0}".format(''.join('0x{:02x} '.format(a) for a in buffer))
        print(setTimeCommand)
        result, success = output_shell(setTimeCommand)
        if (success):
            print(result)

        logging.info("setTime {0}:{1}".format(setTimeCommand, result))
        return success

    def getTime(self):
        buffer = [0x00, 0x01]
        
        getTimeCommand = "./apps/usbhidtool 0x10C4 0x0002 {0}".format(''.join('0x{:02x} '.format(a) for a in buffer))
        result, success = output_shell(getTimeCommand)
        logging.info("getTime {0}:{1}".format(getTimeCommand, result))
        if success and result != 'NULL':
            print(result)
            hexValues = result.split(' ')

            if hexValues[0] == 'NULL\n':
                return False, None

            for hexValue in hexValues:
                buffer.append(int(hexValue, 16))

        mothDate = self.bufferToDate(buffer, 3)
        print("{0}".format(mothDate))

        return success, mothDate
