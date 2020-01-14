import sys
sys.path.append("..") # Adds higher directory to python modules path.

from configuration import configuration as config

import os
from datetime import datetime

now = datetime.now()
deviceName = config.device_name
bucketName = config.aws_bucket_name
sourcePath = config.local_audio_path

# Moth Source
mothPath = config.am_mount_path

# Cloud Destination
s3Bucket = "s3://{0}/{1}".format(bucketName, deviceName)

#Sync files remotely
awsAudioSync = "aws s3 sync {0} {1}/{2}/audio".format(sourcePath,s3Bucket,deviceName,)

print(awsAudioSync)
os.system(awsAudioSync)
