#!/bin/bash

# Check before continuing
read -p "Modify Cron to support PiJuice (y/n)? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then

    DATE=$(date +%Y%m%d)
    filename="cron.${DATE}-000.txt"
    num=0
    while [ -f $filename ]; do
        num=$(( $num + 1 ))
        filename="cron.${DATE}-${num}.txt"
    done

    # Get Cron for su
    mkdir -p cron
    sudo crontab -l > ./cron/$filename

    # Remove all AudioMoth entries
    sed '/AudioMoth/d' ./cron/$filename > ./cron/cron.txt

    # Add new AudioMoth entries
    echo "@reboot /usr/bin/python3 $PWD/system/wakeup.py" >> ./cron/cron.txt
    echo "@reboot /usr/bin/python3 $PWD/system/shutdown.py" >> ./cron/cron.txt

    # Install new CronTab for Sudo
    sudo crontab ./cron/cron.txt
    rm ./cron/cron.txt

    echo 'Cron updated'
fi

# Check before continuing
read -p "Modify udev rules.d to support AudioMoth (y/n)? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then

    # Create the rules.d entries
    echo 'ACTION=="add", ATTRS{model}=="EFM32 MSD Device", SUBSYSTEMS=="scsi", SYMLINK+="moth%n"' | sudo tee /etc/udev/rules.d/99-AudioMoth.rules
    echo '#ACTION=="add", ATTRS{idProduct}=="0002", ATTRS{idVendor}=="10c4", SUBSYSTEMS=="block", SYMLINK+="moth%n"' | sudo tee -a /etc/udev/rules.d/99-AudioMoth.rules
    echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="0002", MODE="0666"' | sudo tee -a /etc/udev/rules.d/99-AudioMoth.rules
    sudo udevadm control --reload

    echo 'rules.d updated'
fi