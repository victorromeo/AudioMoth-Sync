# AudioMoth-Sync

## logs

**All records are in UTC time**

This folder is reserved for the destination of log files generated while processing the python scripts in the parent folder. The logs will be synchronised into the cloud, and deleted daily, via a cron job.

### system-[%Y%m%d]-.log
(daily log file)

The System log is for background tasks which manage the operating system
- job_check_power    Gets details of the current power supply and battery
- job_cleanup        Removes old files
- job_git_pull       Gets the latest AudioMoth-Sync
- job_launch         Starts AudioMoth-Sync
- job_network_switch Switches Wifi networks if offline by highest wpa_supplicant priority
- job_reverse_ssh    Establishes a SSH reverse tunnel to the main agtech server
- job_send_heartbeat Sends a message to the agtech server regularly to notify of connectivity
- job_startup        Called when the host device starts up @reboot
- job_stop           Called to stop the AudioMoth-Sync, setting a config.ini flag
- job_sync_aws       Sends the current audio, photo, video and log data to S3, then pulls latest binary files and AudioMoth firmware

All records should follow the following pattern:

%Y%m%d-%H%m%s $HOSTNAME "alias" /path/to/script.sh

### activity-[%Y%m%d].log

The activity log is for internal operations done within the AudioMoth-Sync application

%Y%m%d-%H%m%s $HOSTNAME "operation" "action" "result"

### event.log

An incremental logfile to record all detection events.
Useful to correlate logs, audio, photos and video files

$EVENT_ID %Y-%m-%dT%H:%m:%s.%fffff:%zzzz $HOSTNAME
