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
from lib.event import event

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

    install_cron_job(tab,f'{job_path()}/job_launch.sh','job0').minute.every(10)
    install_cron_job(tab,f'{job_path()}/job_git_pull.sh','job1').minute.every(10)
    install_cron_job(tab,f'{job_path()}/job_cleanup.sh','job2').hour.every(2)
    install_cron_job(tab,f'{job_path()}/job_check_power.py','job3').hour.every(30)
    install_cron_job(tab,f'{job_path()}/job_network_switch.sh','job4').minute.every(1)
    install_cron_job(tab,f'{job_path()}/job_reverse_ssh.sh','job5').hour.every(1)
    install_cron_job(tab,f'{job_path()}/job_send_heartbeat.py','job6').minute.every(1)
    install_cron_job(tab,f'{job_path()}/job_sync_aws.sh','job7').minute.every(15)

    tab.write()

def on_motion():
    # Creating a new event automatically logs it
    e = event()

    logging.info("on_motion")

    min_recording_time = cfg.getOrAddInt('audio','min_recording_time', 60)

    c.click(cfg.camera.photo_count, cfg.camera.photo_delay_sec)

    sleep(min_recording_time if min_recording_time > 1 and min_recording_time < 3600 else 60)

def on_no_motion():
    logging.info("on_no_motion")

    print("Recording stopping")
    x = Thread(target=am.mountMoth, args=())
    x.start()
    x.join()
    print("Transferring audio")

    d.transfer_audio(cfg.paths.audiomoth, cfg.paths.recordings)

    print("Transferred audio")
    y = Thread(target=am.unmountMoth, args=())
    y.start()
    y.join()

    print("Recording started")

def enqueue(io):
    q.append(io)
    if len(q) > cfg.motion.motion_queue_length:
        q.pop(0)

def motion():
    return len(q) < cfg.motion.motion_queue_length \
        or mean(q) > cfg.motion.motion_threshold_inactive

def movement():
    m = int(pij.status.GetIoDigitalInput(2)['data'])
    print(m, end='', flush=True)
    return m

# Configure
# install_cron_jobs()

attempt=1
max_attempt=3
success=False
while attempt <= max_attempt and not success:
    try:
        am.resetMoth()
        success = am.mountMoth()

        # Clean up the AudioMoth to begin
        d.remove_files(am.mount_path, pattern = "*.WAV", sudo = True)
        d.check_disk(report = True, display = True, path = am.mount_path)

        # Configure the AudioMoth for the next recording session
        am.resetMoth()
        sleep(1)
        am.usbModeOn()
        am.setTime()

        # Unmount to allow recording to commence
        am.unmountMoth()
        success = True
    except:
        print(f'Startup attempt {attempt} of {max_attempt} failed')
        attempt = attempt + 1

if not success:
    logging.warning('AudioMoth startup failed')
    print('Please check AudioMoth')
    exit()

# Main Loop
while True:
    if movement() > 0:
        on_motion()
        q.clear()

        # Detect when motion stops
        enqueue(movement())
        while motion():
            enqueue(movement())

        on_no_motion()

    if cfg.is_reboot_required():
        print('Rebooting')
        logging.info('Rebooting')
        am.unmountMoth()
        cfg.reboot_clear()
        cfg.stop_clear()
        os.system('sudo shutdown -r 1')

    if cfg.is_restart_required():
        print('Restarting')
        logging.info('Restarting')
        am.unmountMoth()
        cfg.restart_clear()
        exit()

    while cfg.is_stop_required():
        cfg.stop()
        print('Paused', flush=True)
        logging.info('Paused')

        while cfg.is_stop_required():
            sleep(1)

        cfg.stop_clear()
        logging.info('Resumed')
        print('Resumed', flush=True)
