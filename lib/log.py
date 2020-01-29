import sys
sys.path.append("..") # Adds higher directory to python modules path.

import logging
import logging.handlers
import os
import re
from lib.config import cfg
import time

class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)
 
    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result

# class MyTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
#   def __init__(self, dir_log):

#    self.dir_log = dir_log

#    filename = self.get_filename() #dir_log here MUST be with os.sep on the end
#    logging.handlers.TimedRotatingFileHandler.__init__(self,filename, when='midnight', interval=1, backupCount=0, encoding=None, utc=True)
  
#   def doRollover(self):
#    """
#    TimedRotatingFileHandler remix - rotates logs on daily basis, and filename of current logfile is time.strftime("%m%d%Y")+".txt" always
#    """ 
#    self.stream.close()
#    # get the time that this sequence started at and make it a TimeTuple
#    t = self.rolloverAt - self.interval
   
#    timeTuple = time.gmtime(t)

#    self.baseFilename = self.get_filename()
#    print(f'{baseFilename}')
#    self.stream = open(self.baseFilename, 'w')
#    self.rolloverAt = self.rolloverAt + self.interval

#   def get_filename(self, t:time)->str:
#       return f'{self.dir_log}/activity.{time:%Y%m%d}.log'

# Create the global logger instance
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))

# Create a handler to manage file rotation
handler = logging.handlers.TimedRotatingFileHandler(f'{cfg.paths.logs}/activity', when='midnight', interval=1, backupCount=0, encoding=None, utc=True)

handler.setLevel(10)

# Set the format of the handler 
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# add a suffix which you want
handler.suffix = ".%Y%m%d.log"

#need to change the extMatch variable to match the suffix for it
handler.extMatch = re.compile(r"^.[0-9]{8}\.log$") 

# finally add handler to logger    
logger.addHandler(handler)
