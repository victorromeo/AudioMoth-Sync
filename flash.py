#!/usr/bin/env python3

from crontab import CronTab, CronItem
from time import sleep
import sys

try:
    from lib.audiomoth import audiomoth
    from lib.config import Config
    from lib.log import logging
except:
    print('Failed to load dependencies')
    exit()

print('Flashing Moth', flush=True)
logging.info('Flashing Moth')

cfg = Config()
cfg.stop_required(True)

n = 120
while not cfg.is_stopped():
    sleep(1)
    n=n-1
    print('s', flush=True)

    if (n < 0): 
        print('Flashing failed waiting for Device to stop', flush=True)
        cfg.stop_clear()
        exit()

# Prevent CRON from starting the AudioMoth Sync
ct = CronTab(user=True)
ci = CronItem()

jobs = ct.find_comment("Job0")
for job in jobs:
    job.enable(False)

ct.write_to_user(user=True)

try:
    am = audiomoth()
    am.flash()

    for job in jobs:
        job.enable(True)

    ct.write_to_user(user=True)
    logging.info('Flashing Moth complete') 

except Exception:
    print(f'Flashing failed {sys.exc_info()[1]}')
    logging.error(f'Flashing failed: {sys.exc_info()[1]}')

cfg.stop_required(False)
