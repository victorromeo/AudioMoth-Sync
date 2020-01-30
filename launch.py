#!/usr/bin/env python3

#import sys
#sys.path.append("./lib")

import os
import crontab
from signal import pause
from time import sleep
from threading import Thread, ThreadError

from lib.log import logger
from lib.audiomoth import audiomoth
from lib.camera import camera
from lib.diskio import diskio
from lib.config import cfg
from lib.event import event, latest_event, event_queue
from lib.power import PiJuicePower as Power
from datetime import datetime, timedelta

c = camera()
am = audiomoth()
d = diskio()
p = Power()
pij = p.pij

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
    logger.info("on_motion")
    c.click(cfg.camera.photo_count, cfg.camera.photo_delay_sec, f'Event:{e.id}')

    init_sleep = e.get_seconds_until_stop()
    sleep(init_sleep if init_sleep > 0 else 1)

    return e

def on_no_motion(e:event):
    logger.info("on_no_motion")

    print("Recording stopping")
    x = Thread(target=am.mountMoth, args=())
    x.start()
    x.join()
    print("Transferring audio")

    d.transfer_audio(cfg.paths.audiomoth, cfg.paths.recordings, e)

    print("Transferred audio")
    y = Thread(target=am.unmountMoth, args=())
    y.start()
    y.join()

    print("Recording started")

def movement(e:event):
    m = int(pij.status.GetIoDigitalInput(2)['data'])
    print(m, end='', flush=True)
    
    return m

def check_restart():
    if cfg.is_restart_required():
        print('Restarting')
        d.sendmail(f"{cfg.name} Server Restarting", f"{cfg.name} Server Restarting", cfg.emailto)
        logger.info('Restarting')
        am.unmountMoth()
        cfg.restart_clear()
        exit()

def check_reboot():
    if cfg.is_reboot_required():
        print('Rebooting')
        logger.info('Rebooting')
        d.sendmail(f"{cfg.name} Server Restarting", f"{cfg.name} Server Rebooting", cfg.emailto)
        am.unmountMoth()
        cfg.reboot_clear()
        cfg.stop_clear()
        os.system('sudo shutdown -r 1')

def check_power():
    if p.should_sleep():
        status = p.status()
        print('Pi powerdown due to Power state')
        logger.info(f'Pi powerdown due to Power state: {status}')
        d.sendmail(f'{cfg.name} Server Powerdown', f'{cfg.name} Server Powerdown \n{status}', cfg.emailto)

def send_status_email():
    global send_status_email_at
    now = datetime.utcnow()

    if send_status_email_at is None:
        send_status_email_at = now

    if send_status_email_at <= now:
        send_status_email_at = now + timedelta(minutes = 5)
        power = p.status()
        wifi_details = d.wifi_details()
        wifi_networks = d.wifi_networks()
        d.sendmail(cfg.name, f"{cfg.name} Server Starting\nWiFi\n{wifi_details}\nNetworks\n{wifi_networks}\npower\n{power}", cfg.emailto)

attempt=1
max_attempt=3
success=False
send_status_email_at = datetime.utcnow()
pi_disk_check = d.check_disk(report = True, display = True, path = cfg.paths.root )

moth_disk_check = {}
send_status_email()

while attempt <= max_attempt and not success:
    try:
        am.resetMoth()
        am.mountMoth()

        # Clean up the AudioMoth to begin
        d.remove_files(am.mount_path, pattern = "*.WAV", sudo = True)
        moth_disk_check = d.check_disk(report = True, display = True, path = am.mount_path)

        # Configure the AudioMoth for the next recording session
        am.usbModeOn()
        am.setTime()

        # Unmount to allow recording to commence
        am.unmountMoth()
        success = True
    except:
        print(f'Startup attempt {attempt} of {max_attempt} failed')
        attempt = attempt + 1

if not success:
    logger.warning('AudioMoth startup failed')
    print('Please check AudioMoth')
    d.sendmail(cfg.name, f"{cfg.name} Error: AudioMoth Failure", cfg.emailto)
    sleep(5)

    exit()

# Main Loop
while True:
    if movement(None) > 0:
        e = on_motion()
        d.sendmail(cfg.name, f"{cfg.name} Motion Event (id:{e.id})", cfg.emailto)

        # Detect when motion stops
        while not e.has_ended(): 
            e.enqueue(movement(e))

        on_no_motion(e)

    check_power()
    check_reboot()
    check_restart()

    while cfg.is_stop_required():
        cfg.stop()
        print('Paused', flush=True)
        d.sendmail(f"{cfg.name} Server Stop", f"{cfg.name} Server Stop", cfg.emailto)
        logger.info('Paused')

        while cfg.is_stop_required():
            sleep(1)

            check_power()
            check_reboot()
            check_restart()

        cfg.stop_clear()
        logger.info('Resumed')
        d.sendmail(f"{cfg.name} Server Resume", f"{cfg.name} Server Resume", cfg.emailto)
        print('Resumed', flush=True)
