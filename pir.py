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


pirEnabled = False
cameraEnabled = False

# Inputs

if (pirEnabled):
    pir = MotionSensor(4)

if (cameraEnabled):
    camera = PiCamera()

minDiskMB = 200
minDiskPercent = 0.2
photoCountOnMotion = 5
photoCountDelaySec = 1

# Default Paths

imagePath = '/home/pi/Documents/visual'
audioPath = '/home/pi/Documents/audio'
mothMountPath = '/media/moth'
mothUUID = ''

# Initialise camera

if (cameraEnabled):
    camera.rotation = 180
    camera.start_preview()

i = 0

def getMothUUID():
    if (len(sys.argv) > 1 and len(sys.argv[1]) > 1):
        mothUUID = sys.argv[1]
        print('UUID: %s' % mothUUID)
        logging.info('UUID: %s', mothUUID)
    else:
        print("UUID required")
        logging.error('UUID required')
        sys.exit()

def mountMoth():
    mount(mothUUID, mothMountPath, '')

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

def on_motion():
    global i
    i = i + 1
    print("motion %s" % i)
    logging.info("Motion Event %d", i)

    # TODO add audio capture commencement

    for _ in itertools.repeat(None, photoCountOnMotion):
        take_photo()
        sleep(photoCountDelaySec)

    check_disk(False)

def on_no_motion():
    print(".")

logging.info("Starting")
logging.debug("photoCountOnMotion:%d",photoCountOnMotion)
logging.debug("photoCountDelaySec:%d",photoCountDelaySec)
logging.debug("minDiskMB:%d",minDiskMB)
logging.debug("minDiskPercent:%0.2f",minDiskPercent)

getMothUUID()

check_disk(True)

if (pirEnabled):
    pir.when_motion = on_motion
    pir.when_no_motion = on_no_motion

pause()
