import sys
sys.path.append("..") # Adds higher directory to python modules path.
sys.path.append("../lib") # Adds higher directory to python modules path.

from configuration import configuration as config
from log import logging
import os
from datetime import datetime

now = datetime.now()
deviceName = config.device_name
bucketName = config.aws_bucket_name
sourcePath = config.local_visual_path

#Sync files remotely
awsVisualSync = "aws s3 sync {0} s3://{1}/{2}/photo".format(sourcePath,bucketName,deviceName)

print(awsVisualSync)
try:
    logging.info('Sync Photos - Start')
    os.system(awsVisualSync)
except:
    logging.info('Sync Photos - Error')
finally:
    logging.info('Sync Photos - Stop')