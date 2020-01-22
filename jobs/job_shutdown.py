#!/usr/bin/env python3

import os
import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)

now = datetime.datetime.now()

activity_log = f'{app_dir}/capture/logs/system.{now:%Y%m%d}.log'

# TODO Stop AudioMoth here

with open(activity_log, 'a+') as l:
    l.write(f'{now:%Y%m%d %H%M%S} "Shutdown" {app_dir}\n')
