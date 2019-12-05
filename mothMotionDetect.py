import logging
logging.basicConfig(filename='logs/activity.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

from gpiozero import MotionSensor, Button, LED
from picamera import PiCamera
from gpiozero.tools import booleanized, all_values, any_values
from signal import pause
from time import sleep
from datetime import datetime
import shutil
from sh import mount, umount
import sys
import itertools

import audiomoth

pirEnabled = True
cameraEnabled = False

# RPI GPIO allocations

pin_pir1 = 24
pin_pir2 = 25

pin_am_rst = 23
pin_am_swo = 22
pin_am_swclk = 21
pin_am_swdio = 20

# Default Paths

imagePath = '/home/pi/Documents/visual'
audioPath = '/home/pi/Documents/audio'

# Initialise AudioMoth (self, swdio, rst, swo, clk)
moth = audiomoth.audiomoth(pin_am_swdio, pin_am_rst, pin_am_swo, pin_am_swclk)

if (pirEnabled):
    pir1 = MotionSensor(pin_pir1)
    pir2 = MotionSensor(pin_pir2)

if (cameraEnabled):
    camera = PiCamera()

# Safety Limits

minDiskMB = 200
minDiskPercent = 0.2
photoCountOnMotion = 5
photoCountDelaySec = 1

i = 0
is_recording = False
is_transferring = False
first_motion = None
last_motion = None

def flashAudioMoth():
    print("Flash of AudioMoth requested")

def check_disk(report):
    total, used, free = shutil.disk_usage("/")

    if (report):
        logging.debug("Disk Total:%d",total)
        logging.debug("Disk Used:%d",used)
        logging.debug("Disk Free:%d",free)

        print("Total: %d MB" % (total // (2**20)))
        print("Used:  %d MB" % (used // (2**20)))
        print("Free:  %d MB" % (free // (2**20)))
        print("Avail: %0.2f %%" % (free / total))

    if ((free / total) < minDiskPercent or (free < minDiskMB)):
        print("Insufficient disk space remaining")
        logging.error("Insufficient disk space remaining %d %d", free, total)
        sys.exit()

def take_photo():
    now = datetime.now()

    if (cameraEnabled):
        camera.capture("{0}/image_{1:04}{2:02}{3:02}_{4:02}{5:02}{6:02}.jpg".format(imagePath,now.year,now.month,now.day,now.hour,now.minute,now.second))

def startRecording():

    if is_transferring:
        return

    # Start the clock
    if not is_recording:
        first_motion = time.time()

    # Update the clock if a new motion event occurs
    last_motion = time.time()

    # Capture a series of photos every time motion occurs
    for _ in itertools.repeat(None, photoCountOnMotion):
        take_photo()
        sleep(photoCountDelaySec)

    # Prevent commencing unmount operations if it is already underway
    if not is_recording:
        is_recording = true

        # Audio capture commences when the AudioMoth is unmounted and the device removed
        moth.unmountMoth()

def transferFilesToLocal():
    if is_transferring:
        return

    is_transferring = True

    mothPath = moth.getMothMountPath()

    listMothFiles = "ls -la {0}/*.WAV".format(mothPath)
    syncFiles = "rsync -r {0}/ {1}".format(mothPath, audioPath)
    removeMothFiles = "rm {0}/*.WAV".format(mothPath)

    logging.info("Fetching AudioMoth files list")
    files, success = output_shell(listFiles)

    if success:
        logging.info(", ".join(files))
        logging.info("Transferring AudioMoth to Local")
        result, success = output_shell(copyFiles)

        if success:
            logging.info("Transfer complete")
            result, success = output_shell(removeMothFiles)

            if success:
                logging.info("AudioMoth files removed")
            else:
                logging.warning("Failed to remove AudioMoth files")
        else:
            logging.warning("Failed to transfer files")
    else:
        logging.warning("Failed to fetch AudioMoth files")

    is_transferring = False

def stopRecording():
    if not is_recording:
        return

    now = time.time()

    while (now - last_motion < 60):
        time.sleep(1)
        now = time.time()

    moth.mountMoth()

    transferFilesToLocal()

def on_motion():
    global i
    i = i + 1
    print("motion %s" % i)
    logging.info("Motion Event %d", i)

    startRecording()

    check_disk(False)

def on_no_motion():
    print(".")

    stopRecording()

logging.info("Starting")
logging.debug("photoCountOnMotion:%d",photoCountOnMotion)
logging.debug("photoCountDelaySec:%d",photoCountDelaySec)
logging.debug("minDiskMB:%d",minDiskMB)
logging.debug("minDiskPercent:%0.2f",minDiskPercent)

# Check disk space

check_disk(True)

# Initialise AudioMoth
moth.mountMoth()
logging.info("Moth mounted: %s", moth.getMothMountPath())

# Initialise camera

if (cameraEnabled):
    print("Camera enabled")
    camera.rotation = 180
    camera.start_preview()

# Initialise pir

if (pirEnabled):
    print("PIR enabled")
    pir1.when_motion = on_motion
    pir1.when_no_motion = on_no_motion
    pir2.when_motion = on_motion
    pir2.when_no_motion = on_no_motion

pause()
