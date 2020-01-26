from lib.config import cfg
from lib.log import logging

# This operation requires that udev has a custom rule to create a symbolic link when the AudioMoth is detected
# To Add the required udev rule, run the following command
#    nano /etc/udev/rules.d/10-local.rules
# And then type following
#      ACTION=="add", ATTRS{model}=="EFM32 MSD Device", SUBSYSTEMS=="scsi", SYMLINK+="moth%n"
#


import time
import os
from datetime import datetime, timezone
import math
from lib.iostate import iostate
from lib.iodevice import iodevice 
from lib.shell import output_shell

# Command to fetch the device name of the AudioMoth
getMothDeviceNameCommand = "ls -l /dev/ | grep 'moth' | grep -E 'sd[a-z]+[0-9]' | awk 'NF>1{print $NF}'"
getMothMountPathCommand = "mount | grep -F '{0}' | cut -d \" \" -f 3"
path_to_watch = "/dev"

class audiomoth:

    def __init__(self):
        self.swdio_pin = cfg.pins.swdio
        self.rst_pin = cfg.pins.rst
        self.swo_pin = cfg.pins.swo
        self.clk_pin = cfg.pins.swclk
        self.pwr_pin = cfg.pins.pwr

        self.mount_path = None
        self.device_name = None
        self.device_path = None

        self.swdio = iodevice(self.swdio_pin,iostate.Float)
        self.rst = iodevice(self.rst_pin,iostate.Float)
        self.swo = iodevice(self.swo_pin,iostate.Float)
        self.clk = iodevice(self.clk_pin,iostate.Float)
        self.pwr = iodevice(self.pwr_pin,iostate.Input, None, False)

    def __del__(self):
        self.pwr.close()
        self.clk.close()
        self.swo.close()
        self.rst.close()
        self.swdio.close()

    def state(self):
        now = datetime.now(timezone.utc).astimezone()
        print(f'{now:%Y%m%d}_{now:%H%M%S} SWDIO:{self.swdio.state()} SWCLK:{self.clk.state()} SWO:{self.swo.state()} RST:{self.rst.state()} PWR:{self.pwr.state()}')

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
            print(f"AudioMoth device {self.device_name} detected at {self.device_path}")
            logging.debug(f"is_detected: {self.device_name} {self.device_path}")
        else:
            print("d", end= '', flush=True)
            logging.debug(f"is_detected:-".format(detected))

        return detected

    def is_mounted(self):

        self.getMothMountPath()
        mounted = self.mount_path is not None and len(self.mount_path) > 3

        if mounted:
            print("AudioMoth device mounted at {0}".format(self.mount_path))
        else:
            print("m", end='', flush=True)

        logging.debug("is_mounted:{0}".format(mounted))
        return mounted

    def usbModeOn(self):
        self.swdio.outputMode(True)
        self.clk.close()
        self.rst.close()
        logging.debug("usbModeOn")

    def usbModeOff(self):
        self.swdio.close()
        logging.debug("usbModeOff")

    def resetMoth(self):
        print("AudioMoth restarting")

        # Pulling the RST pin to ground forces the AudioMoth to restart
        self.rst.outputMode()
        self.rst.low()
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

        print('\nMounting AudioMoth')





        #before = dict ([(f, None) for f in os.listdir (path_to_watch)])

        while (detected and not mounted):

            # Pull the SWDIO pin low, so that when the AudioMoth has restarted, it will start in USB mode
            self.usbModeOn()
            time.sleep (5)

            dTimeout = 60

            detected = self.is_detected()
            while not detected and dTimeout > 0:
                self.usbModeOn()
                time.sleep(dPoll)
                detected = self.is_detected()
                dTimeout -= dPoll

            if not detected:
                logging.error("mountMoth: failed to detect via reset")
                raise Exception("Failed to detected device via reset")

            # Mount the moth
            r, e = output_shell(f'sudo mount -o rw,remount {self.device_path} {cfg.paths.audiomoth}')
            #r, e = output_shell(f'mount {self.device_path} {cfg.paths.audiomoth}')
            print(f'Mount {r} {e}')

            # mounted = self.is_mounted()
            # while not mounted and mTimeout > 0:
            #     time.sleep(mPoll)
            #     mounted = self.is_mounted()
            #     mTimeout -= mPoll

            # if not mounted:
            #     logging.error("mountMoth: failed to mount device via reset")
            #     raise Exception("Failed to mount device via reset")

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

        # Mount the moth
        #r, e = output_shell(f'mount -o rw,remount {self.device_path} {cfg.paths.audiomoth}')
        r, e = output_shell(f'sudo mount {self.device_path} {cfg.paths.audiomoth}')
        print(f'Mount {r} {e}')

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

        mTimeout = 60
        mPoll    = 2
        dTimeout = 10
        dPoll    = 1

        if not self.is_detected():
            logging.warning("unmountMoth: not connected")
            return

        print('\nUnmounting AudioMoth')

        # Get the folder content
        #before = dict ([(f, None) for f in os.listdir (path_to_watch)])

        if self.is_mounted():
            print("Moth currently mounted")

            # Umount the filesystem mount point (Lazily)
            command = f'sudo umount -l {self.device_path}'

            print(command)
            r,e = output_shell(command)
            print(f'Unmount {r} {e}')
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
        try:
            success, _ = self.hid_on()

            if success:
                buffer = [0x00, 0x02, 0x00, 0x00, 0x00, 0x00]
                self.dateToBuffer(buffer, 2, datetime.now(timezone.utc))
                setTimeCommand = "./apps/usbhidtool 0x10C4 0x0002 {0}".format(''.join('0x{:02x} '.format(a) for a in buffer))
                print(setTimeCommand)
                result, success = output_shell(setTimeCommand)
                if (success):
                    print(result)

                logging.info("setTime {0}:{1}".format(setTimeCommand, result))
                print('Set time success.')
            else:
                print('Set time failed. USB HID not enabled.')
        except:
            print('Set time failed. Unexpected error')
        finally:
            self.hid_off()

        return success

    def getTime(self):
        try:
            success, _ = self.hid_on()

            if success:
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
        except:
            print('Set time failed. Unexpected error')
            logging.warn("getTime failed due to unexpected error")
        finally:
            self.hid_off()

        return success, mothDate

    def hid_on(self):
        try:
            # Pull the clock high to enable the USB interface
            self.clk.outputMode()
            self.clk.high()

            for i in range(5, 1):
                time.sleep(1)
                print(i, flush=True)

            dTimeout = 30
            dPoll = 1

            print('d')
            r,_ = output_shell(f'{cfg.paths.root}/apps/flash ')
            print(r)

            while not r.startswith('/dev/tty') and dTimeout > 0:
                time.sleep(dPoll)
                print('d')
                r,_ = output_shell(f'{cfg.paths.root}/apps/flash')
                dTimeout -= dPoll
                print('.')

            if dTimeout <=0:
                print(f'Failed to find Moth: {r}')
        except:
            print('Error occurred while enabling USB HID')
        finally:
            self.clk.low()
        return True, r.strip()

    def hid_off(self):
        self.clk.outputMode()
        self.clk.low()
        self.clk.close()

    def flash(self):
        try:
            success, serial_path = self.hid_on()
            if not success:
                print('Flash failed. HID not enabled')
                raise EnvironmentError('HID not enabled')

            r, success = output_shell(f'{cfg.paths.root}/apps/flash -i {serial_path}')
            i_max = 5

            for i in range(1, i_max):
                if success:
                    serial_number = r.strip()
                    print(f'{serial_number}')
                    break
                else:
                    print(f'Attempt {i} - Failed getting serial {r}')
                    print('n')
                    r, success = output_shell(f'{cfg.paths.root}/apps/flash -i {serial_path}')
                    time.sleep(1)

            flash_image = f'{cfg.paths.root}/apps/AudioMoth-Project.bin'

            if success and os.path.exists(flash_image):

                print(f'Flashing {serial_path} ({serial_number}) with {flash_image}')
                for i in range(1, i_max):
                    print('f')
                    r, success = output_shell(f'{cfg.paths.root}/apps/flash -u {serial_path} {flash_image}')

                    if success and not r.startswith('ERROR'): 
                        print(f'Flashed: {r}')
                        break
                    else:
                        print(f'Attempt {i} - Failed flash {r}')
                        r, success = output_shell(f'{cfg.paths.root}/apps/flash -u {serial_path} {flash_image}')
                        time.sleep(1)

                if not success:
                    print('Flashing failed. Exhausted max attempts.')

        except Exception:
            print('Flashing failed. Unexpected error')
        finally:
            self.hid_off()

