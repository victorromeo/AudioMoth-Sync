# PIJUICE configuration

![PiJuice pins](https://i2.wp.com/learn.pi-supply.com/wp-content/uploads/2017/10/PiJuice-Pinout.png?w=1000&ssl=1)

## Prerequisite steps

1. Power down the Raspberry PI
2. Connect the PiJuice hat onto the Raspberry PI
3. Connect the battery, replacing the supplied low capacity battery
4. Connect the power supply to the PiJuice power port
5. Start the Raspberry PI by pressing the SW1 button, closest to the power port

## Setup the RTC clock

Running `i2cdetect -y 1` from bash will give the following result.  Note where `UU` appears, which in this case below is at `0x68`.

```bash
pi@rpi-stretch-full:~ $ i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- 14 -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- UU -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --                         
pi@rpi-stretch-full:~ $
```

1. To manually set the RTC clock, run `sudo date -s '2020-01-05 12:01:34` then `sudo hwclock -w` to write the time to the RTC chip
2. Add a line `sudo hwclock -s` into the `/etc/rc.local` file, to copy the RTC time back to the system clock at boot.

## Installation

1. First install the command line

  ```bash
  sudo apt-get install pijuice-base
  ```

1. Then install the GUI

   ```bash
   sudo apt-get install pijuice-gui
   ```

## PIR Alteration

The PIR requires a circuit modification to support a 3V3 supply voltage, instead of the onboard voltage regulator.

![PIR Rewire](https://hackster.imgix.net/uploads/attachments/927021/NatureJuice-PIR-Mod.jpg?auto=compress%2Cformat&w=740&h=555&fit=max)

1. Remove the 7133-1 chip, by adding solder to the 4 terminals (1 above and 3 below)
2. remove the diode, again by adding solder to the terminals
3. add an insulated jumper wire between the location of the now removed voltage regulator and diode, (wire shown in green)
4. Remove the header jumper
5. Tune the PIR
6. Connect the PIR to the PiJuice

![PIR Connect](https://hackster.imgix.net/uploads/attachments/927022/NatureJuice-PIR-P3.jpg?auto=compress%2Cformat&w=740&h=555&fit=max)

## Configuration

1. Start a bash terminal
2. Run `pijuice_cli`
3. Select the `System Task` menu page
   1. Select `System task enabled` checkbox
   2. Select the `Software Halt Power Off` Delay period (30 seconds)
   3. Select `Apply Settings`
   4. Select `Back` to return to the main menu
4. Open the `Battery Settings` page
   1. Select the `PJLIPO_12000` battery profile
   2. Using the down direction arrow on your keyboard, scroll down
   3. Select `Apply settings`
   4. Select `Back` to return to the main menu
5. Open the `IO Settings` page
    1. Select `IO2`
    2. Select `Mode: DIGITAL_IN`
    3. Select `Pull: PULLDOWN`
    4. Select `Wakeup: RISING_EDGE`
    5. Select `Apply`
    6. Select `Back` then `Back` again to return to the main menu
6. Select `Wakeup Alarm` page
   1. Select `Wakeup enabled` checkbox
   2. Select `Day`, `Every Day` and `Every Hour`
   3. Select `Minutes Period`
   4. Set Minute to 30 (Configurable)
   5. Select `Set Alarm`
   6. Select `Back` to return to the main menu

## Wake-up configuration

The following script (which is part of the project code already), ensures that following a wake up, the raspberry pi device is configured to allow future wake ups by alarm.

```bash
#!/usr/bin/python3
# This script is started at reboot by cron
# Since the start is very early in the boot sequence we wait for the i2c-1 device

import pijuice, time

while not os.path.exists('/dev/i2c-1'):
    time.sleep(0.1)

pj = pijuice.PiJuice(1, 0x14)

pj.rtcAlarm.SetWakeupEnabled(True)

```

run `sudo crontab -e`

add the following record

`@reboot /usr/bin/python3 /home/pi/Documents/AudioMoth-Sync/pijuiceWakeupEnable.py`
