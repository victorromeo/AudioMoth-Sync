#!/usr/bin/env bash

lockdir=/tmp/am_reverse_ssh.lock

if mkdir "$lockdir"
then
  echo >&2 "successfully acquired lock"

  # Remove lockdir when the script finishes, or when it receives a signal
  trap 'rm -rf "$lockdir"' 0    # remove directory when script finishes

  # Optionally create temporary files in this directory, because
  # they will be removed automatically:
  tmpfile=$lockdir/filelist

else
  echo >&2 "cannot acquire lock, giving up on $lockdir"
  exit 0
fi

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPT_PATH=$(dirname "${SCRIPT}")
# App Root
APP_PATH=$(dirname "${SCRIPT_PATH}"..)

# Log the action
DATE=$(date +"%Y%m%d")
TIME=$(date +"%H%M%S")
LOG="${APP_PATH}/capture/logs/system.$DATE.log"
echo "${DATE} ${TIME} \"Reverse SSH\" $APP_PATH" >> "$LOG"

# Perform the action
ssh -R 19999:localhost:22 ubuntu@agtech.factorem.com.au -i ~/m2.pem
