#!/usr/bin/env python3

#import sys
#sys.path.append("./lib")

import os
import crontab
from signal import pause
from time import sleep
from threading import Thread, ThreadError
from statistics import mean
import pijuice

from lib.log import logging
from lib.audiomoth import audiomoth
from lib.camera import camera
from lib.diskio import diskio
from lib.config import cfg

c = camera()
am = audiomoth()
d = diskio()
pij = pijuice.PiJuice()
q = []
ql = 10
qr = 0.0

def app_path():
    return os.path.dirname(os.path.abspath(__file__))

def job_path():
    return app_path() + '/jobs'

def install_cron_job(tab:crontab.CronTab, command:str, comment:str):
    jobs_by_comment = tab.find_comment(comment)

    for job in jobs_by_comment:
        if job.comment == comment:
            return job
    
    return tab.new(command=command, comment=comment)

def install_cron_jobs():
    tab = crontab.CronTab(user=True)

    install_cron_job(tab,f'{job_path()}/job_git_pull.sh','job1').minute.every(10)
    install_cron_job(tab,f'{job_path()}/job_cleanup.sh','job2').hour.every(2)
    install_cron_job(tab,f'{job_path()}/job_check_power.py','job3').hour.every(1)
    install_cron_job(tab,f'{job_path()}/job_network_switch.sh','job4').minute.every(1)
    install_cron_job(tab,f'{job_path()}/job_reverse_ssh.sh','job5').hour.every(1)
    install_cron_job(tab,f'{job_path()}/job_send_heartbeat.py','job6').minute.every(1)
    install_cron_job(tab,f'{job_path()}/job_sync_aws.sh','job7').minute.every(15)
    
    tab.write()

def on_motion():
    logging.info("on_motion")
    print("Recording starting")
    x = Thread(target=am.unmountMoth, args=())
    y = Thread(target=c.click, args=(cfg.camera.photo_count, cfg.camera.photo_delay_sec))
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
    d.transfer_audio(cfg.paths.audiomoth, cfg.paths.recordings)

def enqueue(io):
    q.append(io)
    if len(q) > cfg.motion.motion_queue_length:
        q.pop(0)

def motion():
    return not (len(q) == cfg.motion.motion_queue_length \
        and mean(q) < cfg.motion.motion_threshold_inactive)

def movement():
    m = int(pij.status.GetIoDigitalInput(2)['data'])
    print(m, end='')
    return m

# Configure
install_cron_jobs()

# Main Loop
while True:
    if movement() > 0:
        on_motion()
        q.clear()

        # Detect when motion stops
        enqueue(movement())
        while motion():
            sleep(1)
            enqueue(movement())

        on_no_motion()

    if cfg.reboot_required():
        print('Rebooting')
        logging.info('Rebooting')
        am.unmountMoth()
        cfg.reboot_clear()
        os.system('sudo shutdown -r 1')
    
    if cfg.restart_required():
        print('Restarting')
        logging.info('Restarting')
        am.unmountMoth()
        cfg.restart_clear()
        exit()