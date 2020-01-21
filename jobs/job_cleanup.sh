#!/usr/bin/env bash

lockdir=/tmp/am_cleanup.lock

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
LOG="${APP_PATH}/capture/logs/activity.$DATE.log"
echo "${DATE} ${TIME} \"Job Cleanup\" $APP_PATH" >> "$LOG"

# Perform the action
find $APP_PATH/capture/logs -type f -mtime +7 -name '*.log' -execdir rm -- '{}' \; >> "$LOG" 2>&1
find $APP_PATH/capture/photos -type f -mtime +7 -name '*.jpg' -execdir rm -- '{}' \; >> "$LOG" 2>&1
find $APP_PATH/capture/recordings -type f -mtime +7 -name '*.wav' -execdir rm -- '{}' \; >> "$LOG" 2>&1

exit 0