import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.audiomoth import audiomoth
from lib.camera import camera
from lib.iodevice import iodevice
from lib.diskio import diskio
from lib.motion import motion
from lib.network import network
import lib.shell
from lib.aws import aws
from lib.config import cfg