#!/bin/bash

usage()
{
cat << EOF
usage: $0 options

This script installs a CRON task to perform regular AWS sync operations

OPTIONS:
   -h                Show this message
   -p <root_path>    Path to AudioMoth-Sync root
   -d <device_name>  Device Name ie. device0001
   -b <bucket_name>  AWS bucket name.
EOF
}

while getopts hp:d:b: option
do
case "${option}"
in
h) 
    usage
    exit 1
    ;;
p) CWD=${OPTARG};;
d) DEVICE=${OPTARG};;
b) BUCKET=${OPTARG};;

esac
done

if [[ -z $CWD || -z $DEVICE || -z $BUCKET ]]
then
     usage
     exit 1
fi

dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "$dt"

echo 'AWS Sync'

# Send the latest images and audio to aws
aws s3 sync "${CWD}"/capture  s3://"${BUCKET}"/devices/"${DEVICE}"

# Get the latest releases of flash, usbhidtool and the Firmware
aws s3 sync s3://"${BUCKET}"/release "${CWD}"/apps

# Move the firmware into the correct location
rm -rf "${CWD}"/firmware/*.bin && mv "${CWD}"/apps/*.bin "${CWD}"/firmware
