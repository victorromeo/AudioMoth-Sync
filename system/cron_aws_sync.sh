usage()
{
cat << EOF
usage: $0 options

This script installs a CRON task to perform regular AWS sync operations

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

if [[ -z $CWD ]]
then
     usage
     exit 1
fi

DATE=$(date +%Y%m%d)
filename="cron.${DATE}-000.txt"
num=0
while [ -f $filename ]; do
    num=$(( $num + 1 ))
    filename="cron.${DATE}-${num}.txt"
done

# Get Cron for su
mkdir -p $CWD/cron
sudo crontab -l > $CWD/cron/$filename

# Remove all AWS sync script entries
sed '/system\/aws_sync\.sh/d' $CWD/cron/$filename > $CWD/cron/cron.txt

# Run the aws_sync.sh script hourly, (git pull etc.) and log the results
echo "@hourly cd $CWD && sh $CWD/system/aws_sync.sh >> $CWD/capture/logs/system.log" >> $CWD/cron/cron.txt

# Install new CronTab for Sudo
sudo crontab $CWD/cron/cron.txt
rm $CWD/cron/cron.txt

echo 'Cron updated'