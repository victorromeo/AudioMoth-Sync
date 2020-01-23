#!/usr/bin/env python3

import os
import datetime

from lib.config import cfg

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
app_dir = script_dir

now = datetime.datetime.now()

activity_log = f'{app_dir}/capture/logs/system.{now:%Y%m%d}.log'

cfg.reboot_set()

with open(activity_log, 'a+') as l:
    l.write(f'{now:%Y%m%d %H%M%S} "Shutdown" {script_path}\n')
