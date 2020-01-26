from datetime import datetime, timezone
from picamera import PiCamera
from time import sleep
from lib.config import cfg
from lib.log import logging

class camera:

    def __init__(self):
        self.copyright = cfg.getOrAdd('photo','copyright','Copyright (c) {0} Monash University')
        self.artist = cfg.getOrAdd('photo','artist',cfg.name)

    def image_filename(self, image_path:str = None, now:datetime = None):
        if now == None:
            now = datetime.now(timezone.utc)

        if image_path == None:
            image_path = cfg.paths.photos

        return f"{now:%Y%m%d}_{now:%H%M%S}"

    def click(self, count:int = 1, delay_ms:int = 0, comment = None):

        if count <= 0 or count > 100:
            logging.warning("click: count out of range ({0})".format(count))
            return

        if delay_ms < 0 or delay_ms > 10000:
            logging.warning("click: delay_ms out of range ({0})".format(delay_ms))
            return

        with PiCamera() as camera:
            camera.exif_tags['IFD0.Copyright'] = self.copyright.format(datetime.now().year)
            camera.exif_tags['IFD0.Artist'] = self.artist
            camera.exif_tags['EXIF.UserComment'] = '' if comment is None else comment.strip()

            camera.resolution = (800, 600)
            camera.start_preview()
            now = datetime.now(timezone.utc).astimezone()
            camera.start_recording(f'{cfg.paths.photos}/{now:%Y%m%d}_{now:%H%M%S}.h264')
            camera.wait_recording(1)
            for i in range(count):
                camera.capture(f'{cfg.paths.photos}/{now:%Y%m%d}_{now:%H%M%S}.jpg', use_video_port=True)
                camera.wait_recording(delay_ms)
            camera.stop_recording()
