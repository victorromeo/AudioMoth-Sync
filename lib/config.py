import os, tempfile
from configparser import ConfigParser, SafeConfigParser
from typing import NamedTuple, List
from enum import Enum, unique
import socket
import datetime
import shutil

class Pins:
    swdio: int
    swo:int
    swclk:int
    pwr:int
    rst:int

class Camera:
    photo_count: int
    photo_delay_sec:int

@unique
class PIRMode(Enum):
    PIJUICE_MODE = 1
    PI_MODE = 2

class Motion:
    mode:PIRMode
    pins:List[int]

class Event:
    event_queue_length:int
    event_start_offset_sec:int
    event_stop_offset_sec:int
    event_threshold_active:float
    event_threshold_inactive:float

class Paths:
    root:str
    logs:str
    photos:str
    recordings:str
    audiomoth:str

class Network:
    ping_test_url: str

class Health:
    min_disk_percent: int
    min_disk_mb: int

class Config:

    config_path:str
    device: str
    pins: Pins
    paths: Paths
    camera: Camera
    motion: Motion
    event: Event
    network: Network
    health: Health

    _reboot: bool
    _restart: bool

    def __init__(self, path:str = None):
        if path == None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_dir = os.path.dirname(script_dir)

            self.config_path = app_dir+"/config.ini"

        self.name = socket.gethostname()
        self.pins = Pins()
        self.paths = Paths()
        self.camera = Camera()
        self.motion = Motion()
        self.event = Event()
        self.network = Network()
        self.health = Health()

        # Read Paths
        self.paths.root = app_dir
        self.paths.recordings =  f'{app_dir}/capture/recordings'
        self.paths.photos =  f'{app_dir}/capture/photos'
        self.paths.logs =  f'{app_dir}/capture/logs'

        self.paths.audiomoth = self.getOrAdd('paths','audiomoth_mount', '/mnt/Moth')

        # Email
        self.emailto = self.getOrAdd('email','to','')

        # Read Audiomoth Pins
        self.pins.swdio = self.getOrAddInt('pins','swdio', fallback=20)
        self.pins.swclk = self.getOrAddInt('pins','swclk', fallback=21)
        self.pins.swo = self.getOrAddInt('pins','swo', fallback=19)
        self.pins.rst = self.getOrAddInt('pins','rst', fallback=16)
        self.pins.pwr = self.getOrAddInt('pins','pwr', fallback=26)

        # Motion

        self.motion.mode = \
            PIRMode.PIJUICE_MODE if self.getOrAdd('motion','mode', fallback='pijuice') == 'pijuice' \
            else PIRMode.PI_MODE if self.getOrAdd('motion','mode', fallback='') == 'pi' \
                else None
        self.motion.pins = [int(x) for x in self.getOrAdd('motion','pins', fallback='').split()] 
        
        # Event
        self.event.event_queue_length = self.getOrAddInt('event','queue_length', fallback=10)
        self.event.event_threshold_active = self.getOrAddFloat('event','threshold_active', fallback=0.1)
        self.event.event_threshold_inactive = self.getOrAddFloat('event','threshold_inactive',fallback=0.0)
        self.event.event_start_offset_sec = self.getOrAddInt('event','start_offset', -30)
        self.event.event_stop_offset_sec = self.getOrAddInt('event','end_offset', 30)

        # Read Camera
        self.camera.photo_count = self.getOrAddInt('camera', 'photos_count', fallback = 5)
        self.camera.photo_delay_sec = self.getOrAddInt('camera', 'photo_delay_sec', fallback = 1)

        # Read Network
        self.network.ping_test_url = self.getOrAdd('network','ping_test_url', fallback = 'https://www.google.com')
        self.network.aws_bucket_name = self.getOrAdd('network', 'aws_bucket_name', fallback = 's3://factorem001')

        # Read Health
        self.health.min_disk_mb = self.getOrAddInt('health','min_disk_mb', fallback = 200)
        self.health.min_disk_percent = self.getOrAddFloat('health', 'min_disk_percent', fallback = '0.1')
        self.health.reboot_required = self.getOrAddBool('health', 'reboot_required', False)
        self.health.restart_required = self.getOrAddBool('health', 'restart_required', False)
        self.health.stop_required = self.getOrAddBool('health','stop_required', False)

    def hasSectionOption(self, src, section, option):

        addSection = False
        addOption = False
        if not src.has_section(section):
            addSection = True
        elif not src.has_option(section, option):
            addOption = True
        return addSection, addOption

    def addSectionOption(self, src, addSection, section, option, fallback):

        tmp = tempfile.NamedTemporaryFile(mode = 'w+t', delete=False)
        dst = ConfigParser()
        for s in src.sections():
            if not dst.has_section(s):
                dst.add_section(s)

            for k, v in src.items(s):
                dst.set(s, k, v)

        if addSection:
            dst.add_section(section)

        print(f'Adding {section} {option} {fallback}')
        dst.set(section, option, str(fallback))
        dst.write(tmp)

        file_name = tmp.name
        tmp.close()
        shutil.copy(file_name, self.config_path)
        os.remove(file_name)

    def getOrAdd(self, section:str, option:str, fallback:str):
        addSection = False
        addOption = False

        src = ConfigParser()
        src.read(self.config_path)

        addSection, addOption = self.hasSectionOption(src, section, option)
            
        if not addSection and not addOption:
            return src.get(section, option, fallback = fallback)

        self.addSectionOption(src, addSection, section, option, fallback)

        return fallback

    def addOrUpdate(self, section:str, option:str, value):
        stored_value = self.getOrAdd(section,option,str(value))
        if stored_value != value:
            self.update(section, option, str(value))
        
        return value

    def getOrAddBool(self, section:str, option:str, fallback:bool):
        addSection = False
        addOption = False

        src = ConfigParser()
        src.read(self.config_path)

        addSection, addOption = self.hasSectionOption(src, section, option)
            
        if not addSection and not addOption:
            return src.getboolean(section, option, fallback = fallback)

        self.addSectionOption(src, addSection, section, option, fallback)

        return fallback

    def getOrAddInt(self, section:str, option:str, fallback:int):
        addSection = False
        addOption = False

        src = ConfigParser()
        src.read(self.config_path)

        addSection, addOption = self.hasSectionOption(src, section, option)
            
        if not addSection and not addOption:
            return src.getint(section, option, fallback = fallback)

        self.addSectionOption(src, addSection, section, option, fallback)

        return fallback

    def getOrAddFloat(self, section:str, option:str, fallback:float):
        addSection = False
        addOption = False

        src = ConfigParser()
        src.read(self.config_path)

        addSection, addOption = self.hasSectionOption(src, section, option)
            
        if not addSection and not addOption:
            return src.getfloat(section, option, fallback = fallback)

        self.addSectionOption(src, addSection, section, option, fallback)

        return fallback

    def update(self, section, option, value):
        parser = SafeConfigParser()
        parser.read(self.config_path)
        if not parser.has_section(section):
            parser.add_section(section)
        parser.set(section, option, str(value))
        with open(self.config_path, "w+") as configfile:
            parser.write(configfile)

    def reboot_set(self):
        self.getOrAddBool('health', 'reboot_required', True)
        self.update('health','reboot_required', True)

    def is_reboot_required(self, required = False):
        r = self.getOrAddBool('health', 'reboot_required', required)
        if required != r:
            self.update('health','reboot_required',required)
        return required

    def reboot_clear(self):
        self.update('health','reboot_required', False)

    def is_restart_required(self):
        return self.getOrAddBool('health', 'restart_required', False)

    def restart_set(self):
        self.getOrAddBool('health', 'restart_required', True)
        self.update('health','restart_required', True)

    def restart_clear(self):
        self.update('health','restart_required', False)

    def stop_set(self, required):
        self.getOrAddBool('health','stop_required', required)
        self.update('health','stop_required', required)

    def is_stop_required(self):
        return self.getOrAddBool('health','stop_required', False)

    def stop(self):
        self.getOrAddBool('health','stopped',False)
        self.update('health', 'stopped', True)

    def stop_clear(self):
        self.getOrAddBool('health','stopped', False)
        self.update('health','stopped',False)

    def is_stopped(self):
        return self.getOrAddBool('health','stopped',False)

cfg = Config()