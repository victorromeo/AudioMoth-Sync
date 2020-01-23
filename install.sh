#!/bin/bash

uname -n > device
echo "$PWD" > root

aws_region="ap-southeast-2"

sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install python3 python3-pip -y
sudo apt-get install wireless-tools -y
sudo apt-get install pijuice-base -y

echo 'Installing AWS CLI'
sudo apt-get install awscli -y
aws --version

# Create the rules.d entries
echo 'ACTION=="add", ATTRS{model}=="EFM32 MSD Device", SUBSYSTEMS=="scsi", SYMLINK+="moth%n"' | sudo tee /etc/udev/rules.d/99-AudioMoth.rules
echo '#ACTION=="add", ATTRS{idProduct}=="0002", ATTRS{idVendor}=="10c4", SUBSYSTEMS=="block", SYMLINK+="moth%n"' | sudo tee -a /etc/udev/rules.d/99-AudioMoth.rules
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="0002", MODE="0666"' | sudo tee -a /etc/udev/rules.d/99-AudioMoth.rules
sudo udevadm control --reload

echo 'rules.d updated'

# Install RTC 
printf -v date '%(%Y-%m-%d %H:%M:%S)T\n' -1
sudo date -s "${date}"
sudo hwclock -w

if cat /etc/rc.local | grep -q -w "sudo hwclock -s"
    then echo "hwclock found, so rc.local does not need to be modified."
    else echo 'sudo hwclock -s' | sudo tee -a /etc/rc.local
fi
echo 'PiJuice RTC clock updated'

sudo mkdir -p /mnt/Moth
sudo chown pi:pi /mnt/Moth
sudo chmod 660 /mnt/Moth

echo 'AudioMoth-Sync installation complete'

