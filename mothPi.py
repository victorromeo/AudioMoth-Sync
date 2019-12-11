from configuration import configuration as config
from log import logging
from signal import pause
from time import sleep
from audiomoth import audiomoth
from motion import motion
from camera import camera
from diskio import diskio
from threading import Thread, ThreadError

m = motion()
c = camera()
am = audiomoth(config.am_swdio_pin, config.am_rst_pin, config.am_swo_pin, config.am_swclk_pin)
d = diskio()

def on_motion():
    logging.info("on_motion")
    print("Recording starting")
    x = Thread(target=am.unmountMoth, args=())
    y = Thread(target=c.click, args=(config.photo_count_on_motion, config.photo_count_delay_sec))
    x.start()
    y.start()
    x.join()
    y.join()
    print("Recording started")
    sleep(30)

def on_no_motion():
    logging.info("on_no_motion")
    print("Recording stopping")
    x = Thread(target=am.mountMoth, args=())
    x.start()
    x.join()
    print("Recording stopped")
    d.transfer_audio(config.am_mount_path, config.local_audio_path)

m.when_motion = on_motion
m.when_no_motion = on_no_motion

d.check_disk()

pause()
