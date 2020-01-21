#!/usr/bin/env python3

import os
import datetime
import pijuice
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)

now = datetime.datetime.now()

activity_log = f'{app_dir}/capture/logs/activity.{now:%Y%m%d}.log'

print(activity_log)

with open(activity_log, 'a+') as l:
    l.write(f'{now:%Y%m%d %H%M%S} "Startup" {app_dir}')

# This script is started at reboot by cron
# Since the start is very early in the boot sequence we wait for the i2c-1 device

while not os.path.exists('/dev/i2c-1'):
    time.sleep(0.1)

pj = pijuice.PiJuice(1, 0x14)

pj.rtcAlarm.SetWakeupEnabled(True)