#!/bin/bash
usage()
{
cat << EOF
usage: $0 options

This script updates the local installation and forces all CRON task updates and therefore must be run as sudo

OPTIONS:
   -h                Show this message
   -p <root_path>    Path to AudioMoth-Sync root
EOF
}

while getopts hp: option
do
case "${option}"
in
h) 
    usage
    exit 1
    ;;
p) CWD=${OPTARG};;
esac
done

if [ -z $CWD ]
then
     usage
     exit 1
fi

dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "$dt"

# Pull the latest GIT repository, to ensure scripts and python packages are their most current
echo 'Updating local git repository'
git pull

# Update the CRON tasks
echo 'Updating CRON tasks'
sh $CWD/system/cron_update.sh -p $CWD
sh $CWD/system/cron_aws_sync.sh -p $CWD
sh $CWD/system/cron_pijuice.sh -p $CWD

echo 'Update Complete'
