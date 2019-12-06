from datetime import datetime
from picamera import PiCamera
from configuration import configuration as config
from time import sleep

class camera:
    _camera = PiCamera()

    def image_filename(self, image_path:str = None, now:datetime = None):
        if now == None:
            now = datetime.now()

        if image_path == None:
            image_path = config.local_visual_path

        return "{0}/{1:04}{2:02}{3:02}{4:02}{5:02}{6:02}.jpg".format(image_path,now.year,now.month,now.day,now.hour,now.minute,now.second)

    def click(self, count:int = 1, delay_ms:int = 0):

        if count <= 0 or count > 100:
            return

        if delay_ms < 0 or delay_ms > 10000:
            return

        for c in range(count):
            self._camera.capture(self.image_filename())

            if delay_ms > 0:
                sleep(delay_ms)
