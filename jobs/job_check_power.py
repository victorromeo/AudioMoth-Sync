#!/usr/bin/env python3

# This script determines the current state of the power source, 
# and shuts down if the calculated power remaining requires it to be conserved.

import pijuice
import os
import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)

now = datetime.datetime.now()

activity_log = f'{app_dir}/capture/logs/activity.{now:%Y%m%d}.log'

pij = pijuice.PiJuice()

result = {
    'status' : {
        "status": pij.status.GetStatus(),
        'batteryVoltage' : pij.status.GetBatteryVoltage(),
        'batteryCurrent' : pij.status.GetBatteryCurrent(),
        'batteryTemperature' : pij.status.GetBatteryTemperature(),
        "ioVoltage" : pij.status.GetIoVoltage(),
        "io1" : {
            "analogInput" : pij.status.GetIoAnalogInput(1) \
                if pij.config.GetIoConfiguration(1)['error'] != 'COMMUNICATION_ERROR' \
                    and pij.config.GetIoConfiguration(1)['data']['mode'] == 'ANALOG_IN' \
                        else None,
            "digitalInput" : pij.status.GetIoDigitalInput(1) \
                if pij.status.GetStatus()['error'] != 'COMMUNICATION_ERROR' \
                    and pij.config.GetIoConfiguration(1)['data']['mode'] == 'DIGITAL_IN' \
                        else None,
            "digitalOutput" : pij.status.GetIoDigitalOutput(1) \
                if pij.status.GetStatus()['error'] != 'COMMUNICATION_ERROR' \
                    and pij.config.GetIoConfiguration(1)['data']['mode'] == 'DIGITAL_OUT' \
                        else None,
            "ioPWM" : pij.status.GetIoPWM(1) \
                if pij.status.GetStatus()['error'] != 'COMMUNICATION_ERROR' \
                    and (pij.config.GetIoConfiguration(1)['data']['mode'] == 'PWM_OUT_PUSHPULL' \
                        or pij.config.GetIoConfiguration(1)['data']['mode'] == 'PWM_OUT_OPEN_DRAIN') \
                        else None,
        },
        "io2" : {
                  "analogInput" : pij.status.GetIoAnalogInput(2) \
                if pij.status.GetStatus()['error'] != 'COMMUNICATION_ERROR' \
                    and pij.config.GetIoConfiguration(2)['data']['mode'] == 'ANALOG_IN' \
                        else None,
            "digitalInput" : pij.status.GetIoDigitalInput(2) \
                if pij.status.GetStatus()['error'] != 'COMMUNICATION_ERROR' \
                    and pij.config.GetIoConfiguration(2)['data']['mode'] == 'DIGITAL_IN' \
                        else None,
            "digitalOutput" : pij.status.GetIoDigitalOutput(2) \
                if pij.status.GetStatus()['error'] != 'COMMUNICATION_ERROR' \
                    and pij.config.GetIoConfiguration(2)['data']['mode'] == 'DIGITAL_OUT' \
                        else None,
            "ioPWM" : pij.status.GetIoPWM(2) \
                if pij.status.GetStatus()['error'] != 'COMMUNICATION_ERROR' \
                    and (pij.config.GetIoConfiguration(2)['data']['mode'] == 'PWM_OUT_PUSHPULL' \
                        or  pij.config.GetIoConfiguration(2)['data']['mode'] == 'PWM_OUT_OPEN_DRAIN') \
                        else None,
        },
    },
    "config": {
        "profile" : pij.config.GetBatteryProfile(),
        "chargingConfig" : pij.config.GetChargingConfig(),
        "sw1" : pij.config.GetButtonConfiguration('SW1'),
        "sw2" : pij.config.GetButtonConfiguration('SW2'),
        "sw3" : pij.config.GetButtonConfiguration('SW3'),
        "io1" : pij.config.GetIoConfiguration(1),
        "io2" : pij.config.GetIoConfiguration(2),
    },
    "power": {
        "powerOff": pij.power.GetPowerOff(),
        "systemPowerSwitch": pij.power.GetSystemPowerSwitch(),
        "wakeUpOnCharge": pij.power.GetWakeUpOnCharge(),
        "watchdog" : pij.power.GetWatchdog()
    }
}

with open(activity_log, 'a+') as l:
    l.write(f'\n{now:%Y%m%d %H%M%S} "Check Battery" {app_dir} {result}\n')

if __name__ == '__main__':
    print(result)
