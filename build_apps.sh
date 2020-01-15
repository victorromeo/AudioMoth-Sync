#!/bin/bash

# exit when any command fails
set -e

# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

## Show description

echo "Build sub-components for AudioMoth-Sync"
echo " - AudioMoth firmware"
echo " - AudioMoth flash"
echo " - AudioMoth usbhidtool"

# Check before continuing
read -p "Are you sure? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Recreate build folder
    mkdir -p build
    cd build

    sudo apt-get update -y
    sudo apt-get upgrade -y
    sudo apt-get install git curl pv cmake make -y

    # Build dependencies are architecture specific

    if ! [ -f "./gcc-arm-none-eabi.tar.bz2" ]; then

        echo 'Fetching gcc-arm-none-eabi'
        arch=$(uname -m)

        if [[ $arch == x86_64* ]]; then
            echo "X64 Architecture"
            curl -L -o gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2 https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2019q4/RC2.1/gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2?revision=6e63531f-8cb1-40b9-bbfc-8a57cdfc01b4&la=en&hash=F761343D43A0587E8AC0925B723C04DBFB848339
            ln -s gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2 gcc-arm-none-eabi.tar.bz2 

        elif [[ $arch == i*86 ]]; then
            echo "X32 Architecture"
            curl -L -o gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2 https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2019q4/RC2.1/gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2?revision=6e63531f-8cb1-40b9-bbfc-8a57cdfc01b4&la=en&hash=F761343D43A0587E8AC0925B723C04DBFB848339
            ln -s gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2 gcc-arm-none-eabi.tar.bz2 

        elif  [[ $arch == arm* ]]; then
            echo "ARM Architecture"
            curl -L -o gcc-arm-none-eabi-9-2019-q4-major-aarch64-linux.tar.bz2 https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2019q4/RC2.1/gcc-arm-none-eabi-9-2019-q4-major-aarch64-linux.tar.bz2?revision=490085f7-6fa7-49d0-b860-f437916e05eb&la=en&hash=568E0D184DE11F1FE02538BABB850CA41BC7C1CD
            ln -s gcc-arm-none-eabi-9-2019-q4-major-aarch64-linux.tar.bz2 gcc-arm-none-eabi.tar.bz2 

        fi

    else echo 'Found gcc-arm-none-eabi.tar.bz2 skipping download'
    fi

    echo 'Extracting gcc-arm-none-eabi. Please wait.'
    rm -rf gcc-arm-none-eabi
    mkdir gcc-arm-none-eabi
    pv gcc-arm-none-eabi.tar.bz2 | tar -xj --strip-components=1 -C ./gcc-arm-none-eabi

    export PATH=$PATH:$PWD/gcc-arm-none-eabi/arm-none-eabi/bin/

    build_path=$PWD

    # Building the AudioMoth firmware
    rm -rf ./AudioMoth-MSD
    git clone --recurse-submodules https://github.com/victorromeo/AudioMoth-MSD.git 
    cd AudioMoth-MSD

    mkdir -p build-release
    cd build-release
    cmake -DCMAKE_BUILD_TYPE=Release ..
    make
    # TODO copy firmware to firmware folder

    cd $build_path

    # Building AudioMoth flash
    rm -rf ./Flash
    git clone https://github.com/OpenAcousticDevices/Flash.git
    cd Flash/src/non-windows/linux
    chmod 700 build.sh
    ./build.sh

    cd $build_path

    # Building AudioMoth USB HID Tool
    rm -rf ./USB-HID-Tool
    git clone https://github.com/OpenAcousticDevices/USB-HID-Tool.git
    cd USB-HID-Tool/src/linux
    chmod 700 build.sh
    ./build.sh
fi

