import os
from datetime import datetime

now = datetime.now()
deviceName = "AgTech01"
bucketName = "factorem001"

# Moth Source
mothPath = "/media/pi/MothMon"

# Cloud Destination
s3Bucket = "s3://{0}/{1}".format(bucketName, deviceName)

# Default Local Paths
audioPath = "audio"
photoPath = "visual"

# Take a photo
takePhoto = 'raspistill -o ./{0}/{1:%Y%m%d%H%M}.jpg'.format(photoPath, now)
print(takePhoto)
#os.system(takePhoto)

# Copy audio files locally
listMothFiles = "ls -la {0}/*.WAV".format(mothPath)
copyFiles = "cp ./{0}/*.WAV {1}".format(mothPath, audioPath)
delMothFiles = "rm {0}/*.WAV".format(mothPath)
delLocalFiles = "rm ./{0}/*.WAV".format(audioPath)

print(listMothFiles)
print(copyFiles)
print(delMothFiles)
print(delLocalFiles)

#os.system(listFiles)
#os.system(copyFiles)
 
#Sync files remotely
awsAudioSync = "aws s3 sync ./{0} {1}/{0}".format(audioPath,s3Bucket)
awsVisualSync = "aws s3 sync ./{0} {1}/{0}".format(photoPath,s3Bucket)

print(awsAudioSync)
#os.system(awsAudioSync)
print(awsVisualSync)
#os.system(awsVisualSync)
