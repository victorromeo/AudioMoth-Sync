usage()
{
cat << EOF
usage: $0 options

This script installs a CRON task to perform regular AWS sync operations

OPTIONS:
   -h                Show this message
   -p <root_path>    Path to AudioMoth-Sync root
   -d <device_name>  Device Name
   -b <bucket name>  Bucket Name
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

if [ -z $CWD ]
then
     usage
     exit 1
fi

# Create a Cron backup store
mkdir -p $CWD/cron

DATE=$(date +%Y%m%d)
filename="cron.${DATE}-00000.txt"
num=0
while [ -f $CWD/cron/$filename ]; do
    num=$(( $num + 1 ))
    filename=$(printf "cron.%s-%05d.txt" $DATE $num)
done

# Get Cron for su
sudo crontab -l > $CWD/cron/$filename
cat $CWD/cron/$filename > $CWD/cron/cron.txt

# Remove all AWS sync script entries
sed -i '/system\/aws_sync\.sh/d' $CWD/cron/cron.txt

# Run the aws_sync.sh script hourly, (git pull etc.) and log the results
echo "@hourly cd $CWD && sh $CWD/system/aws_sync.sh -p $CWD -b $BUCKET -d $DEVICE >> $CWD/capture/logs/system.log" >> $CWD/cron/cron.txt

# Install new CronTab for Sudo
sudo crontab $CWD/cron/cron.txt

echo 'Cron updated'
